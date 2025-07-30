"""
addellipse
===============================================================================
"""

from wbDefcon import Contour, Point

from ..cursor import cursors
from .base import IDLE, RUBBERBANDING, AddShapeTool


class AddEllipse(AddShapeTool):
    cursor = cursors["DrawEllipse"]

    def on_LEFT_UP(self, event):
        if self.glyph is not None:
            x, y, w, h = self.dimension
            if w and h:
                left = self.canvas.screenToCanvasX(x)
                top = self.canvas.screenToCanvasY(y)
                right = self.canvas.screenToCanvasX(x + w)
                bottom = self.canvas.screenToCanvasY(y + h)
                bcp_x = self.canvas.screenToCanvasXrel(w) * 0.276
                bcp_y = self.canvas.screenToCanvasYrel(h) * -0.276
                center_x = (left + right) / 2.0
                center_y = (bottom + top) / 2.0
                ellipse = Contour()
                # left to bottom
                ellipse.appendPoint(Point((left, center_y - bcp_y)))
                ellipse.appendPoint(Point((center_x - bcp_x, bottom)))
                ellipse.appendPoint(Point((center_x, bottom), "curve", True))
                # bottom to right
                ellipse.appendPoint(Point((center_x + bcp_x, bottom)))
                ellipse.appendPoint(Point((right, center_y - bcp_y)))
                ellipse.appendPoint(Point((right, center_y), "curve", True))
                # right to top
                ellipse.appendPoint(Point((right, center_y + bcp_y)))
                ellipse.appendPoint(Point((center_x + bcp_x, top)))
                ellipse.appendPoint(Point((center_x, top), "curve", True))
                # top to left
                ellipse.appendPoint(Point((center_x - bcp_x, top)))
                ellipse.appendPoint(Point((left, center_y + bcp_y)))
                ellipse.appendPoint(Point((left, center_y), "curve", True))
                ellipse.selected = True
                ellipse.round()
                self.unselectAll()
                self.glyph.appendContour(ellipse)
        AddShapeTool.on_LEFT_UP(self, event)

    def draw(self, gc):
        if self.state == RUBBERBANDING and not None in (
            self.xClick,
            self.yClick,
            self.x,
            self.y,
        ):
            gc.SetPen(self.pen)
            gc.SetBrush(self.brush)
            gc.DrawEllipse(*self.dimension)
