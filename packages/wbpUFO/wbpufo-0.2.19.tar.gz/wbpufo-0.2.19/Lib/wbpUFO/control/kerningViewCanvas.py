"""
kerningViewCanvas
===============================================================================
"""
import logging

import wx
from fontTools.misc.transform import Transform
from fontTools.pens.transformPen import TransformPen
from wbDefcon import Glyph
from wbDefcon.pens import graphicsPen

log = logging.getLogger(__name__)

class KerningViewCanvas(wx.ScrolledWindow):
    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.ALWAYS_SHOW_SB | wx.HSCROLL | wx.VSCROLL,
    ):
        super().__init__(parent, id=id, pos=pos, size=size, style=style, name="KerningViewCanvas")
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.SetBackgroundColour("WHITE")
        self._glyphs = []
        self.glyphPositions = [(0, self.linespace)]
        self._caretIndex = 0
        # Connect Events
        # window events
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SCROLLWIN, self.on_SCROLLWIN)
        # mouse events
        self.Bind(wx.EVT_MOUSEWHEEL, self.on_MOUSEWHEEL)

    # --------------------------------------------------------------------------
    # Properties
    # --------------------------------------------------------------------------

    @property
    def fontsize(self):
        return self.Parent.fontsize

    @fontsize.setter
    def fontsize(self, value):
        self.Parent.fontsize = value

    @property
    def linespace(self):
        return self.Parent.fontsize * self.Parent.linespace / 100

    @property
    def descender(self):
        return self.linespace - self.fontsize

    @property
    def glyphs(self):
        for glyph in self._glyphs:
            yield glyph

    @property
    def glyphCount(self):
        return len(self._glyphs)

    # --------------------------------------------------------------------------
    # Public Methods
    # --------------------------------------------------------------------------

    def insertGlyph(self, index, glyph):
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
            self._glyphs.insert(index, _glyph)
            self.caretIndex = index + 1
            self.SetFocus()

    def appendGlyph(self, glyph):
        self.insertGlyph(self.glyphCount, glyph)

    def insertGlyphAtCaret(self, glyph):
        self.insertGlyph(self.caretIndex, glyph)

    def clearGlyphs(self):
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
            if self.caretIndex >= index:
                self.caretIndex -= 1
            self.Refresh()
            self.SetFocus()
            return glyph

    def handleNotification(self, notification):
        log.debug("handleNotification: %r", notification)
        self.Refresh()

    # =================================================================
    # Event Handlers
    # =================================================================

    def on_SCROLLWIN(self, event):
        self.Refresh()
        event.Skip()

    def OnDraw(self, dc):
        dc.SetBackground(wx.TheBrushList.FindOrCreateBrush(self.GetBackgroundColour()))
        dc.Clear()
        gc = wx.GraphicsContext.Create(dc)
        gc.SetBrush(wx.BLACK_BRUSH)
        gc.SetPen(wx.TRANSPARENT_PEN)
        for i, glyph in enumerate(self.glyphs):
            if glyph == "\n":
                continue
            scale = self.fontsize / glyph.font.info.unitsPerEm
            graphicsPen.path = gc.CreatePath()
            graphicsPen.glyphSet = glyph.layer
            transform = (
                Transform().translate(*self.glyphPositions[i]).scale(scale, -scale)
            )
            pen = TransformPen(graphicsPen, transform)
            glyph.draw(pen)
            gc.FillPath(graphicsPen.path, wx.WINDING_RULE)

    def on_MOUSEWHEEL(self, event):
        if event.AltDown():
            value = event.GetWheelRotation()
            fontsize = self.fontsize
            if value > 0:
                fontsize += 5
            else:
                fontsize -= 5
            self.fontsize = fontsize
        event.Skip()
