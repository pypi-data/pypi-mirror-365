import plotly.graph_objs as go
import matplotlib.pyplot as plt


def equal_xy_scale(fig_object):
    """
    Ensure equal scale on both x and y axes for Matplotlib figures.

    This function checks if the provided object is a Matplotlib `Axes` or `Figure`,
    and applies equal scaling to all the subplots.

    Parameters:
    fig_object : Matplotlib `Axes` or `Figure` object
        The figure or axes to apply equal scaling to.
    """
    if isinstance(fig_object, go.Figure):
        fig_object.update_layout(
            xaxis=dict(
                scaleanchor="y",  # Lock x-axis scale to y-axis
                scaleratio=1,  # Ensure equal scale ratio
            ),
            yaxis=dict(
                scaleanchor="x",  # Lock y-axis scale to x-axis
                scaleratio=1,  # Ensure equal scale ratio
            ),
        )
    elif isinstance(fig_object, plt.Axes):  # Check if it's an Axes object
        fig_object.set_aspect("equal", "box")
    elif isinstance(fig_object, plt.Figure):  # If it's a Figure, apply to all axes
        for ax in fig_object.get_axes():
            ax.set_aspect("equal", "box")
    else:
        raise TypeError("The object is not a valid Matplotlib Figure or Axes")

    return fig_object
