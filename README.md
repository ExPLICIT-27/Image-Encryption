# Quantum Image Encryptor

A modern GUI application for image encryption using Arnold's Cat Map algorithm.

## Features

- 🌓 Dark/Light theme support
- 🖼️ Image preview with drag & drop
- ✨ Modern UI with animations
- 📊 Visual progress feedback
- 🎛️ Intuitive controls
- 📂 Recent files tracking
- 🔔 Toast notifications
- 📱 Responsive design

## Setup

1. Install the required packages:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python modern_gui.py
```

## Usage

1. Click on the preview area or drag & drop a PPM image
2. Adjust the number of encryption iterations (1-10)
3. Click "Scramble" to encrypt or "Unscramble" to decrypt
4. The processed image will be saved in the respective output folder

## Output Directories

- `Scrambled/`: Contains encrypted images
- `Outputs/`: Contains decrypted images
- `Inputs/`: Place your input PPM images here

## Notes

- Only PPM image format is supported
- The encryption strength depends on the number of iterations
- Higher iterations provide stronger encryption but take longer to process 