#!/usr/bin/env python3
"""
Compatibility check script for Real-ESRGAN with modern packages.
This script verifies that the upgraded Real-ESRGAN works correctly with newer dependencies.
"""

import sys
import importlib
import subprocess
from pathlib import Path

def check_package_version(package_name, min_version=None):
    """Check if a package is installed and optionally verify minimum version."""
    try:
        module = importlib.import_module(package_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✓ {package_name}: {version}")

        if min_version:
            # Simple version comparison (can be improved)
            if version != 'unknown' and version >= min_version:
                print(f"  ✓ Version {version} >= {min_version}")
            else:
                print(f"  ⚠ Version {version} < {min_version} (recommended)")

        return True
    except ImportError:
        print(f"✗ {package_name}: Not installed")
        return False

def test_basic_imports():
    """Test basic imports to ensure compatibility."""
    print("Testing basic imports...")

    try:
        import torch
        print(f"✓ PyTorch: {torch.__version__}")
        print(f"  CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"  CUDA version: {torch.version.cuda}")
    except ImportError as e:
        print(f"✗ PyTorch import failed: {e}")
        return False

    try:
        import cv2
        print(f"✓ OpenCV: {cv2.__version__}")
    except ImportError as e:
        print(f"✗ OpenCV import failed: {e}")
        return False

    try:
        import numpy as np
        print(f"✓ NumPy: {np.__version__}")
    except ImportError as e:
        print(f"✗ NumPy import failed: {e}")
        return False

    return True

def test_realesrgan_imports():
    """Test Real-ESRGAN specific imports."""
    print("\nTesting Real-ESRGAN imports...")

    try:
        from basicsr.archs.rrdbnet_arch import RRDBNet
        print("✓ BasicSR RRDBNet import successful")
    except ImportError as e:
        print(f"✗ BasicSR RRDBNet import failed: {e}")
        return False

    try:
        from realesrgan import RealESRGANer
        print("✓ RealESRGANer import successful")
    except ImportError as e:
        print(f"✗ RealESRGANer import failed: {e}")
        return False

    try:
        from realesrgan.archs.srvgg_arch import SRVGGNetCompact
        print("✓ SRVGGNetCompact import successful")
    except ImportError as e:
        print(f"✗ SRVGGNetCompact import failed: {e}")
        return False

    return True

def test_modern_package_compatibility():
    """Test compatibility with modern packages like briaai/RMBG-2.0."""
    print("\nTesting modern package compatibility...")

    # Test if we can import common modern packages
    modern_packages = [
        ('torch', '2.0.0'),
        ('torchvision', '0.15.0'),
        ('numpy', '1.21.0'),
        ('cv2', '4.8.0'),  # OpenCV
        ('PIL', '9.0.0'),  # Pillow
        ('scipy', '1.9.0'),
        ('skimage', '0.19.0'),  # scikit-image
    ]

    all_good = True
    for package, min_version in modern_packages:
        if not check_package_version(package, min_version):
            all_good = False

    return all_good

def test_basic_functionality():
    """Test basic Real-ESRGAN functionality."""
    print("\nTesting basic functionality...")

    try:
        import torch
        from basicsr.archs.rrdbnet_arch import RRDBNet
        from realesrgan import RealESRGANer

        # Test model creation
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=6, num_grow_ch=32, scale=4)
        print("✓ RRDBNet model creation successful")

        # Test device handling
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model = model.to(device)
        print(f"✓ Model moved to {device} successfully")

        # Test forward pass
        dummy_input = torch.randn(1, 3, 64, 64).to(device)
        with torch.no_grad():
            output = model(dummy_input)
        print(f"✓ Forward pass successful, output shape: {output.shape}")

        return True

    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False

def main():
    """Main compatibility check function."""
    print("Real-ESRGAN Compatibility Check")
    print("=" * 40)

    # Add the project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    tests = [
        ("Basic imports", test_basic_imports),
        ("Real-ESRGAN imports", test_realesrgan_imports),
        ("Modern package compatibility", test_modern_package_compatibility),
        ("Basic functionality", test_basic_functionality),
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
    print("\n" + "=" * 40)
    print("COMPATIBILITY CHECK SUMMARY")
    print("=" * 40)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All compatibility checks passed! Real-ESRGAN is ready for modern environments.")
    else:
        print("⚠ Some compatibility issues detected. Please check the output above.")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)