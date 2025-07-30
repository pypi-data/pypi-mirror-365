"""
canvas
===============================================================================

Implementation of the Canvas in a Glyph View.
"""
from __future__ import annotations

import logging
import os
import weakref
from typing import TYPE_CHECKING, Dict, Optional, Tuple

import wx
from fontTools.misc.transform import Transform
from wbBase.document import dbg
from wbDefcon import Color, Font, Glyph, Guideline

from ...dialog.findGlyphDialog import FindGlyphDialog
from .drawing import FontLevelPlanes, LayerPlanes
from .tool import (
    AddEllipse,
    AddRectangle,
    MagicWand,
    ToolDraw,
    ToolEdit,
    ToolErase,
    ToolKnife,
    ToolMeter,
    ToolPan,
    ToolReverse,
    ToolRotate,
    ToolScale,
    ToolStartpoint,
    ToolZoom,
)
from .tool.base import WORKING

if TYPE_CHECKING:
    from weakref import ReferenceType
    from wbBase.application import App
    from ...view.glyph import UfoGlyphView
    from .editPanel import GlyphEditPanel
    from .tool.base import GlyphTool
    from .drawing.base import DrawingPlaneStack

log = logging.getLogger(__name__)

DISPLAY_NORMAL = 0
DISPLAY_PREVIEW = 1


class Canvas(wx.ScrolledWindow):
    """
    The drawing area of the glyph editor
    """

    refreshNotifications = (
        "Glyph.Changed",
        # "Glyph.NameChanged",
        "Glyph.WidthChanged",
        "Glyph.ContoursChanged",
        "Glyph.AnchorsChanged",
        "Glyph.GuidelinesChanged",
        "Glyph.ComponentsChanged",
        "Glyph.ComponentBaseGlyphDataChanged",
    )
    fontNotifications = ("Font.GuidelinesChanged",)
    layerSetNotifications = (
        "LayerSet.LayerOrderChanged",
        "LayerSet.LayerAdded",
        "LayerSet.LayerDeleted",
        "LayerSet.LayerNameChanged",
    )

    def __init__(self, parent, doc=None):
        style = 0
        wx.ScrolledWindow.__init__(
            self,
            parent,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.DefaultSize,
            style,
            "GlyphEditCanvas",
        )
        self.ClientSize: wx.Size
        self.Parent: GlyphEditPanel
        self.doc = doc
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.SetBackgroundColour("WHITE")
        self.canvasSize = wx.Size(6000, 10000)  # in font units
        self.canvasOrigin = wx.Point(2000, 4000)  # in font units
        self.SetScrollRate(1, 1)
        self._zoom = 0.5  # screen pixel per font unit
        self._minZoom = 0.05
        self._maxZoom = 20
        self._font: Optional[ReferenceType[Font]] = None
        self._glyph: Optional[ReferenceType[Glyph]] = None
        self.transform: Optional[Transform] = None
        self.drawingPlanes = []
        self.tools: Dict[str, GlyphTool] = {}
        self._tool: str = "ToolEdit"
        self._prevTool: str = "ToolEdit"
        self.glyphCommands = ["FlipHorizontal", "FlipVertical"]
        self.displayMode = DISPLAY_NORMAL

        # Connect Events
        # window events
        self.Bind(wx.EVT_ENTER_WINDOW, self.on_ENTER_WINDOW)
        # wx.EVT_LEAVE_WINDOW(self, self.on_LEAVE_WINDOW)
        self.Bind(wx.EVT_SET_FOCUS, self.on_SET_FOCUS)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.on_SIZE)
        self.Bind(wx.EVT_SCROLLWIN, self.on_SCROLLWIN)
        self.Bind(wx.EVT_MOUSE_CAPTURE_LOST, self.on_MOUSE_CAPTURE_LOST)

        # mouse events
        self.Bind(wx.EVT_MOUSEWHEEL, self.on_MOUSEWHEEL)
        # wx.EVT_RIGHT_DOWN(self, self.on_RIGHT_DOWN)

        # keyboard events
        self.Bind(wx.EVT_KEY_DOWN, self.on_KEY_DOWN)
        self.Bind(wx.EVT_KEY_UP, self.on_KEY_UP)

        self._initTools()

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    def Destroy(self):
        del self.glyph
        wx.LogDebug("Canvas.Destroy()")
        return super(Canvas, self).Destroy()

    # -------------------------------------------------------------------------
    # properties
    # -------------------------------------------------------------------------

    @property
    def app(self) -> App:
        return wx.GetApp()

    @property
    def view(self) -> UfoGlyphView:
        return self.Parent.Parent.view

    @property
    def font(self) -> Optional[Font]:
        if self._font is None:
            return None
        return self._font()

    @font.setter
    def font(self, font:Optional[Font]):
        if font is None:
            del self.font
            return
        assert isinstance(font, Font)
        currentFont = self.font
        if font != currentFont:
            del self.font
            for notificationName in self.fontNotifications:
                font.addObserver(
                    self, "handleNotification", notification=notificationName
                )
            layerSet = font.layers
            for notificationName in self.layerSetNotifications:
                layerSet.addObserver(
                    self, "handleNotification", notification=notificationName
                )
            self._font = weakref.ref(font)
        self.updateDrawingPlanes()

    @font.deleter
    def font(self):
        currentFont = self.font
        if isinstance(currentFont, Font):
            for notificationName in self.fontNotifications:
                currentFont.removeObserver(self, notificationName)
            for notificationName in self.layerSetNotifications:
                currentFont.layers.removeObserver(self, notificationName)
        self._font = None

    @property
    def glyph(self) -> Optional[Glyph]:
        if self._glyph is None:
            return None
        return self._glyph()

    @glyph.setter
    def glyph(self, glyph: Optional[Glyph]):
        dbg(f"Canvas set glyph {glyph}")
        if glyph is None:
            del self.glyph
            return
        assert isinstance(glyph, Glyph)
        assert glyph.font == self.font
        if self.glyph == glyph:
            return
        del self.glyph
        for layer in glyph.layerSet:
            for notificationName in self.refreshNotifications:
                if glyph.name in layer and not layer[glyph.name].hasObserver(
                    self, notificationName
                ):
                    layer[glyph.name].addObserver(
                        self, "handleNotification", notificationName
                    )
        self._glyph = weakref.ref(glyph)
        self.Refresh()

    @glyph.deleter
    def glyph(self):
        currentGlyph = self.glyph
        if isinstance(currentGlyph, Glyph):
            for layer in currentGlyph.layerSet:
                for notificationName in self.refreshNotifications:
                    if currentGlyph.name in layer and layer[
                        currentGlyph.name
                    ].hasObserver(self, notificationName):
                        layer[currentGlyph.name].removeObserver(self, notificationName)
        self._glyph = None

    def handleNotification(self, notification):
        log.debug("Canvas.handleNotification %r", notification)
        if notification.name.startswith("LayerSet."):
            self.updateDrawingPlanes()
        try:
            self.Refresh()
        except RuntimeError:
            wx.LogDebug("Refresh failed in Canvas.handleNotification")

    def showNextGlyph(self) -> None:
        """Show next glyph based on glyph order in glyphGridPanel."""
        glyphNames = self.font.document.frame.glyphGridPanel.glyphNames
        currentIndex = glyphNames.index(self.glyph.name)
        if self.font is not None and currentIndex < len(glyphNames) - 1:
            self.view.glyph = self.font[glyphNames[currentIndex + 1]]

    def showPreviousGlyph(self) -> None:
        """Show previous glyph based on glyph order in glyphGridPanel."""
        assert isinstance(self.font, Font)
        glyphNames = self.font.document.frame.glyphGridPanel.glyphNames
        currentIndex = glyphNames.index(self.glyph.name)
        if currentIndex > 0:
            self.view.glyph = self.font[glyphNames[currentIndex - 1]]

    # Drawing Planes ----------------------------

    @property
    def layerPlanes(self) -> Tuple[LayerPlanes, ...]:
        return tuple(p for p in self.drawingPlanes if isinstance(p, LayerPlanes))

    @property
    def fontLevelPlanesStack(self) -> Optional[FontLevelPlanes]:
        for planeStack in self.drawingPlanes:
            if isinstance(planeStack, FontLevelPlanes):
                return planeStack

    def updateDrawingPlanes(self):
        oldPlanes = {}
        newPlanes = []
        for planeStack in self.drawingPlanes:
            if isinstance(planeStack, FontLevelPlanes):
                newPlanes.append(planeStack)
            elif isinstance(planeStack, LayerPlanes):
                oldPlanes[planeStack.name] = planeStack
        if not newPlanes:
            newPlanes.append(FontLevelPlanes(self))
        for layerName in self.font.layers.layerOrder:
            if layerName in oldPlanes:
                newPlanes.append(oldPlanes[layerName])
            else:
                newPlanes.append(LayerPlanes(self, layerName))
        self.drawingPlanes = newPlanes
        self.getActiveDrawingPlaneStack()

    def getDrawingPlaneStack(self, name) -> Optional[DrawingPlaneStack]:
        for planeStack in self.drawingPlanes:
            if planeStack.name == name:
                return planeStack

    def getActiveDrawingPlaneStack(self):
        for planeStack in self.drawingPlanes:
            if planeStack.active:
                return planeStack
        planeStack = self.getDrawingPlaneStack(self.font.layers.defaultLayer.name)
        planeStack.active = True
        return planeStack

    # UnDo / ReDo handling ----------------------------

    def CanUndo(self) -> bool:
        return self.glyph.canUndo()

    def Undo(self):
        self.glyph.undo()

    def CanRedo(self) -> bool:
        return self.glyph.canRedo()

    def Redo(self):
        self.glyph.redo()

    # Find ---------------------------------------

    def CanFind(self) -> bool:
        return True

    def doFind(self):
        # wx.LogInfo('Ctrl + F pressed')
        if self.font is not None:
            with FindGlyphDialog(self, self.glyph.layer) as findGlyphDialog:
                findGlyphDialog.layer = self.glyph.layer
                if findGlyphDialog.ShowModal() == wx.ID_OK:
                    if findGlyphDialog.selctedGlyph is not None:
                        self.font[findGlyphDialog.selctedGlyph].show(view=self.view)
                    elif (
                        findGlyphDialog.checkBox_create.Value
                        and findGlyphDialog.choice_findAttr.StringSelection == "Name"
                    ):
                        newGlyphName = findGlyphDialog.textCtrl_findValue.Value
                        if newGlyphName not in self.font:
                            newGlyph = self.font.newGlyph(newGlyphName)
                            newGlyph.show(view=self.view)

    # Zooming ---------------------------------------

    @property
    def zoom(self) -> float:
        return self._zoom

    @zoom.setter
    def zoom(self, value:float):
        newVal = min(max(round(float(value), 2), self._minZoom), self._maxZoom)
        if newVal != self._zoom:
            self._zoom = newVal
            self.SetVirtualSize(
                wx.Size(round(self.canvasSize.width * newVal), round(self.canvasSize.height * newVal))
            )

    @zoom.deleter
    def zoom(self):
        self.zoom = 1

    def CanZoomIn(self) -> bool:
        return self.zoom < self._maxZoom

    def ZoomIn(self):
        self.Freeze()
        x = self.screenToCanvasX(self.ClientSize.width / 2)
        y = self.screenToCanvasY(self.ClientSize.height / 2)
        self.zoom *= 1.2
        self.centerCanvasOnScreen(x, y)
        self.Thaw()

    def CanZoomOut(self) -> bool:
        return self.zoom > self._minZoom

    def ZoomOut(self):
        self.Freeze()
        x = self.screenToCanvasX(self.ClientSize.width / 2)
        y = self.screenToCanvasY(self.ClientSize.height / 2)
        self.zoom *= 0.8
        self.centerCanvasOnScreen(x, y)
        self.Thaw()

    def CanZoom100(self) -> bool:
        return self.zoom != 1.0

    def Zoom100(self):
        self.Freeze()
        x = self.screenToCanvasX(self.ClientSize.width / 2)
        y = self.screenToCanvasY(self.ClientSize.height / 2)
        self.zoom = 1.0
        self.centerCanvasOnScreen(x, y)
        self.Thaw()

    # tool handling -----------------------------------------------------------

    def _initTools(self):
        self.tools["ToolEdit"] = ToolEdit(self)
        self.tools["ToolDraw"] = ToolDraw(self)
        self.tools["ToolZoom"] = ToolZoom(self)
        self.tools["ToolPan"] = ToolPan(self)
        self.tools["MagicWand"] = MagicWand(self)
        self.tools["AddRectangle"] = AddRectangle(self)
        self.tools["AddEllipse"] = AddEllipse(self)
        self.tools["ToolRotate"] = ToolRotate(self)
        self.tools["ToolScale"] = ToolScale(self)
        self.tools["ToolErase"] = ToolErase(self)
        self.tools["ToolMeter"] = ToolMeter(self)
        self.tools["ToolKnife"] = ToolKnife(self)
        self.tools["ToolStartpoint"] = ToolStartpoint(self)
        self.tools["ToolReverse"] = ToolReverse(self)
        # self._tool = "ToolEdit"
        # self._prevTool = "ToolEdit"
        self.tools[self._tool].activate()

    @property
    def currentTool(self) -> GlyphTool:
        return self.tools[self._tool]

    def has_Tool(self, name: str) -> bool:
        return name in self.tools

    def getTool(self, name:str) -> Optional[GlyphTool]:
        return self.tools.get(name)

    def isToolActive(self, name:str) -> bool:
        """
        Is the tool with the given name active?
        """
        return self._tool == name

    def selectTool(self, name:str) -> None:
        """
        Select the tool given by name.
        """
        if name in self.tools and name != self._tool:
            self.tools[self._tool].activate(False)
            self._prevTool = self._tool
            self._tool = name
            self.tools[self._tool].activate(True)

    def unselectTool(self) -> None:
        """
        Unselect the current tool and reselect the previus one.
        """
        self.tools[self._tool].activate(False)
        self._tool = self._prevTool
        self.tools[self._tool].activate(True)
        self._prevTool = "ToolEdit"

    # # command handling -----------------------------------------------------------

    # def has_GlyphCommand(self, commandName):
    #     return commandName in self.glyphCommands

    # def applyGlyphCommand(self, commandName):
    #     if commandName in self.glyphCommands:
    #         wx.LogWarning('Glyph Command "%s" not yet implemented' % commandName)

    # calculate canvas coordinates to screen coordinates ------------------------

    @property
    def ViewStart(self):
        return self.GetViewStart()

    def canvasToScreenX(self, value) -> int:
        return int(round((value + self.canvasOrigin.x) * self.zoom - self.ViewStart[0]))

    def canvasToScreenXrel(self, value) -> int:
        return int(round(value * self.zoom))

    def canvasToScreenY(self, value) -> int:
        return int(
            round((value - self.canvasOrigin.y) * -self.zoom - self.ViewStart[1])
        )

    def canvasToScreenYrel(self, value) -> int:
        return int(round(value * -self.zoom))

    # calculate screen coordinates to canvas coordinates ------------------------

    def screenToCanvasX(self, value) -> float:
        return (value + self.ViewStart[0]) / self.zoom - self.canvasOrigin.x

    def screenToCanvasXrel(self, value) -> float:
        return value / self.zoom

    def screenToCanvasY(self, value) -> float:
        return self.canvasOrigin.y + (value + self.ViewStart[1]) / -self.zoom

    def screenToCanvasYrel(self, value) -> float:
        return value / -self.zoom

    # scroll the canvas ---------------------------------------------------------

    def moveCanvasOnScreen(self, canvas_x, canvas_y, screen_x, screen_y):
        """
        Try to scroll canvas position (canvas_x, canvas_y) [drawing units]
        to screen position (screen_x, screen_y) [Screen pixes]
        """
        dx = self.screenToCanvasX(screen_x) - canvas_x
        dy = self.screenToCanvasY(screen_y) - canvas_y
        self.Scroll(
            self.ViewStart[0] - self.canvasToScreenXrel(dx),
            self.ViewStart[1] - self.canvasToScreenYrel(dy),
        )
        self.Refresh()
        self.updateRuler()

    def centerCanvasOnScreen(self, canvas_x, canvas_y):
        self.moveCanvasOnScreen(
            canvas_x, canvas_y, self.ClientSize.x / 2, self.ClientSize.y / 2
        )

    def updateRuler(self):
        self.Parent.rulerTop.Refresh()
        self.Parent.rulerLeft.Refresh()

    # -------------------------------------------------------------------------
    # Event handler methods
    # -------------------------------------------------------------------------

    def on_ENTER_WINDOW(self, event):
        if self.glyph is not None and isinstance(self.currentTool, ToolEdit):
            planes = self.getActiveDrawingPlaneStack()
            if planes and planes["GlyphGuide"].locked:
                event.Skip()
                return
            guidelineParent = None
            if self.Parent.rulerTop.createGuideline:
                angle = 0
                guidelineParent = self.Parent.rulerTop.createGuideline
                self.Parent.rulerTop.createGuideline = None
            elif self.Parent.rulerLeft.createGuideline:
                angle = 90
                guidelineParent = self.Parent.rulerLeft.createGuideline
                self.Parent.rulerLeft.createGuideline = None
            else:
                event.Skip()
                return
            guideline = Guideline(
                guidelineDict=dict(
                    x=round(self.screenToCanvasX(event.X)),
                    y=round(self.screenToCanvasY(event.Y)),
                    angle=angle,
                )
            )
            if guidelineParent == "Glyph":
                glyph = self.glyph
                glyph.undoManager.saveState()
                glyph.disableNotifications()
                glyph.appendGuideline(guideline)
            elif guidelineParent == "Font":
                self.font.appendGuideline(guideline)
            planes["GlyphGuide"].visibleActive = True
            self.fontLevelPlanesStack["FontGuide"].visible = True
            tool = self.currentTool
            tool.unselectAll()
            tool.state = WORKING
            tool.subject = guideline
            if not self.HasCapture():
                self.CaptureMouse()
            self.SetFocus()
        event.Skip()

    def on_SET_FOCUS(self, event:wx.FocusEvent):
        if self.app.documentManager.currentView != self.view:
            wx.LogDebug(
                f"{self} on_SET_FOCUS: {self.app.documentManager.currentView} {self.view}"
            )
            self.view.Activate()
        event.Skip()

    def on_SIZE(self, event:wx.SizeEvent):
        self.Refresh()
        event.Skip()

    def on_SCROLLWIN(self, event):
        self.Refresh()
        self.updateRuler()
        event.Skip()

    def on_MOUSE_CAPTURE_LOST(self, event):
        self.ReleaseMouse()
        self.Refresh()
        event.Skip()

    def on_MOUSEWHEEL(self, event:wx.MouseEvent):
        if event.AltDown():
            val = event.GetWheelRotation()
            canvas_x = self.screenToCanvasX(event.GetX())
            canvas_y = self.screenToCanvasY(event.GetY())
            self.Freeze()
            if val > 0:
                self.zoom *= 1.2
            else:
                self.zoom *= 0.8
            self.moveCanvasOnScreen(canvas_x, canvas_y, event.GetX(), event.GetY())
            self.Thaw()
        event.Skip()

    def OnPaint(self, event:wx.PaintEvent):
        self.transform = (
            Transform()
            .translate(-self.ViewStart[0], -self.ViewStart[1])
            .scale(self.zoom, -self.zoom)
            .translate(self.canvasOrigin.x, -self.canvasOrigin.y)
        )
        bitmap = wx.Bitmap(self.ClientSize.width, self.ClientSize.height)
        dc = wx.BufferedPaintDC(self, bitmap)
        self.OnDraw(dc)

    def OnDraw(self, dc: wx.BufferedPaintDC):
        use_cairo = False
        activePlaneStack = self.getActiveDrawingPlaneStack()
        backgroundColour = wx.WHITE
        if activePlaneStack.layer.color:
            hue = activePlaneStack.layer.color.hue
            backgroundColour = Color.from_hsv(hue, 0.05, 1.0).wx
        dc.SetBackground(wx.TheBrushList.FindOrCreateBrush(backgroundColour))
        dc.Clear()
        if use_cairo:
            wxdir = os.path.dirname(wx.__file__) + os.pathsep
            if not wxdir in os.environ.get("PATH", ""):
                os.environ["PATH"] = wxdir + os.environ.get("PATH", "")
            gcr = wx.GraphicsRenderer.GetCairoRenderer()
            print(gcr)
            gc = gcr.CreateContext(dc)
        else:
            gc = wx.GraphicsContext.Create(dc)
        if self.displayMode == DISPLAY_NORMAL:
            # first: draw all visible and inactive PlaneStacks in backgroud
            for plane in [
                p for p in self.drawingPlanes if (p.visible and not p.active)
            ]:
                plane.draw(gc)
            # second: draw the active PlaneStack in foreground
            activePlaneStack.draw(gc)
            # third: let the current tool draw it's stuff
            self.currentTool.draw(gc)
        elif self.displayMode == DISPLAY_PREVIEW:
            glyphFill = activePlaneStack.get("GlyphFill")
            glyphFill.draw(gc)

    def on_KEY_DOWN(self, event: wx.KeyEvent):
        """
        Handle key down event
        """
        alt = event.AltDown()
        # cmd = event.CmdDown()
        ctrl = event.ControlDown()
        shift = event.ShiftDown()
        unicodeKey = event.GetUnicodeKey()
        if unicodeKey == wx.WXK_NONE:
            key = event.KeyCode
        else:
            key = chr(unicodeKey)
        if key == " ":  # Space pressed
            if not alt | ctrl | shift:
                self.selectTool("ToolPan")
            elif ctrl and not alt | shift:
                self.selectTool("ToolZoom")
        elif key == "Q":
            self.selectTool("ToolErase")
        elif key == "W":
            self.selectTool("ToolKnife")
        elif key == "T":
            self.selectTool("ToolMeter")
        elif key == "R":
            self.selectTool("AddRectangle")
        elif key == "E":
            self.selectTool("AddEllipse")
        elif key == "-" and not ctrl:
            self.Zoom100()
        elif key in ("+", wx.WXK_NUMPAD_ADD) and ctrl:
            self.ZoomIn()
        elif key in ("-", wx.WXK_NUMPAD_SUBTRACT) and ctrl:
            self.ZoomOut()
        elif key == "<" and self.displayMode == DISPLAY_NORMAL:
            self.displayMode = DISPLAY_PREVIEW
            self.Refresh()
        elif key == ",":
            self.showPreviousGlyph()
        elif key == ".":
            self.showNextGlyph()
        elif key == wx.WXK_CONTROL:
            if ctrl and not (alt | shift) and self.isToolActive("ToolPan"):
                self.selectTool("ToolZoom")
            elif ctrl and not alt and self.isToolActive("ToolEdit"):
                self.selectTool("MagicWand")
        elif key == wx.WXK_ALT:
            event.StopPropagation()
        if not alt:
            event.Skip()

    def on_KEY_UP(self, event: wx.KeyEvent):
        """
        Handle key up event
        """
        # alt = event.AltDown()
        # cmd = event.CmdDown()
        # ctrl = event.ControlDown()
        # shift = event.ShiftDown()
        unicodeKey = event.GetUnicodeKey()
        if unicodeKey == wx.WXK_NONE:
            key = event.KeyCode
        else:
            key = chr(unicodeKey)
        if key == " ":  # Space released
            if self.isToolActive("ToolPan"):
                self.unselectTool()
            if self.isToolActive("ToolZoom"):
                self.unselectTool()
        elif key in ("Q", "W", "E", "R", "T"):
            self.unselectTool()
        elif key == "<" and self.displayMode == DISPLAY_PREVIEW:
            self.displayMode = DISPLAY_NORMAL
            self.Refresh()
        elif key == wx.WXK_CONTROL:
            if self.isToolActive("ToolZoom"):
                self.unselectTool()
            if self.isToolActive("MagicWand"):
                self.unselectTool()
        elif key == wx.WXK_ALT:
            self.SetFocus()
            event.StopPropagation()
            return
        event.Skip()
