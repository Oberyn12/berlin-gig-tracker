"""
Generate PWA icon PNGs using only stdlib (no Pillow needed).

Creates web/icon-192.png and web/icon-512.png — simple dark background
with a white music note (♪). Called once during setup.

Run from repo root:
    python setup/generate_icons.py
"""
import struct
import zlib
from pathlib import Path

WEB_DIR = Path(__file__).parent.parent / "web"


def _make_png(size: int) -> bytes:
    """Generate a minimal valid PNG: dark bg (#0a0a0a) with a centred white circle."""
    width = height = size
    bg = (10, 10, 10)     # #0a0a0a
    fg = (255, 255, 255)  # white

    # Build raw pixel rows
    rows = bytearray()
    cx, cy, r = width // 2, height // 2, int(size * 0.32)

    for y in range(height):
        rows.append(0)  # filter type None per row
        for x in range(width):
            dx, dy = x - cx, y - cy
            # Draw a filled circle in the centre
            if dx * dx + dy * dy <= r * r:
                # Draw a simple ♪ shape using a smaller offset circle + stem
                # Circle head: top-right quadrant
                hx, hy = int(size * 0.12), int(size * -0.05)
                hr = int(size * 0.10)
                in_head = (dx - hx) ** 2 + (dy - hy) ** 2 <= hr ** 2
                # Stem: vertical bar
                in_stem = abs(dx - hx - hr // 2) <= max(2, size // 60) and -int(size * 0.28) <= dy - hy <= int(size * 0.05)
                # Flag: horizontal bar at top of stem
                in_flag = in_stem and dy - hy <= -int(size * 0.14) and dx - hx - hr // 2 <= int(size * 0.16)

                if in_head or in_stem or in_flag:
                    rows += bytes(fg)
                else:
                    rows += bytes(bg)
            else:
                rows += bytes(bg)

    compressed = zlib.compress(bytes(rows), 9)

    def chunk(tag: bytes, data: bytes) -> bytes:
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)  # 8-bit RGB
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", compressed)
        + chunk(b"IEND", b"")
    )


def main():
    WEB_DIR.mkdir(parents=True, exist_ok=True)
    for size, name in [(192, "icon-192.png"), (512, "icon-512.png")]:
        path = WEB_DIR / name
        path.write_bytes(_make_png(size))
        print(f"✓ {path} ({size}×{size})")


if __name__ == "__main__":
    main()
