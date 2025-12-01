"""
Script to install ML packages with fallback options
Run this if you encounter installation issues
"""

import subprocess
import sys
import os

def install_package(package_name, fallback_versions=None):
    """Install a package with fallback versions"""
    print(f"Installing {package_name}...")
    
    # Try main package first
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✅ {package_name} installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package_name}")
        
        # Try fallback versions
        if fallback_versions:
            for version in fallback_versions:
                try:
                    full_package = f"{package_name.split('>=')[0]}{version}"
                    print(f"Trying fallback: {full_package}")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", full_package])
                    print(f"✅ {full_package} installed successfully!")
                    return True
                except subprocess.CalledProcessError:
                    continue
        
        print(f"❌ All installation attempts failed for {package_name}")
        return False

def main():
    print("🚀 Installing ML packages for Smart Farming Assistant")
    print("=" * 60)
    
    # Upgrade pip first
    print("Upgrading pip...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        print("✅ Pip upgraded successfully!")
    except:
        print("⚠️ Pip upgrade failed, continuing...")
    
    # Install packages with fallbacks
    packages = [
        ("numpy>=1.20.0", ["==1.24.3", "==1.23.5", "==1.21.6"]),
        ("pandas>=1.3.0", ["==2.0.3", "==1.5.3", "==1.4.4"]),
        ("scikit-learn>=1.0.0", ["==1.2.2", "==1.1.3", "==1.0.2"]),
        ("joblib>=1.1.0", ["==1.3.2", "==1.2.0", "==1.1.1"]),
    ]
    
    success_count = 0
    for package, fallbacks in packages:
        if install_package(package, fallbacks):
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"Installation Summary: {success_count}/{len(packages)} packages installed")
    
    if success_count == len(packages):
        print("🎉 All ML packages installed successfully!")
        print("You can now run: python train_model.py")
    else:
        print("⚠️  Some packages failed to install.")
        print("You can try running the crop recommendation without ML (mock data will be used)")

if __name__ == "__main__":
    main()
