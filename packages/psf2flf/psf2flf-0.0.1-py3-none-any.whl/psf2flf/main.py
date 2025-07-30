import argparse
from pathlib import Path
from .psf import load_psf_file
from .psf2flf import convert_psf_to_flf


def show_info(source: Path):
    font = load_psf_file(source)

    # Determine PSF version from font properties
    if hasattr(font, "flags") and font.width != 8:
        psf_version = "PSF2"
    else:
        psf_version = "PSF1" if font.width == 8 else "PSF2"

    print(f"Font: {source}")
    print(f"Format: {psf_version}")
    print(f"Width: {font.width}")
    print(f"Height: {font.height}")
    print(f"Flags: 0x{font.flags:08x}")

    # Decode PSF2 flags
    if hasattr(font, "flags"):
        flag_meanings = []
        if font.flags & 0x01:
            flag_meanings.append("HAS_UNICODE_TABLE")
        if not flag_meanings:
            flag_meanings.append("No flags set")
        print(f"Flag meanings: {', '.join(flag_meanings)}")

    print(f"Glyph count: {len(font.glyphs)}")

    # Show header and data layout info for PSF2
    print(f"Header size: {font.headersize}")
    print(f"Glyph data start: {font.glyph_data_start}")
    print(f"Glyph data length: {font.glyph_data_length}")
    print(f"Unicode data start: {font.unicode_data_start}")
    print(f"Unicode data length: {font.unicode_data_length}")

    if font.glyphs:
        bytes_per_glyph = len(font.glyphs[0])
        print(f"Bytes per glyph: {bytes_per_glyph}")

        # Calculate expected bytes for comparison
        expected_bytes = (font.width * font.height + 7) // 8
        print(f"Expected bytes (w*h/8): {expected_bytes}")

        if bytes_per_glyph != expected_bytes:
            ratio = bytes_per_glyph / expected_bytes
            print(f"Ratio (actual/expected): {ratio:.2f}")

            # Additional analysis for kbd-style fonts
            if bytes_per_glyph < expected_bytes:
                # Fewer bytes than expected - header width might be wrong
                actual_width_bits = bytes_per_glyph * 8 // font.height
                if actual_width_bits * font.height == bytes_per_glyph * 8:
                    print(f"Likely actual width: {actual_width_bits} pixels")
            elif bytes_per_glyph > expected_bytes:
                # More bytes than expected - vpitch padding or multiple planes
                if bytes_per_glyph % expected_bytes == 0:
                    planes = bytes_per_glyph // expected_bytes
                    print(f"Possible {planes} bitplanes detected")
                else:
                    # Check for vpitch-style padding
                    rows_in_storage = bytes_per_glyph * 8 // font.width
                    print(f"Storage rows: {rows_in_storage} (vs display height: {font.height})")
                    if rows_in_storage > font.height:
                        print(f"Possible vpitch padding: {rows_in_storage - font.height} extra rows")

    if hasattr(font, "unicode_map") and font.unicode_map:
        print(f"Unicode mapping entries: {len(font.unicode_map)}")


def convert_single(source: Path, dest: Path, use_short_blocks: bool = True):
    font = load_psf_file(source)

    # For single file conversion, dest is the output file
    if dest.suffix == ".flf":
        out_path = dest
    else:
        # If no .flf extension, add it
        out_path = dest.with_suffix(".flf")

    # Create parent directory if needed
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert with the specified output path
    from .psf2flf import write_flf_file

    write_flf_file(font, out_path, use_short_blocks)
    print(f"{source}\t{out_path}")


def convert_all(source_dir: Path, dest_dir: Path, use_short_blocks: bool = True):
    psf_files = list(source_dir.glob("*.psf")) + list(source_dir.glob("*.psf.gz"))
    for path in psf_files:
        try:
            font = load_psf_file(path)
            name = path.stem.replace(".psf", "").replace(".gz", "")
            out_path = convert_psf_to_flf(font, name, dest_dir, use_short_blocks)
            print(f"{path}\t{out_path}")
        except Exception as e:
            print(f"{path}\tERROR: {e}")


def main():
    parser = argparse.ArgumentParser(description="Convert PSF fonts to FLF (FIGlet) format.")
    parser.add_argument("source", nargs="?", help="PSF font file or input directory")
    parser.add_argument("dest", nargs="?", help="Output file (single) or directory (--all)")
    parser.add_argument("--all", action="store_true", help="Convert all PSF fonts in a directory")
    parser.add_argument("--info", action="store_true", help="Show font information instead of converting")
    parser.add_argument("--tall", action="store_true", help="Use full-size 1:1 pixel mapping instead of default 2x1 compression")
    args = parser.parse_args()

    if args.info:
        if not args.source:
            parser.error("You must provide a source PSF file when using --info.")
        show_info(Path(args.source))
    elif args.all:
        if not args.source or not args.dest:
            parser.error("You must provide source and dest directories when using --all.")
        convert_all(Path(args.source), Path(args.dest), not args.tall)
    else:
        if not args.source or not args.dest:
            parser.error("You must provide a source PSF file and dest file.")
        convert_single(Path(args.source), Path(args.dest), not args.tall)


if __name__ == "__main__":
    main()
