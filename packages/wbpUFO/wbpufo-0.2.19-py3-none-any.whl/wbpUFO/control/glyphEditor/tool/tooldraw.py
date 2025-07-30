"""
tooldraw
===============================================================================

Implementation of the draw tool for the glyph editor
"""
import logging

from wbDefcon import Contour, Point

from ..cursor import cursors
from .base import IDLE, WORKING, GlyphTool

log = logging.getLogger(__name__)


class ToolDraw(GlyphTool):
    """
    Tool to draw contours
    """

    cursor = cursors["DrawStart"]

    def __init__(self, parent):
        super().__init__(parent)
        self.currentContour = None
        self.startPoint = None

    def reset(self):
        print("ToolDraw.reset")
        super().reset()
        self.currentContour = None
        self.startPoint = None

    def setCursor(self):
        # if isinstance(self.subject, Point):
        if self.subject is None:
            if self.startPoint is None:
                self.canvas.SetCursor(cursors["DrawStart"])
            else:
                self.canvas.SetCursor(cursors["Draw"])

    # -------------------------------------------------------------------------
    # Event handler methods
    # -------------------------------------------------------------------------

    def on_LEFT_DOWN(self, event):
        super().on_LEFT_DOWN(event)
        glyph = self.glyph
        if glyph is not None:
            stack = self.activeStack
            if not stack["OnCurvePoints"].locked:
                glyph.undoManager.saveState()
                if self.currentContour is None:
                    self.currentContour = Contour()
                    glyph.appendContour(self.currentContour)
                x1 = self.canvas.screenToCanvasX(self.x)
                y1 = self.canvas.screenToCanvasY(self.y)
                newPoint = Point((x1, y1), "line")
                if self.startPoint is None:
                    newPoint.segmentType = "move"
                    self.startPoint = newPoint
                self.currentContour.appendPoint(newPoint)
                self.state = WORKING
        event.Skip()

    def on_LEFT_UP(self, event):
        if self.canvas.HasCapture():
            self.canvas.ReleaseMouse()
        # self.reset()
        glyph = self.glyph
        if glyph is not None:
            try:
                glyph.enableNotifications()
            except KeyError:
                pass
        self.canvas.Refresh()
        event.Skip()

    def on_MOTION(self, event):
        super().on_MOTION(event)
        glyph = self.glyph
        if glyph is not None:
            canvas_x = self.canvas.screenToCanvasX(self.x)
            canvas_y = self.canvas.screenToCanvasY(self.y)
            if event.Dragging() and self.state == WORKING:
                dx = self.canvas.screenToCanvasXrel(self.x - self.xPrev)
                dy = self.canvas.screenToCanvasYrel(self.y - self.yPrev)
            else:
                if self.state == IDLE:
                    self.hitTest()
                    self.setCursor()
        event.Skip()
