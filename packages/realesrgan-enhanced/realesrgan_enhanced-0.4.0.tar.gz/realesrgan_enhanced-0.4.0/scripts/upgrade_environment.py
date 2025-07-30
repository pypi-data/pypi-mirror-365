#!/usr/bin/env python3
"""
Environment upgrade script for Real-ESRGAN.
This script helps users upgrade their environment to modern versions for better compatibility.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{description}...")
    print(f"Running: {command}")

    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major == 3 and version.minor >= 8:
        print("✓ Python version is compatible")
        return True
    else:
        print("⚠ Python version should be 3.8 or higher")
        return False

def upgrade_pip():
    """Upgrade pip to latest version."""
    return run_command(
        f"{sys.executable} -m pip install --upgrade pip",
        "Upgrading pip"
    )

def install_modern_torch():
    """Install modern PyTorch with CUDA support."""
    print("\nInstalling modern PyTorch...")

    # Check if CUDA is available
    try:
        import torch
        if torch.cuda.is_available():
            print("CUDA is available, installing PyTorch with CUDA support")
            command = f"{sys.executable} -m pip install torch>=2.1.0 torchvision>=0.16.0 torchaudio>=2.1.0 --index-url https://download.pytorch.org/whl/cu118"
        else:
            print("CUDA not available, installing CPU-only PyTorch")
            command = f"{sys.executable} -m pip install torch>=2.1.0 torchvision>=0.16.0 torchaudio>=2.1.0"

        return run_command(command, "Installing PyTorch")
    except ImportError:
        print("PyTorch not installed, installing CPU-only version")
        command = f"{sys.executable} -m pip install torch>=2.1.0 torchvision>=0.16.0 torchaudio>=2.1.0"
        return run_command(command, "Installing PyTorch")

def install_modern_requirements():
    """Install modern requirements."""
    project_root = Path(__file__).parent.parent
    requirements_file = project_root / "requirements-modern.txt"

    if requirements_file.exists():
        return run_command(
            f"{sys.executable} -m pip install -r {requirements_file}",
            "Installing modern requirements"
        )
    else:
        print("⚠ requirements-modern.txt not found, using default requirements.txt")
        requirements_file = project_root / "requirements.txt"
        return run_command(
            f"{sys.executable} -m pip install -r {requirements_file}",
            "Installing requirements"
        )

def install_realesrgan():
    """Install Real-ESRGAN in development mode."""
    project_root = Path(__file__).parent.parent
    return run_command(
        f"cd {project_root} && {sys.executable} setup.py develop",
        "Installing Real-ESRGAN in development mode"
    )

def verify_installation():
    """Verify that the installation was successful."""
    print("\nVerifying installation...")

    try:
        import torch
        print(f"✓ PyTorch {torch.__version__} installed")

        import cv2
        print(f"✓ OpenCV {cv2.__version__} installed")

        import numpy as np
        print(f"✓ NumPy {np.__version__} installed")

        from basicsr.archs.rrdbnet_arch import RRDBNet
        print("✓ BasicSR installed")

        from realesrgan import RealESRGANer
        print("✓ Real-ESRGAN installed")

        print("\n🎉 Installation verification successful!")
        return True

    except ImportError as e:
        print(f"✗ Installation verification failed: {e}")
        return False

def main():
    """Main upgrade function."""
    print("Real-ESRGAN Environment Upgrade Script")
    print("=" * 50)

    # Check Python version
    if not check_python_version():
        print("\n⚠ Please upgrade Python to version 3.8 or higher")
        return False

    # Upgrade steps
    steps = [
        ("Upgrading pip", upgrade_pip),
        ("Installing modern PyTorch", install_modern_torch),
        ("Installing modern requirements", install_modern_requirements),
        ("Installing Real-ESRGAN", install_realesrgan),
        ("Verifying installation", verify_installation),
    ]

    for step_name, step_func in steps:
        if not step_func():
            print(f"\n❌ Upgrade failed at step: {step_name}")
            return False

    print("\n" + "=" * 50)
    print("🎉 Environment upgrade completed successfully!")
    print("\nYou can now run the compatibility check:")
    print("python scripts/check_compatibility.py")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)