# %%

from regmonkey_style.config import CONFIG
import matplotlib.pyplot as plt


def add_transparency(colors, alpha):
    """
    Add transparency to a list of colors in #RRGGBB format.

    Args:
        colors (list): List of color hex codes in #RRGGBB format.
        alpha (float): Transparency level (0.0 to 1.0).

    Returns:
        list: List of colors with added transparency in #RRGGBBAA format.
    """

    def hex_with_alpha(color, alpha):
        """
        Add alpha transparency to a single hex color.

        Args:
            color (str): Color hex code in #RRGGBB format.
            alpha (float): Transparency level (0.0 to 1.0).

        Returns:
            str: Color hex code in #RRGGBBAA format.
        """
        alpha_hex = f"{int(alpha * 255):02x}"
        return color + alpha_hex

    return [hex_with_alpha(color, alpha) for color in colors]


class Templates:
    @classmethod
    def regmonkey_scatter(cls):
        custom_colorway = plt.cycler(
            color=add_transparency(
                CONFIG.color_style.qualitative_scatter_color, CONFIG.scatter.opacity
            )
        )
        custom_layout_template = cls._create_layout_template(custom_colorway)
        custom_linewidth_template = cls._create_gridline_template(
            CONFIG.common.gridline.gridwidth * 4,
            CONFIG.common.gridline.gridwidth * 10,
        )

        custom_template = custom_layout_template | custom_linewidth_template

        ## update
        scatter_custom = dict(
            {"lines.markersize": CONFIG.scatter.markersize.matplotlib}
        )

        custom_template.update(scatter_custom)
        return custom_template

    @classmethod
    def regmonkey_line(cls):
        custom_colorway = plt.cycler(
            color=add_transparency(
                CONFIG.color_style.qualitative_line_color, CONFIG.line.opacity
            )
        )
        custom_layout_template = cls._create_layout_template(custom_colorway)
        custom_linewidth_template = cls._create_gridline_template(
            CONFIG.common.gridline.gridwidth * 4,
            CONFIG.common.gridline.gridwidth * 10,
        )

        custom_template = custom_layout_template | custom_linewidth_template

        return custom_template

    @classmethod
    def regmonkey_twoline(cls):
        custom_colorway = plt.cycler(
            color=CONFIG.color_style.two_line_color
        ) + plt.cycler(linestyle=["-", "-", "-", "--", "--", ":", ":"])

        custom_layout_template = cls._create_layout_template(custom_colorway)
        custom_linewidth_template = cls._create_gridline_template(
            CONFIG.common.gridline.gridwidth * 8,
            CONFIG.common.gridline.gridwidth * 10,
        )

        custom_template = custom_layout_template | custom_linewidth_template

        return custom_template

    @classmethod
    def regmonkey_boxplot(cls):
        custom_colorway = plt.cycler(
            color=add_transparency(CONFIG.color_style.two_line_color, 0.8)
        )

        custom_layout_template = cls._create_layout_template(custom_colorway)
        custom_linewidth_template = cls._create_gridline_template(
            CONFIG.common.gridline.gridwidth * 8,
            CONFIG.common.gridline.gridwidth * 10,
        )

        custom_boxplot_template = dict(
            {
                "axes.spines.left": False,
                "boxplot.medianprops.color": CONFIG.boxplot.line_color,
                "boxplot.flierprops.markersize": CONFIG.boxplot.markersize.matplotlib,
                "boxplot.flierprops.markeredgecolor": CONFIG.boxplot.outliercolor,
                "boxplot.flierprops.markersize": 5,
                "patch.facecolor": "white",
                "boxplot.patchartist": True,
                "patch.force_edgecolor": True,
                "boxplot.capprops.color": CONFIG.boxplot.line_color,
                "boxplot.boxprops.color": CONFIG.boxplot.line_color,
            }
        )

        custom_template = custom_layout_template | custom_linewidth_template
        custom_template.update(custom_boxplot_template)

        return custom_template

    @classmethod
    def _create_layout_template(cls, color_way):
        matplotlib_plotly_ratio = 1.3
        default_layout = dict(
            {
                "figure.facecolor": CONFIG.color_style.background_color,
                "axes.facecolor": CONFIG.color_style.background_color,
                "axes.edgecolor": "black",
                "font.size": CONFIG.common.fontsize.text_fontsize
                / matplotlib_plotly_ratio,
                "axes.titlelocation": "left",
                "axes.titlesize": CONFIG.common.fontsize.title_fontsize
                / (matplotlib_plotly_ratio * 1.1),
                "axes.labelsize": CONFIG.common.fontsize.xlabel_fontsize
                / matplotlib_plotly_ratio,
                "xtick.labelsize": CONFIG.common.fontsize.tick_fontsize
                / matplotlib_plotly_ratio,
                "ytick.labelsize": CONFIG.common.fontsize.tick_fontsize
                / matplotlib_plotly_ratio,
                "legend.fontsize": CONFIG.common.fontsize.legend_fontsize
                / matplotlib_plotly_ratio,
                "legend.frameon": False,
                "legend.loc": "upper right",  # Change location to upper left
                "axes.grid": True,
                "grid.linestyle": ":",
                "grid.color": CONFIG.color_style.grid_color,
                "axes.spines.top": False,
                "axes.spines.right": False,
                "axes.spines.left": True,
                "axes.spines.bottom": True,
                "axes.prop_cycle": color_way,
                "figure.subplot.wspace": 0.2,
                "text.color": CONFIG.color_style.text_color,  # Set text color
                "axes.labelcolor": CONFIG.color_style.text_color,  # Set axes label color
                "xtick.color": CONFIG.color_style.text_color,  # Set x-tick color
                "ytick.color": CONFIG.color_style.text_color,  # Set y-tick color
                "axes.titlecolor": CONFIG.color_style.text_color,  # Set axes title color
            }
        )
        return default_layout

    @classmethod
    def _create_gridline_template(cls, gridline_width, axesline_width):
        default_layout = dict(
            {
                "grid.linewidth": gridline_width,
                "axes.linewidth": axesline_width,
            }
        )
        return default_layout
