"""
Degradation functions for Real-ESRGAN
Compatible with newer torchvision versions
"""
import math
import random
import torch
import torch.nn.functional as F

# Use the correct import for newer torchvision versions
try:
    from torchvision.transforms.functional import rgb_to_grayscale
except ImportError:
    # Fallback for older versions
    try:
        from torchvision.transforms.functional_tensor import rgb_to_grayscale
    except ImportError:
        def rgb_to_grayscale(img):
            if img.shape[0] == 3:
                return 0.299 * img[0:1] + 0.587 * img[1:2] + 0.114 * img[2:3]
            return img


def circular_lowpass_kernel(cutoff, kernel_size, pad_to=0):
    """2D sinc filter"""
    if kernel_size % 2 == 0:
        raise ValueError('kernel_size must be an odd number.')

    kernel = torch.zeros(kernel_size, kernel_size)
    kernel_center = kernel_size // 2

    for i in range(kernel_size):
        for j in range(kernel_size):
            distance = math.sqrt((i - kernel_center)**2 + (j - kernel_center)**2)
            if distance <= kernel_center:
                kernel[i, j] = cutoff * math.j0(cutoff * distance) / (2 * math.pi)
            else:
                kernel[i, j] = 0

    kernel = kernel / kernel.sum()
    return kernel


def random_mixed_kernels(kernel_list, kernel_prob, kernel_size=21, **kwargs):
    """Randomly generate mixed kernels"""
    kernel_type = random.choices(kernel_list, kernel_prob)[0]

    if kernel_type == 'iso':
        kernel = random_bivariate_gaussian(kernel_size, **kwargs, isotropic=True)
    elif kernel_type == 'aniso':
        kernel = random_bivariate_gaussian(kernel_size, **kwargs, isotropic=False)
    else:
        # Default to isotropic gaussian
        kernel = random_bivariate_gaussian(kernel_size, **kwargs, isotropic=True)

    return kernel


def random_bivariate_gaussian(kernel_size, sigma_x_range=(0.2, 1.0),
                             sigma_y_range=(0.2, 1.0), rotation_range=(-math.pi, math.pi),
                             noise_range=None, isotropic=True):
    """Generate bivariate Gaussian kernel"""
    assert kernel_size % 2 == 1, 'Kernel size must be an odd number.'

    sigma_x = random.uniform(sigma_x_range[0], sigma_x_range[1])

    if isotropic:
        sigma_y = sigma_x
        rotation = 0
    else:
        sigma_y = random.uniform(sigma_y_range[0], sigma_y_range[1])
        rotation = random.uniform(rotation_range[0], rotation_range[1])

    kernel = bivariate_gaussian(kernel_size, sigma_x, sigma_y, rotation, isotropic=isotropic)

    if noise_range is not None:
        noise = random.uniform(noise_range[0], noise_range[1])
        kernel = kernel * noise

    return kernel


def bivariate_gaussian(kernel_size, sig_x, sig_y, theta, isotropic=True):
    """Generate bivariate Gaussian kernel"""
    grid, _, _ = mesh_grid(kernel_size)

    if isotropic:
        sigma_matrix = torch.tensor([[sig_x**2, 0], [0, sig_x**2]])
    else:
        sigma_matrix = sig_x**2 * torch.tensor([[1, 0], [0, (sig_y/sig_x)**2]])

    rotation_matrix = torch.tensor([[torch.cos(theta), -torch.sin(theta)],
                                   [torch.sin(theta), torch.cos(theta)]])
    rotation_matrix = rotation_matrix.float()
    sigma_matrix = torch.mm(torch.mm(rotation_matrix, sigma_matrix), rotation_matrix.T)

    kernel = torch.exp(-0.5 * torch.sum(torch.mm(grid.reshape(-1, 2), torch.inverse(sigma_matrix)) * grid.reshape(-1, 2), dim=1))
    kernel = kernel.reshape(kernel_size, kernel_size)
    kernel = kernel / kernel.sum()

    return kernel


def mesh_grid(kernel_size):
    """Generate mesh grid"""
    ax = torch.arange(-kernel_size // 2 + 1., kernel_size // 2 + 1.)
    xx, yy = torch.meshgrid(ax, ax)
    xy = torch.stack([xx, yy], dim=-1)
    return xy, xx, yy


def random_add_poisson_noise_pt(img, scale_range=(0, 1.0), gray_prob=0.4):
    """Add random poisson noise"""
    b, _, h, w = img.size()
    device = img.device
    gray_noise = torch.rand(b, 1, 1, 1, device=device) < gray_prob
    poisson_scale = torch.empty(b, 1, 1, 1, device=device).uniform_(*scale_range)
    gray_scale = torch.empty(b, 1, 1, 1, device=device).uniform_(10, 25)

    if gray_noise.any():
        img_gray = rgb_to_grayscale(img)
        noise_gray = torch.poisson(img_gray * gray_scale) / gray_scale
        img = img * (1 - gray_noise) + noise_gray * gray_noise

    rgb_scale = torch.empty(b, 3, 1, 1, device=device).uniform_(16, 32)
    noise_rgb = torch.poisson(img * rgb_scale) / rgb_scale
    img = img * (1 - gray_noise) + noise_rgb * gray_noise

    return img


def random_add_gaussian_noise_pt(img, sigma_range=(0, 1.0), gray_prob=0.4, clip=True, rounds=False):
    """Add random gaussian noise"""
    b, _, h, w = img.size()
    device = img.device
    gray_noise = torch.rand(b, 1, 1, 1, device=device) < gray_prob
    sigma = torch.empty(b, 1, 1, 1, device=device).uniform_(*sigma_range)

    if gray_noise.any():
        img_gray = rgb_to_grayscale(img)
        noise_gray = torch.randn(b, 1, h, w, device=device) * sigma
        img = img * (1 - gray_noise) + (img_gray + noise_gray) * gray_noise
    else:
        noise_rgb = torch.randn(b, 3, h, w, device=device) * sigma
        img = img + noise_rgb

    if clip and rounds:
        img = torch.clamp((img * 255.0).round(), 0, 255) / 255.
    elif clip:
        img = torch.clamp(img, 0, 1)
    elif rounds:
        img = (img * 255.0).round() / 255.

    return img