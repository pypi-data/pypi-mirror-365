"""
toolknife
===============================================================================
"""
import logging
import math

import wx
from booleanOperations import BooleanOperationManager as Boolean
from wbBase.tools import get_wxBrush, get_wxPen
from wbDefcon import Contour, Point
from wbDefcon.pens.lineIntersectionPen import LineIntersectionPen

from ..cursor import cursors
from .base import WORKING, GlyphTool

log = logging.getLogger(__name__)


class LineContourIntersectionPen(LineIntersectionPen):
    """
    Works like LineIntersectionPen but ignores components.
    """

    def addComponent(self, glyphName, transformation):
        pass


class ToolKnife(GlyphTool):
    cursor = cursors["Knife"]
    pen = get_wxPen(wx.Colour(128, 128, 150, 128))
    brush = get_wxBrush(wx.Colour(128, 128, 150, 64))
    cutpen = get_wxPen(wx.Colour(255, 64, 64, 255))

    def __init__(self, parent):
        super().__init__(parent)
        self.intersections = []
        self.lineIntersectionPen = LineContourIntersectionPen()
        self.knifeStartPoint = None
        self.knifeEndPoint = None
        self.cutStartPoint = None
        self.cutEndPoint = None

    def reset(self):
        super().reset()
        self.knifeStartPoint = None
        self.knifeEndPoint = None
        self.cutStartPoint = None
        self.cutEndPoint = None

    @property
    def knifeLine(self):
        if self.knifeStartPoint and self.knifeEndPoint:
            return (self.knifeStartPoint, self.knifeEndPoint)
        return None

    @staticmethod
    def midpoint(p1, p2):
        return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)

    # -------------------------------------------------------------------------
    # Event handler methods
    # -------------------------------------------------------------------------

    def on_LEFT_DOWN(self, event):
        super().on_LEFT_DOWN(event)
        glyph = self.glyph
        if glyph is not None:
            self.lineIntersectionPen.glyphSet = glyph.layer
            self.knifeStartPoint = (
                round(self.canvas.screenToCanvasX(self.x)),
                round(self.canvas.screenToCanvasY(self.y)),
            )
            self.state = WORKING
        event.Skip()

    def on_LEFT_UP(self, event):
        glyph = self.glyph
        if glyph is not None:
            if self.intersections and self.cutStartPoint and self.cutEndPoint:
                p0 = self.cutStartPoint
                p1 = self.cutEndPoint
                distance = self.distance(p0, p1)
                cutRect = Contour()
                d = 0.01
                cutRect.appendPoint(Point((p0[0], p0[1] - d), "line"))
                cutRect.appendPoint(
                    Point(
                        (p0[0] + distance, p0[1] - d),
                        "line",
                    )
                )
                cutRect.appendPoint(
                    Point(
                        (p0[0] + distance, p0[1] + d),
                        "line",
                    )
                )
                cutRect.appendPoint(Point((p0[0], p0[1] + d), "line"))
                dx = p1[0] - p0[0]
                dy = p1[1] - p0[1]
                angle = math.degrees(math.atan2(dy, dx))
                cutRect.rotateBy(angle, p0)
                contours = list(glyph)
                glyph.disableNotifications()
                glyph.undoManager.saveState()
                glyph.clearContours()
                Boolean.difference(
                    contours,
                    [cutRect],
                    glyph.getPointPen(),
                )
                glyph.enableNotifications()
                glyph.postNotification("Glyph.ContoursChanged")
        super().on_LEFT_UP(event)

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
            self.knifeEndPoint = (
                round(self.canvas.screenToCanvasX(x)),
                round(self.canvas.screenToCanvasY(y)),
            )
            points = []
            glyph = self.glyph
            if glyph is not None:
                line = self.knifeLine
                if line:
                    pen = self.lineIntersectionPen
                    if line != pen.line:
                        pen.line = line
                        glyph.draw(pen)
                points = list(pen.intersections) + [
                    self.knifeStartPoint,
                    self.knifeEndPoint,
                ]
                points.sort()
                if glyph.pointInside(points[0]):
                    try:
                        self.cutStartPoint = self.midpoint(points[1], points[2])
                    except IndexError:
                        self.cutStartPoint = None
                    points = points[2:]
                else:
                    self.cutStartPoint = points[0]
                    points = points[1:]
                if points:
                    if glyph.pointInside(points[-1]):
                        try:
                            self.cutEndPoint = self.midpoint(points[-3], points[-2])
                        except IndexError:
                            self.cutEndPoint = None
                        points = points[:-2]
                    else:
                        self.cutEndPoint = points[-1]
                        points = points[:-1]
                else:
                    self.cutEndPoint = None
            self.intersections = points
            self.canvas.Refresh()
        event.Skip()

    def draw(self, gc):
        if self.state == WORKING and self.knifeStartPoint and self.knifeEndPoint:
            transformPoint = self.canvas.transform.transformPoint
            start = transformPoint(self.knifeStartPoint)
            end = transformPoint(self.knifeEndPoint)
            gc.SetPen(self.pen)
            gc.StrokeLine(start[0], start[1], end[0], end[1])
            if self.intersections:
                gc.SetPen(self.cutpen)
                for i in range(0, len(self.intersections), 2):
                    try:
                        p0 = transformPoint(self.intersections[i])
                        p1 = transformPoint(self.intersections[i + 1])
                        gc.StrokeLine(p0[0], p0[1], p1[0], p1[1])
                    except IndexError:
                        continue
                s = 2
                gc.SetPen(self.pen)
                gc.SetBrush(self.brush)
                for point in self.intersections:
                    try:
                        x, y = transformPoint(point)
                        x = round(x)
                        y = round(y)
                    except ValueError:
                        continue
                    gc.DrawEllipse(x - s, y - s, 2 * s, 2 * s)
