# PDASC (Panda ASCII)

A high-performance terminal-based ASCII art converter that transforms images, videos, and live camera feeds into colored ASCII art. Features hardware-accelerated processing with Numba, custom font-based character mapping, and a proprietary `.asc` file format with Zstandard compression for instant playback.

![Demo Image](docs/demo_image.png)
_High-resolution image converted to colored ASCII art_

![Demo Video](docs/demo_video.gif )<br>
_Video playback at 24fps_

## Features

- **Multiple Input Sources**

  - Static images (PNG, JPG, GIF, BMP, TIFF, WebP)
  - Video files (MP4, AVI, MOV, MKV, WebM, FLV, WMV, M4V)
  - Live camera feed with real-time processing
  - Pre-encoded `.asc` files for instant playback

- **Advanced Processing**

  - Hardware-accelerated conversion using Numba JIT compilation
  - Customizable character sets generated from any TrueType font
  - Configurable ASCII density (number of characters used)
  - Adjustable block size for quality vs. performance tuning
  - Full RGB color support with terminal ANSI 24-bit color codes

- **Audio Support**

  - Synchronized audio playback for videos
  - Real-time audio streaming during live camera mode
  - PCM16 audio encoding in `.asc` format

- **Instant Playback**

  - Custom `.asc` (ASCII Container) binary format with Zstandard compression
  - Pre-rendered ANSI escape sequences stored directly
  - Minimal processing overhead during playback (decompression only)
  - Frame-accurate synchronization with audio

- **Web Interface**

  - Interactive image converter with real-time preview
  - Adjustable sliders for ASCII density and block size
  - Color toggle for colored/grayscale output
  - Drag-and-drop image upload
  - Video player with full controls for `.asc.mp4` files

- **GPU-Accelerated Video Processing**
  - OpenGL shader-based ASCII rendering for videos
  - Outputs `.asc.mp4` format for web playback
  - Necessary for smooth browser performance (browsers can't efficiently update thousands of span tags at 30+ FPS)

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Play Command](#play-command)
  - [Encode Command](#encode-command)
  - [Website Command](#website-command)
  - [Command Options](#command-options)
- [The .asc File Format](#the-asc-file-format)
- [How It Works](#how-it-works)
- [Performance Optimization](#performance-optimization)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Installation

### Prerequisites

- Python 3.10 or higher
- A modern terminal with 24-bit color support (most modern terminals)
- FFmpeg (required for all video and audio processing) - download from [ffmpeg.org](https://ffmpeg.org)

### Install with pip

```bash
pip install -r requirements.txt
```

### Install with uv

```bash
# Install uv if you haven't already
pip install uv

# Install dependencies
uv sync
```

**Required packages:**

- `numpy` - Fast numerical operations
- `Pillow` - Image processing
- `numba` - JIT compilation for performance
- `sounddevice` - Audio playback
- `opencv-python` - Camera and video processing
- `zstandard` - Fast compression/decompression
- `flask` - Web server for interactive interface
- `moderngl` - GPU-accelerated video processing

### Font Setup

The project comes pre-bundled with two fonts in the `fonts/` directory:

- `CascadiaMono.ttf` - Default monospace font (Windows Terminal default)
- `font8x8.ttf` - 8×8 pixel font for compact rendering

You can also use any TrueType font by specifying a custom path with the `--font` option.

**Other recommended fonts:**

- JetBrains Mono
- Fira Code
- Any monospace TrueType font

## Quick Start

```bash
# Display an image in terminal
python cli.py play image.png

# Play a video with audio in terminal
python cli.py play video.mp4

# Use your webcam
python cli.py play camera

# Encode a video to .asc format for instant playback
python cli.py encode video.mp4 -o output.asc

# Play the encoded file (blazing fast!)
python cli.py play output.asc

# Launch interactive web interface
python cli.py website

# Convert video with GPU acceleration and play in browser
python cli.py play video.mp4 --website
```

## Usage

The CLI has three main commands: `play` (for displaying/playing), `encode` (for creating `.asc` files), and `website` (for launching the web interface).

### Play Command

Display images, play videos, stream from camera, or play `.asc` files.

```bash
python cli.py play <input> [options]
```

**Input types:**

- Path to an image file
- Path to a video file
- Path to a `.asc` file
- Path to a `.asc.mp4` file (GPU-processed video for web)
- `camera` for webcam input

**Examples:**

```bash
# Display an image in terminal
python cli.py play photo.png

# Play a video without audio
python cli.py play movie.mp4 --no-audio

# Use webcam with higher ASCII density
python cli.py play camera -n 70

# Play with larger block size (lower resolution, better performance)
python cli.py play video.mp4 -b 16

# Play with custom font
python cli.py play image.png -f "fonts/JetBrainsMono.ttf"

# Use a different camera (default is 0)
python cli.py play camera -c 1

# Convert video with GPU and play in browser (only -n supported, not -b)
python cli.py play video.mp4 --website -n 32

# Specify custom output path for web video
python cli.py play video.mp4 --website -o custom_output.asc.mp4

# Play existing .asc.mp4 file in browser
python cli.py play output.asc.mp4 --website

# Enable debug mode to show FPS
python cli.py play video.mp4 --debug
```

### Encode Command

Convert images or videos to the `.asc` format for instant playback with minimal processing overhead.

```bash
python cli.py encode <input> -o <output.asc> [options]
```

**Examples:**

```bash
# Encode a video with default settings
python cli.py encode movie.mp4 -o movie.asc

# Encode an image without color
python cli.py encode photo.png -o photo.asc --no-color

# Encode with custom ASCII density
python cli.py encode video.mp4 -o video.asc -n 70

# Encode with larger blocks for better performance
python cli.py encode large_video.mp4 -o output.asc -b 16
```

### Website Command

Launch an interactive web interface for real-time ASCII art conversion.

```bash
python cli.py website
```

**Features:**

- Drag-and-drop image upload
- Real-time ASCII preview
- Adjustable ASCII character count (2-64)
- Adjustable block size (2-32)
- Color toggle
- Auto-scaling to fit browser window

The website will be available at `http://localhost:5000` by default.

### Command Options

| Option         | Short | Default                  | Description                                                                                                                             | Availability                               |
| -------------- | ----- | ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| `--block-size` | `-b`  | `8`                      | Size of character blocks (pixels per character). Must be a factor of image dimensions. Higher = lower resolution but better performance | `play` (except with `--website`), `encode` |
| `--num-ascii`  | `-n`  | `8`                      | Number of ASCII characters to use (2-95, capped at available characters). Higher = more detail in grayscale gradients                   | `play`, `encode`                           |
| `--font`       | `-f`  | `fonts/CascadiaMono.ttf` | Path to TrueType font file for character generation                                                                                     | `play`, `encode`                           |
| `--no-color`   | -     | `False`                  | Disable color output (grayscale only)                                                                                                   | `play`, `encode`                           |
| `--no-audio`   | -     | `False`                  | Disable audio playback for videos                                                                                                       | `play`, `encode`                           |
| `--camera`     | `-c`  | `0`                      | Camera index when using camera input                                                                                                    | `play`                                     |
| `--output`     | `-o`  | `ascii_out.asc`          | Output file path                                                                                                                        | `encode`, `play --website`                 |
| `--debug`      | -     | `False`                  | Enable debug mode to show FPS and other debug info                                                                                      | `play`                                     |
| `--website`    | -     | `False`                  | Open a local website to display the ASCII video                                                                                         | `play`                                     |

**Note on block size:** The block size must be a factor of both the image width and height, and must not be larger than the image dimensions. If invalid, the program will fail.

**Note on ASCII characters:** The `--num-ascii` parameter will automatically cap at the total number of available ASCII characters (95 printable characters).

## The .asc File Format

The `.asc` (ASCII Container) format is a custom binary format designed for instant playback of ASCII art animations. It stores pre-rendered ANSI escape sequences compressed with Zstandard, enabling near-instant decompression and zero conversion overhead during playback.

### Storage Characteristics

The `.asc` format typically requires **~20× more storage** than the original image/video due to storing complete ANSI escape sequences for every frame. However, Zstandard compression (level 5) significantly reduces this overhead.

**Example compression results** (see [sizes.txt](sizes.txt) for detailed benchmarks):

- **5326 frames, 720p (960×720), block-size 4, num-ascii 32, colored with audio:**
  - Original video (H.264): 48.3 MB
  - Uncompressed ANSI: 3.62 GB
  - Zstandard level 5 (colored): 722.15 MB (~5× compression)
  - Zstandard level 5 (no color): 93.55 MB (~38.7× compression)
  - Audio (uncompressed PCM16): 35.85 MB

Color output requires significantly more storage than grayscale due to RGB color codes for each character.

### Design Philosophy

The `.asc` format prioritizes **instant playback** over storage efficiency. By pre-rendering all frames as complete ANSI strings during encoding and compressing them with Zstandard (level 5), playback requires only decompression—no conversion processing. The format balances reasonable file sizes with minimal CPU overhead during playback, making it ideal for smooth, frame-accurate video playback in terminal environments.

### Format Specification

#### Header (24 bytes)

| Offset | Size | Type   | Description                                   |
| ------ | ---- | ------ | --------------------------------------------- |
| 0x00   | 4    | char   | Magic number: "ASII" (ASCII with compression) |
| 0x04   | 2    | uint16 | Version number (currently 2)                  |
| 0x06   | 2    | uint16 | Flags (bit field)                             |
| 0x08   | 4    | float  | FPS (frames per second)                       |
| 0x0C   | 4    | uint32 | Frame count                                   |
| 0x10   | 8    | -      | Reserved for future use                       |

#### Flags (bit field)

```txt
Bit 0: IS_VIDEO  (0x01) - Multiple frames (video)
Bit 1: HAS_AUDIO (0x02) - Audio data is present
Bits 2-15: Reserved
```

#### Frame Index Section

Following the header, frame lengths are stored for quick random access:

| Offset   | Size | Type   | Description                         |
| -------- | ---- | ------ | ----------------------------------- |
| variable | 4    | uint32 | Frame 1 uncompressed length (bytes) |
| +4       | 4    | uint32 | Frame 2 uncompressed length (bytes) |
| ...      | ...  | ...    | ... (one entry per frame)           |

#### Compressed Frame Data

After the frame index:

| Offset   | Size     | Type   | Description                     |
| -------- | -------- | ------ | ------------------------------- |
| variable | 4        | uint32 | Compressed data size (bytes)    |
| +4       | variable | bytes  | Zstandard-compressed frame data |

The compressed data contains all frames concatenated together. Each frame string contains:

- ANSI 24-bit color escape sequences (`\033[38;2;R;G;Bm`)
- ASCII characters (typically doubled for better aspect ratio)
- Newline characters for row separation
- ANSI reset sequences

**Example frame string structure (before compression):**

```txt
\033[38;2;45;67;89m##\033[38;2;50;70;92m##...\n\033[38;2;42;65;88m##...
```

#### Audio Section (optional)

If `HAS_AUDIO` flag is set, audio data follows the compressed frames:

| Offset   | Size     | Type   | Description              |
| -------- | -------- | ------ | ------------------------ |
| variable | 4        | uint32 | Audio data size in bytes |
| +4       | 1        | uint8  | Audio format (1 = PCM16) |
| +5       | 4        | uint32 | Sample rate (Hz)         |
| +9       | 1        | uint8  | Number of channels       |
| +10      | variable | bytes  | Raw PCM16 audio data     |

### Why Use .asc Files?

Despite requiring ~20× more raw storage before compression, `.asc` files offer significant advantages:

1. **Minimal processing overhead** - Only decompression, no conversion
2. **Frame-perfect synchronization** - Eliminates conversion lag
3. **Consistent performance** - Predictable CPU usage
4. **Instant startup** - Fast initial decompression
5. **Reasonable file sizes** - Good compression with Zstandard
6. **Predictable playback** - Same experience on all hardware

The format is ideal for scenarios where smooth, reliable playback is more important than real-time conversion.

## How It Works

### 1. Character Mapping Generation

The system analyzes a TrueType font to create an optimal character-to-brightness mapping:

```python
# Generate luminance values for each printable ASCII character
color_ramp = generate_color_ramp(font_path="fonts/CascadiaMono.ttf")

# Select N characters with the most uniform brightness distribution
char_map = get_charmap(color_ramp, levels=8)
# Result: " .:-=+*#%@" (from darkest to brightest)
```

Each character is rendered at 48×48 pixels, and its average luminance is computed. Characters are then mapped to the nearest quantized luminance value to create a uniform grayscale ramp.

### 2. Image Processing Pipeline

```txt
Input Image/Frame
    ↓
Divide into blocks (e.g., 8×8 pixels)
    ↓
Compute average color per block (Numba-accelerated)
    ↓
Calculate luminance: L = 0.2126R + 0.7152G + 0.0722B
    ↓
Map luminance to character index
    ↓
Generate ANSI escape sequence with RGB color
    ↓
Assemble complete frame string
    ↓
Compress with Zstandard (encode) or Render to terminal (play)
```

### 3. Numba Acceleration

The core processing loop is JIT-compiled with Numba for near-C performance:

```python
@njit(parallel=True, fastmath=True, cache=True)
def compute_blocks(img, cs, gray_levels, color):
    # Parallel processing of image blocks
    # Significantly faster than pure Python
    ...
```

### 4. GPU Video Rendering for Web Playback

For video playback in browsers with the `--website` flag, PDASC uses ModernGL with OpenGL shaders to render ASCII video. This approach is necessary because browsers cannot efficiently update thousands of nested span tags at 30+ FPS:

```python
# Fragment shader processes each pixel in parallel
# Converts RGB to ASCII character lookup
# Outputs .asc.mp4 for web playback
```

The GPU rendering outputs to `ascii_{video_name}.asc.{video_ext}` by default, or to a custom path specified with the `-o` parameter when using `play --website`. This creates a standard video file that browsers can play smoothly.

### 5. Terminal Rendering

Output uses ANSI escape sequences for:

- 24-bit true color: `\033[38;2;{r};{g};{b}m`
- Cursor positioning: `\033[H` (home position)
- Alternate screen buffer: `\033[?1049h` (enter) / `\033[?1049l` (exit)
- Cursor visibility: `\033[?25l` (hide) / `\033[?25h` (show)

### 6. Encoding Process

When encoding to `.asc` format:

1. Process each video frame through the conversion pipeline
2. Render each frame to a complete ANSI string
3. Compress all frames together using Zstandard level 5
4. Write frame length index for random access
5. Write compressed frame data
6. Optionally extract and append PCM16 audio data
7. Store metadata (FPS, frame count, flags) in header

### 7. Playback Process

When playing `.asc` files:

1. Read header to determine FPS and frame count
2. Decompress all frames using Zstandard (fast one-time operation)
3. Write strings directly to terminal at target FPS
4. Stream audio in parallel if present
5. No conversion or re-processing required

## Performance Optimization

### Block Size vs. Quality

| Block Size | Resolution | Performance | Use Case                       |
| ---------- | ---------- | ----------- | ------------------------------ |
| 4×4        | Very High  | Good        | High-quality images and videos |
| 8×8        | High       | Better      | Default, recommended           |
| 16×16      | Medium     | Best        | Lower-end hardware             |
| 32×32      | Low        | Fastest     | Very limited hardware          |

**Note:** Block size affects encoding time and output quality. Playback performance depends mainly on decompression speed. Block size must be a factor of both image width and height.

### Number of ASCII Characters

| Num ASCII | Detail | Character Set Size | Use Case                    |
| --------- | ------ | ------------------ | --------------------------- |
| 4-16      | Low    | Small              | Artistic effect, retro look |
| 32-64     | Medium | Medium             | Good balance                |
| 70-95     | High   | Large              | Maximum detail preservation |

### Best Practices

1. **For webcam/real-time**: Use `-b 8 -n 32` for smooth live processing
2. **For high-quality images**: Use `-b 4 -n 70` for maximum detail
3. **For video playback**: Always encode to `.asc` first for best performance
4. **For web playback**: Use `--website` flag with GPU acceleration
5. **For storage constraints**: Use grayscale (`--no-color`) for 5-8× smaller files
6. **For terminal size constraints**: Match block size to terminal dimensions

## Examples

### Example 1: Display an Image

```bash
python cli.py play landscape.png -n 50 -b 8
```

![Landscape Example](docs/landscape.png)
_Landscape image with 50 ASCII characters_

### Example 2: Webcam Streaming

```bash
python cli.py play camera -b 12 -n 40
```

![Webcam Example](docs/camera.gif)<br>
_Real-time webcam feed at 30 FPS_

### Example 3: Grayscale Art

```bash
python cli.py play artwork.png --no-color -n 95 -b 2
```

![Grayscale Example](docs/painting_grayscale.png)
_Black and white image with maximum character variety and resolution_

### Example 4: Interactive Web Interface

```bash
python cli.py website
```

Then open `http://localhost:5000` in your browser to use the interactive converter.

### Example 5: GPU-Rendered Web Video

```bash
python cli.py play movie.mp4 --website
```

Renders the video using GPU shaders and opens a web player for smooth browser playback. The output is saved to `ascii_movie.asc.mp4` by default.

## Troubleshooting

### Camera Not Working

```bash
# Error: "Could not open camera 0"
# Solution: Try different camera index
python cli.py play camera -c 1

# On Linux, check available cameras:
ls /dev/video*
```

### Video Playback Issues

**Frames dropping or stuttering:**

- Increase block size during encoding: `-b 16`
- Reduce ASCII density: `-n 32`
- Ensure you're playing from `.asc` file, not converting in real-time

**Audio out of sync:**

- This typically occurs when processing frames in real-time
- Always encode to `.asc` format first for perfect synchronization

### Terminal Issues

**Colors not displaying:**

- Ensure your terminal supports 24-bit color
- Test with: `printf "\x1b[38;2;255;100;0mTRUECOLOR\x1b[0m\n"`
- Try different terminal emulators (Windows Terminal, iTerm2, Alacritty)

**Display cut off:**

- The program automatically scales to fit terminal size
- Maximize your terminal window for best results
- Use smaller block sizes for more content in limited space

### FFmpeg Errors

**FFmpeg not found:**

- Download and install FFmpeg from [ffmpeg.org](https://ffmpeg.org)
- Ensure FFmpeg is in your system PATH
- Test with: `ffmpeg -version`

**Install instructions:**

- Ubuntu/Debian: `sudo apt install ffmpeg`
- macOS: `brew install ffmpeg`
- Windows: Download from [ffmpeg.org](https://ffmpeg.org) and add to PATH

**Out of memory during encoding:**

- Process videos in smaller chunks
- Use larger block sizes to reduce frame string size
- Close other applications to free RAM

**Compression takes too long:**

- This is normal for long videos with high detail
- Consider using larger block sizes (`-b 16` or `-b 32`)
- Compression is a one-time cost for much faster playback

### Font Errors

```bash
# Error: "Font file not found"
# Solution: Use bundled fonts or specify full path
python cli.py play image.png -f "fonts/CascadiaMono.ttf"
python cli.py play image.png -f "fonts/font8x8.ttf"

# Or use system fonts
python cli.py play image.png -f "/usr/share/fonts/truetype/jetbrains/JetBrainsMono.ttf"
```

### Web Interface Issues

**Website won't start:**

- Ensure Flask is installed: `pip install flask`
- Check if port 5000 is already in use
- Try a different port by modifying the Flask app

**Image upload fails:**

- Check file size (max 16MB by default)
- Ensure image format is supported
- Check browser console for errors

### Block Size Errors

```bash
# Error: Block size must be a factor of image dimensions
# Solution: Choose a block size that divides evenly into width and height
# For a 1920×1080 image, valid block sizes include: 2, 4, 5, 8, 10, 12, 15, 16, 20, 24, etc.
python cli.py play image.png -b 8  # Works for most images
```

## License

MIT License

Copyright (c) 2026 Colin Politi (ColinThePanda)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
