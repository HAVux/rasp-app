import os
import platform
import subprocess
import sys

def run(cmd, shell=False):
    print(f"👉 {cmd}")
    subprocess.run(cmd, shell=shell, check=True)

def install_linux():
    print("🐧 Detected Linux (Raspberry Pi / Ubuntu)")
    run(["sudo", "apt", "update"])
    run(["sudo", "apt", "install", "-y",
         "python3-venv", "libsdl2-dev", "libsdl2-image-dev", "libsdl2-mixer-dev",
         "libsdl2-ttf-dev", "libmtdev-dev", "libgl1-mesa-dev", "libgles2-mesa-dev",
         "zlib1g-dev", "libjpeg-dev", "libpng-dev", "libffi-dev", "libsqlite3-dev"
    ])
    run(["python3", "-m", "venv", "kivy_venv"])
    run(["bash", "-c", "source kivy_venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"])

def install_windows():
    print("🪟 Detected Windows")
    run(["python", "-m", "venv", "kivy_venv"])
    pip_cmd = (
        r'kivy_venv\Scripts\activate && '
        r'pip install --upgrade pip && '
        r'pip install -r requirements.txt && '
        r'pip install -r requirements_win.txt'
    )
    run(["cmd", "/c", pip_cmd], shell=True)

def main():
    system = platform.system()
    try:
        if system == "Linux":
            install_linux()
        elif system == "Windows":
            install_windows()
        else:
            print(f"⚠️ Unsupported OS: {system}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during installation: {e}")
        sys.exit(1)

    print("✅ Environment setup complete! To activate:")
    if system == "Linux":
        print("  source kivy_venv/bin/activate")
    else:
        print("  call kivy_venv\\Scripts\\activate")

if __name__ == "__main__":
    main()