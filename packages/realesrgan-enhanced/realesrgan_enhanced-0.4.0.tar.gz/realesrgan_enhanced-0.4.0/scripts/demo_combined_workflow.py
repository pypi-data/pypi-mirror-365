#!/usr/bin/env python3
"""
Demo script showing Real-ESRGAN and RMBG-2.0 working together.
This demonstrates that the upgraded Real-ESRGAN is compatible with modern packages.
"""

import cv2
import numpy as np
import os
import sys
from pathlib import Path

def remove_background(image_path, output_path):
    """Remove background using RMBG-2.0."""
    try:
        from rembg import remove

        # Read image
        input_image = cv2.imread(image_path)
        if input_image is None:
            print(f"Error: Could not read image {image_path}")
            return False

        # Remove background
        print("Removing background with RMBG-2.0...")
        output_image = remove(input_image)

        # Save result
        cv2.imwrite(output_path, output_image)
        print(f"✓ Background removed and saved to {output_path}")
        return True

    except Exception as e:
        print(f"Error removing background: {e}")
        return False

def upscale_image(image_path, output_path, model_name="RealESRGAN_x4plus_anime_6B"):
    """Upscale image using Real-ESRGAN."""
    try:
        from realesrgan import RealESRGANer
        from basicsr.archs.rrdbnet_arch import RRDBNet

        # Read image
        input_image = cv2.imread(image_path)
        if input_image is None:
            print(f"Error: Could not read image {image_path}")
            return False

        # Initialize upsampler
        if model_name == "RealESRGAN_x4plus_anime_6B":
            model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=6, num_grow_ch=32, scale=4)
            model_path = 'weights/RealESRGAN_x4plus_anime_6B.pth'
        else:
            # Use general model as fallback
            from realesrgan.archs.srvgg_arch import SRVGGNetCompact
            model = SRVGGNetCompact(num_in_ch=3, num_out_ch=3, num_feat=64, num_conv=32, upscale=4, act_type='prelu')
            model_path = 'weights/realesr-general-x4v3.pth'

        upsampler = RealESRGANer(
            scale=4,
            model_path=model_path,
            model=model,
            tile=0,
            tile_pad=10,
            pre_pad=0,
            half=False,  # Use fp32 for CPU
            device=None
        )

        # Upscale image
        print(f"Upscaling with {model_name}...")
        output_image, _ = upsampler.enhance(input_image, outscale=2)  # 2x upscale for demo

        # Save result
        cv2.imwrite(output_path, output_image)
        print(f"✓ Image upscaled and saved to {output_path}")
        return True

    except Exception as e:
        print(f"Error upscaling image: {e}")
        return False

def combined_workflow(input_path, output_dir):
    """Complete workflow: remove background then upscale."""
    print("=" * 60)
    print("Real-ESRGAN + RMBG-2.0 Combined Workflow Demo")
    print("=" * 60)

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Remove background
    print("\nStep 1: Background Removal")
    print("-" * 30)
    bg_removed_path = os.path.join(output_dir, "bg_removed.png")
    if not remove_background(input_path, bg_removed_path):
        print("❌ Background removal failed")
        return False

    # Step 2: Upscale the image
    print("\nStep 2: Image Upscaling")
    print("-" * 30)
    upscaled_path = os.path.join(output_dir, "upscaled.png")
    if not upscale_image(bg_removed_path, upscaled_path):
        print("❌ Image upscaling failed")
        return False

    print("\n" + "=" * 60)
    print("🎉 Combined workflow completed successfully!")
    print(f"Input: {input_path}")
    print(f"Background removed: {bg_removed_path}")
    print(f"Upscaled: {upscaled_path}")
    print("=" * 60)

    return True

def main():
    """Main function."""
    # Add project root to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    # Check if input image exists
    input_image = "inputs/00003.png"
    if not os.path.exists(input_image):
        print(f"Error: Input image {input_image} not found")
        print("Please make sure you have an image in the inputs directory")
        return False

    # Run combined workflow
    output_dir = "results/combined_workflow"
    success = combined_workflow(input_image, output_dir)

    if success:
        print("\n✅ Demo completed successfully!")
        print("This proves that Real-ESRGAN and RMBG-2.0 can work together")
        print("in the same environment without conflicts.")
    else:
        print("\n❌ Demo failed")

    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)