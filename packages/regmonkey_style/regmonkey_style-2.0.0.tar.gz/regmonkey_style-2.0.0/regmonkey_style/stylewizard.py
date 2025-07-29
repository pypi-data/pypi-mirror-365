# %%
from regmonkey_style.config import CONFIG
import plotly.io as pio
import matplotlib.pyplot as plt
import seaborn as sns
import regmonkey_style.common.setup_custom_font as scf
import regmonkey_style.plotly_custom.templates as pct
import regmonkey_style.matplotlib_custom.templates as mct
from regmonkey_style.common import utils


def show_available_fonts():
    return CONFIG.font_style.available_list


def show_available_templates():
    return CONFIG.templates


def set_font(font=CONFIG.font_style.default_font):
    if font not in CONFIG.font_style.available_list:
        if scf.is_font_available(font):
            scf.setup_font_from_system(font)
            return None
        else:
            raise ValueError("{} is not in templates list".format(font))    
    scf.add_custom_font(font)


def set_templates(template):
    """
    Set the Plotly/Matplotlib template for the application.

    Args:
        template (str): The name of the template to set.

    Raises:
        ValueError: If the specified template is not in the list of available templates.
    """
    if template not in CONFIG.templates:
        raise ValueError(f"{template} is not in the templates list")

    # Set Plotly template
    __set_plotly_template(template)

    # Set Matplotlib template
    __set_matplotlib_template(template)


def __set_plotly_template(template):
    """
    Set the Plotly template for the application.

    Args:
        template (str): The name of the template to set.
    """
    plotly_template_instance = pct.Templates
    plotly_custom_template = getattr(plotly_template_instance, template)()
    pio.templates[template] = plotly_custom_template
    pio.templates.default = template


def __set_matplotlib_template(template):
    """
    Set the Matplotlib template for the application.

    Args:
        template (str): The name of the template to set.
    """
    matplotlib_template_instance = mct.Templates
    matplotlib_custom_template = getattr(matplotlib_template_instance, template)()
    sns.set_style(rc=matplotlib_custom_template)
    plt.rcParams.update(matplotlib_custom_template)


def equal_xy_scale(figure_object):
    """
    Ensure equal scaling for the x and y axes of a Plotly figure.

    Args:
        figure_object: The Plotly or Matplotlib figure object to modify.

    Returns:
        figure_object: The modified Plotly figure object with equal x and y scaling.
    """
    return utils.equal_xy_scale(figure_object)


def restore_default():
    """
    Restore the default Plotly template and Matplotlib settings.

    This function resets the Plotly template to the default "plotly" template
    and restores the default Matplotlib settings.
    """
    pio.templates.default = "plotly"
    plt.rcdefaults()
