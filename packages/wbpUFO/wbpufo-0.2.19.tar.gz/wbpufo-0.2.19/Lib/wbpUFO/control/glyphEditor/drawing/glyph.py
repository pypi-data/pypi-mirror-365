"""
glyph
===============================================================================
"""
import logging
from math import atan2, pi

import wx
from fontTools.pens.transformPen import TransformPen
from wbBase.tools import get_wxBrush, get_wxFont, get_wxPen
from wbDefcon.pens import ContourHit, HitTestPen, graphicsPen, graphicsRoundingPen

from ....config import (
    NODESHAPE_CIRCLE,
    NODESHAPE_DIAMOND,
    NODESHAPE_SQUARE,
    NODESHAPE_STAR,
    NODESHAPE_TRIANGLE,
    cfgBrush,
    cfgPen,
    cfgShape,
    cfgSize,
)
from .base import DrawingPlane, DrawingPlaneStack, GuidelinePlaneMixin

log = logging.getLogger(__name__)

SelectionPen = wx.RED_PEN


class GlyphLevelPlain(DrawingPlane):
    """
    Base class for all glyph level drawing planes
    """

    visibleActiveDflt = True
    visibleInactiveDflt = False

    def __init__(self, parent, name):
        super().__init__(parent, name)
        self._visibleActive = self.visibleActiveDflt
        self._visibleInactive = self.visibleInactiveDflt

    @property
    def visible(self):
        active = self.parent.active
        return (active and self._visibleActive) or (
            self._visibleInactive and not active
        )

    @property
    def visibleActive(self):
        return self._visibleActive

    @visibleActive.setter
    def visibleActive(self, value):
        newValue = bool(value)
        if newValue != self._visibleActive:
            visible = self.visible
            self._visibleActive = newValue
            if self.visible != visible:
                self.canvas.Refresh()

    @property
    def visibleInactive(self):
        return self._visibleInactive

    @visibleInactive.setter
    def visibleInactive(self, value):
        newValue = bool(value)
        if newValue != self._visibleInactive:
            visible = self.visible
            self._visibleInactive = newValue
            if self.visible != visible:
                self.canvas.Refresh()

    @property
    def glyphName(self):
        return self.parent.parent.glyph.name

    @property
    def layer(self):
        return self.parent.parent.font.layers[self.parent.name]

    @property
    def glyph(self):
        g = self.parent.parent.glyph
        if g is not None:
            glyphName = g.name
            layer = self.parent.parent.font.layers[self.parent.name]
            if glyphName in layer:
                return layer[glyphName]


class LabelPlain(GlyphLevelPlain):
    """
    Base class to draw labels of points and anchors on Canvas.
    Not intended to be intantiated directly.
    """

    visibleActiveDflt = False
    visibleInactiveDflt = False
    lockedDflt = True
    LabelFont = get_wxFont(pointSize=7, faceName="Small Fonts")
    LabelPen = wx.TRANSPARENT_PEN
    LabelBrush = get_wxBrush(wx.Colour(230, 230, 240, 200))
    # Label types
    LT_POSITION = 1
    LT_NAME = 3
    LT_IDENTFIER = 3

    def __init__(self, parent, name):
        super().__init__(parent, name)
        self.labelType = self.LT_POSITION

    @property
    def points(self):
        "Needs to be implemented by subclasses"
        raise NotImplementedError

    def draw(self, gc:wx.GraphicsContext):
        gc.SetBrush(self.LabelBrush)
        gc.SetPen(self.LabelPen)
        gc.SetFont(self.LabelFont, wx.BLACK)
        d = 3  # distace between point and label
        s = 2  # space around text
        for point in self.points:
            if self.labelType == self.LT_POSITION:
                text = f"{point.x:.0f} / {point.y:.0f}"
            elif self.labelType == self.LT_NAME:
                if not point.name:
                    continue
                text = point.name
            elif self.labelType == self.LT_IDENTFIER:
                if not point.identifier:
                    continue
                text = point.identifier
            w, h = gc.GetTextExtent(text)
            w = int(round(w)) + 2 * s
            h = int(round(h)) + 2 * s
            x, y = self.transform.transformPoint((point.x, point.y))
            x = round(x)
            y = round(y)
            gc.DrawRoundedRectangle(x + d, y + d, w, h, d)
            gc.DrawText(text, x + d + s, y + d + s - 1)


class ShapeDrawPlain(GlyphLevelPlain):
    """Base class for nodes and anchors"""

    def drawShape(self, gc:wx.GraphicsContext, point, node):
        x, y = self.transform.transformPoint((point.x, point.y))
        x = round(x)
        y = round(y)
        if hasattr(point, "color") and point.color is not None:
            brush = get_wxBrush(point.color.wx)
        else:
            brush = node["brush"]
        if self.parent.active:
            if point.selected:
                gc.SetPen(SelectionPen)
            else:
                gc.SetPen(node["pen"])
            gc.SetBrush(brush)
        else:
            gc.SetBrush(self.getInactiveBrush(brush))
            gc.SetPen(self.getInactivePen(node["pen"]))
        shape = node["shape"]
        s = node["size"]
        if shape == NODESHAPE_CIRCLE:
            gc.DrawEllipse(x - s, y - s, 2 * s, 2 * s)
        elif shape == NODESHAPE_SQUARE:
            gc.DrawRectangle(x - s, y - s, 2 * s, 2 * s)
        elif shape == NODESHAPE_DIAMOND:
            gc.DrawLines([(x - s, y), (x, y - s), (x + s, y), (x, y + s), (x - s, y)])
        elif shape == NODESHAPE_TRIANGLE:
            gc.DrawLines([(x - s, y + s), (x, y - s), (x + s, y + s), (x - s, y + s)])
        elif shape == NODESHAPE_STAR:
            if s > 7:
                i = 2
            else:
                i = 1
            gc.DrawLines(
                [
                    (x - s, y),
                    (x - i, y - i),
                    (x, y - s),
                    (x + i, y - i),
                    (x + s, y),
                    (x + i, y + i),
                    (x, y + s),
                    (x - i, y + i),
                    (x - s, y),
                ]
            )


class GlyphMetricPlane(GlyphLevelPlain):
    """Draw left and right margin of glyph on Canvas"""

    pen = get_wxPen(color="gray", style=wx.PENSTYLE_LONG_DASH)

    def __init__(self, parent):
        super().__init__(parent, "GlyphMetric")

    def draw(self, gc:wx.GraphicsContext):
        gc.SetPen(self.pen)
        for w in (0, self.glyph.width):
            x = round(self.transform.transformPoint((w, 0))[0])
            gc.StrokeLine(x, 0, x, gc.GetSize()[1])


class GlyphGuidePlane(GlyphLevelPlain, GuidelinePlaneMixin):
    """Draw guidelines of glyph on Canvas"""

    selected_pen = get_wxPen(
        color=wx.Colour(255, 0, 0, 64), width=3, style=wx.PENSTYLE_SOLID
    )

    def __init__(self, parent):
        super().__init__(parent, "GlyphGuide")

    def draw(self, gc:wx.GraphicsContext):
        self.drawGuidelines(gc, self.glyph.guidelines)

    def hitTest(self, x, y):
        return self.hitTestGuidelines(x, y, self.glyph.guidelines)


class GlyphOutlinePlane(GlyphLevelPlain):
    """Draw glyph outline on Canvas"""

    visibleActiveDflt = True
    visibleInactiveDflt = True
    GlyphOutlinePen = wx.BLACK_PEN
    GlyphSelectionPen = wx.RED_PEN
    LabelFont = get_wxFont(pointSize=7, faceName="Small Fonts")

    def __init__(self, parent):
        super().__init__(parent, "GlyphOutline")
        self.hitTestPen = HitTestPen()

    def getInactivePen(self, pen):
        if self.layer.color:
            return get_wxPen(
                self.getInactiveColour(self.layer.color.wx), pen.Width, pen.Style
            )
        return super().getInactivePen(pen)

    def draw(self, gc:wx.GraphicsContext):
        pen = TransformPen(graphicsRoundingPen, self.transform)
        gc.SetFont(self.LabelFont, wx.LIGHT_GREY)
        for contour in self.glyph:
            if len(contour) == 0:
                continue
            if self.parent.active:
                point = contour[0]
                x, y = self.transform.transformPoint((point.x, point.y))
                # draw contour index
                gc.DrawText(str(self.glyph.contourIndex(contour)), x - 10, y - 15)
                # draw direction indicator
                d = 4
                directionIndicator = gc.CreatePath()
                directionIndicator.MoveToPoint(0, 0)
                directionIndicator.AddCurveToPoint(0, 2 * d, 0, 2 * d, 2 * d, 2 * d)
                directionIndicator.MoveToPoint(d, d)
                directionIndicator.AddLineToPoint(2 * d, 2 * d)
                directionIndicator.AddLineToPoint(d, 3 * d)
                matrix = gc.CreateMatrix()
                matrix.Translate(x, y)
                try:
                    angle = atan2(-(contour[1].y - point.y), contour[1].x - point.x)
                except IndexError:
                    angle = 0
                matrix.Rotate(angle)
                directionIndicator.Transform(matrix)
                gc.SetPen(wx.GREY_PEN)
                gc.StrokePath(directionIndicator)
            for segmentIndex, segment in enumerate(contour.segments):
                segmentType = segment[-1].segmentType
                if segmentType != "move":
                    graphicsRoundingPen.path = gc.CreatePath()
                    if segmentIndex == 0:
                        start = contour.segments[-1][-1]
                    else:
                        start = contour.segments[segmentIndex - 1][-1]
                    pen.moveTo(start)
                    if segmentType == "line":
                        pen.lineTo(segment[0])
                    elif segmentType == "curve":
                        pen.curveTo(*segment)
                    elif segmentType == "qcurve":
                        pen.qCurveTo(*segment)
                    else:
                        log.error("unhandled segment type: %r", segmentType)
                    pen.endPath()
                    if self.parent.active:
                        segmentSelected = start.selected
                        for point in segment:
                            segmentSelected &= point.selected
                        if segmentSelected:
                            gc.SetPen(self.GlyphSelectionPen)
                        else:
                            gc.SetPen(self.GlyphOutlinePen)
                    else:
                        gc.SetPen(self.getInactivePen(self.GlyphOutlinePen))
                    gc.StrokePath(graphicsRoundingPen.path)

    def hitTest(self, x, y):
        if self.glyph:
            self.hitTestPen.reset()
            self.hitTestPen.position = (x, y)
            self.hitTestPen.tolerance = self.canvas.screenToCanvasXrel(3)
            self.glyph.draw(self.hitTestPen)
            hit = self.hitTestPen.hit
            if hit is not None:
                return ContourHit(self.glyph, *hit)


class GlyphComponentPlain(GlyphLevelPlain):
    """
    Draw glyph components on Canvas
    """

    visibleActiveDflt = True
    visibleInactiveDflt = True
    ComponentBrush = get_wxBrush(wx.Colour(192, 192, 192, 200))
    ComponentPen = wx.GREY_PEN
    ComponentSelectionPen = wx.RED_PEN
    LabelFont = get_wxFont(pointSize=7, faceName="Small Fonts")

    def __init__(self, parent):
        super().__init__(parent, "GlyphComponent")

    def draw(self, gc:wx.GraphicsContext):
        gc.SetBrush(self.ComponentBrush)
        gc.SetFont(self.LabelFont, wx.BLACK)
        graphicsRoundingPen.glyphSet = self.layer
        pen = TransformPen(graphicsRoundingPen, self.transform)
        for componentIndex, component in enumerate(self.glyph.components):
            graphicsRoundingPen.path = gc.CreatePath()
            component.draw(pen)
            if component.selected:
                gc.SetPen(self.ComponentSelectionPen)
            else:
                gc.SetPen(self.ComponentPen)
            gc.DrawPath(graphicsRoundingPen.path, wx.WINDING_RULE)
            point = graphicsRoundingPen.path.Box.LeftBottom
            gc.DrawText(str(componentIndex), point.x, point.y)

    def hitTest(self, x, y):
        for component in self.glyph.components:
            if component.pointInside((x, y)):
                return component


class OnCurvePointsPlain(ShapeDrawPlain):
    """
    Draw labels for On-Curve Points
    """

    Start = {
        "brush": cfgBrush("Start", wx.TRANSPARENT_BRUSH),
        "pen": cfgPen("Start", wx.BLUE_PEN),
        "shape": cfgShape("Start", NODESHAPE_CIRCLE),
        "size": cfgSize("Start", 4),
    }

    Move = {
        "brush": cfgBrush("Move", wx.BLUE_BRUSH),
        "pen": cfgPen("Move", wx.GREY_PEN),
        "shape": cfgShape("Move", NODESHAPE_SQUARE),
        "size": cfgSize("Move", 3),
    }

    Line = {
        "brush": cfgBrush("Line", wx.RED_BRUSH),
        "pen": cfgPen("Line", wx.GREY_PEN),
        "shape": cfgShape("Line", NODESHAPE_SQUARE),
        "size": cfgSize("Line", 3),
    }

    LineSmooth = {
        "brush": cfgBrush("LineSmooth", wx.RED_BRUSH),
        "pen": cfgPen("LineSmooth", wx.GREY_PEN),
        "shape": cfgShape("LineSmooth", NODESHAPE_TRIANGLE),
        "size": cfgSize("LineSmooth", 3),
    }

    PScurve = {
        "brush": cfgBrush("PScurve", wx.GREEN_BRUSH),
        "pen": cfgPen("PScurve", wx.GREY_PEN),
        "shape": cfgShape("PScurve", NODESHAPE_DIAMOND),
        "size": cfgSize("PScurve", 3),
    }

    PScurveSmooth = {
        "brush": cfgBrush("PScurveSmooth", wx.GREEN_BRUSH),
        "pen": cfgPen("PScurveSmooth", wx.GREY_PEN),
        "shape": cfgShape("PScurveSmooth", NODESHAPE_CIRCLE),
        "size": cfgSize("PScurveSmooth", 3),
    }

    TTcurve = {
        "brush": cfgBrush("TTcurve", wx.CYAN_BRUSH),
        "pen": cfgPen("TTcurve", wx.GREY_PEN),
        "shape": cfgShape("TTcurve", NODESHAPE_SQUARE),
        "size": cfgSize("TTcurve", 3),
    }

    def __init__(self, parent):
        super().__init__(parent, "OnCurvePoints")

    def draw(self, gc:wx.GraphicsContext):
        for contour in self.glyph:
            for point in contour.onCurvePoints:
                if point.segmentType == "move":
                    node = self.Move
                elif point.segmentType == "line":
                    if point.smooth:
                        node = self.LineSmooth
                    else:
                        node = self.Line
                elif point.segmentType == "curve":
                    if point.smooth:
                        node = self.PScurveSmooth
                    else:
                        node = self.PScurve
                elif point.segmentType == "qcurve":
                    node = self.TTcurve
                self.drawShape(gc, point, node)
            if contour.onCurvePoints:
                self.drawShape(gc, contour.onCurvePoints[0], self.Start)

    def hitTest(self, x, y):
        delta = self.canvas.screenToCanvasXrel(4)
        min_x = x - delta
        max_x = x + delta
        min_y = y - delta
        max_y = y + delta
        for contour in self.glyph:
            for point in contour.onCurvePoints:
                if min_x <= point.x <= max_x and min_y <= point.y <= max_y:
                    return point


class OnCurveLabelPlain(LabelPlain):
    """
    Draw labels of on-curve-points on Canvas.
    """

    def __init__(self, parent):
        super().__init__(parent, "OnCurvePointLabels")

    @property
    def points(self):
        result = []
        for contour in self.glyph:
            result.extend(contour.onCurvePoints)
        return result


class OffCurvePointsPlain(ShapeDrawPlain):
    """
    Draw Off-Curve-Points and conecting lines
    """

    TToff = {
        "brush": cfgBrush("TToff", wx.CYAN_BRUSH),
        "pen": cfgPen("TToff", wx.GREY_PEN),
        "shape": cfgShape("TToff", NODESHAPE_CIRCLE),
        "size": cfgSize("TToff", 2),
    }

    PSoff = {
        "brush": cfgBrush("PSoff", wx.YELLOW_BRUSH),
        "pen": cfgPen("PSoff", wx.GREY_PEN),
        "shape": cfgShape("PSoff", NODESHAPE_CIRCLE),
        "size": cfgSize("PSoff", 2),
    }

    ConnectionPen = wx.LIGHT_GREY_PEN

    def __init__(self, parent):
        super().__init__(parent, "OffCurvePoints")

    def draw(self, gc:wx.GraphicsContext):
        for contour in self.glyph:
            for segmentIndex, segment in enumerate(contour.segments):
                segmentType = segment[-1].segmentType
                if segmentType in ("curve", "qcurve"):
                    if segmentIndex == 0:
                        start = contour.segments[-1][-1]
                    else:
                        start = contour.segments[segmentIndex - 1][-1]
                    x0, y0 = self.transform.transformPoint(start)
                    x0 = round(x0)
                    y0 = round(y0)
                    if segmentType == "curve":
                        node = self.PSoff
                        x1, y1 = self.transform.transformPoint(segment[0])
                        x1 = round(x1)
                        y1 = round(y1)
                        if self.parent.active:
                            if segment[0].selected:
                                gc.SetPen(SelectionPen)
                            else:
                                gc.SetPen(self.ConnectionPen)
                        else:
                            gc.SetPen(self.getInactivePen(self.ConnectionPen))
                        gc.StrokeLine(x0, y0, x1, y1)
                        x2, y2 = self.transform.transformPoint(segment[1])
                        x2 = round(x2)
                        y2 = round(y2)
                        x3, y3 = self.transform.transformPoint(segment[2])
                        x3 = round(x3)
                        y3 = round(y3)
                        if self.parent.active:
                            if segment[1].selected:
                                gc.SetPen(SelectionPen)
                            else:
                                gc.SetPen(self.ConnectionPen)
                        else:
                            gc.SetPen(self.getInactivePen(self.ConnectionPen))
                        gc.StrokeLine(x2, y2, x3, y3)
                        self.drawShape(gc, segment[0], node)
                        self.drawShape(gc, segment[1], node)
                    elif segmentType == "qcurve":
                        node = self.TToff
                        points = []
                        for point in segment:
                            x1, y1 = self.transform.transformPoint(point)
                            x1 = round(x1)
                            y1 = round(y1)
                            gc.StrokeLine(x0, y0, x1, y1)
                            x0 = x1
                            y0 = y1
                            points.append(point)
                        for point in points[:-1]:
                            self.drawShape(gc, point, node)

    def hitTest(self, x, y):
        delta = self.canvas.screenToCanvasXrel(4)
        min_x = x - delta
        max_x = x + delta
        min_y = y - delta
        max_y = y + delta
        for contour in self.glyph:
            for point in [p for p in contour if p.segmentType is None]:
                if min_x <= point.x <= max_x and min_y <= point.y <= max_y:
                    return point


class OFFCurveLabelPlain(LabelPlain):
    """
    Draw labels of off-curve-points on Canvas.
    """

    def __init__(self, parent):
        super().__init__(parent, "OffCurvePointLabels")

    @property
    def points(self):
        result = []
        for contour in self.glyph:
            for point in contour:
                if point.segmentType is None:
                    result.append(point)
        return result


class AnchorsPlane(ShapeDrawPlain):
    """
    Draw Anchors on canvas.
    """

    Anchor = {
        "brush": cfgBrush("Anchor", wx.RED_BRUSH),
        "pen": cfgPen("Anchor", wx.GREY_PEN),
        "shape": cfgShape("Anchor", NODESHAPE_STAR),
        "size": cfgSize("Anchor", 7),
    }

    def __init__(self, parent):
        super().__init__(parent, "Anchors")

    def draw(self, gc:wx.GraphicsContext):
        for anchor in self.glyph.anchors:
            x, y = self.transform.transformPoint((anchor.x, anchor.y))
            x = round(x)
            y = round(y)
            self.drawShape(gc, anchor, self.Anchor)

    def hitTest(self, x, y):
        delta = self.canvas.screenToCanvasXrel(4)
        min_x = x - delta
        max_x = x + delta
        min_y = y - delta
        max_y = y + delta
        for anchor in self.glyph.anchors:
            if min_x <= anchor.x <= max_x and min_y <= anchor.y <= max_y:
                return anchor


class AnchorLabelPlain(LabelPlain):
    """
    Draw labels of anchors on Canvas.
    """

    visibleActiveDflt = True

    def __init__(self, parent):
        super().__init__(parent, "AnchorLabels")
        self.labelType = self.LT_NAME

    @property
    def points(self):
        return self.glyph.anchors


class GlyphFillPlane(GlyphLevelPlain):
    """
    Draw solid fill of glyph shape.
    """

    visibleActiveDflt = False
    visibleInactiveDflt = False
    lockedDflt = True
    GlyphFillBrush = wx.BLACK_BRUSH
    GlyphFillPen = wx.TRANSPARENT_PEN

    def __init__(self, parent):
        super().__init__(parent, "GlyphFill")

    def draw(self, gc:wx.GraphicsContext):
        if self.parent.active:
            gc.SetBrush(self.GlyphFillBrush)
            gc.SetPen(self.GlyphFillPen)
        else:
            gc.SetBrush(self.getInactiveBrush(self.GlyphFillBrush))
            gc.SetPen(self.getInactivePen(self.GlyphFillPen))
        graphicsPen.path = gc.CreatePath()
        graphicsPen.glyphSet = self.layer
        pen = TransformPen(graphicsPen, self.transform)
        self.glyph.draw(pen)
        gc.FillPath(graphicsPen.path, wx.WINDING_RULE)


class RedArrowPlane(GlyphLevelPlain):
    """
    Draw Red-Arrow problem indicators
    """

    visibleActiveDflt = False
    visibleInactiveDflt = False
    RedArrow = {
        "brush": cfgBrush("RedArrow", wx.RED_BRUSH),
        "pen": cfgPen("RedArrow", wx.GREY_PEN),
        "shape": cfgShape("RedArrow", NODESHAPE_DIAMOND),
        "size": cfgSize("RedArrow", 18),
    }

    def __init__(self, parent):
        super().__init__(parent, "RedArrows")

    def drawArrow(self, gc:wx.GraphicsContext, position, errors):
        message = []
        for error in errors:
            if error.vector:
                vector = error.vector
            else:
                vector = (-1, 1)
            angle = atan2(vector[0], -vector[1])
            if error.badness:
                message.append(f"{error.kind} (Severity {error.badness:0.1f})")
            else:
                message.append(f"{error.kind}")
        messageText = ", ".join(message)
        x, y = self.transform.transformPoint((position[0], position[1]))
        size = self.RedArrow["size"]
        head_ratio = 0.6
        w = size * 0.5
        tail_width = 0.2

        gc.SetBrush(self.RedArrow["brush"])
        arrowPath = gc.CreatePath()
        arrowPath.MoveToPoint(0, 0)
        arrowPath.AddLineToPoint(-size * head_ratio, w * 0.5)
        arrowPath.AddLineToPoint(-size * head_ratio, -size * tail_width * 0.5)
        arrowPath.AddLineToPoint(-size, -size * tail_width * 0.5)
        arrowPath.AddLineToPoint(-size, size * tail_width * 0.5)
        arrowPath.AddLineToPoint(-size * head_ratio, size * tail_width * 0.5)
        arrowPath.AddLineToPoint(-size * head_ratio, -w * 0.5)
        arrowPath.CloseSubpath()
        matrix = gc.CreateMatrix()
        matrix.Translate(x, y)
        matrix.Rotate(angle)
        arrowPath.Transform(matrix)
        gc.FillPath(arrowPath)
        # draw Labels
        LabelFont = get_wxFont(pointSize=size * 0.5, faceName="Small Fonts")
        gc.SetFont(LabelFont, wx.LIGHT_GREY)
        w, h = gc.GetTextExtent(messageText)
        text_x, text_y = matrix.TransformPoint(0, 0)
        direction = angle / pi

        if 0 < direction <= 0.4:  # text left
            text_x -= w + 1.2 * size
            text_y -= size
        elif 0.4 < direction <= 0.6:  # text above center
            text_x -= 0.5 * w
            text_y -= h + size
        elif direction > 0.6:  # text right
            text_x += 1.2 * size
            text_y -= size
        elif 0 > direction >= -0.4:  # text left
            text_x -= w + 1.2 * size
            text_y += size
        elif -0.4 > direction >= -0.6:  # text below center
            text_x -= 0.5 * w
            text_y += size
        elif -0.6 > direction:  # right
            text_x += 1.2 * size
            text_y += size

        gc.DrawText(messageText, text_x, text_y)

    def draw(self, gc:wx.GraphicsContext):
        errors_by_position = {}
        for error in self.glyph.getOutlineErrors():
            if error.position is not None:
                if (error.position[0], error.position[1]) in errors_by_position:
                    errors_by_position[(error.position[0], error.position[1])].extend(
                        [error]
                    )
                else:
                    errors_by_position[(error.position[0], error.position[1])] = [error]
        for position, errors in errors_by_position.items():
            self.drawArrow(gc, position, errors)


class AccentCloudPlane(GlyphLevelPlain):
    """
    Not used yet!
    """

    def __init__(self, parent):
        super(AccentCloudPlane, self).__init__(parent, "AccentCloud")

    def draw(self, gc:wx.GraphicsContext):
        for anchor in self.glyph.anchors:
            if anchor.name == "top":
                pass


class LayerPlanes(DrawingPlaneStack):
    """
    Collection of Glyph Level Plains
    """

    childType = GlyphLevelPlain
    activeDflt:bool = False
    visibleInactiveDflt:bool = True
    inactiveAlphaDflt:int = 180

    def __init__(self, parent, name):
        super(LayerPlanes, self).__init__(parent, name)
        self._visibleInactive = self.visibleInactiveDflt
        self.addPlane(GlyphMetricPlane)
        self.addPlane(GlyphGuidePlane)
        self.addPlane(GlyphFillPlane)
        self.addPlane(GlyphComponentPlain)
        self.addPlane(OffCurvePointsPlain)
        self.addPlane(OFFCurveLabelPlain)
        self.addPlane(GlyphOutlinePlane)
        self.addPlane(OnCurvePointsPlain)
        self.addPlane(OnCurveLabelPlain)
        self.addPlane(AnchorsPlane)
        self.addPlane(AnchorLabelPlain)
        self.addPlane(RedArrowPlane)
        self._hitTestOrder = [
            "Anchors",
            "OffCurvePoints",
            "OnCurvePoints",
            "GlyphComponent",
            "GlyphMetric",
            "GlyphGuide",
            "GlyphOutline",
        ]

    @property
    def visible(self) -> bool:
        return self.active or self._visibleInactive

    @property
    def visibleInactive(self) -> bool:
        return self._visibleInactive

    @visibleInactive.setter
    def visibleInactive(self, value):
        newValue = bool(value)
        if newValue != self._visibleInactive:
            visible = self.visible
            self._visibleInactive = newValue
            if self.visible != visible:
                self.canvas.Refresh()

    @property
    def layer(self):
        return self.parent.font.layers[self.name]

    @property
    def glyph(self):
        g = self.parent.glyph
        if g is not None:
            glyphName = g.name
            if glyphName in self.layer:
                return self.layer[glyphName]

    def draw(self, gc:wx.GraphicsContext):
        if self.glyph is not None:
            for plane in [p for p in self._drawingPlanes if p.visible]:
                plane.draw(gc)
        elif self.active:
            canvas = self.canvas
            g = canvas.glyph
            if g is None:
                glyphName = "<None>"
            else:
                glyphName = g.name
            text = f'No glyph "{glyphName}" on layer "{self.name}"'
            cw, ch = canvas.Size
            gc.SetFont(get_wxFont(pointSize=18), wx.BLACK)
            w, h = gc.GetTextExtent(text)
            x = (cw - w) / 2
            y = (ch + h) / 2
            gc.DrawText(text, x, y)
