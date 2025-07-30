from __future__ import annotations

import logging
import pickle
from typing import TYPE_CHECKING, Iterator, List, Optional, Tuple, Union

import wx
from fontTools.misc.transform import Transform
from fontTools.pens.transformPen import TransformPen
from wbDefcon import Font, Glyph
from wbDefcon.pens import graphicsPen
from wbFontParts import RGlyph
from wbBase.tools import get_wxBrush

from ..document import UfoDocument

if TYPE_CHECKING:
    from wbBase.application import App
    from wbDefcon import Info
    from .glyphViewPanel import GlyphViewPanel

    DragResult = int

log = logging.getLogger(__name__)


class GlyphViewCanvasDropTarget(wx.DropTarget):
    """
    DropTarget to handle dropped glyphs
    """

    DataObject: wx.CustomDataObject

    def __init__(self, canvas: GlyphViewCanvas):
        super().__init__()
        self.canvas: GlyphViewCanvas = canvas
        self.SetDataObject(wx.CustomDataObject("application.UFO-WB.glyphNames"))
        self.SetDefaultAction(wx.DragCopy)

    @property
    def app(self) -> App:
        return wx.GetApp()

    def OnEnter(self, x, y, defResult: DragResult):
        self.canvas.SetFocus()
        return defResult

    def OnDragOver(self, x, y, defResult: DragResult):
        self.canvas.setCaretPosition(x, y)
        return defResult

    def OnDrop(self, x: int, y: int) -> bool:
        return True

    def OnData(self, x, y, defResult: DragResult) -> DragResult:
        if self.GetData():
            glyphNameData = self.DataObject.GetData()
            if glyphNameData:
                glyphNameDict = pickle.loads(glyphNameData)
                font = None
                for doc in [
                    d
                    for d in self.app.documentManager.documents
                    if isinstance(d, UfoDocument)
                ]:
                    if id(doc.font) == glyphNameDict["font"]:
                        font = doc.font
                        break
                if not font:
                    return wx.DragError
                for glyph in [font[g] for g in glyphNameDict["glyphs"] if g in font]:
                    self.canvas.insertGlyphAtCaret(glyph)
                return defResult
        return wx.DragNone


class GlyphViewCanvas(wx.ScrolledWindow):
    """
    Canvas to draw glyphs on.
    """

    Parent: GlyphViewPanel
    refreshNotifications = (
        "Glyph.Changed",
        "Glyph.WidthChanged",
        "Glyph.ContoursChanged",
        "Glyph.ComponentsChanged",
        "Glyph.ComponentBaseGlyphDataChanged",
    )

    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.ALWAYS_SHOW_SB | wx.HSCROLL | wx.VSCROLL,
    ):
        super().__init__(parent, id=id, pos=pos, size=size, style=style)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.SetBackgroundColour("WHITE")
        self.SetDropTarget(GlyphViewCanvasDropTarget(self))
        self._glyphs: List[Union[str, Glyph]] = []
        self.glyphPositions: List[Tuple[int, int]] = [(0, self.linespace)]

        # set caret
        self.Caret = wx.Caret(self, 2, self.linespace)
        self._caretIndex: int = 0
        self.Caret.Move(self.glyphPositions[self.caretIndex])
        self.Caret.Show()

        # Connect Events
        # window events
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SCROLLWIN, self.on_SCROLLWIN)
        # keyboard events
        self.Bind(wx.EVT_KEY_DOWN, self.on_KEY_DOWN)
        self.Bind(wx.EVT_CHAR, self.on_CHAR)

        # mouse events
        self.Bind(wx.EVT_LEFT_DOWN, self.on_LEFT_DOWN)
        self.Bind(wx.EVT_LEFT_UP, self.on_LEFT_UP)
        self.Bind(wx.EVT_LEFT_DCLICK, self.on_LEFT_DCLICK)
        self.Bind(wx.EVT_MOUSEWHEEL, self.on_MOUSEWHEEL)

    @property
    def app(self) -> App:
        return wx.GetApp()

    @property
    def fontsize(self) -> int:
        return round(self.Parent.fontsize)

    @fontsize.setter
    def fontsize(self, value: int):
        self.Parent.fontsize = int(value)

    @property
    def linespace(self) -> int:
        return round(self.Parent.fontsize * self.Parent.linespace / 100)

    @property
    def descender(self) -> int:
        return self.linespace - self.fontsize

    @property
    def showKerning(self) -> bool:
        return self.Parent.checkBox_showKerning.Value

    @property
    def glyphs(self) -> Iterator[Union[str, Glyph]]:
        self.checkGlyphs()
        for glyph in self._glyphs:
            yield glyph

    @property
    def glyphCount(self) -> int:
        """
        :return: Number of glyphs shown on the canvas, incl. line breaks
        """
        self.checkGlyphs()
        return len(self._glyphs)

    @property
    def caretIndex(self) -> int:
        """
        :return: Index of the current cursor position
        """
        return self._caretIndex

    @caretIndex.setter
    def caretIndex(self, value: int) -> None:
        self._caretIndex = abs(int(value))
        self.Refresh()

    @property
    def currentFont(self) -> Optional[Font]:
        """
        :return: Font at the current cursor position
        """
        self.checkGlyphs()
        if not self._glyphs:
            doc = self.app.documentManager.currentDocument
            if isinstance(doc, UfoDocument):
                return doc.font
            return None
        glyph = self._glyphs[max(self._caretIndex - 1, 0)]
        if self._caretIndex == 0 and isinstance(glyph, Glyph):
            return glyph.font
        for index in reversed(range(self._caretIndex)):
            glyph = self._glyphs[index]
            if isinstance(glyph, Glyph):
                return glyph.font
        return None

    @property
    def fonts(self) -> Tuple[Font]:
        self.checkGlyphs()
        _fonts = []
        for glyph in self._glyphs:
            if (
                isinstance(glyph, Glyph)
                and glyph.font is not None
                and glyph.font not in _fonts
            ):
                _fonts.append(glyph.font)
        return tuple(_fonts)

    def insertGlyph(self, index: int, glyph: Union[str, Glyph]):
        _glyph = None
        if isinstance(glyph, str) and glyph in ("\n", "\r"):
            _glyph = "\n"
        elif isinstance(glyph, Glyph):
            _glyph = glyph
        elif isinstance(glyph, RGlyph):
            _glyph = glyph.naked()
        if _glyph is not None:
            if isinstance(_glyph, Glyph):
                for notificationName in self.refreshNotifications:
                    if not _glyph.hasObserver(self, notificationName):
                        _glyph.addObserver(self, "handleNotification", notificationName)
                if _glyph.font not in self.fonts:
                    _glyph.font.kerning.addObserver(
                        self, "handleNotification", "Kerning.Changed"
                    )
            self._glyphs.insert(index, _glyph)
            self.caretIndex = index + 1
            self.SetFocus()

    def appendGlyph(self, glyph: Union[str, Glyph]):
        self.insertGlyph(self.glyphCount, glyph)

    def insertGlyphAtCaret(self, glyph: Union[str, Glyph]):
        self.insertGlyph(self.caretIndex, glyph)

    def checkGlyphs(self):
        """
        Remove all glyphs from fonts which have been closed
        """
        allFonts = [
            d.font
            for d in self.app.documentManager.documents
            if isinstance(d, UfoDocument)
        ]
        glyphs = []
        for glyph in self._glyphs:
            if isinstance(glyph, str):
                glyphs.append(glyph)
            elif glyph.font in allFonts:
                glyphs.append(glyph)
        if self._glyphs != glyphs:
            self._glyphs = glyphs
            self._caretIndex = 0

    def clearGlyphs(self) -> None:
        for font in self.fonts:
            font.kerning.removeObserver(self, "Kerning.Changed")
        for glyph in self._glyphs:
            if isinstance(glyph, str):
                continue
            for notificationName in self.refreshNotifications:
                glyph.removeObserver(self, notificationName)
        self._glyphs = []
        self.caretIndex = 0

    def popGlyph(self, index):
        if 0 <= index < self.glyphCount:
            glyph = self._glyphs.pop(index)
            if isinstance(glyph, Glyph) and glyph not in self._glyphs:
                for notificationName in self.refreshNotifications:
                    glyph.removeObserver(self, notificationName)
                if glyph.font not in self.fonts:
                    glyph.font.kerning.removeObserver(self, "Kerning.Changed")
            if self.caretIndex >= index:
                self.caretIndex -= 1
            self.Refresh()
            self.SetFocus()
            return glyph
        return None

    def setCaretPosition(self, x: int, y: int) -> None:
        if not self._glyphs:
            self.caretIndex = 0
            return
        self.checkGlyphs()
        view_x, view_y = self.GetViewStart()
        position = wx.Point(x + view_x, y + view_y)
        prev_x = None
        prev_y = None
        for i, (px, py) in enumerate(self.glyphPositions):
            if prev_x is not None and prev_y is not None:
                glyphRect = wx.Rect(
                    round(prev_x),
                    round(py - self.fontsize),
                    round(px - prev_x),
                    round(self.linespace),
                )
                if glyphRect.Top > position.y:
                    self.caretIndex = i - 1
                    return
                if glyphRect.Contains(position):
                    self.caretIndex = i - 1
                    return
            prev_x = px
            prev_y = py
        self.caretIndex = self.glyphCount

    def handleNotification(self, notification):
        log.debug("handleNotification: %r", notification)
        self.Refresh()

    def Refresh(self) -> None:
        self.Caret.SetSize(2, self.linespace)
        super().Refresh()

    # =================================================================
    # event handlers
    # =================================================================

    def on_SCROLLWIN(self, event):
        self.Refresh()
        event.Skip()

    def OnPaint(self, event: wx.PaintEvent) -> None:
        self.checkGlyphs()
        width, height = self.ClientSize
        current_x = 0
        current_y = self.fontsize
        self.glyphPositions.clear()
        self.glyphPositions.append((current_x, current_y))
        prev_glyph = None
        scale = 1
        for glyph in self._glyphs:
            if isinstance(glyph, Glyph) and glyph.font is not None:
                font = glyph.font
                if isinstance(font, Font):
                    info: Info = font.info
                    scale = self.fontsize / info.unitsPerEm
                    if (
                        isinstance(prev_glyph, Glyph)
                        and self.showKerning
                        and font == prev_glyph.font
                    ):
                        kernValue = font.kerning.find((prev_glyph.name, glyph.name))
                        if kernValue:
                            prev_x, prev_y = self.glyphPositions[-1]
                            prev_x += kernValue * scale
                            self.glyphPositions[-1] = (prev_x, prev_y)
                            current_x += round(kernValue * scale)
                glyphWidth = glyph.width * scale
                current_x += glyphWidth
            elif glyph == "\n":
                current_x = 0
                current_y += self.linespace
                prev_glyph = None

            width = max(width, current_x)
            height = max(height, current_y + self.descender)
            self.glyphPositions.append((current_x, current_y))
            prev_glyph = glyph
        self.VirtualSize = (width, height)
        caret_x, caret_y = self.glyphPositions[self.caretIndex]
        caret_y -= self.fontsize
        view_x, view_y = self.GetViewStart()
        caret_x -= view_x
        caret_y -= view_y
        self.Caret.Move(round(caret_x), round(caret_y))
        bitmap = wx.Bitmap(self.VirtualSize.width, self.VirtualSize.height)
        dc = wx.BufferedPaintDC(self, bitmap, wx.BUFFER_VIRTUAL_AREA)
        self.OnDraw(dc)

    def OnDraw(self, dc: wx.BufferedPaintDC) -> None:
        dc.SetBackground(get_wxBrush(self.GetBackgroundColour()))
        dc.Clear()
        gc: wx.GraphicsContext
        gc = wx.GraphicsContext.Create(dc)
        gc.SetBrush(wx.BLACK_BRUSH)
        gc.SetPen(wx.TRANSPARENT_PEN)
        for i, glyph in enumerate(self.glyphs):
            if isinstance(glyph, Glyph):
                scale = 1
                font = glyph.font
                if isinstance(font, Font):
                    scale = self.fontsize / font.info.unitsPerEm
                graphicsPen.path = gc.CreatePath()
                graphicsPen.glyphSet = glyph.layer
                transform = (
                    Transform().translate(*self.glyphPositions[i]).scale(scale, -scale)
                )
                pen = TransformPen(graphicsPen, transform)
                try:
                    glyph.draw(pen)
                    gc.FillPath(graphicsPen.path, wx.WINDING_RULE)
                except TypeError:
                    log.error("Can't draw glyph %r", glyph)

    def on_KEY_DOWN(self, event: wx.KeyEvent):
        # alt = event.AltDown()
        # cmd = event.CmdDown()
        # ctrl = event.ControlDown()
        # shift = event.ShiftDown()
        unicodeKey = event.GetUnicodeKey()
        if unicodeKey in (wx.WXK_NONE, wx.WXK_BACK, wx.WXK_DELETE, wx.WXK_RETURN):
            key = event.KeyCode
        else:
            key = chr(unicodeKey)
        if key == wx.WXK_HOME and self.caretIndex > 0:
            # move cursor home
            self.caretIndex = 0
        elif key == wx.WXK_LEFT:
            # move cursor one char left
            if self.caretIndex <= 0:
                wx.Bell()
                return
            self.caretIndex -= 1
        elif key == wx.WXK_RIGHT:
            # move cursor one char right
            if self.caretIndex >= self.glyphCount:
                wx.Bell()
                return
            self.caretIndex += 1
        elif key == wx.WXK_END and self.caretIndex < self.glyphCount:
            self.caretIndex = self.glyphCount
        elif key == wx.WXK_BACK:
            if self.caretIndex <= 0:
                wx.Bell()
                return
            self.popGlyph(self.caretIndex - 1)
        elif key == wx.WXK_DELETE:
            if self.caretIndex >= self.glyphCount:
                wx.Bell()
                return
            self.popGlyph(self.caretIndex)
        elif key == wx.WXK_RETURN:
            # insert new line at cursor
            self.insertGlyphAtCaret("\n")
        else:
            event.Skip()

    def on_CHAR(self, event: wx.KeyEvent):
        font = self.currentFont
        if font is None:
            wx.Bell()
            return
        glyphNames = font.unicodeData.get(event.GetUnicodeKey())
        if not glyphNames:
            wx.Bell()
            return
        self.insertGlyphAtCaret(font[glyphNames[0]])

    def on_LEFT_DOWN(self, event: wx.MouseEvent):
        self.setCaretPosition(event.GetX(), event.GetY())

    def on_LEFT_UP(self, event: wx.MouseEvent):
        # print("on_LEFT_UP")
        self.SetFocus()
        event.Skip()

    def on_LEFT_DCLICK(self, event: wx.MouseEvent):
        # print("on_LEFT_DCLICK")
        if not self._glyphs:
            return
        glyph = self._glyphs[self.caretIndex]
        if isinstance(glyph, Glyph):
            glyph.font.showGlyph(glyph.name)
        event.Skip()

    def on_MOUSEWHEEL(self, event: wx.MouseEvent):
        if event.AltDown():
            value = event.GetWheelRotation()
            fontsize = self.fontsize
            if value > 0:
                fontsize += 5
            else:
                fontsize -= 5
            self.fontsize = fontsize
        event.Skip()
