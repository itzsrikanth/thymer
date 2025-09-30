#!/usr/bin/env python3
"""Build script for creating Thymer binary with Nuitka."""

import subprocess
import sys
import platform
from pathlib import Path


def build_binary():
    """Build standalone binary using Nuitka."""
    
    print("Building Thymer binary with Nuitka...")
    
    # Determine output name based on platform
    system = platform.system().lower()
    output_name = "thymer"
    if system == "windows":
        output_name += ".exe"
    
    # Nuitka build command
    cmd = [
        sys.executable,
        "-m", "nuitka",
        "--onefile",  # Create single executable
        "--enable-plugin=anti-bloat",  # Reduce size
        "--assume-yes-for-downloads",  # Auto-download dependencies
        f"--output-filename={output_name}",
        "--output-dir=dist",
        "--product-name=Thymer",
        "--file-description=Developer Productivity Timer",
        "--company-name=Thymer Contributors",
        "--product-version=0.1.0",
        "--file-version=0.1.0",
        "--include-package=textual",
        "--include-package=rich",
        "--remove-output",  # Clean build artifacts
        "src/app.py",
    ]
    
    # Add platform-specific options
    if system == "darwin":
        cmd.extend([
            "--macos-create-app-bundle",
            "--macos-app-name=Thymer",
            "--static-libpython=no",  # Disable static libpython on macOS
        ])
    elif system == "windows":
        cmd.append("--windows-console-mode=attach")
    
    try:
        subprocess.run(cmd, check=True)
        print(f"\n✅ Binary built successfully: dist/{output_name}")
        
        # Show size
        binary_path = Path("dist") / output_name
        if binary_path.exists():
            size_mb = binary_path.stat().st_size / (1024 * 1024)
            print(f"📦 Binary size: {size_mb:.2f} MB")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    build_binary()
