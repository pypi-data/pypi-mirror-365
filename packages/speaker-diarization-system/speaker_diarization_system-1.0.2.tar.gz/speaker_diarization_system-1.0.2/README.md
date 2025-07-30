```
  ██╗     ██╗   ██╗██╗  ██╗██╗██╗   ██╗███╗   ███╗ 
  ██║     ██║   ██║██║ ██╔╝██║██║   ██║████╗ ████║ 
  ██║     ██║   ██║█████╔╝ ██║██║   ██║██╔████╔██║ 
  ██║     ██║   ██║██╔═██╗ ██║██║   ██║██║╚██╔╝██║ 
  ███████╗╚██████╔╝██║  ██╗██║╚██████╔╝██║ ╚═╝ ██║ 
  ╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝     ╚═╝ 
```

# Speaker Diarization & Splitting System

A powerful Python script that automatically identifies different speakers in an audio file and splits them into separate, clean tracks. Built by **Lukium**.

---

## Overview

This project uses AI-powered speaker diarization (thanks to `pyannote.audio`) to process audio files containing multiple speakers. It intelligently determines who is speaking and when, then exports a separate audio file for each person.

The key feature is its ability to remove **crosstalk**. The output tracks contain silence when the speaker is not talking, ensuring that overlapping speech is eliminated. This makes it an ideal tool for podcast editing, interview transcription, character animation workflows, and any other task requiring isolated speaker audio.

## Features

-   **🎙️ Multi-Speaker Diarization:** Identifies and separates an unlimited number of speakers in a single audio file.
-   **🧹 Crosstalk Removal:** Generates clean, non-overlapping audio tracks for each speaker.
-   **⚙️ Batch Processing:** Automatically processes all supported audio files (`.wav`, `.mp3`, `.m4a`, `.flac`) in the `audio/pending` directory.
-   **🚀 GPU Acceleration:** Automatically detects and uses an NVIDIA GPU for significantly faster processing.
-   **🗣️ Flexible Speaker Count:** You can specify an exact number of speakers, a min/max range, or let the model detect it automatically.
-   **🤫 Verbose/Quiet Mode:** Run in quiet mode for clean output, or use the `--verbose` flag to see detailed logs for debugging.

## 🤖 Automated Sanity Checks
The main split_speakers.py script is designed to make the first run as smooth as possible by including automated checks for common setup problems. If you forget a step, the script will try to help you fix it.

Missing FFmpeg: If the script can't find ffmpeg in your system's PATH, it will print an error with instructions and automatically open the FFmpeg download page in your browser before exiting.

Hugging Face Model Access: The script proactively checks if you have accepted the user agreements for the required pyannote models. If you haven't accepted one, it will print a message identifying the specific model and automatically open its Hugging Face page for you to accept the terms.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

1.  **Python 3.9+**
2.  **Git** (for cloning the repository).
3.  **NVIDIA GPU with CUDA Drivers** (required for GPU acceleration).
4.  **FFmpeg:** The script requires FFmpeg for audio processing.
    -   Download from: [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)
    -   Ensure the `bin` folder from the download is added to your system's `PATH`.

## Setup & Installation

This project uses **`uv`** for fast and reliable Python package management. The setup process is guided by an interactive script.

1.  **Clone the Repository**
    ```bash
    git clone <your-repository-url>
    cd <your-repository-folder>
    ```

2.  **Install `uv`**
    If you don't have `uv` installed, follow the official instructions for your OS:
    [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv)

3.  **Create & Activate a Virtual Environment**
    It's critical to run this project in a dedicated virtual environment. **Run your terminal as an Administrator** for this process on Windows.
    ```bash
    # Create the environment with pip bootstrapped
    uv venv .venv --seed

    # Activate it (on Windows)
    .venv\Scripts\activate
    ```

4.  **Run the Interactive Setup Script**
    This script will detect your hardware and install the correct dependencies.
    ```bash
    python install.py
    ```
    Follow the on-screen prompts. If you have an NVIDIA GPU, it will ask if you want to install the CUDA-enabled libraries.

5.  **Create `.env` File**
    Create a file named `.env` in the project's root directory. Get a **read** access token from [Hugging Face](https://huggingface.co/settings/tokens) and add it to the file:
    ```
    HF_TOKEN=hf_YourAccessTokenGoesHere
    ```

6.  **Accept Hugging Face Agreements**
    You must accept the user conditions for the gated models used by this project. Visit the links below, make sure you are logged in, and click the "Access repository" button on each page.
    -   [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
    -   [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0)

## Usage

1.  **Place Files:** Add the audio files you want to process into the `audio/pending` directory.
2.  **Run the Script:** Execute the script from your terminal with your virtual environment active.

#### Command Examples:

-   **Automatic speaker detection:**
    ```bash
    python split_speakers.py
    ```
-   **Specify an exact number of speakers (e.g., 2):**
    ```bash
    python split_speakers.py 2
    ```
-   **Specify a range of speakers (e.g., min 2, max 4):**
    ```bash
    python split_speakers.py 2 4
    ```
-   **Run in verbose/debug mode:**
    ```bash
    python split_speakers.py --verbose
    ```

#### File Workflow:

-   **Input:** `audio/pending/your_file.wav`
-   **Processed Original:** `audio/processed/your_file.wav`
-   **Output:** `audio/completed/your_file_SPEAKER_00.wav`, `audio/completed/your_file_SPEAKER_01.wav`, etc.

## Troubleshooting

-   **`Permission denied` Errors during Setup:** You must run your terminal (PowerShell/Command Prompt) **as an Administrator** on Windows to ensure the setup script can write to the virtual environment directory.
-   **`nvidia-smi` Not Found:** This means your NVIDIA drivers are not installed correctly or `nvidia-smi.exe` is not in your system's `PATH`.
-   **Hugging Face Errors:** If you get a `401` or `GatedRepoError`, double-check that your `HF_TOKEN` in the `.env` file is correct and that you have accepted the user agreements for both required models.
-   **Latest Libraries Causing Bugs?** If you suspect a new library version has introduced a bug, you can install a known-stable set of dependencies by running the setup script in failsafe mode: `python install.py --failsafe`.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.