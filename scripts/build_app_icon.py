#!/usr/bin/env python3
"""Generate a simple SITESELECT app icon PNG (1024x1024)."""

from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw


def main() -> None:
    out = Path("assets/siteselect_1024.png")
    out.parent.mkdir(parents=True, exist_ok=True)

    size = 1024
    img = Image.new("RGBA", (size, size), (18, 34, 60, 255))
    d = ImageDraw.Draw(img)

    # rounded square backdrop
    d.rounded_rectangle((80, 80, 944, 944), radius=190, fill=(25, 118, 210, 255))

    # map-pin style mark
    d.ellipse((310, 220, 714, 624), fill=(255, 255, 255, 245))
    d.ellipse((420, 330, 604, 514), fill=(25, 118, 210, 255))
    d.polygon([(512, 865), (380, 560), (644, 560)], fill=(255, 255, 255, 245))

    img.save(out)
    print(out)


if __name__ == "__main__":
    main()
