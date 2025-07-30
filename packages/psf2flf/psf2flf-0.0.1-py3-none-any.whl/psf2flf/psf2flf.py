from pathlib import Path
from .psf import PSFFont

BLOCKS = {
    0b0000: " ",
    0b0001: "▗",
    0b0010: "▖",
    0b0011: "▄",
    0b0100: "▝",
    0b0101: "▐",
    0b0110: "▞",
    0b0111: "▟",
    0b1000: "▘",
    0b1001: "▚",
    0b1010: "▌",
    0b1011: "▙",
    0b1100: "▀",
    0b1101: "▜",
    0b1110: "▛",
    0b1111: "█",
}

GLYPHS = [chr(i) for i in range(32, 127)]
DEFAULT_CHAR = ord("?")


def bitmap_to_pixels(bitmap: bytes, width: int, height: int) -> list[list[bool]]:
    """Convert bitmap bytes to a 2D list of boolean pixels - exact Perl script logic."""
    pixels = []
    bytes_per_row = (width + 7) // 8

    # Match Perl script exactly: for each row, for each byte in row, for each bit in byte
    for y in range(height):
        row = []
        x = 0
        for byte_idx in range(bytes_per_row):
            bitmap_offset = y * bytes_per_row + byte_idx
            if bitmap_offset < len(bitmap):
                byte_value = bitmap[bitmap_offset]
            else:
                byte_value = 0

            # Process 8 bits, MSB first (like Perl: for (my $bit = 8; $bit--;))
            for bit in range(8):
                if x < width:  # Only add pixels within width
                    pixel_on = byte_value & (1 << (7 - bit))
                    row.append(bool(pixel_on))
                x += 1

        pixels.append(row)

    return pixels


def render_block_glyph(
    pixel_array: list[list[bool]], width: int, height: int, use_short_blocks: bool = True
) -> list[str]:
    """Render a glyph using block characters from pixel data."""
    if use_short_blocks:
        return render_short_blocks(pixel_array, width, height)
    else:
        return render_full_pixels(pixel_array, width, height)


def render_short_blocks(pixel_array: list[list[bool]], width: int, height: int) -> list[str]:
    """Render using 2x1 block compression (top/bottom halves)."""
    lines = []

    for y in range(0, height, 2):
        line = ""
        for x in range(width):
            # Get top and bottom pixels with proper bounds checking
            top_pixel = pixel_array[y][x] if y < height and x < width else False
            bottom_pixel = pixel_array[y + 1][x] if y + 1 < height and x < width else False

            # Choose block character based on top/bottom pattern
            if top_pixel and bottom_pixel:
                line += "█"  # Full block
            elif top_pixel and not bottom_pixel:
                line += "▀"  # Top half block
            elif not top_pixel and bottom_pixel:
                line += "▄"  # Bottom half block
            else:
                line += " "  # Empty
        lines.append(line)

    return lines


def render_full_pixels(pixel_array: list[list[bool]], width: int, height: int) -> list[str]:
    """Render using 1:1 pixel mapping."""
    lines = []

    for y in range(height):
        line = ""
        for x in range(width):
            if pixel_array[y][x]:
                line += "█"
            else:
                line += " "
        lines.append(line)

    return lines


def calculate_flf_dimensions(font_width: int, font_height: int, use_short_blocks: bool):
    """Calculate FLF output dimensions based on font size and compression mode."""
    if use_short_blocks:
        # 2x1 block compression (top/bottom)
        fig_height = (font_height + 1) // 2
        max_length = font_width
        display_width = font_width
    else:
        # 1:1 pixel mapping
        fig_height = font_height
        max_length = font_width
        display_width = font_width

    return fig_height, max_length, display_width


def write_flf_file(font: PSFFont, output_path: Path, use_short_blocks: bool = True):
    """Write FLF file with proper formatting."""
    height, width = font.height, font.width
    fig_height, max_length, display_width = calculate_flf_dimensions(width, height, use_short_blocks)

    hardblank = "$"
    layout = 0

    with output_path.open("w", encoding="utf-8") as f:
        f.write(f"flf2a{hardblank} {fig_height} {fig_height - 1} {max_length} 0 {layout} 0 0 {len(GLYPHS)}\n")
        for ch in GLYPHS:
            code = ord(ch)
            glyph = font.glyphs[code] if code < len(font.glyphs) else font.glyphs[DEFAULT_CHAR]
            rendered = render_block_glyph(glyph, font.width, font.height, use_short_blocks)

            # Ensure each character has exactly fig_height lines
            while len(rendered) < fig_height:
                rendered.append("")

            # Pad each line to max_length with hardblank and add terminators
            for i, line in enumerate(rendered):
                # Replace spaces with hardblank and pad to max_length
                padded_line = line.replace(" ", hardblank)
                while len(padded_line) < max_length:
                    padded_line += hardblank

                if i < len(rendered) - 1:
                    f.write(padded_line + "@\n")
                else:
                    f.write(padded_line + "@@\n")


def convert_psf_to_flf(font: PSFFont, name: str, output_dir: Path, use_short_blocks: bool = True) -> Path:
    height, width = font.height, font.width
    fig_height, max_length, display_width = calculate_flf_dimensions(width, height, use_short_blocks)

    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{name}-{display_width}x{height}.flf"

    write_flf_file(font, path, use_short_blocks)
    return path
