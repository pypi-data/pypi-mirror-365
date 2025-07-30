"""
addrectangle
===============================================================================
"""

from wbDefcon import Contour, Point

from ..cursor import cursors
from .base import RUBBERBANDING, AddShapeTool


class AddRectangle(AddShapeTool):
    """Add rectangular contour to the current glyph"""

    cursor = cursors["DrawRectangle"]

    def on_LEFT_UP(self, event):
        if self.glyph is not None:
            x, y, w, h = self.dimension
            if w and h:
                left = self.canvas.screenToCanvasX(x)
                top = self.canvas.screenToCanvasY(y)
                right = self.canvas.screenToCanvasX(x + w)
                bottom = self.canvas.screenToCanvasY(y + h)
                rectangle = Contour()
                rectangle.appendPoint(Point((left, top), "line"))
                rectangle.appendPoint(Point((left, bottom), "line"))
                rectangle.appendPoint(Point((right, bottom), "line"))
                rectangle.appendPoint(Point((right, top), "line"))
                rectangle.selected = True
                rectangle.round()
                self.unselectAll()
                self.glyph.appendContour(rectangle)
        super().on_LEFT_UP(event)

    def draw(self, gc):
        if self.state == RUBBERBANDING and not None in (
            self.xClick,
            self.yClick,
            self.x,
            self.y,
        ):
            gc.SetPen(self.pen)
            gc.SetBrush(self.brush)
            gc.DrawRectangle(*self.dimension)
