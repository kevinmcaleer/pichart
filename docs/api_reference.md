#### 3. **docs/api_reference.md**
A concise reference for all classes and key methods, derived from the docstrings.

```markdown
# PiChart API Reference

## Chart
A class for plotting data as bars, lines, or points.

- `__init__(display, title="", x_label=None, y_label=None, values=None)`: Create a chart.
  - `display`: Required display object.
  - `values`: List of numbers to plot.
- `update()`: Draw the chart.
- Properties:
  - `x, y`: Position (int).
  - `width, height`: Size (int).
  - `show_bars, show_lines, show_datapoints, show_labels`: Toggle display styles (bool).
  - `background_colour, data_colour, etc.`: Set colors (dict).

## Card
A text-only card, inherits from Chart.

- `__init__(display, x=0, y=0, width=100, height=100, title="")`: Create a card.
- `update()`: Draw the card.

## ImageTile
A tile for displaying JPEG images.

- `__init__(display, filename=None, x=0, y=0, width=100, height=100)`: Create an image tile.
  - `filename`: Path to JPEG file.
- `update()`: Draw the image with a border.

## Container
Manages multiple charts or cards in a grid.

- `__init__(display, width=None, height=None)`: Create a container.
- `add_chart(item)`: Add a Chart, Card, or ImageTile.
- `update()`: Draw all items.
- `cols`: Set number of columns (int).
- Properties: `background_colour`, `data_colour`, etc., apply to all items.
