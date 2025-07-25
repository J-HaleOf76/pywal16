"""
                                      '||
... ...  .... ... ... ... ...  ....    ||
 ||'  ||  '|.  |   ||  ||  |  '' .||   ||
 ||    |   '|.|     ||| |||   .|' ||   ||
 ||...'     '|       |   |    '|..'|' .||.
 ||      .. |
''''      ''
Created by Dylan Araps.
"""

import argparse
import logging
import os
import shutil
import sys

from .settings import __version__, CACHE_DIR, CONF_DIR
from . import colors
from . import export
from . import image
from . import reload
from . import sequences
from . import theme
from . import util
from . import wallpaper
from . import donation
from . import eastereggs


show_colorama_warning = False
if sys.platform.startswith("win"):
    try:
        import colorama
        colorama.just_fix_windows_console()
    except ImportError:
        no_colorama_terms = [
                "wezterm",
                "alacritty",
                "hyper",
                "putty",
                "ghostty",
                "mintty",
                ]
        if os.environ.get("TERMINAL") not in no_colorama_terms and \
           os.environ.get("TERM_PROGRAM") not in no_colorama_terms:
            show_colorama_warning = True


def get_args():
    """Get the script arguments."""
    description = "wal - Generate colorschemes on the fly"
    arg = argparse.ArgumentParser(description=description)

    arg.add_argument(
        "-a",
        metavar='"alpha"',
        help="Set terminal background transparency. \
              Must be a number between 0 and 100. \
              *Only works in terminals that implement OSC-11 (URxvt)*",
    )

    arg.add_argument(
        "-b", metavar="background", help="Custom background color to use."
    )

    arg.add_argument(
        "--fg", metavar="foreground", help="Custom foreground color to use."
    )

    arg.add_argument(
        "--backend",
        metavar="backend",
        help="Which color backend to use. \
                           Use 'wal --backend' to list backends.",
        const="list_backends",
        type=str,
        nargs="?",
    )

    arg.add_argument(
        "--out-dir",
        metavar="out_dir",
        help="Cache dir to export themes. \
              Default is 'XDG_CACHE_HOME/wal'. \
              This can also be set with the env var: 'PYWAL_CACHE_DIR'",
        type=str,
        nargs="?",
    )

    arg.add_argument(
        "--theme",
        "-f",
        metavar="/path/to/file or theme_name",
        help="Which colorscheme file to use. \
                           Use 'wal --theme' to list builtin and user themes.",
        const="list_themes",
        nargs="?",
    )

    arg.add_argument(
        "--iterative",
        action="store_true",
        help="When pywal is given a directory as input and this "
        "flag is used: Go through the images in order "
        "instead of shuffled.",
    )

    arg.add_argument(
        "--cols16",
        metavar="method",
        required=False,
        nargs="?",
        default=False,
        const="darken",
        choices=["darken", "lighten"],
        help="Use 16 color output " '"darken" or "lighten" default: darken',
    )

    arg.add_argument(
        "--recursive",
        action="store_true",
        help="When pywal is given a directory as input and this "
        "flag is used: Search for images recursively in "
        "subdirectories instead of the root only.",
    )

    arg.add_argument(
        "--saturate", metavar="-1.0 - 1.0", help="Set the color saturation."
    )

    arg.add_argument(
        "--preview",
        action="store_true",
        help="Print the current color palette.",
    )

    arg.add_argument(
        "--vte",
        action="store_true",
        help="Fix text-artifacts printed in VTE terminals.",
    )

    arg.add_argument(
        "-c", action="store_true", help="Delete all cached colorschemes."
    )

    arg.add_argument(
        "-i",
        metavar='"/path/to/img.jpg"',
        help="Which image or directory to use.",
    )

    arg.add_argument(
        "-l", action="store_true", help="Generate a light colorscheme."
    )

    arg.add_argument(
        "-n", action="store_true", help="Skip setting the wallpaper."
    )

    arg.add_argument(
        "-o",
        metavar='"script_name"',
        action="append",
        help='External script to run after "wal".',
    )

    arg.add_argument(
        "-p",
        metavar='"theme_name"',
        help="permanently save theme to "
        "$XDG_CONFIG_HOME/wal/colorschemes with "
        "the specified name",
    )

    arg.add_argument(
        "-q", action="store_true", help="Quiet mode, don't print anything."
    )

    arg.add_argument(
        "-r",
        action="store_true",
        help="'wal -r' is deprecated: Use \
                           (cat ~/.cache/wal/sequences &) instead.",
    )

    arg.add_argument(
        "-R", action="store_true", help="Restore previous colorscheme."
    )

    arg.add_argument(
        "-s", action="store_true", help="Skip changing colors in terminals."
    )

    arg.add_argument(
        "-t", action="store_true", help="Skip changing colors in tty."
    )

    arg.add_argument("-v", action="store_true", help='Print "wal" version.')

    arg.add_argument(
        "-w",
        action="store_true",
        help="Use last used wallpaper for color generation.",
    )

    arg.add_argument(
        "-e",
        action="store_true",
        help="Skip reloading gtk/xrdb/i3/sway/polybar",
    )

    arg.add_argument(
        "--contrast",
        metavar="1.0-21.0",
        required=False,
        type=float,
        nargs="?",
        help="Specify a minimum contrast ratio between palette "
        "colors and the source image according to W3 "
        "contrast specifications. Values between 1.5-4.5 "
        "typically work best.",
    )

    return arg


def parse_args_exit(parser):
    """Process args that exit."""
    args = parser.parse_args()

    if len(sys.argv) <= 1:
        parser.print_help()
        sys.exit(1)

    if args.v:
        parser.exit(0, "wal %s\n" % __version__)

    if args.preview:
        print("Current colorscheme:", sep="")
        colors.palette()
        sys.exit(0)

    if args.r:
        reload.colors()
        sys.exit(0)

    if args.c:
        scheme_dir = os.path.join(CACHE_DIR, "schemes")
        shutil.rmtree(scheme_dir, ignore_errors=True)
        sys.exit(0)

    if (
        not args.i
        and not args.theme
        and not args.R
        and not args.w
        and not args.backend
    ):
        parser.error(
            "No input specified.\n" "--backend, --theme, -i or -R are required."
        )

    if args.theme == "list_themes":
        theme.list_out()
        sys.exit(0)

    if args.backend == "list_backends":
        print(
            "\n - ".join(
                ["\033[1;32mBackends\033[0m:", *colors.list_backends()]
            )
        )
        sys.exit(0)


def parse_args(parser):
    """Process args."""
    args = parser.parse_args()

    if args.q:
        logging.getLogger().disabled = True
        sys.stdout = sys.stderr = open(os.devnull, "w")

    if args.a:
        util.alpha_integrify(args.a)
        util.Color.passed_alpha_num = args.a
        util.Color.alpha_num = args.a or util.Color.alpha_num

    if args.i and not args.theme:
        image_file = image.get(
            args.i, iterative=args.iterative, recursive=args.recursive
        )
        colors_plain = colors.get(
            image_file,
            args.l,
            args.backend,
            sat=args.saturate,
            c16=args.cols16,
            cst=args.contrast,
        )

    if args.theme:
        colors_plain = theme.file(args.theme, args.l, c16=args.cols16)
        if args.i:
            colors_plain["wallpaper"] = args.i

    if args.R:
        colors_plain = theme.file(os.path.join(CACHE_DIR, "colors.json"))

    if args.w:
        cached_wallpaper = util.read_file(os.path.join(CACHE_DIR, "wal"))
        colors_plain = colors.get(
            cached_wallpaper[0],
            args.l,
            args.backend,
            sat=args.saturate,
            c16=args.cols16,
            cst=args.contrast,
        )

    if args.b:
        args.b = "#%s" % (args.b.strip("#"))
        colors_plain["special"]["background"] = args.b
        colors_plain["colors"]["color0"] = args.b

    if args.fg:
        args.fg = "#%s" % (args.fg.strip("#"))
        colors_plain["special"]["foreground"] = args.fg
        colors_plain["colors"]["color15"] = args.fg

    if not args.n:
        wallpaper.change(colors_plain["wallpaper"])

    if args.p:
        theme.save(colors_plain, args.p, args.l)

    sequences.send(colors_plain, to_send=not args.s, vte_fix=args.vte)

    if sys.stdout.isatty():
        colors.palette()

    if args.out_dir:
        export.every(colors_plain, CACHE_DIR)
    else:
        export.every(colors_plain)

    if not args.e:
        reload.env(tty_reload=not args.t)

    if args.o:
        for cmd in args.o:
            util.disown([cmd])


def main():
    """Main script function."""
    global CACHE_DIR
    default_cache_dir = CACHE_DIR
    util.create_dir(os.path.join(CONF_DIR, "templates"))
    util.create_dir(os.path.join(CONF_DIR, "colorschemes/light/"))
    util.create_dir(os.path.join(CONF_DIR, "colorschemes/dark/"))

    util.setup_logging()

    if show_colorama_warning:
        logging.warning("colorama is not present")

    parser = get_args()

    args = parser.parse_args()
    if args.out_dir:
        CACHE_DIR = args.out_dir
    else:
        CACHE_DIR = default_cache_dir

    parse_args_exit(parser)
    parse_args(parser)
    donation.donation_message()
    eastereggs.eemsg()


if __name__ == "__main__":
    main()
