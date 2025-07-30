"""
toolzoom
===============================================================================
"""

import wx

from wbBase.tools import get_wxBrush, get_wxPen
from ..cursor import cursors

from .base import RUBBERBANDING, GlyphTool


class ToolZoom(GlyphTool):
    cursor = cursors["ZoomIn"]
    brush = get_wxBrush(wx.Colour(200, 200, 200, 64))
    pen = get_wxPen(wx.Colour(128, 128, 128, 128))

    def on_LEFT_DOWN(self, event):
        GlyphTool.on_LEFT_DOWN(self, event)
        self.state = RUBBERBANDING
        event.Skip()

    def on_LEFT_UP(self, event):
        if all([i is not None for i in (self.xClick, self.yClick, self.x, self.y)]):
            x = min(self.xClick, self.x)
            y = min(self.yClick, self.y)
            w = abs(self.xClick - self.x)
            h = abs(self.yClick - self.y)
            if w or h:
                canvas_x = self.canvas.screenToCanvasX(x + w / 2)
                canvas_y = self.canvas.screenToCanvasY(y + h / 2)
                rubberbandRatio = float(w) / float(h)
                screenRatio = float(self.canvas.ClientSize.width) / float(
                    self.canvas.ClientSize.height
                )
                if rubberbandRatio > screenRatio:
                    factor = float(self.canvas.ClientSize.width) / float(w)
                else:
                    factor = float(self.canvas.ClientSize.height) / float(h)
                self.canvas.zoom *= factor
                self.canvas.centerCanvasOnScreen(canvas_x, canvas_y)
        GlyphTool.on_LEFT_UP(self, event)

    def on_MOTION(self, event):
        GlyphTool.on_MOTION(self, event)
        if event.Dragging():
            if self.state == RUBBERBANDING:
                x = min(self.xClick, self.xPrev)
                y = min(self.yClick, self.yPrev)
                w = abs(self.xClick - self.xPrev)
                h = abs(self.yClick - self.yPrev)
                rubberband = wx.Rect(x, y, w, h)
                x = min(self.xClick, self.x)
                y = min(self.yClick, self.y)
                w = abs(self.xClick - self.x)
                h = abs(self.yClick - self.y)
                rubberband.Union(wx.Rect(x, y, w, h))
                rubberband.Inflate(1, 1)
                self.canvas.RefreshRect(rubberband)
        event.Skip()

    def draw(self, gc):
        if self.state == RUBBERBANDING and not None in (
            self.xClick,
            self.yClick,
            self.x,
            self.y,
        ):
            gc.SetPen(self.pen)
            gc.SetBrush(self.brush)
            gc.DrawRectangle(
                min(self.xClick, self.x),
                min(self.yClick, self.y),
                abs(self.xClick - self.x),
                abs(self.yClick - self.y),
            )
