"""
Generate a colorscheme using Colorz.
"""

import logging
import sys

try:
    import colorz

except ImportError:
    logging.error("colorz wasn't found on your system.")
    logging.error("Try another backend. (wal --backend)")
    sys.exit(1)

from .. import colors
from .. import util


def gen_colors(img):
    """Generate a colorscheme using Colorz."""
    # pylint: disable=not-callable
    raw_colors = colorz.colorz(img, n=6, bold_add=0)
    return [util.rgb_to_hex([*color[0]]) for color in raw_colors]


def adjust(cols, light, cols16):
    """Create palette."""
    raw_colors = [cols[0], *cols, "#FFFFFF", "#000000", *cols, "#FFFFFF"]
    raw_colors[0] = util.darken_color(cols[0], 0.80)

    return colors.generic_adjust(raw_colors, light, cols16)


def get(img, light=False, cols16=False):
    """Get colorscheme."""
    cols = gen_colors(img)

    if len(cols) < 6:
        logging.error("colorz failed to generate enough colors.")
        logging.error("Try another backend or another image. (wal --backend)")
        sys.exit(1)

    return adjust(cols, light, cols16)
