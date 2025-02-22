# PiChart
# Tiny dashboard Charts for MicroPython
# Kevin McAleer
# June 2022, Improved February 2025

VERSION = "2.2.0"

import jpegdec

# Module-level constants
DEFAULT_COLORS = {
    'BACKGROUND': {'red': 0, 'green': 0, 'blue': 0},
    'BORDER': {'red': 0, 'green': 0, 'blue': 0},
    'GRID': {'red': 0, 'green': 0, 'blue': 0},
    'TITLE': {'red': 0, 'green': 0, 'blue': 0},
    'DATA': {'red': 0, 'green': 0, 'blue': 0},
}
DEFAULT_SIZES = {
    'DATA_POINT_RADIUS': 2,
    'DATA_POINT_WIDTH': 10,
    'BORDER_WIDTH': 2,
    'TEXT_HEIGHT': 16,
    'GRID_SPACING': 10,
    'BAR_GAP': 3,
}
DEBUG = False  # Toggle for debug output

def log_debug(message: str) -> None:
    """Print debug messages if DEBUG is True.

    Args:
        message: The debug message to print.
    """
    if DEBUG:
        print(f"DEBUG: {message}")

class Chart:
    """A chart for plotting data on a MicroPython display.

    Use this to visualize data as bars, lines, or points. Set position, size, and colors
    after creation if needed.

    Attributes:
        x, y: Position on the display (default 0, 0).
        width, height: Size of the chart (default 100, 100).
        show_bars: Show data as bars (default True).
        show_lines: Connect data points with lines (default False).
        show_datapoints: Show data points as circles (default False).
        scale_to_fit: Scale data to fit chart width (default False).
    """
    SHOW_AXES_DEFAULT = False
    def __init__(self, display, title: str = "", x_label: str = None, y_label: str = None, 
                 values: list = None):
        """Create a new chart.

        Args:
            display: The display object (e.g., PicoGraphics).
            title: Chart title (default empty string).
            x_label: X-axis label (optional).
            y_label: Y-axis label (optional).
            values: List of numeric data to plot (default empty list).

        Raises:
            ValueError: If display is None or values contain non-numeric data.
        """
        if not display:
            raise ValueError("Display object is required")
        
        self._display = display
        self._pen_cache = {}  # Cache for pens to reduce memory usage
        self.title = title
        self._x_label = x_label
        self._y_label = y_label
        self.values = values or []
        self._min_val = None
        self._max_val = None
        self._y_scale = 1
        self._x_scale = 1  # New attribute for horizontal scaling
        
        # Positioning and size
        self.x = 0
        self.y = 0
        self.width = 100
        self.height = 100
        self.border_width = DEFAULT_SIZES['BORDER_WIDTH']
        self.text_height = DEFAULT_SIZES['TEXT_HEIGHT']
        
        # Display options
        self.show_datapoints = False
        self.show_lines = False
        self.show_bars = True
        self._show_labels = False
        self.grid = True
        self.grid_spacing = DEFAULT_SIZES['GRID_SPACING']
        self.bar_gap = DEFAULT_SIZES['BAR_GAP']
        self.data_point_radius = DEFAULT_SIZES['DATA_POINT_RADIUS']
        self.data_point_width = DEFAULT_SIZES['DATA_POINT_WIDTH']
        
        # Colors
        self.background_colour = DEFAULT_COLORS['BACKGROUND'].copy()
        self.border_colour = DEFAULT_COLORS['BORDER'].copy()
        self.grid_colour = DEFAULT_COLORS['GRID'].copy()
        self.title_colour = DEFAULT_COLORS['TITLE'].copy()
        self.data_colour = DEFAULT_COLORS['DATA'].copy()
        
        # New scaling option
        self._scale_to_fit = False  # Default to False (manual spacing)
        
        # Validate and scale data if provided
        if self.values:
            self._validate_data(self.values)
            self._scale_data()
        self.show_x_axis = self.SHOW_AXES_DEFAULT
        self.show_y_axis = self.SHOW_AXES_DEFAULT
        self.axis_label_colour = DEFAULT_COLORS['TITLE'].copy()

    def _draw_x_axis(self):
        axis_pen = self._get_pen(self.axis_label_colour)
        self._display.set_pen(axis_pen)
        y_pos = self.y + self.height - self.border_width - 10
        # print(f"self.y: {self.y}, ypos: {y_pos}")
        # self._display.line(self.x + self.border_width, y_pos, self.x + self.width - self.border_width, y_pos)
        if self.values:
            self._display.text(str(self.values[0]), self.x + self.border_width, y_pos + 2, scale=1)
            self._display.text(str(self.values[len(self.values)//2]), self.x + (self.width // 2), y_pos + 2, scale=1)
            self._display.text(str(self.values[-1]), self.x + self.width - self.border_width - 10, y_pos + 2, scale=1)
    
    def _draw_y_axis(self):
        axis_pen = self._get_pen(self.axis_label_colour)
        self._display.set_pen(axis_pen)
        x_pos = self.x + self.border_width + 10
        # print(f"self.x: {self.x}, xpos: {x_pos}")
        # self._display.line(x_pos, self.y + self.border_width, x_pos, self.y + self.height - self.border_width)
        if self.values:
            self._display.text(str(self._min_val), x_pos - 10, self.y + self.height - self.border_width - 10, scale=1)
            self._display.text(str((self._min_val + self._max_val) // 2), x_pos - 10, self.y + (self.height // 2) - 5, scale=1)
            self._display.text(str(self._max_val), x_pos - 10, self.y + self.border_width, scale=1)

    def set_values(self, new_values: list) -> None:
        """Update the chart data and recalculate scaling.

        Args:
            new_values: New list of numeric data to plot.
        """
        self.values = new_values or []
        if self.values:
            self._validate_data(self.values)
            self._scale_data()

    @property
    def show_labels(self) -> bool:
        """Whether to show data value labels above points or bars."""
        return self._show_labels

    @show_labels.setter
    def show_labels(self, value: bool) -> None:
        """Set whether to show data value labels.

        Args:
            value: True to show labels, False to hide them.
        """
        self._show_labels = bool(value)
        self.data_point_radius = DEFAULT_SIZES['DATA_POINT_RADIUS'] * (4 if value else 1)

    @property
    def scale_to_fit(self) -> bool:
        """Whether to scale data to fit the chart width.

        Returns:
            True if scaling to fit, False for fixed spacing.
        """
        return self._scale_to_fit

    @scale_to_fit.setter
    def scale_to_fit(self, value: bool) -> None:
        """Set whether to scale data to fit the chart width.

        Args:
            value: True to scale width to fit all data, False to use fixed spacing.
        """
        self._scale_to_fit = bool(value)
        if self.values:
            self._scale_data()  # Recalculate scaling if data exists

    def _get_pen(self, color: dict) -> int:
        """Get a pen (color) from the cache or create a new one.

        Args:
            color: Dict with 'red', 'green', 'blue' keys (0-255).

        Returns:
            Pen ID for the display.
        """
        color_key = (color['red'], color['green'], color['blue'])
        if color_key not in self._pen_cache:
            self._pen_cache[color_key] = self._display.create_pen(
                color['red'], color['green'], color['blue']
            )
        return self._pen_cache[color_key]

    def _validate_data(self, values: list) -> None:
        """Check that data is valid.

        Args:
            values: List of data to validate.

        Raises:
            ValueError: If values are empty or contain non-numeric items.
        """
        if not values:
            raise ValueError("Data values cannot be empty")
        if not all(isinstance(v, (int, float)) for v in values):
            raise ValueError("All data values must be numeric")
        if any(v < -1000 or v > 1000 for v in values):
            log_debug("Data values outside typical range (-1000 to 1000)")

    def _scale_data(self) -> None:
        """Adjust data scale to fit both chart height and width if scale_to_fit is True."""
        self._min_val = min(self.values) if self.values else 0
        self._max_val = max(self.values) if self.values else 1
        if self._max_val == self._min_val:
            self._max_val += 1  # Avoid division by zero
            self._min_val -= 1

        # Vertical scaling (height)
        plot_height = (self.height - self.text_height) - (self.border_width * 2)
        self._y_scale = plot_height / (self._max_val - self._min_val)

        # Horizontal scaling (width) if scale_to_fit is True
        if self._scale_to_fit and self.values:
            num_values = len(self.values)
            self.bar_gap = 0
            plot_width = self.width - (self.border_width * 2) - (self.bar_gap * (num_values - 1))
#             print(f"Plot width: {plot_width}, number of values: {num_values}")
            if num_values > 1:
                self._x_scale = plot_width / (num_values - 1)  # Space between points
            else:
                self._x_scale = plot_width  # Single point
        else:
            self._x_scale = self.data_point_width + self.bar_gap  # Fixed spacing

    @staticmethod
    def map_value(x: float, in_min: float, in_max: float, out_min: float, out_max: float) -> float:
        """Map a value from one range to another.

        Args:
            x: Value to map.
            in_min: Minimum of input range.
            in_max: Maximum of input range.
            out_min: Minimum of output range.
            out_max: Maximum of output range.

        Returns:
            Mapped value as a float.
        """
        if in_max == in_min:
            return out_min
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def draw_border(self) -> None:
        """Draw a border around the chart."""
        border_pen = self._get_pen(self.border_colour)
        self._display.set_pen(border_pen)
        x, y = self.x, self.y
        w, h = self.width, self.height
        x1, y1 = x + w, y + h
        self._display.set_clip(x, y, x1, y1)

        for i in range(self.border_width):
            self._display.line(x + i, y + i, x + i, y1 - i)  # Left
            self._display.line(x + i, y + i, x1 - i, y + i)  # Top
            self._display.line(x + i, y1 - i - 1, x1 - i, y1 - i - 1)  # Bottom
            self._display.line(x1 - i - 1, y + i, x1 - i - 1, y1 - i)  # Right

        self._display.remove_clip()

    def draw_grid(self) -> None:
        """Draw a grid inside the chart."""
        grid_pen = self._get_pen(self.grid_colour)
        self._display.set_pen(grid_pen)
        x, y = self.x, self.y
        w, h = self.width, self.height

        cols = w // self.grid_spacing
        rows = h // self.grid_spacing

        for i in range(cols):
            self._display.line(x + self.grid_spacing * i, y, x + self.grid_spacing * i, y + h)
        for j in range(rows):
            self._display.line(x, y + self.grid_spacing * j, x + w, y + self.grid_spacing * j)

    def update(self) -> None:
        """Draw the chart on the display.

        Call this to refresh the chart after changing data or settings.
        """
        try:
            if not self.values:
                log_debug("No data to display")
                return

            # Clear the chart area
            background_pen = self._get_pen(self.background_colour)
            self._display.set_pen(background_pen)
            self._display.set_clip(self.x, self.y, self.x + self.width, self.y + self.height)
            self._display.rectangle(self.x, self.y, self.width, self.height)
            self._display.remove_clip()

            # Draw grid if enabled
            if self.grid:
                self.draw_grid()

            # Draw title
            title_pen = self._get_pen(self.title_colour)
            self._display.set_pen(title_pen)
            title_x_pos = self.x + (self.width - self._display.measure_text(self.title, 1)) // 2 - self.border_width * 2
            
            # self._display.text(self.title, self.x + self.border_width + 1, self.y + self.border_width + 1, self.width)
            self._display.text(self.title, title_x_pos, 
                             self.y + self.border_width + 1, self.width)

            # Prepare data drawing
            data_pen = self._get_pen(self.data_colour)
            data_pen_dim = self._get_pen({
                'red': self.data_colour['red'] // 4,
                'green': self.data_colour['green'] // 4,
                'blue': self.data_colour['blue'] // 4
            })
            plot_area_height = (self.height - self.text_height) - (self.border_width * 2)
            plot_area_width = self.width - (self.border_width * 2)
            x_pos = self.x + self.border_width + 2
            y_base = self.y + self.height - self.border_width - 2
            prev_x, prev_y = x_pos, y_base

            self._display.set_clip(self.x + self.border_width, self.y + self.text_height,
                                 self.x + self.width, self.y + self.height - self.border_width)

            num_values = len(self.values)
            if num_values == 0:
                return

            # Calculate bar/point width based on scaling
            if self._scale_to_fit:
                if num_values > 1:
                    point_spacing = plot_area_width // (num_values - 1)  # Evenly space points
                else:
                    point_spacing = plot_area_width  # Single point takes full width
                bar_width = point_spacing - self.bar_gap if self.show_bars else self.data_point_width
#                 print(f'point spacing {point_spacing} bar width {bar_width}')
                if bar_width < 1:
                    bar_width = 1  # Minimum width
            else:
                bar_width = self.data_point_width
                point_spacing = self._x_scale  # Fixed spacing

            for idx, value in enumerate(self.values):
                scaled_height = int(self.map_value(value, self._min_val, self._max_val, 0, plot_area_height))
                y_pos = y_base - scaled_height
                log_debug(f"Value: {value}, Scaled height: {scaled_height}, X: {x_pos}, Y: {y_pos}")

                if self.show_bars:
                    self._display.set_pen(data_pen)
                    self._display.rectangle(x_pos, y_pos, bar_width, scaled_height)

                if self.show_datapoints:
                    center_x = x_pos + bar_width // 2
                    self._display.set_pen(data_pen_dim)
                    self._display.circle(center_x, y_pos, self.data_point_radius * 2)
                    self._display.set_pen(data_pen)
                    self._display.circle(center_x, y_pos, self.data_point_radius)

                if self.show_lines and idx > 0:
                    self._display.set_pen(data_pen)
                    self._display.line(prev_x + bar_width // 2, prev_y, x_pos + bar_width // 2, y_pos)

                if self._show_labels:
                    self._display.set_pen(data_pen)
                    label_x = x_pos if self._scale_to_fit else x_pos - (self.data_point_width // 2)
                    self._display.text(str(value), label_x, y_pos - 10, self.width - x_pos)

                prev_x, prev_y = x_pos, y_pos
                x_pos += point_spacing

            if self.show_x_axis:
                self._draw_x_axis()
            if self.show_y_axis:
                self._draw_y_axis()

            self._display.remove_clip()
            self.draw_border()
            self._display.update()

        except Exception as e:
            log_debug(f"Chart update error: {e}")

class Card(Chart):
    """A simple text card for displaying information.

    Inherits from Chart but only shows text, no data plotting.

    Attributes:
        x, y: Position on the display.
        width, height: Size of the card.
    """

    def __init__(self, display, x: int = 0, y: int = 0, width: int = 100, height: int = 100, 
                 title: str = ""):
        """Create a new card.

        Args:
            display: The display object (e.g., PicoGraphics).
            x: X position (default 0).
            y: Y position (default 0).
            width: Width in pixels (default 100).
            height: Height in pixels (default 100).
            title: Text to display (default empty string).
        """
        super().__init__(display, title=title)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self._text_scale = 1
        self.grid = False  # Cards typically don’t need grids

    def _scale_text(self) -> int:
        """Find the best text scale to fit the title.

        Returns:
            Scale factor (1 or higher).
        """
        self._display.set_font("bitmap8")
        max_width = self.width - (self.border_width * 2)
        max_height = self.height - (self.border_width * 2)
        scale = 2  # Start with a reasonable scale

        while scale > 0:
            text_width = self._display.measure_text(self.title, scale)
            text_height = 8 * scale
            if text_width <= max_width and text_height <= max_height:
                print(f"Text width: {text_width}, height: {text_height}, scale: {scale}")
                return scale
            scale -= 1
        return 1

    def update(self) -> None:
        """Draw the card on the display with centered, potentially wrapped text."""
        try:
            background_pen = self._get_pen(self.background_colour)
            title_pen = self._get_pen(self.title_colour)
            self._display.set_pen(background_pen)
            self._display.rectangle(self.x, self.y, self.width, self.height)

            if self.grid:
                self.draw_grid()

            self.draw_border()
            self._text_scale = self._scale_text()
            self._display.set_font("bitmap8")

            # Calculate available width for text (excluding borders)
            max_text_width = self.width - (self.border_width * 2)
            text_length = self._display.measure_text(self.title, self._text_scale)
            
            # Center the text horizontally
            title_x = self.x + (self.width - text_length) // 2
            # Center the text vertically (assuming 8 pixels per line height)
            title_y = self.y + (self.height - (self._text_scale * 8)) // 2

            self._display.set_pen(title_pen)
            # Draw text with wrapping if it exceeds max_text_width
            if text_length > max_text_width:
                # Use max_text_width as the wordwrap parameter
                self._display.text(self.title, self.x + self.border_width, title_y, max_text_width, self._text_scale)
                print(f"Text wrapped: width={text_length}, max_width={max_text_width}, scale={self._text_scale}")
            else:
                # Draw centered text without wrapping
                self._display.text(self.title, title_x, title_y, max_text_width, self._text_scale)
                print(f"Text centered: width={text_length}, x={title_x}, y={title_y}, scale={self._text_scale}")

            self._display.update()

        except Exception as e:
            log_debug(f"Card update error: {e}")

class ImageTile:
    """A tile for showing an image with a border.

    Uses JPEG decoding via the jpegdec library.

    Attributes:
        x, y: Position on the display.
        width, height: Size of the tile.
    """

    def __init__(self, display, filename: str = None, x: int = 0, y: int = 0, 
                 width: int = 100, height: int = 100):
        """Create a new image tile.

        Args:
            display: The display object (e.g., PicoGraphics).
            filename: Path to the JPEG file (default None).
            x: X position (default 0).
            y: Y position (default 0).
            width: Width in pixels (default 100).
            height: Height in pixels (default 100).

        Raises:
            ValueError: If display is None.
        """
        if not display:
            raise ValueError("Display object is required")
        self._display = display
        self.filename = filename
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.border_colour = DEFAULT_COLORS['BORDER'].copy()
        self.border_width = DEFAULT_SIZES['BORDER_WIDTH']

    def draw_border(self) -> None:
        """Draw a border around the image."""
        border_pen = self._display.create_pen(
            self.border_colour['red'], self.border_colour['green'], self.border_colour['blue']
        )
        self._display.set_pen(border_pen)
        x, y = self.x, self.y
        w, h = self.width, self.height
        x1, y1 = x + w, y + h
        self._display.set_clip(x, y, x1, y1)

        for i in range(self.border_width):
            self._display.line(x + i, y + i, x + i, y1 - i)  # Left
            self._display.line(x + i, y + i, x1 - i, y + i)  # Top
            self._display.line(x + i, y1 - i - 1, x1 - i, y1 - i - 1)  # Bottom
            self._display.line(x1 - i - 1, y + i, x1 - i - 1, y1 - i)  # Right

        self._display.remove_clip()

    def update(self) -> None:
        """Draw the image tile on the display."""
        try:
            if not self.filename:
                log_debug("No image file specified")
                return
            j = jpegdec.JPEG(self._display)
            j.open_file(self.filename)
            self._display.set_clip(self.x, self.y, self.x + self.width, self.y + self.height)
            j.decode(self.x, self.y, jpegdec.JPEG_SCALE_HALF)
            self._display.remove_clip()
            self.draw_border()
            self._display.update()
        except Exception as e:
            log_debug(f"ImageTile update error: {e}")

class Container:
    """A container to hold and arrange multiple charts or cards.

    Displays items in a grid layout based on the number of columns set.

    Attributes:
        cols: Number of columns in the grid (default 1).
    """

    def __init__(self, display, width: int = None, height: int = None):
        """Create a new container.

        Args:
            display: The display object (e.g., PicoGraphics).
            width: Container width (defaults to display width).
            height: Container height (defaults to display height).

        Raises:
            ValueError: If display is None.
        """
        if not display:
            raise ValueError("Display object is required")
        self._display = display
        self.charts = []
        self.cols = 1
        self.width = width or display.get_bounds()[0]
        self.height = height or display.get_bounds()[1]
        self._background_colour = DEFAULT_COLORS['BACKGROUND'].copy()
        self._title_colour = DEFAULT_COLORS['TITLE'].copy()
        self._data_colour = DEFAULT_COLORS['DATA'].copy()
        self._grid_colour = DEFAULT_COLORS['GRID'].copy()
        self._border_colour = DEFAULT_COLORS['BORDER'].copy()
        self._border_width = DEFAULT_SIZES['BORDER_WIDTH']

    def add_chart(self, item) -> None:
        """Add a chart or card to the container.

        Args:
            item: Chart, Card, or ImageTile instance to add.
        """
        if item not in self.charts:
            self.charts.append(item)
            item.background_colour = self._background_colour
            item.title_colour = self._title_colour
            item.data_colour = self._data_colour
            item.grid_colour = self._grid_colour
            item.border_colour = self._border_colour
            item.border_width = self._border_width

    def update(self) -> None:
        """Draw all items in the container.

        Arranges items in a grid based on cols and total items.
        """
        try:
            if not self.charts:
                log_debug("No charts in container")
                return

            rows = (len(self.charts) + self.cols - 1) // self.cols  # Ceiling division
            item_width = self.width // self.cols
            item_height = self.height // rows

            for idx, item in enumerate(self.charts):
                col = idx % self.cols
                row = idx // self.cols
                item.x = col * item_width
                item.y = row * item_height
                item.width = item_width
                item.height = item_height
                item.update()

        except Exception as e:
            log_debug(f"Container update error: {e}")

    @property
    def background_colour(self) -> dict:
        """Get the background color for all items."""
        return self._background_colour

    @background_colour.setter
    def background_colour(self, value: dict) -> None:
        """Set the background color for all items.

        Args:
            value: Dict with 'red', 'green', 'blue' keys (0-255).
        """
        self._background_colour = value
        for item in self.charts:
            item.background_colour = value

    @property
    def grid_colour(self) -> dict:
        """Get the grid color for all items."""
        return self._grid_colour

    @grid_colour.setter
    def grid_colour(self, value: dict) -> None:
        """Set the grid color for all items.

        Args:
            value: Dict with 'red', 'green', 'blue' keys (0-255).
        """
        self._grid_colour = value
        for item in self.charts:
            item.grid_colour = value

    @property
    def data_colour(self) -> dict:
        """Get the data color for all items."""
        return self._data_colour

    @data_colour.setter
    def data_colour(self, value: dict) -> None:
        """Set the data color for all items.

        Args:
            value: Dict with 'red', 'green', 'blue' keys (0-255).
        """
        self._data_colour = value
        for item in self.charts:
            item.data_colour = value

    @property
    def title_colour(self) -> dict:
        """Get the title color for all items."""
        return self._title_colour

    @title_colour.setter
    def title_colour(self, value: dict) -> None:
        """Set the title color for all items.

        Args:
            value: Dict with 'red', 'green', 'blue' keys (0-255).
        """
        self._title_colour = value
        for item in self.charts:
            item.title_colour = value

    @property
    def border_colour(self) -> dict:
        """Get the border color for all items."""
        return self._border_colour

    @border_colour.setter
    def border_colour(self, value: dict) -> None:
        """Set the border color for all items.

        Args:
            value: Dict with 'red', 'green', 'blue' keys (0-255).
        """
        self._border_colour = value
        for item in self.charts:
            item.border_colour = value

    @property
    def border_width(self) -> int:
        """Get the border width for all items."""
        return self._border_width

    @border_width.setter
    def border_width(self, value: int) -> None:
        """Set the border width for all items.

        Args:
            value: Width in pixels.
        """
        self._border_width = value
        for item in self.charts:
            item.border_width = value