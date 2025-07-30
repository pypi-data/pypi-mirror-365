"""
font
===============================================================================
"""
import logging

import wx

from wbBase.tools import get_wxBrush, get_wxPen

from .base import DrawingPlane, DrawingPlaneStack, GuidelinePlaneMixin

log = logging.getLogger(__name__)


class FontLevelPlain(DrawingPlane):
    """
    Base class for all font level drawing planes
    """

    visibleDflt = True

    def __init__(self, parent, name):
        super().__init__(parent, name)
        self._visible = self.visibleDflt

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value:bool):
        newVal = bool(value)
        if newVal != self._visible:
            self._visible = newVal
            self.canvas.Refresh()


# -------------------------------------------------------------------------
# Font level plains
# -------------------------------------------------------------------------


class VerticalMetricPlane(FontLevelPlain):
    """
    Font level metrics like, ascender, descender ...
    """

    pen = get_wxPen(color="gray", style=wx.PENSTYLE_LONG_DASH)

    def __init__(self, parent):
        super().__init__(parent, "VerticalMetric")

    def draw(self, gc:wx.GraphicsContext):
        gc.SetPen(self.pen)
        transformPoint = self.transform.transformPoint
        w = gc.GetSize()[0]
        info = self.font.info
        for h in (info.ascender, info.capHeight, info.xHeight, 0, info.descender):
            if h is not None:
                y = round(transformPoint((0, h))[1])
                gc.StrokeLine(0, y, w, y)


class AlignmentZonesPlane(FontLevelPlain):
    """
    Draw PostScript alignment zones of the font
    """

    visibleDflt = False
    pen = get_wxPen(color=wx.Colour(0, 0, 255, 128), style=wx.PENSTYLE_LONG_DASH)
    brush = get_wxBrush(color=wx.Colour(0, 0, 255, 32))

    def __init__(self, parent):
        super().__init__(parent, "AlignmentZones")

    def draw(self, gc:wx.GraphicsContext):
        gc.SetPen(self.pen)
        gc.SetBrush(self.brush)
        transformPoint = self.transform.transformPoint
        w = gc.GetSize()[0] + 1
        x = -1
        blueValues = (
            self.font.info.postscriptBlueValues + self.font.info.postscriptOtherBlues
        )
        for bottom, top in [
            (blueValues[i], blueValues[i + 1]) for i in range(0, len(blueValues), 2)
        ]:
            y = round(transformPoint((0, top))[1])
            h = abs(y - round(transformPoint((0, bottom))[1]))
            log.debug("y = %s, h = %s", y, h)
            gc.DrawRectangle(x, y, w, h)


class FontGuidePlane(FontLevelPlain, GuidelinePlaneMixin):
    """
    Draw guidelines of font on Canvas
    """

    selected_pen = get_wxPen(
        color=wx.Colour(255, 0, 0, 64), width=3, style=wx.PENSTYLE_SOLID
    )

    def __init__(self, parent):
        super().__init__(parent, "FontGuide")

    def draw(self, gc:wx.GraphicsContext):
        self.drawGuidelines(gc, self.font.guidelines)

    def hitTest(self, x, y):
        return self.hitTestGuidelines(x, y, self.font.guidelines)


class FontLevelPlanes(DrawingPlaneStack):
    """
    Collection of font level drawing planes
    """

    childType = FontLevelPlain
    visible = True

    def __init__(self, parent):
        super().__init__(parent, "Font")
        self.addPlane(VerticalMetricPlane)
        self.addPlane(AlignmentZonesPlane)
        self.addPlane(FontGuidePlane)
