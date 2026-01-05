from PIL import Image
from panda_color import Color
import numpy as np

def quantize_grayscale(image: Image.Image, quantization_levels: int = 8) -> Image.Image:
    img_data = np.array(image, dtype=np.float32) / 255.0
    height, width, channels = img_data.shape
    out_data = np.zeros_like(img_data)
    
    for y in range(height):
        for x in range(width):
            in_pix = img_data[y, x]
            gray = sum([0.2126 * in_pix[0], 0.7152 * in_pix[1], 0.0722 * in_pix[2]])
            quantized = np.floor(gray * quantization_levels) / (quantization_levels - 1)
            out_data[y, x] = [quantized, quantized, quantized]
    
    out_data = (out_data * 255).astype(np.uint8)
    
    return Image.fromarray(out_data, "RGB")
    
def get_ascii(image: Image.Image, char_map: str, chunk_size: int = 8, quantization_levels: int = 8):
    img_data = np.array(image, dtype=np.float32) / 255.0
    height, width, channels = img_data.shape
    if width % chunk_size != 0 or height % chunk_size != 0:
        raise ValueError("Invalid chunk size. Image width and height must be a multiple of chunk size")
    
    out : list[list[str]] = np.empty((height // chunk_size, width // chunk_size), dtype=str).tolist()
    
    for y in range(0, height, chunk_size):
        for x in range(0, width, chunk_size):
            chunk = img_data[y:y + chunk_size, x:x + chunk_size]
            mean_value = np.mean(chunk)
            char = char_map[int((mean_value * quantization_levels))]
            out[y//8][x//8] = char
    
    return out

def display_ascii(ascii: list[list[str]]):
    for row in ascii:
        new_row = [char * 2 for char in row]
        print("".join(new_row))

img = Image.open("test.png").convert('RGB')
quantized_grayscale = quantize_grayscale(img, 8)
ascii = get_ascii(quantized_grayscale, " `;<l]wg@")
display_ascii(ascii)

quantized_grayscale.save("out_quantize.png")