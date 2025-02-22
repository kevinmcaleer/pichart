# PiChart User Guide

## Overview
PiChart lets you create simple dashboards on MicroPython displays. Use it to plot data (e.g., sensor readings), show status cards, or display images.

## Setup
1. **Hardware**: Connect a display (e.g., Pico Display Pack) to your Pico.
2. **Firmware**: Flash your device with a MicroPython build including `jpegdec` (e.g., Pimoroni’s).
3. **Install**: Upload `pichart.py` to your device’s root directory.

## Basic Usage
### Creating a Chart
```python
from pichart import Chart
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY

display = PicoGraphics(display=DISPLAY_PICO_DISPLAY)
chart = Chart(display, title="Pressure", values=[1010, 1012, 1008, 1015])
chart.x = 0
chart.y = 0
chart.width = 240
chart.height = 135
chart.update()  # Draws the chart
```

# Adding a Text Card
```python
from pichart import Card
card = Card(display, x=0, y=140, width=240, height=50, title="Status: OK")
card.update()
```

# Using a Container
```python
from pichart import Container
container = Container(display)
container.add_chart(chart)
container.add_chart(card)
container.cols = 1  # Stack vertically
container.update()
```

# Customization
- Colors: Set `background_colour`, `data_colour`, etc., with `{'red': 0-255, 'green': 0-255, 'blue': 0-255}`.
- Display Options: `Toggle show_bars`, `show_lines`, `show_datapoints`, `show_labels`, and `grid`.
- Size: Adjust `x`, `y`, `width`, `height` for each item.

# Tips
- Call `update()` after changing settings or data.
- Keep data lists small (e.g., <50 items) to avoid memory issues.
- Use DEBUG=True in `pichart.py` for troubleshooting.

# Troubleshooting
- Blank Display: Check display initialization and firmware compatibility.
- Errors: Enable DEBUG and check the console for messages.
