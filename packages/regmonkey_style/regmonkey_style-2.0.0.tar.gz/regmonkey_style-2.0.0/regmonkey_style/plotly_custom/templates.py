# %%
from regmonkey_style.config import CONFIG


class Templates:
    @classmethod
    def regmonkey_scatter(cls):
        custom_template = dict(
            {
                "data": {
                    "scatter": [
                        {
                            "mode": "markers",
                            "opacity": CONFIG.scatter.opacity,
                            "marker": {"size": CONFIG.scatter.markersize.plotly},
                            "line": {"width": CONFIG.common.line_width},
                        }
                    ]
                },
                "layout": cls._create_layout_template(
                    CONFIG.color_style.qualitative_scatter_color
                ),
            }
        )

        return custom_template

    @classmethod
    def regmonkey_line(cls):
        custom_template = dict(
            {
                "data": {
                    "scatter": [
                        {
                            "mode": "lines",
                            "opacity": CONFIG.line.opacity,
                            "marker": {"size": CONFIG.scatter.markersize.plotly},
                            "line": {"width": CONFIG.common.line_width},
                            "connectgaps": True,
                        }
                    ]
                },
                "layout": cls._create_layout_template(
                    CONFIG.color_style.qualitative_line_color
                ),
            }
        )

        return custom_template

    @classmethod
    def regmonkey_twoline(cls):
        custom_template = dict(
            {
                "data": {
                    "scatter": [
                        {
                            "mode": "markers+lines",
                            "line": {"dash": "solid"},
                            "connectgaps": True,
                        },
                        {
                            "mode": "markers+lines",
                            "line": {"dash": "solid"},
                            "connectgaps": True,
                        },
                        {
                            "mode": "markers+lines",
                            "line": {"dash": "solid"},
                            "connectgaps": True,
                        },
                        {
                            "mode": "markers+lines",
                            "line": {"dash": "dash"},
                            "connectgaps": True,
                        },
                        {
                            "mode": "markers+lines",
                            "line": {"dash": "dash"},
                            "connectgaps": True,
                        },
                        {
                            "mode": "markers+lines",
                            "line": {"dash": "dot"},
                            "connectgaps": True,
                        },
                        {
                            "mode": "markers+lines",
                            "line": {"dash": "dot"},
                            "connectgaps": True,
                        },
                    ]
                },
                "layout": cls._create_layout_template(
                    CONFIG.color_style.two_line_color
                ),
            }
        )

        return custom_template

    @classmethod
    def regmonkey_boxplot(cls):
        custom_layout_template = cls._create_layout_template(
            CONFIG.color_style.two_line_color
        )
        # Define the layout as a dictionary
        custom_layout_template.update(
            {
                "boxmode": "group",  # Group boxes for comparison
                "plot_bgcolor": CONFIG.color_style.background_color,
                "margin": CONFIG.boxplot.margin.plotly,
                "font": {
                    "size": CONFIG.boxplot.fontsize.text_fontsize,
                    "color": "black",
                },
                "xaxis": {
                    "title": {
                        "text": "X-axis Title",
                        "standoff": CONFIG.common.fontsize.standoff,
                    },
                    "tickfont": {"size": CONFIG.boxplot.fontsize.xlabel_fontsize},
                    "showgrid": False,
                    "showline": True,
                    "zeroline": False,
                },
                "yaxis": {
                    "title": {
                        "text": "Y-axis Title",
                        "standoff": CONFIG.common.fontsize.standoff,
                    },
                    "tickfont": {"size": CONFIG.boxplot.fontsize.tick_fontsize},
                    # "scaleanchor": "x",  # Lock y-axis scale to x-axis
                    # "scaleratio": 1,  # Ensure equal scale ratio
                    "showgrid": True,
                    "showline": False,
                    "zeroline": False,
                    "griddash": CONFIG.boxplot.gridline.griddash.plotly,
                    "gridcolor": CONFIG.color_style.grid_color,
                    "gridwidth": CONFIG.boxplot.gridline.gridwidth,
                },
                "legend": {
                    "font": {"size": CONFIG.common.fontsize.tick_fontsize},
                    "bgcolor": CONFIG.color_style.legend_background_color,
                    "traceorder": "normal",
                },
            }
        )
        # Create a template with the layout
        custom_template = dict(
            layout=custom_layout_template,
            # data={
            #     "box":[  # The box property should be a list
            #         dict(
            #             jitter=CONFIG.boxplot.jitter,  # Jitter applied globally
            #             marker=dict(
            #                 color=CONFIG.boxplot.outliercolor,
            #                 size=CONFIG.boxplot.markersize.plotly,
            #                 outliercolor=CONFIG.boxplot.outliercolor,
            #                 line=dict(outlierwidth=0),
            #             ),
            #             line=dict(color="black", width=1.3),
            #             fillcolor="white",
            #             width=0.5,
            #             boxpoints="suspectedoutliers",  # Show suspected outliers
            #         ),
            #     ]
            # },
        )

        return custom_template

    @classmethod
    def _create_layout_template(cls, color_way):
        """
        Create a default layout template for Plotly.

        Args:
            color_way (list): List of colors to be used in the color cycle.

        Returns:
            dict: A dictionary representing the default layout template.
        """

        default_layout = dict(
            {
                "plot_bgcolor": "#EFF5F5",
                "margin": CONFIG.common.margin.plotly,
                "shapes": [],  # You can add shapes here if needed
                "paper_bgcolor": CONFIG.color_style.paper_bgcolor,
                "colorway": color_way,  # Color cycle for lines
                "font": {
                    "size": CONFIG.common.fontsize.text_fontsize,
                    "color": CONFIG.color_style.text_color,
                },
                "title": {
                    "font": {"size": CONFIG.common.fontsize.title_fontsize},
                    "x": 0.001,  # Horizontal position (left-aligned),
                    "yanchor": "top",
                    "xanchor": "left",
                    "xref": "paper"
                },
                "autosize": True,
                "legend": {
                    "font": {"size": CONFIG.common.fontsize.tick_fontsize},
                    "bgcolor": CONFIG.color_style.legend_background_color,
                    "traceorder": "normal",
                },
                "xaxis": {
                    "title": {
                        "text": "X-axis Title",
                        "standoff": CONFIG.common.fontsize.standoff,
                    },
                    "tickfont": {"size": CONFIG.common.fontsize.tick_fontsize},
                    "showgrid": True,
                    "showline": True,
                    "griddash": "dot",
                    "gridcolor": CONFIG.color_style.grid_color,
                    "gridwidth": CONFIG.common.gridline.gridwidth,
                    "zeroline": True,
                    "zerolinecolor": CONFIG.color_style.zeroline_color,
                    "zerolinewidth": CONFIG.common.gridline.gridwidth,
                },
                "yaxis": {
                    "title": {
                        "text": "Y-axis Title",
                        "standoff": CONFIG.common.fontsize.standoff,
                    },
                    "tickfont": {"size": CONFIG.common.fontsize.tick_fontsize},
                    # "scaleanchor": "x",  # Lock y-axis scale to x-axis
                    # "scaleratio": 1,  # Ensure equal scale ratio
                    "showgrid": True,
                    "showline": True,
                    "griddash": "dot",
                    "gridcolor": CONFIG.color_style.grid_color,
                    "gridwidth": CONFIG.common.gridline.gridwidth,
                    "zeroline": True,
                    "zerolinecolor": CONFIG.color_style.zeroline_color,
                    "zerolinewidth": CONFIG.common.gridline.gridwidth,
                },
            }
        )
        return default_layout
