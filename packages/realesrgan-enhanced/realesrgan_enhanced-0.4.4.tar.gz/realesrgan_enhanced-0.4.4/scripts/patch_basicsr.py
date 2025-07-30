#!/usr/bin/env python3
"""
Standalone script to patch basicsr for torchvision compatibility
"""
import sys
from pathlib import Path

def find_basicsr_path():
    try:
        import basicsr
        return Path(basicsr.__file__).parent
    except ImportError:
        print("❌ basicsr not found")
        return None

def patch_basicsr_degradations():
    basicsr_path = find_basicsr_path()
    if not basicsr_path:
        return False
    degradations_file = basicsr_path / "data" / "degradations.py"
    if not degradations_file.exists():
        print(f"❌ {degradations_file} not found")
        return False
    with open(degradations_file, 'r') as f:
        content = f.read()
    if "from torchvision.transforms.functional import rgb_to_grayscale" in content:
        print("✅ basicsr already patched")
        return True
    new_content = content.replace(
        "from torchvision.transforms.functional_tensor import rgb_to_grayscale",
        "from torchvision.transforms.functional import rgb_to_grayscale"
    )
    # Backup
    with open(str(degradations_file) + ".backup", 'w') as f:
        f.write(content)
    with open(degradations_file, 'w') as f:
        f.write(new_content)
    print("✅ basicsr patched successfully!")
    return True

def main():
    patch_basicsr_degradations()

if __name__ == "__main__":
    main()