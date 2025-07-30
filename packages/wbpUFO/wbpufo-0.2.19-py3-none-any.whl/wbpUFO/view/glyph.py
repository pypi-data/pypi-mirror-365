from __future__ import annotations

import logging
import os
import weakref
from typing import TYPE_CHECKING, Optional

import wx
from wbBase.document import dbg
from wbBase.document.notebook import DocumentPageMixin
from wbBase.document.view import View
from wbDefcon import Font, Glyph

from ..control.glyphEditor.editPanel import GlyphEditPanel

if TYPE_CHECKING:
    from ..control.glyphEditor.canvas import Canvas
    from ..document import UfoDocument

log = logging.getLogger(__name__)


class UfoGlyphWindow(wx.Notebook, DocumentPageMixin):
    # canvas: Canvas
    document: UfoDocument

    def __init__(self, parent, doc: UfoDocument, view: UfoGlyphView):
        wx.Notebook.__init__(
            self,
            parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.NB_FIXEDWIDTH | wx.NO_BORDER,
            name="UfoGlyphWindow",
        )
        DocumentPageMixin.__init__(self, doc, view)
        self._glyph = None
        self._font = None
        # canvas page
        self.editPanel = GlyphEditPanel(self, doc=doc)
        # self.canvas = self.editPanel.canvas  # is this realy needed?
        self.AddPage(self.editPanel, "Canvas", False)

        self.Layout()
        self.font = self.document.font

    @property
    def canvas(self) -> Canvas:
        """
        The canvas control of this window.
        """
        return self.editPanel.canvas

    @property
    def metric(self) -> Canvas:
        """
        The Glyph Metric control of this window.
        """
        return self.editPanel.metric

    @property
    def font(self) -> Optional[Font]:
        """
        The font associated with this window.
        """
        if self._font is None:
            return None
        return self._font()

    @font.setter
    def font(self, font: Font):
        assert isinstance(font, Font)
        assert self._font is None
        self.canvas.font = font
        self._font = weakref.ref(font)

    @font.deleter
    def font(self):
        del self.canvas.font
        self._font = None

    @property
    def glyph(self) -> Optional[Glyph]:
        """
        The glyph associated with this window.
        """
        return self._glyph

    @glyph.setter
    def glyph(self, glyph: Glyph):
        dbg(f"UfoGlyphWindow set glyph {glyph}")
        if glyph is None:
            del self.glyph
            return
        assert isinstance(glyph, Glyph)
        assert glyph.font == self.font
        if self.glyph != glyph:
            del self.glyph
            glyph.addObserver(self, "handleNotification", "Glyph.NameChanged")
            self.canvas.glyph = glyph
            self.metric.glyph = glyph
            self._glyph = glyph
            # self.title = "Glyph - %s" % glyph.name
            if self.font.path:
                self.title = (
                    f"Glyph - {glyph.name} of {os.path.basename(self.font.path)}"
                )
            else:
                self.title = f"Glyph - {glyph.name}"

    @glyph.deleter
    def glyph(self):
        if isinstance(self._glyph, Glyph):
            self._glyph.removeObserver(self, "Glyph.NameChanged")
        del self.canvas.glyph
        del self.metric.glyph
        self._glyph = None

    def handleNotification(self, notification):
        if notification.name == "Glyph.NameChanged":
            if self.font.path:
                self.title = f"Glyph - {notification.data['newValue']} of {os.path.basename(self.font.path)}"
            else:
                self.title = f"Glyph - {notification.data['newValue']}"

    def Destroy(self):
        # self.canvas = None
        self.editPanel.Destroy()
        return super().Destroy()


class UfoGlyphView(View):
    """
    View component of the UFO Glyph editor.
    """
    frameType = UfoGlyphWindow
    typeName = "UFO Glyph View"
    _frame: UfoGlyphWindow
    frame: UfoGlyphWindow

    @staticmethod
    def getIcon() -> wx.Bitmap:
        return wx.ArtProvider.GetBitmap("G", wx.ART_FRAME_ICON)

    @property
    def font(self) -> Optional[Font]:
        """
        The font associated with this view.
        """
        if self._document and self._document._data:
            return self._document._data
        return None

    @property
    def glyph(self) -> Optional[Glyph]:
        """
        The glyph associated with this view.
        """
        if self._frame:
            return self._frame.glyph
        return None

    @glyph.setter
    def glyph(self, glyph: Glyph):
        dbg(f"UfoGlyphView set glyph {glyph}")
        if glyph is None:
            del self.glyph
            return
        assert isinstance(glyph, Glyph)
        assert glyph.font == self.font
        if self.glyph != glyph:
            del self.glyph
            self._frame.glyph = glyph

    @glyph.deleter
    def glyph(self):
        del self._frame.glyph

    def OnCreate(self, doc: UfoDocument, flags: int):
        dbg(f'UfoGlyphView.OnCreate(doc="{doc}", flags={flags})', indent=1)
        self._document = doc
        self._frame = self.frameType(self.documentNotebook, doc, self)
        self.documentNotebook.AddPage(
            self._frame,
            doc.printableName,
            True,
            self.getIcon()
        )
        dbg(indent=0)
        return True

    def Destroy(self):
        dbg("UfoGlyphView.Destroy", indent=1)
        super().Destroy()
        dbg(indent=0)
