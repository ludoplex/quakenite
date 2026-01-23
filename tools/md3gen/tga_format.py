#!/usr/bin/env python3
"""
TGA texture file reader/writer for id Tech 3 compatible textures.

Supports:
- Uncompressed RGB (type 2)
- Uncompressed RGBA (type 2 with alpha)
- RLE compressed RGB (type 10)
"""

import struct
from pathlib import Path
from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass
class TGAImage:
    """TGA image data."""
    width: int
    height: int
    pixels: bytes  # BGR or BGRA, bottom-to-top row order
    has_alpha: bool = False


def write_tga(image: TGAImage, filepath: Path):
    """Write an uncompressed TGA file."""
    pixel_depth = 32 if image.has_alpha else 24

    # Image descriptor: bit 5 = 0 (origin bottom-left), bits 0-3 = alpha bits
    image_descriptor = 8 if image.has_alpha else 0

    header = struct.pack(
        '<3B2HB2H2HBB',
        0,                    # idLength
        0,                    # colorMapType
        2,                    # imageType (uncompressed true-color)
        0,                    # colorMapOrigin
        0,                    # colorMapLength
        0,                    # colorMapDepth
        0,                    # xOrigin
        0,                    # yOrigin
        image.width,          # width
        image.height,         # height
        pixel_depth,          # pixelDepth
        image_descriptor      # imageDescriptor
    )

    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'wb') as f:
        f.write(header)
        f.write(image.pixels)


def read_tga(filepath: Path) -> TGAImage:
    """Read an uncompressed or RLE TGA file."""
    with open(filepath, 'rb') as f:
        data = f.read()

    (
        id_length, colormap_type, image_type,
        cm_origin, cm_length, cm_depth,
        x_origin, y_origin,
        width, height,
        pixel_depth, image_descriptor
    ) = struct.unpack_from('<3B2HB2H2HBB', data, 0)

    if image_type not in (2, 10):
        raise ValueError(f"Unsupported TGA image type: {image_type}")

    has_alpha = pixel_depth == 32
    bytes_per_pixel = 4 if has_alpha else 3

    pixel_offset = 18 + id_length
    if colormap_type == 1:
        pixel_offset += cm_length * (cm_depth // 8)

    if image_type == 2:
        # Uncompressed
        pixel_data = data[pixel_offset:pixel_offset + width * height * bytes_per_pixel]
    else:
        # RLE compressed
        pixel_data = _decode_tga_rle(
            data[pixel_offset:], width, height, bytes_per_pixel
        )

    # Flip if origin is top-left (bit 5 set)
    if image_descriptor & 0x20:
        pixel_data = _flip_vertical(pixel_data, width, height, bytes_per_pixel)

    return TGAImage(
        width=width,
        height=height,
        pixels=pixel_data,
        has_alpha=has_alpha
    )


def _decode_tga_rle(data: bytes, width: int, height: int, bpp: int) -> bytes:
    """Decode RLE compressed TGA pixel data."""
    output = bytearray()
    total_pixels = width * height
    pixels_read = 0
    offset = 0

    while pixels_read < total_pixels and offset < len(data):
        packet_header = data[offset]
        offset += 1

        count = (packet_header & 0x7F) + 1

        if packet_header & 0x80:
            # RLE packet: repeat single pixel
            pixel = data[offset:offset + bpp]
            offset += bpp
            output.extend(pixel * count)
        else:
            # Raw packet: copy pixels
            size = count * bpp
            output.extend(data[offset:offset + size])
            offset += size

        pixels_read += count

    return bytes(output)


def _flip_vertical(data: bytes, width: int, height: int, bpp: int) -> bytes:
    """Flip image vertically (top to bottom)."""
    row_size = width * bpp
    rows = [data[i * row_size:(i + 1) * row_size] for i in range(height)]
    return b''.join(reversed(rows))


# =============================================================================
# Image Generation Utilities
# =============================================================================

def create_solid_color(
    width: int, height: int,
    r: int, g: int, b: int, a: Optional[int] = None
) -> TGAImage:
    """Create a solid color TGA image."""
    has_alpha = a is not None

    if has_alpha:
        pixel = bytes([b, g, r, a])  # BGRA
    else:
        pixel = bytes([b, g, r])     # BGR

    pixels = pixel * (width * height)

    return TGAImage(
        width=width,
        height=height,
        pixels=pixels,
        has_alpha=has_alpha
    )


def create_checkerboard(
    width: int, height: int,
    color1: Tuple[int, int, int] = (255, 0, 255),   # Magenta
    color2: Tuple[int, int, int] = (0, 0, 0),       # Black
    check_size: int = 8
) -> TGAImage:
    """Create a checkerboard pattern TGA (classic missing texture)."""
    pixels = bytearray()

    for y in range(height):
        for x in range(width):
            check_x = (x // check_size) % 2
            check_y = (y // check_size) % 2

            if check_x ^ check_y:
                pixels.extend([color1[2], color1[1], color1[0]])  # BGR
            else:
                pixels.extend([color2[2], color2[1], color2[0]])

    return TGAImage(width=width, height=height, pixels=bytes(pixels), has_alpha=False)


def create_gradient(
    width: int, height: int,
    color_start: Tuple[int, int, int] = (0, 0, 0),
    color_end: Tuple[int, int, int] = (255, 255, 255),
    vertical: bool = True
) -> TGAImage:
    """Create a gradient TGA for testing."""
    pixels = bytearray()

    for y in range(height):
        for x in range(width):
            if vertical:
                t = y / (height - 1) if height > 1 else 0
            else:
                t = x / (width - 1) if width > 1 else 0

            r = int(color_start[0] * (1 - t) + color_end[0] * t)
            g = int(color_start[1] * (1 - t) + color_end[1] * t)
            b = int(color_start[2] * (1 - t) + color_end[2] * t)
            pixels.extend([b, g, r])  # BGR

    return TGAImage(width=width, height=height, pixels=bytes(pixels), has_alpha=False)


def create_wood_texture(width: int = 256, height: int = 256) -> TGAImage:
    """Create a simple procedural wood-like texture."""
    import math
    pixels = bytearray()

    base_color = (139, 90, 43)  # Brown
    dark_color = (100, 60, 30)
    light_color = (180, 120, 60)

    for y in range(height):
        for x in range(width):
            # Create wood grain pattern
            noise = math.sin(x * 0.1 + y * 0.02) * 0.5 + 0.5
            noise += math.sin(y * 0.15) * 0.3
            noise = max(0, min(1, noise))

            # Blend between dark and light
            r = int(dark_color[0] * (1 - noise) + light_color[0] * noise)
            g = int(dark_color[1] * (1 - noise) + light_color[1] * noise)
            b = int(dark_color[2] * (1 - noise) + light_color[2] * noise)

            pixels.extend([b, g, r])  # BGR

    return TGAImage(width=width, height=height, pixels=bytes(pixels), has_alpha=False)


def apply_team_tint(
    image: TGAImage,
    tint_rgb: Tuple[int, int, int],
    strength: float = 0.5
) -> TGAImage:
    """Apply a color tint to an image for team variants."""
    bpp = 4 if image.has_alpha else 3
    pixels = bytearray(image.pixels)

    for i in range(0, len(pixels), bpp):
        b, g, r = pixels[i], pixels[i + 1], pixels[i + 2]

        # Blend with tint color
        r = int(r * (1 - strength) + tint_rgb[0] * strength)
        g = int(g * (1 - strength) + tint_rgb[1] * strength)
        b = int(b * (1 - strength) + tint_rgb[2] * strength)

        pixels[i] = min(255, max(0, b))
        pixels[i + 1] = min(255, max(0, g))
        pixels[i + 2] = min(255, max(0, r))

    return TGAImage(
        width=image.width,
        height=image.height,
        pixels=bytes(pixels),
        has_alpha=image.has_alpha
    )


if __name__ == "__main__":
    # Generate test textures
    output_dir = Path("test_textures")
    output_dir.mkdir(exist_ok=True)

    # Missing texture pattern
    checker = create_checkerboard(256, 256)
    write_tga(checker, output_dir / "missing_texture.tga")
    print("Generated missing_texture.tga")

    # Solid colors for placeholders
    for name, color in [("red", (255, 0, 0)), ("blue", (0, 0, 255)), ("gray", (128, 128, 128))]:
        img = create_solid_color(256, 256, *color)
        write_tga(img, output_dir / f"solid_{name}.tga")
        print(f"Generated solid_{name}.tga")

    # Wood texture
    wood = create_wood_texture()
    write_tga(wood, output_dir / "wood_planks.tga")
    print("Generated wood_planks.tga")

    print(f"\nGenerated test TGA files in {output_dir}/")
