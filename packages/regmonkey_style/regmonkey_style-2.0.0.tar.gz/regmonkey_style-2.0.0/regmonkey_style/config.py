# %%
import pathlib
import yaml
from pydantic import BaseModel


class ColorStyle(BaseModel):
    qualitative_scatter_color: list[str]
    qualitative_line_color: list[str]
    discrete_color_sequence: list[str]
    two_line_color: list[str]
    background_color: str
    paper_bgcolor: str
    text_color: str
    legend_background_color: str
    grid_color: str
    zeroline_color: str


class FontStyle(BaseModel):
    default_font: str
    available_list: list[str]


class Margin(BaseModel):
    plotly: dict


class Griddash(BaseModel):
    plotly: str
    matplotlib: str


class Gridline(BaseModel):
    gridwidth: float
    griddash: Griddash


class Markersize(BaseModel):
    matplotlib: int
    plotly: int


class Fontsize(BaseModel):
    title_fontsize: int
    xlabel_fontsize: int
    ylabel_fontsize: int
    legend_fontsize: int
    text_fontsize: int
    tick_fontsize: int
    standoff: int


class Common(BaseModel):
    fontsize: Fontsize
    margin: Margin
    gridline: Gridline
    line_width: int


class Scatter(BaseModel):
    opacity: float
    markersize: Markersize


class Line(BaseModel):
    opacity: float


class Boxplot(BaseModel):
    opacity: float
    outliercolor: str
    line_color: str
    fillcolor: str
    jitter: float
    markersize: Markersize
    fontsize: Fontsize
    linewdith: float
    gridline: Gridline
    margin: Margin


class Config(BaseModel):
    """Config is a model for the configuration file of the project.
    This model should be generated from new_config function.
    """

    color_style: ColorStyle
    font_style: FontStyle
    common: Common
    scatter: Scatter
    line: Line
    boxplot: Boxplot
    templates: list[str]


def new_config(path_to_config: pathlib.Path) -> Config:
    """Generates a Config object from a yaml file.

    Args:
        path_to_config (str): Path to the configuration file.

    Returns:
        Config: A Config object.

    Example:
        >>> new_config(
        ...     "../configs/config.yaml"
        ... )
        Config(discrete_color_sequence=["#0E3666", "#428CE6", "#B4D7FF", "#E8F1FE"])
    """

    with open(path_to_config) as f:
        yaml_config = yaml.safe_load(f)
    config: Config = Config.model_validate(yaml_config)

    return config


PATH_TO_CONFIG: pathlib.Path = (
    pathlib.Path(__file__).parent / "configs/config.yaml"
)  # For package use, use __file__ instead of relative path
CONFIG: Config = new_config(path_to_config=PATH_TO_CONFIG)
