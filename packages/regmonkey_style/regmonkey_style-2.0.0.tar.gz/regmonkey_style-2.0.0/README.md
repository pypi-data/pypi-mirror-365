Sure, here's a README for the [`regmonkey_style`](https://github.com/RyoNakagami/regmonkey-style) package:

# regmonkey_style

[`regmonkey_style`](https://github.com/RyoNakagami/regmonkey-style) is a Python package designed to simplify the customization of Plotly visualizations. It provides functions to set default fonts, show available fonts and templates, set custom fonts and templates, and ensure equal scaling for x and y axes in Plotly figures.

## Installation

To install the package, use pip:

```sh
pip install git+https://github.com/ryonakagami/regmonkey_style.git
```

## Usage

### Importing the Package

```python
from regmonkey_style import set_default, show_available_fonts, show_available_templates, set_font, set_templates, equal_xy_scale, restore_default
```

### Functions

#### `set_default()`

Sets the default font style for Plotly visualizations.

```python
set_default()
```

#### `show_available_fonts()`

Returns a list of available fonts.

```python
fonts = show_available_fonts()
print(fonts)
```

#### `show_available_templates()`

Returns a list of available templates.

```python
templates = show_available_templates()
print(templates)
```

#### `set_font(font)`

Sets a custom font for Plotly visualizations. Raises a [`ValueError`] if the font is not in the available list.

```python
try:
    set_font('CustomFont')
except ValueError as e:
    print(e)
```

#### `set_templates(template)`

Sets a custom template for Plotly visualizations. Raises a [`ValueError`] if the template is not in the available list.

```python
try:
    set_templates('CustomTemplate')
except ValueError as e:
    print(e)
```

#### `equal_xy_scale(figure_object)`

Ensures that the x and y axes of a Plotly figure have equal scaling.

```python
import plotly.graph_objects as go

fig = go.Figure()
# Add data to the figure
fig = equal_xy_scale(fig)
fig.show()
```

#### `restore_default()`

Restores the default Plotly template.

```python
restore_default()
```

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/RyoNakagami/regmonkey-style/blob/main/LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## Contact

For any questions or issues, please contact the maintainer at [Ryo Nakagami](nakagamiryo@alumni.u-tokyo.ac.jp).
