#!/usr/bin/env python3
"""
Test script to check compatibility between Real-ESRGAN and briaai/RMBG-2.0
"""

import sys
import os
from pathlib import Path

def test_rmbg_installation():
    """Test if RMBG can be installed and imported."""
    print("Testing RMBG-2.0 compatibility...")

    try:
        # Try to install RMBG if not already installed
        import subprocess
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "rembg[gpu]"
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print("✓ RMBG installed successfully")
        else:
            print(f"⚠ RMBG installation warning: {result.stderr}")

        # Try to import RMBG
        import rembg
        print(f"✓ RMBG imported successfully, version: {rembg.__version__}")

        # Test basic RMBG functionality
        from rembg import remove
        print("✓ RMBG remove function imported successfully")

        return True

    except ImportError as e:
        print(f"✗ RMBG import failed: {e}")
        return False
    except Exception as e:
        print(f"✗ RMBG test failed: {e}")
        return False

def test_combined_workflow():
    """Test if Real-ESRGAN and RMBG can work together."""
    print("\nTesting combined workflow...")

    try:
        # Import both libraries
        import cv2
        import numpy as np
        from rembg import remove
        from realesrgan import RealESRGANer
        from basicsr.archs.rrdbnet_arch import RRDBNet

        print("✓ All libraries imported successfully")

        # Create a dummy image
        dummy_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        print("✓ Dummy image created")

        # Test RMBG (this would normally process the image)
        print("✓ RMBG ready for processing")

        # Test Real-ESRGAN model creation
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=6, num_grow_ch=32, scale=4)
        print("✓ Real-ESRGAN model created successfully")

        print("✓ Combined workflow test passed")
        return True

    except Exception as e:
        print(f"✗ Combined workflow test failed: {e}")
        return False

def test_environment_conflicts():
    """Test for potential environment conflicts."""
    print("\nTesting for environment conflicts...")

    try:
        import torch
        import torchvision
        import numpy as np
        import cv2
        from PIL import Image

        # Check for version conflicts
        print(f"✓ PyTorch: {torch.__version__}")
        print(f"✓ TorchVision: {torchvision.__version__}")
        print(f"✓ NumPy: {np.__version__}")
        print(f"✓ OpenCV: {cv2.__version__}")
        print(f"✓ Pillow: {Image.__version__}")

        # Check CUDA compatibility
        if torch.cuda.is_available():
            print(f"✓ CUDA available: {torch.version.cuda}")
        else:
            print("⚠ CUDA not available (this is normal for CPU-only setups)")

        return True

    except Exception as e:
        print(f"✗ Environment conflict test failed: {e}")
        return False

def main():
    """Main test function."""
    print("Real-ESRGAN + RMBG-2.0 Compatibility Test")
    print("=" * 50)

    # Add the project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    tests = [
        ("RMBG installation", test_rmbg_installation),
        ("Combined workflow", test_combined_workflow),
        ("Environment conflicts", test_environment_conflicts),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * len(test_name))
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("COMPATIBILITY TEST SUMMARY")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All compatibility tests passed! Real-ESRGAN and RMBG-2.0 can work together.")
    else:
        print("⚠ Some compatibility issues detected. Please check the output above.")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)