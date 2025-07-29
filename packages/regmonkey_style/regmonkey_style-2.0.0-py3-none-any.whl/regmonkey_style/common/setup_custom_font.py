import os
import matplotlib
from matplotlib import font_manager
import plotly.io as pio

FONTS_DIR = "../fonts/"


def get_font_path(PATH):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), FONTS_DIR + PATH))


def add_custom_font(FONT_NAME: str) -> None:
    # setup
    current_template = pio.templates.default
    font_dirs = [get_font_path(FONT_NAME)]
    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
    for f in font_files:
        font_manager.fontManager.addfont(f)
        pio.templates[current_template]["layout"]["font"] = dict(family=f)

    SYSTEM_FONT_NAME = font_manager.FontProperties(fname=font_files[0]).get_name()
    matplotlib.rcParams["font.family"] = SYSTEM_FONT_NAME
    pio.templates[current_template]["layout"]["font"] = dict(family=SYSTEM_FONT_NAME)


def is_font_available(font_name: str) -> bool:
    fonts = font_manager.findSystemFonts()
    for font in fonts:
        if font_name in font:
            return True
    return False


def setup_font_from_system(SYSTEM_FONT_NAME: str) -> None:
    # setup
    current_template = pio.templates.default

    matplotlib.rcParams["font.family"] = SYSTEM_FONT_NAME
    pio.templates[current_template]["layout"]["font"] = dict(family=SYSTEM_FONT_NAME)
