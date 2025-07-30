# ===================================================================================
# SETUP SCRIPT FOR SPEAKER DIARIZATION
# ===================================================================================
#
# PURPOSE:
# This script sets up the Python virtual environment for the speaker diarization
# project. It intelligently detects your hardware (NVIDIA GPU) and installs the
# correct dependencies.
#
# USAGE:
# This script is designed to be run with 'uv', a fast Python package manager.
#
# 1. Create a new virtual environment:
#    uv venv .venv --seed
#
# 2. Activate the environment:
#    .venv\Scripts\activate
#
# 3. Run this setup script:
#    python setup.py
#
#
# --- MODES OF OPERATION ---
#
# 1. Default Mode (Recommended First Try):
#    COMMAND: python setup.py
#    - This installs the LATEST available versions of all required libraries.
#    - Use this mode to get the newest features and bug fixes. This should be
#      your first choice when setting up the project.
#
# 2. Failsafe Mode (The Stable Backup):
#    COMMAND: python setup.py --failsafe
#    - This installs a specific, locked-down set of library versions from the
#      `requirements.txt` file. These versions are known to be stable and
#      work together correctly.
#    - Use this mode if the default installation (with the latest libraries)
#      is causing unexpected errors or crashes. This is the "it just works" option.
#
# ===================================================================================

import argparse
import subprocess
import sys
import shutil


def run_command(command):
    """
    Runs a command in a subprocess and exits the script if the command fails.

    Args:
        command (list): A list of strings representing the command to run.
    """
    try:
        # Execute the command, checking for a non-zero exit code which indicates an error.
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        # This error is caught if the command runs but returns an error (e.g., package not found).
        print(f"ERROR: Command failed with exit code {e.returncode}")
        print(f"Command was: {' '.join(command)}")
        sys.exit(1)
    except FileNotFoundError:
        # This error is caught if the command itself (e.g., 'uv') cannot be found.
        print(f"ERROR: Command not found: {command[0]}")
        print(
            "Please ensure uv is installed and you are in the correct virtual environment."
        )
        sys.exit(1)


def check_nvidia_gpu():
    """
    Checks for the presence of an NVIDIA GPU and drivers by calling 'nvidia-smi'.

    Returns:
        bool: True if an NVIDIA GPU and drivers are detected, False otherwise.
    """
    # shutil.which is a reliable way to check if a command exists in the system's PATH.
    if not shutil.which("nvidia-smi"):
        return False
    try:
        # Run nvidia-smi and hide its output. We only care if it runs successfully.
        subprocess.run(["nvidia-smi"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        # If the command fails or isn't found, assume no usable GPU.
        return False


def main():
    """Main setup function to parse arguments and install dependencies."""

    # --- Argument Parsing ---
    # Set up the command-line interface to accept the --failsafe flag.
    parser = argparse.ArgumentParser(
        description="Installs dependencies for the speaker diarization script."
    )
    parser.add_argument(
        "--failsafe",
        action="store_true",
        help="Install stable pinned versions from requirements.txt instead of the latest versions.",
    )
    args = parser.parse_args()

    print("🚀 Starting environment setup...")

    # --- Package Selection Logic ---
    # Decide which list of packages to install based on the --failsafe flag.
    packages_to_install = []

    if args.failsafe:
        # Failsafe mode: Read the exact versions from requirements.txt.
        print(
            "🛡️  Failsafe mode enabled: Installing pinned versions from requirements.txt..."
        )
        try:
            with open("requirements.txt", "r", encoding="utf-8") as f:
                packages_to_install = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                ]
        except FileNotFoundError:
            print("ERROR: requirements.txt not found for failsafe mode.")
            sys.exit(1)
    else:
        # Default mode: Use a list of package names to get the latest versions.
        print(
            "🚀 Default mode: Installing the latest versions of all packages..."
        )
        packages_to_install = [
            "pyannote.audio",
            "python-dotenv",
            "huggingface_hub",
            "pydub",
        ]

    # --- Command Building ---
    # Start building the single, unified 'uv pip install' command.
    install_command = ["uv", "pip", "install"]
    # PyTorch packages are always listed explicitly to ensure they are included.
    all_packages = ["torch", "torchvision", "torchaudio"] + packages_to_install

    # Check for a GPU and ask the user how to proceed.
    if check_nvidia_gpu():
        print("✅ NVIDIA GPU detected.")
        choice = input(
            "Do you want to install the GPU (CUDA) version of PyTorch? (y/n): "
        ).lower()
        if choice == "y":
            print("🔧 Preparing for unified GPU installation...")
            # Add the special flags needed for uv to search both PyPI and the PyTorch index.
            install_command.extend(
                [
                    "--extra-index-url",
                    "https://download.pytorch.org/whl/cu121",
                    "--index-strategy",
                    "unsafe-best-match",
                ]
            )
    else:
        print("ℹ️ No NVIDIA GPU detected. Preparing for CPU-only installation.")

    # Add all selected packages to the final command list.
    install_command.extend(all_packages)

    # --- Execution ---
    # Run the final, fully constructed command.
    print("\n--- Installing all dependencies in a single step ---")
    run_command(install_command)

    print("\n🎉 Setup complete! Your environment is ready.")


if __name__ == "__main__":
    main()
