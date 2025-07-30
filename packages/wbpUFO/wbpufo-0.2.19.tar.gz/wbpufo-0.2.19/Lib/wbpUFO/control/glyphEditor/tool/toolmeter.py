"""
toolmeter
===============================================================================

Impementation of the Meter tool for the glyph editor
"""
import wx

from wbDefcon.pens.lineIntersectionPen import LineIntersectionPen
from wbBase.tools import get_wxBrush, get_wxFont, get_wxPen

from ..cursor import cursors

from .base import WORKING, GlyphTool


class ToolMeter(GlyphTool):
    """
    Tool to mesure distances between intersection points with a drawn line.
    """
    cursor = cursors["Meter"]
    pen = get_wxPen(wx.Colour(128, 128, 150, 220))
    brush = get_wxBrush(wx.Colour(128, 128, 150, 64))
    labelfont = get_wxFont(pointSize=7, faceName="Small Fonts")
    labelpen = wx.TRANSPARENT_PEN
    labelbrush = get_wxBrush(wx.Colour(230, 230, 240, 100))

    def __init__(self, parent):
        super().__init__(parent)
        self.lineIntersectionPen = LineIntersectionPen()
        self.meterStartPoint = None
        self.meterEndPoint = None

    def reset(self):
        super().reset()
        self.lineIntersectionPen.reset()
        self.meterStartPoint = None
        self.meterEndPoint = None

    @property
    def meterLine(self):
        if self.meterStartPoint and self.meterEndPoint:
            return (self.meterStartPoint, self.meterEndPoint)
        return None

    @property
    def intersections(self):
        glyph = self.glyph
        if glyph is None:
            return []
        line = self.meterLine
        if not line:
            return []
        pen = self.lineIntersectionPen
        if line != pen.line:
            pen.line = line
            glyph.draw(pen)
        return list(pen.intersections)

    # -------------------------------------------------------------------------
    # Event handler methods
    # -------------------------------------------------------------------------

    def on_LEFT_DOWN(self, event):
        super().on_LEFT_DOWN(event)
        glyph = self.glyph
        if glyph is not None:
            self.lineIntersectionPen.glyphSet = glyph.layer
            self.meterStartPoint = (
                round(self.canvas.screenToCanvasX(self.x)),
                round(self.canvas.screenToCanvasY(self.y)),
            )
            self.state = WORKING
        event.Skip()

    def on_MOTION(self, event):
        super().on_MOTION(event)
        if event.Dragging() and self.state == WORKING:
            x = self.x
            y = self.y
            if self.shiftDown:
                dx = abs(self.xClick - self.x)
                dy = abs(self.yClick - self.y)
                if dx > dy:
                    y = self.yClick
                else:
                    x = self.xClick
            self.meterEndPoint = (
                round(self.canvas.screenToCanvasX(x)),
                round(self.canvas.screenToCanvasY(y)),
            )
            self.canvas.Refresh()
        event.Skip()

    def draw(self, gc):
        if self.state == WORKING:
            gc.SetFont(self.labelfont, wx.BLACK)
            transformPoint = self.canvas.transform.transformPoint
            start = transformPoint(self.meterStartPoint)
            end = transformPoint(self.meterEndPoint)
            gc.SetPen(self.pen)
            gc.StrokeLine(start[0], start[1], end[0], end[1])
            d = 3
            s = 3
            points = list(self.intersections)
            points.append(self.meterStartPoint)
            points.append(self.meterEndPoint)
            points.sort()
            xPrev = None
            yPrev = None
            for i, intersection in enumerate(points):
                if intersection:
                    try:
                        x, y = transformPoint(intersection)
                        x = round(x)
                        y = round(y)
                    except ValueError:
                        continue
                    gc.SetPen(self.pen)
                    gc.SetBrush(self.brush)
                    gc.DrawEllipse(x - s, y - s, 2 * s, 2 * s)
                    text = "%.1f / %.1f" % (intersection[0], intersection[1])
                    w, h = gc.GetTextExtent(text)
                    w = int(round(w)) + 2 * s
                    h = int(round(h)) + 2 * s
                    gc.SetPen(self.labelpen)
                    gc.SetBrush(self.labelbrush)
                    gc.DrawRoundedRectangle(x + d, y + d, w, h, d)
                    gc.DrawText(text, x + d + s, y + d + s - 1)
                    if i > 0 and points[i - 1]:
                        try:
                            dist = self.distance(points[i - 1], intersection)
                        except ValueError:
                            dist = 0
                        if dist > 0.5:
                            text = "%.1f" % dist
                            w, h = gc.GetTextExtent(text)
                            w = int(round(w)) + 2 * s
                            h = int(round(h)) + 2 * s
                            xDist = int(round(xPrev + (x - xPrev) * 0.5))
                            yDist = int(round(yPrev + (y - yPrev) * 0.5))
                            gc.DrawRoundedRectangle(xDist - w - d, yDist - d - h, w, h, d)
                            gc.DrawText(text, xDist - w - d + s, yDist - d - h + s - 1)
                    xPrev = x
                    yPrev = y
