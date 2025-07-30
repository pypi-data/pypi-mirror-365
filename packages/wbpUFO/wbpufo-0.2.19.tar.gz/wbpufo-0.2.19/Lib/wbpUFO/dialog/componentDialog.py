"""
componentDialog
===============================================================================
"""

import wx

from .componentDialogUI import ComponentDialogUI
from .findGlyphDialog import FindGlyphDialog


class ComponentDialog(ComponentDialogUI):
    def __init__(self, parent, component):
        super().__init__(parent)
        self.sizerDlgButtonsOK.SetDefault()
        self.layer = component.layer
        self.baseGlyph = component.baseGlyph
        self.offset = component.offset
        self.scale = component.scale

    @property
    def baseGlyph(self):
        return self.textCtrl_name.Value

    @baseGlyph.setter
    def baseGlyph(self, value):
        self.textCtrl_name.Value = value

    @property
    def offset(self):
        x = self.spinCtrl_pos_x.Value
        y = self.spinCtrl_pos_y.Value
        return x, y

    @offset.setter
    def offset(self, value):
        x, y = value
        self.spinCtrl_pos_x.Value = round(x)
        self.spinCtrl_pos_y.Value = round(y)
        # 		print 'set offset', x, y

    @property
    def scale(self):
        x = self.spinCtrl_scale_x.Value
        y = self.spinCtrl_scale_y.Value
        return x / 100.0, y / 100.0

    @scale.setter
    def scale(self, value):
        x, y = value
        self.spinCtrl_scale_x.Value = round(x * 100.0)
        self.spinCtrl_scale_y.Value = round(y * 100.0)

    def on_button_name(self, event):
        with FindGlyphDialog(self, self.layer) as findGlyphDialog:
            # findGlyphDialog.layer = self.layer
            if (
                findGlyphDialog.ShowModal() == wx.ID_OK
                and findGlyphDialog.selctedGlyph is not None
            ):
                self.baseGlyph = findGlyphDialog.selctedGlyph

