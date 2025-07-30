"""
findGlyphDialog
===============================================================================
"""
import logging
import zlib

import wx

from wbDefcon import Font, Layer
from wbFontParts import RFont, RLayer

from .findGlyphDialogUI import FindGlyphDialogUI

log = logging.getLogger(__name__)

###########################################################################
## Class FindGlyphDialog
###########################################################################


class FindGlyphDialog(FindGlyphDialogUI):
    """
    Dialog to search for a glyph in a font or layer.
    """

    def __init__(self, parent, font_or_layer, allowSelection=False):
        super().__init__(parent)
        self.sizerDialogButtonsOK.SetDefault()
        self._layer = None
        self.layer = font_or_layer
        self.glyphnames = self.layer.keys()
        self.characters = {"%04X" % k: v[0] for k, v in self.layer.unicodeData.items()}
        self.dataFind = []
        self.selctedGlyph = None
        self.allowSelection = allowSelection
        self.textCtrl_findValue.SetFocus()

    @property
    def layer(self):
        return self._layer

    @layer.setter
    def layer(self, value):
        if isinstance(value, Font):
            self._layer = value.layers.defaultLayer
        elif isinstance(value, RFont):
            self._layer = value.naked().layers.defaultLayer
        elif isinstance(value, Layer):
            self._layer = value
        elif isinstance(value, RLayer):
            self._layer = value.naked()
        else:
            log.error("got font_or_layer as %r", value)

    def updateFindData(self):
        self.selctedGlyph = None
        self.listCtrl_glyphs.SetItemCount(0)
        text = self.textCtrl_findValue.GetValue()
        if text:
            findAttr = self.choice_findAttr.StringSelection
            findCompare = self.choice_findCompare.StringSelection
            if findAttr == "Name":
                if findCompare == "equals to":
                    self.dataFind = sorted([n for n in self.glyphnames if n == text])
                elif findCompare == "starts with":
                    self.dataFind = sorted(
                        [
                            (n, self.characters.get(n, ""))
                            for n in self.glyphnames
                            if n.startswith(text)
                        ]
                    )
                elif findCompare == "ends with":
                    self.dataFind = sorted(
                        [
                            (n, self.characters.get(n, ""))
                            for n in self.glyphnames
                            if n.endswith(text)
                        ]
                    )
                elif findCompare == "contains":
                    self.dataFind = sorted(
                        [
                            (n, self.characters.get(n, ""))
                            for n in self.glyphnames
                            if text in n
                        ]
                    )
                else:
                    self.dataFind = []
            elif findAttr == "Unicode":
                sortByUni = lambda i: i[1]
                if findCompare == "equals to":
                    self.dataFind = sorted(
                        [(v, k) for k, v in self.characters.items() if k == text],
                        key=sortByUni,
                    )
                elif findCompare == "starts with":
                    self.dataFind = sorted(
                        [
                            (v, k)
                            for k, v in self.characters.items()
                            if k.startswith(text)
                        ],
                        key=sortByUni,
                    )
                elif findCompare == "ends with":
                    self.dataFind = sorted(
                        [
                            (v, k)
                            for k, v in self.characters.items()
                            if k.endswith(text)
                        ],
                        key=sortByUni,
                    )
                elif findCompare == "contains":
                    self.dataFind = sorted(
                        [(v, k) for k, v in self.characters.items() if text in k],
                        key=sortByUni,
                    )
                else:
                    self.dataFind = []
        else:
            self.dataFind = []
        self.listCtrl_glyphs.SetItemCount(len(self.dataFind))
        self.listCtrl_glyphs.SetItemState(
            0, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED
        )

    def _getGlyphBitmap(self, glyph, width=72, height=72, captionHeight=0) -> wx.Bitmap:
        bitmap = wx.Bitmap.FromRGBA(width, height)
        bitmapdata = zlib.decompress(
            glyph.getRepresentation(
                "bitmap",
                width=width,
                height=height,
                captionHeight=captionHeight,
            )
        )
        bitmap.CopyFromBuffer(bitmapdata, wx.BitmapBufferFormat_RGBA)
        return bitmap

    # -------------------------------------------------------------------------
    # Event handler methods
    # -------------------------------------------------------------------------

    def on_TEXT_ENTER(self, event):
        if self.selctedGlyph is not None:
            self.EndModal(wx.ID_OK)

    def onfindAttr_CHOICE(self, event):
        self.updateFindData()

    def onfindCompare_CHOICE(self, event):
        self.updateFindData()

    def on_TEXT(self, event):
        self.updateFindData()

    def on_LIST_ITEM_SELECTED(self, event):
        self.selctedGlyph = self.listCtrl_glyphs.GetItemText(event.Index)
        self.bitmapGlyph.SetBitmap(self._getGlyphBitmap(self.layer[self.selctedGlyph]))
        event.Skip()

    def on_LIST_ITEM_ACTIVATED(self, event):
        self.selctedGlyph = self.listCtrl_glyphs.GetItemText(event.Index)
        self.bitmapGlyph.SetBitmap(self._getGlyphBitmap(self.layer[self.selctedGlyph]))
        if self.selctedGlyph is not None:
            self.EndModal(wx.ID_OK)

    def on_buttonSelect(self, event):
        self.layer.selectedGlyphNames = [i[0] for i in self.dataFind]

    def update_buttonSelect(self, event):
        event.Enable(self.allowSelection and len(self.dataFind) > 0)
