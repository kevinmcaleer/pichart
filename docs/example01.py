from pichart import Chart
from presto import Presto

presto = Presto(ambient_light=True)
display = presto.display
WIDTH, HEIGHT = display.get_bounds()

chart = Chart(display, title="Temp", values=[20, 22, 25, 23, 34])
chart.width = 240
chart.height = 135
chart.data_colour = {'red': 255, 'green': 0, 'blue': 0}
chart.update()
presto.update()