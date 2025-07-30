"""
Compatibility layer for different torchvision versions
"""
import torchvision

def get_rgb_to_grayscale():
    """Get rgb_to_grayscale function compatible with different torchvision versions"""
    try:
        # Try new API (torchvision >= 0.16.0)
        from torchvision.transforms.functional import rgb_to_grayscale
        return rgb_to_grayscale
    except ImportError:
        try:
            # Try old API (torchvision < 0.16.0)
            from torchvision.transforms.functional_tensor import rgb_to_grayscale
            return rgb_to_grayscale
        except ImportError:
            # Fallback implementation
            def rgb_to_grayscale_fallback(img):
                """Fallback rgb_to_grayscale implementation"""
                if img.shape[0] == 3:
                    # Convert RGB to grayscale using standard weights
                    return 0.299 * img[0:1] + 0.587 * img[1:2] + 0.114 * img[2:3]
                return img
            return rgb_to_grayscale_fallback

# Patch basicsr if needed
def patch_basicsr():
    """Patch basicsr to use compatible rgb_to_grayscale function"""
    try:
        import basicsr.data.degradations
        if hasattr(basicsr.data.degradations, 'rgb_to_grayscale'):
            # Already patched
            return

        # Import and patch
        rgb_to_grayscale = get_rgb_to_grayscale()
        basicsr.data.degradations.rgb_to_grayscale = rgb_to_grayscale
    except ImportError:
        # basicsr not installed, skip patching
        pass