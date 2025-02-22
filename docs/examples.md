# PiChart Examples

## Simple Bar Chart
```python
from pichart import Chart
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY

display = PicoGraphics(display=DISPLAY_PICO_DISPLAY)
chart = Chart(display, title="Temp", values=[20, 22, 25, 23])
chart.width = 240
chart.height = 135
chart.data_colour = {'red': 255, 'green': 0, 'blue': 0}
chart.update()
```

## Dashboard with Chart and Card
```python
from pichart import Chart, Card, Container
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY

display = PicoGraphics(display=DISPLAY_PICO_DISPLAY)
chart = Chart(display, title="Humidity", values=[60, 65, 62, 70])
chart.x = 0
chart.y = 0
chart.width = 240
chart.height = 100

card = Card(display, x=0, y=100, width=240, height=35, title="Dry")

container = Container(display)
container.add_chart(chart)
container.add_chart(card)
container.update()
```

## Image Tile

```python
from pichart import ImageTile
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY

display = PicoGraphics(display=DISPLAY_PICO_DISPLAY)
tile = ImageTile(display, filename="image.jpg", width=240, height=135)
tile.update()
```
