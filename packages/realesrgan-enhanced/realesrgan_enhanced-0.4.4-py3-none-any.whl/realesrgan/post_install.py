#!/usr/bin/env python3
"""
Post-install script to automatically patch basicsr for torchvision compatibility
"""
import os
import sys
import importlib
from pathlib import Path

def find_basicsr_path():
    """Find basicsr installation path"""
    try:
        import basicsr
        return Path(basicsr.__file__).parent
    except ImportError:
        return None

def patch_basicsr_degradations():
    """Patch basicsr degradations.py file"""
    basicsr_path = find_basicsr_path()
    if not basicsr_path:
        print("❌ basicsr not found")
        return False

    degradations_file = basicsr_path / "data" / "degradations.py"
    if not degradations_file.exists():
        print(f"❌ {degradations_file} not found")
        return False

    # Read current content
    with open(degradations_file, 'r') as f:
        content = f.read()

    # Check if already patched
    if "from torchvision.transforms.functional import rgb_to_grayscale" in content:
        print("✅ basicsr already patched")
        return True

    # Apply patch
    old_import = "from torchvision.transforms.functional_tensor import rgb_to_grayscale"
    new_import = "from torchvision.transforms.functional import rgb_to_grayscale"

    if old_import in content:
        content = content.replace(old_import, new_import)

        # Backup original if not exists
        backup_file = degradations_file.with_suffix('.py.backup')
        if not backup_file.exists():
            with open(backup_file, 'w') as f:
                f.write(content.replace(new_import, old_import))

        # Write patched content
        with open(degradations_file, 'w') as f:
            f.write(content)

        print("✅ basicsr patched successfully")
        return True
    else:
        print("❌ Could not find import to patch")
        return False

def main():
    """Main function"""
    print("🔧 Auto-patching basicsr for torchvision compatibility...")

    # Apply patch
    success = patch_basicsr_degradations()
    if success:
        print("✅ Real-ESRGAN NumPy 2.x compatibility setup complete!")
        return True
    else:
        print("❌ Failed to patch basicsr")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)