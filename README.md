# PiChart - Tiny Dashboard Charts for MicroPython

PiChart is a lightweight library for creating charts, cards, and image tiles on MicroPython displays, optimized for devices like the Raspberry Pi Pico with Pimoroni displays. Plot data as bars, lines, or points, display text cards, or show JPEG images in a customizable grid layout.

## Features
- Bar, line, and point chart types
- Text cards for simple info displays
- JPEG image tiles with borders
- Grid-based container for layout management
- Customizable colors, sizes, and display options

## Requirements
- MicroPython firmware (e.g., Pimoroni’s build with `jpegdec`)
- A compatible display (e.g., Pico Display Pack)
- Hardware: Raspberry Pi Pico or similar MicroPython device

## Installation
1. Copy `pichart.py` to your MicroPython device using a tool like Thonny or rshell.
2. Ensure your MicroPython firmware includes `jpegdec` (included in Pimoroni’s builds).

## Quick Start
```python
from pichart import Chart, Container
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY

# Set up display
display = PicoGraphics(display=DISPLAY_PICO_DISPLAY)

# Create a chart
chart = Chart(display, title="Temp", values=[20, 25, 22, 28])
chart.x = 10
chart.y = 10
chart.width = 220
chart.height = 120
chart.data_colour = {'red': 255, 'green': 0, 'blue': 0}  # Red bars

# Add to container and draw
container = Container(display)
container.add_chart(chart)
container.update()
