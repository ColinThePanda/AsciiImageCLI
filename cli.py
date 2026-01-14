#!/usr/bin/env python3

# Suppress resource_tracker semaphore warnings from sounddevice
# Must be done before any other imports
import os
os.environ['PYTHONWARNINGS'] = 'ignore'

import warnings
warnings.filterwarnings(
    "ignore",
    message=".*resource_tracker.*semaphore.*"
)

from core import AsciiConverter, AsciiDisplayer, AsciiEncoder, generate_color_ramp, get_charmap, render_charmap, VideoAsciiConverter, process_video
from web import create_video_server, ImageServer
from PIL import Image
import argparse
import sys

def add_common_args(parser):
    """Add arguments common to both play and encode"""
    parser.add_argument(
        "-b", "--block-size",
        type=int,
        default=8,
        help="Size of character blocks (default: 8)"
    )
    
    parser.add_argument(
        "-n", "--num-ascii",
        type=int,
        default=8,
        help="Number of ASCII characters to use (default: 8)"
    )
    
    parser.add_argument(
        "-f", "--font",
        type=str,
        default=os.path.join(os.path.dirname(__file__), "fonts", "CascadiaMono.ttf"),
        help="Path to font file to create the ASCII character set from and to display on the website"
    )
    
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable color output"
    )
    
    parser.add_argument(
        "--no-audio",
        action="store_true",
        help="Disable audio playback for videos"
    )

def cmd_play(args):
    """Play command - display images/videos/camera"""
    # Validate font
    if not os.path.exists(args.font):
        print(f"Error: Font file '{args.font}' not found", file=sys.stderr)
        sys.exit(1)
    
    converter = AsciiConverter(num_ascii=args.num_ascii, chunk_size=args.block_size, font_path=args.font)
    displayer = AsciiDisplayer(converter, args.debug)
    
    try:
        if args.input == "camera":
            print(f"Starting camera {args.camera} (press Ctrl+C to stop)")
            displayer.display_camera(camera_index=args.camera, color=not args.no_color)
        else:
            # Validate input file
            if not os.path.exists(args.input):
                print(f"Error: File '{args.input}' not found", file=sys.stderr)
                sys.exit(1)
            
            # Determine file type
            video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v'}
            image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
            special_extensions = {'.asc'}
            
            ext = os.path.splitext(args.input)[-1].lower()
            
            if ext not in video_extensions and ext not in image_extensions and ext not in special_extensions:
                print(f"Error: Unsupported file extension '{ext}'", file=sys.stderr)
                print(f"Supported: .asc, {', '.join(sorted(video_extensions | image_extensions))}", file=sys.stderr)
                sys.exit(1)
            
            if ext == '.asc':
                print(f"Playing .asc file: {args.input}")
                displayer.display_asc_file(args.input, not args.no_audio)
            elif ext in video_extensions:
                print(f"Playing video: {args.input}")
                displayer.display_video(
                    video_path=args.input,
                    play_audio=not args.no_audio,
                    color=not args.no_color
                )
            else:
                print(f"Displaying image: {args.input}")
                displayer.display_image(image=Image.open(args.input), color=not args.no_color)
                
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def cmd_encode(args):
    """Encode command - save encoded ASCII to file"""
    # Validate font
    if not os.path.exists(args.font):
        print(f"Error: Font file '{args.font}' not found", file=sys.stderr)
        sys.exit(1)
    
    print(f"Encoding {args.input} to {args.output}")
    # Validate input file
    if not os.path.exists(args.input):
        print(f"Error: File '{args.input}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Determine file type
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v'}
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
    
    ext = os.path.splitext(args.input)[-1].lower()
    
    if ext not in video_extensions and ext not in image_extensions:
        print(f"Error: Unsupported file extension '{ext}'", file=sys.stderr)
        print(f"Supported: {', '.join(sorted(video_extensions | image_extensions))}", file=sys.stderr)
        sys.exit(1)
    
    encoder = AsciiEncoder()
    converter = AsciiConverter(num_ascii=args.num_ascii, chunk_size=args.block_size, font_path=args.font)
    
    if ext in video_extensions:
        encoder.encode_video_to_asc(args.input, args.output, not args.no_audio, not args.no_color, converter)
    else:
        encoder.encode_image_to_asc(args.input, args.output, not args.no_color, converter)

def cmd_website(args):
    if args.input:
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v'}
        ext = os.path.splitext(args.input)[-1].lower()
        if os.path.splitext(os.path.splitext(args.input)[0])[-1].lower() == '.asc':
            app = create_video_server(args.input)
            app.run()
        elif ext in video_extensions:
            with open("shaders/ascii.frag") as file:
                frac_src = file.read()
            font_path = os.path.join(os.path.dirname(__file__), "fonts", "font8x8.ttf")
            charmap_img = render_charmap(get_charmap(generate_color_ramp(font_path=font_path), levels=16), font_path=font_path)
            converter = VideoAsciiConverter(frac_src, charmap_img, not args.no_color)
            out_path = process_video(converter, args.input, args.output, not args.no_audio)
            app = create_video_server(out_path)
            app.run()
        else:
            print("Invalid input for website. Must be a valid video file or not specified")
    else:
        app = ImageServer(font_path=os.path.join(os.path.dirname(__file__), "fonts", "CascadiaMono.ttf"))
        app.run(port=args.port)

def main():
    parser = argparse.ArgumentParser(
        description="Convert images and videos to ASCII art",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Play subcommand
    play_parser = subparsers.add_parser(
        'play',
        help='Display images/videos/camera as ASCII art',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s play image.png
  %(prog)s play video.mp4 --no-audio
  %(prog)s play camera -c 0
  %(prog)s play image.jpg -b 16 -n 70
        """
    )
    
    add_common_args(play_parser)
    
    play_parser.add_argument(
        "-c", "--camera",
        type=int,
        default=0,
        help="Camera index when using camera input (default: 0)"
    )
    
    play_parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode to show FPS and other debug info"
    )
    
    play_parser.set_defaults(func=cmd_play)
    
    # Encode subcommand
    encode_parser = subparsers.add_parser(
        'encode',
        help='Encode video/image to compressed ASCII file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s encode video.mp4 -o output.asc
  %(prog)s encode image.png -o output.asc --no-color
        """
    )
    
    encode_parser.add_argument(
        "input",
        type=str,
        help="Path to input video or image file"
    )
    
    encode_parser.add_argument(
        "-o", "--output",
        type=str,
        default="ascii_out.asc",
        help="Output file path"
    )
    
    add_common_args(encode_parser)
    
    encode_parser.set_defaults(func=cmd_encode)
    
    website_parser = subparsers.add_parser(
        'website',
        help='Open image demo website or website to display ASCII shaded video',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage:
  %(prog)s website
        """
    )
    
    website_parser.add_argument(
        "input",
        nargs='?',
        type=str,
        default=None,
        help='Path to video to display on website (optional)'
    )
    
    website_parser.add_argument(
        "-o", "--output",
        type=str,
        default="",
        help="Output file path"
    )
    
    website_parser.add_argument(
        "-p", "--port",
        type=int,
        default=5000,
        help="Port to run website on"
    )
    
    website_parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable color output"
    )
    
    website_parser.add_argument(
        "--no-audio",
        action="store_true",
        help="Disable audio playback for videos"
    )
    
    website_parser.set_defaults(func=cmd_website)
    
    args = parser.parse_args()
    
    # Show help if no command specified
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Call correct sub-command
    args.func(args)

if __name__ == "__main__":
    main()