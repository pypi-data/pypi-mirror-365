"""
base
===============================================================================
"""

from __future__ import annotations

import logging
from math import asin, hypot, pi, sqrt
from typing import TYPE_CHECKING, Optional, Tuple, Any

import wx
from wbBase.tools import get_wxPen

from ..cursor import cursors
from ..drawing import LayerPlanes
from ..menu import DefaultEditMenu

if TYPE_CHECKING:
    from ..canvas import Canvas
    from ..drawing.base import DrawingPlaneStack

log = logging.getLogger(__name__)

IDLE = 0
WORKING = 1
RUBBERBANDING = 2

DEGREE = 180 / pi


class GlyphTool(wx.EvtHandler):
    """
    Base class for glyph edit tools
    """

    cursor = cursors["Default"]
    pen = get_wxPen(wx.Colour(0, 0, 0, 255))
    brush = wx.NullBrush

    def __init__(self, parent):
        super().__init__()
        self.canvas: Canvas = parent
        self.contoursChanged: bool = False
        self.anchorsChanged: bool = False
        self.componentsChanged: bool = False
        self.glyphGuidelinesChanged: bool = False
        self.fontGuidelinesChanged: bool = False
        self.state: int = IDLE
        self._active: bool = False
        self.subject: Optional[Any] = None
        self.x: int = 0
        self.y: int = 0
        self.xClick: Optional[int] = None
        self.yClick: Optional[int] = None
        self.xPrev: Optional[int] = None
        self.yPrev: Optional[int] = None
        self.shiftDown: bool = False
        # Mouse Events
        self.Bind(wx.EVT_LEFT_DOWN, self.on_LEFT_DOWN)
        self.Bind(wx.EVT_LEFT_UP, self.on_LEFT_UP)
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_RIGHT_DOWN)
        self.Bind(wx.EVT_MOTION, self.on_MOTION)

    def __repr__(self):
        return "<%s: active=%r>" % (self.__class__.__name__, self.active)

    @staticmethod
    def distance(p0, p1):
        dx = p1[0] - p0[0]
        dy = p1[1] - p0[1]
        return hypot(dx, dy)

    @property
    def activeStack(self) -> Optional[DrawingPlaneStack]:
        return self.canvas.getActiveDrawingPlaneStack()

    @property
    def glyph(self):
        stack = self.activeStack
        if isinstance(stack, LayerPlanes):
            return stack.glyph

    # Tool activation ------------------

    @property
    def active(self) -> bool:
        """
        Active state of the tool
        """
        return self._active

    def activate(self, value: bool = True) -> bool:
        assert isinstance(value, bool)
        if value:
            return self.onActivate()
        return self.onDeactivate()

    def onActivate(self) -> bool:
        if not self._active:
            self.canvas.PushEventHandler(self)
            self.canvas.SetCursor(self.cursor)
            self.reset()
            self._active = True
            return True
        return False

    def onDeactivate(self) -> bool:
        if self._active:
            self.canvas.PopEventHandler()
            self.canvas.SetCursor(cursors["Default"])
            self.reset()
            self._active = False
            return True
        return False

    def reset(self):
        self.x = 0
        self.y = 0
        self.xClick = None
        self.yClick = None
        self.xPrev = None
        self.yPrev = None
        self.state = IDLE
        self.shiftDown = False
        self.contoursChanged = False
        self.anchorsChanged = False
        self.componentsChanged = False
        self.glyphGuidelinesChanged = False
        self.fontGuidelinesChanged = False

    def hitTest(self):
        # check for pointing Stuff under cursor
        canvas_x = self.canvas.screenToCanvasX(self.x)
        canvas_y = self.canvas.screenToCanvasY(self.y)
        pointed = None
        self.subject = None
        # perform hit test on editable layers
        for plainName in self.activeStack.hitTestOrder:
            plain = self.activeStack.get(plainName)
            if plain.visible and not plain.locked:
                pointed = plain.hitTest(canvas_x, canvas_y)
                if pointed is not None and pointed != self.subject:
                    self.subject = pointed
                    break
        if self.subject is None:
            planes = self.canvas.fontLevelPlanesStack
            if planes:
                for plainName in planes.hitTestOrder:
                    plain = planes.get(plainName)
                    if plain.visible and not plain.locked:
                        pointed = plain.hitTest(canvas_x, canvas_y)
                        if pointed is not None and pointed != self.subject:
                            self.subject = pointed
                            break

    # Selection ------------------

    def isAnySelected(self) -> bool:
        glyph = self.glyph
        if glyph is not None:
            for contour in glyph:
                for point in contour:
                    if point.selected:
                        return True
            for anchor in glyph.anchors:
                if anchor.selected:
                    return True
            for component in glyph.components:
                if component.selected:
                    return True
            for guideline in glyph.guidelines:
                if guideline.selected:
                    return True
        for guideline in self.canvas.font.guidelines:
            if guideline.selected:
                return True
        return False

    def unselectAll(self) -> None:
        glyph = self.glyph
        if glyph is not None:
            for contour in glyph:
                contour.selected = False
            for anchor in glyph.anchors:
                anchor.selected = False
            for component in glyph.components:
                component.selected = False
            for guideline in glyph.guidelines:
                guideline.selected = False
        for guideline in self.canvas.font.guidelines:
            guideline.selected = False

    def postNotifications(self):
        # log.debug("postNotifications")
        # log.debug("activeStack       %s", self.activeStack)
        # log.debug("glyph             %s", self.glyph)
        # log.debug("contoursChanged   %s", self.contoursChanged)
        # log.debug("anchorsChanged    %s", self.anchorsChanged)
        # log.debug("componentsChanged %s", self.componentsChanged)
        # log.debug("glyphGuidelinesChanged %s", self.glyphGuidelinesChanged)
        # log.debug("fontGuidelinesChanged %s", self.fontGuidelinesChanged)
        glyph = self.glyph
        if glyph is not None:
            anyChanged = False
            glyph.disableNotifications()
            glyph.round(
                roundPoints=self.contoursChanged,
                roundAnchors=self.anchorsChanged,
                roundComponents=self.componentsChanged,
            )
            if self.glyphGuidelinesChanged:
                for guideline in glyph.guidelines:
                    guideline.round()
            glyph.enableNotifications()
            glyph.font.holdNotifications()
            if self.fontGuidelinesChanged:
                for guideline in glyph.font.guidelines:
                    guideline.round()
            if self.contoursChanged:
                for contour in glyph:
                    contour.destroyAllRepresentations()
                    contour.postNotification(notification="Contour.Changed")
                # componentReferences = glyph.font.componentReferences.get(glyph.name, ())
                # for compositeName in componentReferences:
                #     for component in glyph.font[compositeName].components:
                #         component.destroyAllRepresentations()
                glyph.postNotification(notification="Glyph.ContoursChanged")
                self.contoursChanged = False
                anyChanged = True
            if self.anchorsChanged:
                glyph.postNotification(notification="Glyph.AnchorsChanged")
                self.anchorsChanged = False
                anyChanged = True
            if self.componentsChanged:
                glyph.postNotification(notification="Glyph.ComponentsChanged")
                self.componentsChanged = False
                anyChanged = True
            if self.glyphGuidelinesChanged:
                glyph.postNotification(notification="Glyph.GuidelinesChanged")
                self.glyphGuidelinesChanged = False
                anyChanged = True
            if anyChanged:
                glyph.dirty = True
                glyph.postNotification(notification="Glyph.Changed")
            glyph.font.releaseHeldNotifications()

    def draw(self, gc):
        """
        may be overridden by subclass
        """

    # -------------------------------------------------------------------------
    # Event handler methods
    # -------------------------------------------------------------------------

    def on_LEFT_DOWN(self, event: wx.MouseEvent):
        if not self.canvas.HasCapture():
            self.canvas.CaptureMouse()
        self.shiftDown = event.ShiftDown()
        if self.glyph is not None:
            self.xClick = self.x = event.GetX()
            self.yClick = self.y = event.GetY()

    def on_LEFT_UP(self, event: wx.MouseEvent):
        if self.canvas.HasCapture():
            self.canvas.ReleaseMouse()
        self.reset()
        glyph = self.glyph
        if glyph is not None:
            try:
                glyph.enableNotifications()
            except KeyError:
                pass
        self.canvas.Refresh()
        event.Skip()

    def on_RIGHT_DOWN(self, event: wx.MouseEvent):
        if self.state == IDLE:
            menu = DefaultEditMenu(self.canvas, self.subject)
            menu.x = self.canvas.screenToCanvasX(self.x)
            menu.y = self.canvas.screenToCanvasY(self.y)
            self.canvas.PopupMenu(menu, wx.DefaultPosition)
        else:
            event.Skip()

    def on_MOTION(self, event: wx.MouseEvent):
        self.shiftDown = event.ShiftDown()
        self.xPrev = self.x
        self.yPrev = self.y
        self.x = event.GetX()
        self.y = event.GetY()


class AddShapeTool(GlyphTool):
    """
    Base class for tools which add shapes like ellipsis or rectangles.
    """

    brush = wx.NullBrush
    pen = get_wxPen(wx.Colour(0, 0, 0, 255))

    @property
    def dimension(self):
        if (
            self.glyph is not None
            and self.xClick is not None
            and self.yClick is not None
        ):
            x = min(self.xClick, self.x)
            y = min(self.yClick, self.y)
            w = abs(self.xClick - self.x)
            h = abs(self.yClick - self.y)
            if self.shiftDown:
                w = h = max(w, h)
            return x, y, w, h
        return 0, 0, 0, 0

    # -------------------------------------------------------------------------
    # Event handler methods
    # -------------------------------------------------------------------------

    def on_LEFT_DOWN(self, event):
        GlyphTool.on_LEFT_DOWN(self, event)
        if self.glyph is not None:
            self.state = RUBBERBANDING
        event.Skip()

    def on_MOTION(self, event: wx.MouseEvent):
        GlyphTool.on_MOTION(self, event)
        if (
            event.Dragging()
            and self.state == RUBBERBANDING
            and self.xClick is not None
            and self.yClick is not None
            and self.xPrev is not None
            and self.yPrev is not None
        ):
            x = min(self.xClick, self.xPrev)
            y = min(self.yClick, self.yPrev)
            w = abs(self.xClick - self.xPrev)
            h = abs(self.yClick - self.yPrev)
            rubberband = wx.Rect(x, y, w, h)
            rubberband.Union(wx.Rect(*self.dimension))
            rubberband.Inflate(1, 1)
            self.canvas.RefreshRect(rubberband)
        event.Skip()


class TransformBaseTool(GlyphTool):
    """
    Base class for transformation tools.
    """

    pen = get_wxPen(wx.Colour(128, 128, 128, 128))
    cursor = cursors["MarkCenter"]

    def __init__(self, parent):
        GlyphTool.__init__(self, parent)
        self.angleSnap = 15
        self.center: Optional[Tuple[int, int]] = None
        self.ratio = None

    @property
    def angle(self):
        if self.state == WORKING and self.center is not None:
            x = self.canvas.canvasToScreenX(self.center[0])
            y = self.canvas.canvasToScreenY(self.center[1])
            dx = x - self.x
            dy = y - self.y
            if dx == 0 and dy == 0:
                angle = 0
            elif dx > 0:
                angle = 180 - asin(dy / sqrt(dx**2 + dy**2)) * DEGREE
            else:
                angle = asin(dy / sqrt(dx**2 + dy**2)) * DEGREE
            if self.shiftDown:
                angle = round(angle / self.angleSnap) * self.angleSnap
            return -angle

    def draw(self, gc: wx.GraphicsContext):
        if self.state == WORKING and self.center is not None:
            d = 3
            x = self.canvas.canvasToScreenX(self.center[0])
            y = self.canvas.canvasToScreenY(self.center[1])
            gc.SetPen(self.pen)
            gc.StrokeLine(x - d, y - d, x + d, y + d)
            gc.StrokeLine(x + d, y - d, x - d, y + d)
            gc.StrokeLine(x, y, self.x, self.y)

    # -------------------------------------------------------------------------
    # Event handler methods
    # -------------------------------------------------------------------------

    def on_LEFT_DOWN(self, event):
        GlyphTool.on_LEFT_DOWN(self, event)
        glyph = self.glyph
        if glyph is not None:
            self.center = (
                self.canvas.screenToCanvasX(self.xClick),
                self.canvas.screenToCanvasY(self.yClick),
            )
            glyph.undoManager.saveState()
            glyph.disableNotifications()
            self.state = WORKING
        event.Skip()

    def on_LEFT_UP(self, event):
        glyph = self.glyph
        if glyph is not None:
            glyph.enableNotifications()
            self.postNotifications()
        super().on_LEFT_UP(event)
