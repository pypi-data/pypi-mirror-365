"""
tooledit
===============================================================================

Implementation of the edit tool for the glyph editor
"""
import logging
from math import atan2, degrees

import wx
from wbBase.tools import get_wxBrush, get_wxPen
from wbDefcon import Anchor, Component, Guideline, Point
from wbDefcon.pens import ContourHit

from ....dialog.anchorDialog import AnchorDialog
from ....dialog.componentDialog import ComponentDialog
from ....dialog.guidelineDialog import GuidelineDialog
from ..cursor import cursors
from .base import IDLE, RUBBERBANDING, WORKING, GlyphTool

log = logging.getLogger(__name__)


class ToolEdit(GlyphTool):
    """
    Tool to edit contours, anchors, components, guidelines
    """

    brush = get_wxBrush(wx.Colour(200, 200, 200, 64))
    pen = get_wxPen(wx.Colour(128, 128, 128, 128))

    def __init__(self, parent):
        super().__init__(parent)
        self.Bind(wx.EVT_LEFT_DCLICK, self.on_LEFT_DCLICK)
        # Keyboard Events
        self.Bind(wx.EVT_KEY_DOWN, self.on_KEY_DOWN)

    def setCursor(self):
        if self.subject is None:
            self.canvas.SetCursor(cursors["Default"])
        elif isinstance(self.subject, Point):
            if self.subject.selected:
                self.canvas.SetCursor(cursors["EditSelection"])
            else:
                self.canvas.SetCursor(cursors["EditPoint"])
        elif isinstance(self.subject, Anchor):
            if self.subject.selected:
                self.canvas.SetCursor(cursors["EditSelection"])
            else:
                self.canvas.SetCursor(cursors["EditAnchor"])
        elif isinstance(self.subject, Component):
            if self.subject.selected:
                self.canvas.SetCursor(cursors["EditSelection"])
            else:
                self.canvas.SetCursor(cursors["EditComponent"])
        elif isinstance(self.subject, Guideline):
            if self.subject.selected:
                self.canvas.SetCursor(cursors["EditSelection"])
            else:
                self.canvas.SetCursor(cursors["EditGuideline"])
        elif isinstance(self.subject, ContourHit):
            if self.subject.selected:
                self.canvas.SetCursor(cursors["EditSelection"])
            else:
                self.canvas.SetCursor(cursors["EditContour"])

    def moveSelection(self, dx, dy):
        glyph = self.glyph
        for contour in glyph:
            for point in contour:
                if point.selected:
                    point.move((dx, dy))
                    self.contoursChanged = True
        for anchor in glyph.anchors:
            if anchor.selected:
                anchor.move((dx, dy))
                self.anchorsChanged = True
        for component in glyph.components:
            if component.selected:
                component.move((dx, dy))
                self.componentsChanged = True
        for guideline in glyph.guidelines:
            if guideline.selected:
                guideline.move((dx, dy))
                self.glyphGuidelinesChanged = True
        for guideline in glyph.font.guidelines:
            if guideline.selected:
                guideline.move((dx, dy))
                self.fontGuidelinesChanged = True

    # -------------------------------------------------------------------------
    # Event handler methods
    # -------------------------------------------------------------------------

    def on_LEFT_DCLICK(self, event):
        if isinstance(self.subject, Component):
            # show ComponentDialog to edit component details
            component = self.subject
            with ComponentDialog(self.canvas, component) as componentDialog:
                if componentDialog.ShowModal() == wx.ID_OK:
                    component.baseGlyph = componentDialog.baseGlyph
                    component.offset = componentDialog.offset
                    component.scale = componentDialog.scale
        elif isinstance(self.subject, Anchor):
            # show AnchorDialog to edit anchor details
            anchor = self.subject
            with AnchorDialog(self.canvas, anchor.asDict()) as anchorDialog:
                if anchorDialog.ShowModal() == wx.ID_OK:
                    d = anchorDialog.anchorDict
                    anchor.x = d["x"]
                    anchor.y = d["y"]
                    anchor.name = d["name"]
                    anchor.color = d["color"]
        elif isinstance(self.subject, Guideline):
            # show GuidelineDialog to edit guideline details
            guideline = self.subject
            with GuidelineDialog(
                self.canvas, guideline.getDataForSerialization()
            ) as guidelineDiaolog:
                if guidelineDiaolog.ShowModal() == wx.ID_OK:
                    guideline.setDataFromSerialization(guidelineDiaolog.guidelineDict)
        elif isinstance(self.subject, ContourHit):
            # select whole contour
            self.subject.contour.selected = not self.subject.contour.selected
            self.canvas.Refresh()

    def on_LEFT_DOWN(self, event):
        super().on_LEFT_DOWN(event)
        glyph = self.glyph
        if self.subject is None:
            self.state = RUBBERBANDING
        elif glyph is not None:
            glyph.undoManager.saveState()
            # glyph.disableNotifications()
            glyph.holdNotifications()
            self.state = WORKING
        event.Skip()

    def on_LEFT_UP(self, event:wx.MouseEvent):
        log.debug("on_LEFT_UP: %r", self.state)
        glyph = self.glyph
        if glyph is not None:
            if self.state == RUBBERBANDING:
                x0 = self.canvas.screenToCanvasX(self.xClick)
                y0 = self.canvas.screenToCanvasY(self.yClick)
                x1 = self.canvas.screenToCanvasX(self.x)
                y1 = self.canvas.screenToCanvasY(self.y)
                stack = self.activeStack
                glyph.selectRect(
                    (x0, y0, x1, y1),
                    addToSelection=event.ShiftDown(),
                    selectPoints=not stack["OnCurvePoints"].locked,
                    selectComponents=not stack["GlyphComponent"].locked,
                    selectAnchors=not stack["Anchors"].locked,
                    selectGuidelines=not stack["GlyphGuide"].locked,
                )
                glyph.font.selectRect(
                    (x0, y0, x1, y1),
                    addToSelection=event.ShiftDown(),
                    selectGuidelines=not stack["GlyphGuide"].locked,
                )
            elif self.state == WORKING:
                # try:
                #     glyph.enableNotifications()
                # except KeyError:
                #     pass
                if not self.subject.selected:
                    if not event.ShiftDown():
                        self.unselectAll()
                    if not event.AltDown():
                        self.subject.selected = True
                        if (
                            isinstance(self.subject, Point)
                            and self.subject.segmentType is not None
                        ):
                            for contour in glyph:
                                if self.subject in contour.onCurvePoints:
                                    contour.updateSelection()
                    else:
                        if isinstance(self.subject, ContourHit) and len(self.subject.segment) == 1:
                            # convert line segment to curve
                            self.subject.convertToCurve()
                self.postNotifications()
            if glyph.dispatcher.areNotificationsHeld(glyph):
                glyph.releaseHeldNotifications()
        super().on_LEFT_UP(event)

    def on_RIGHT_DOWN(self, event):
        if self.state == WORKING and not self.subject.selected:
            # right click while left is down on unselected objets
            glyph = self.glyph
            if isinstance(self.subject, Anchor):
                glyph.removeAnchor(self.subject)
                self.anchorsChanged = True
            elif isinstance(self.subject, Component):
                glyph.removeComponent(self.subject)
                self.componentsChanged = True
            elif isinstance(self.subject, Guideline):
                if self.subject.glyph is None:
                    glyph.font.removeGuideline(self.subject)
                    self.fontGuidelinesChanged = True
                else:
                    glyph.removeGuideline(self.subject)
                    self.glyphGuidelinesChanged = True
            elif isinstance(self.subject, Point):
                point = self.subject
                for contour in glyph:
                    if point in contour:
                        segmentIndex = contour.segmentIndex(point)
                        if segmentIndex >= 0:
                            if glyph.dispatcher.areNotificationsDisabled():
                                glyph.enableNotifications()
                            if point.segmentType is None:
                                # right click on off-curve point, convert to line
                                segment = contour.segments[segmentIndex]
                                segment[-1].segmentType = "line"
                                segment[-1].smooth = False
                                for p in segment[:-1]:
                                    contour.removePoint(p)
                            else:
                                # right click on on-curve point, remove the segment
                                contour.removeSegment(segmentIndex, True)
                                if len(contour) == 0:
                                    glyph.removeContour(contour)
                            self.contoursChanged = True
            elif isinstance(self.subject, ContourHit):
                # right click on contour, split the segment
                if glyph.dispatcher.areNotificationsDisabled():
                    glyph.enableNotifications()
                if event.AltDown():
                    self.subject.convertToCurve()
                else:
                    self.subject.splitAndInsertPoint()
                self.contoursChanged = True
            if self.contoursChanged or self.componentsChanged:
                glyph.destroyRepresentation("outlineErrors")
            self.state = IDLE
            self.canvas.Refresh()
            self.postNotifications()
        else:
            super().on_RIGHT_DOWN(event)

    def on_MOTION(self, event):
        super().on_MOTION(event)
        glyph = self.glyph
        if glyph is not None:
            canvas_x = self.canvas.screenToCanvasX(self.x)
            canvas_y = self.canvas.screenToCanvasY(self.y)
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
                elif self.state == WORKING:
                    dx = self.canvas.screenToCanvasXrel(self.x - self.xPrev)
                    dy = self.canvas.screenToCanvasYrel(self.y - self.yPrev)
                    if dx or dy:
                        if self.subject.selected:
                            self.moveSelection(dx, dy)
                        else:
                            self.unselectAll()
                            if isinstance(self.subject, Point):
                                if self.subject.segmentType is None:
                                    self.subject.move((dx, dy))
                                    self.subject.selected = True
                                else:
                                    self.subject.selected = True
                                    for contour in glyph:
                                        if self.subject in contour.onCurvePoints:
                                            contour.updateSelection()
                                            for point in contour:
                                                if point.selected:
                                                    point.move((dx, dy))
                                self.contoursChanged = True
                            elif isinstance(self.subject, Component):
                                self.subject.move((dx, dy))
                                self.componentsChanged = True
                            elif isinstance(self.subject, Anchor):
                                self.subject.move((dx, dy))
                                self.anchorsChanged = True
                            elif isinstance(self.subject, Guideline):
                                if event.AltDown():
                                    self.subject.angle = degrees(
                                        atan2(
                                            canvas_y - self.subject.y,
                                            canvas_x - self.subject.x,
                                        )
                                    )
                                else:
                                    self.subject.move((dx, dy))
                                if self.subject.glyph is None:
                                    self.fontGuidelinesChanged = True
                                else:
                                    self.glyphGuidelinesChanged = True
                        if any(
                            (
                                self.contoursChanged,
                                self.anchorsChanged,
                                self.componentsChanged,
                            )
                        ):
                            glyph.destroyRepresentation("outlineErrors")
                        self.canvas.Refresh()
            else:
                if self.state == IDLE:
                    self.hitTest()
                    self.setCursor()
        event.Skip()

    def on_KEY_DOWN(self, event):
        if self.isAnySelected():
            key = event.GetKeyCode()
            modifiers = event.GetModifiers()
            glyph = self.glyph
            glyph.undoManager.saveState()
            if key in (wx.WXK_LEFT, wx.WXK_RIGHT, wx.WXK_UP, wx.WXK_DOWN):
                # move selection with arrow keys
                distance = 1
                if modifiers == wx.MOD_SHIFT:
                    distance = 10
                elif modifiers == wx.MOD_CONTROL:
                    distance = 100
                elif modifiers == wx.MOD_SHIFT | wx.MOD_CONTROL:
                    distance = 1000
                if key == wx.WXK_LEFT:
                    move = (-distance, 0)
                elif key == wx.WXK_RIGHT:
                    move = (distance, 0)
                elif key == wx.WXK_UP:
                    move = (0, distance)
                elif key == wx.WXK_DOWN:
                    move = (0, -distance)
                self.moveSelection(*move)
            elif key == wx.WXK_DELETE:
                # delete selection
                for contour in reversed(glyph):
                    if contour.selected:
                        glyph.removeContour(contour)
                        self.contoursChanged = True
                    else:
                        for point in reversed(contour):
                            if point.selected:
                                contour.removePoint(point)
                                self.contoursChanged = True
                for anchor in glyph.anchors:
                    if anchor.selected:
                        glyph.removeAnchor(anchor)
                        self.anchorsChanged = True
                for component in glyph.components:
                    if component.selected:
                        glyph.removeComponent(component)
                        self.componentsChanged = True
                for guideline in glyph.guidelines:
                    if guideline.selected:
                        glyph.removeGuideline(guideline)
                        self.glyphGuidelinesChanged = True
                for guideline in glyph.font.guidelines:
                    if guideline.selected:
                        glyph.font.removeGuideline(guideline)
                        self.fontGuidelinesChanged = True
            if self.contoursChanged or self.componentsChanged:
                glyph.destroyRepresentation("outlineErrors")
            self.postNotifications()
            self.canvas.Refresh()
        else:
            event.Skip()

    def draw(self, gc):
        if self.state == RUBBERBANDING and None not in (
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
