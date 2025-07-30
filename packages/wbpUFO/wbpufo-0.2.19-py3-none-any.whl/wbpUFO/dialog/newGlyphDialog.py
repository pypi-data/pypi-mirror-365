"""
newGlyphDialog
===============================================================================
"""
import re
import string

import wx

from .newGlyphDialogUI import NewGlyphDialogUI


class GlyphNameValidator(wx.Validator):
    validChars = string.ascii_letters + string.digits + "_."
    validPattern = r"^[a-zA-Z_][a-zA-Z0-9_.]*$"

    def __init__(self):
        super().__init__()
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        return GlyphNameValidator()

    def Validate(self, win):
        textCtrl = self.GetWindow()
        text = textCtrl.GetValue()
        if len(text) == 0:
            wx.MessageBox("Glyph name must not be empty!", "Error")
            textCtrl.SetBackgroundColour("pink")
            textCtrl.SetFocus()
            textCtrl.Refresh()
            return False
        else:
            textCtrl.SetBackgroundColour(
                wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
            )
            textCtrl.Refresh()
            return True

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True

    def OnChar(self, event):
        key = event.GetKeyCode()
        if (
            key < wx.WXK_SPACE
            or key == wx.WXK_DELETE
            or key > 255
            or chr(key) in self.validChars
        ):
            event.Skip()
            return
        if not wx.Validator.IsSilent():
            wx.Bell()
        return


class NewGlyphDialog(NewGlyphDialogUI):
    def __init__(self):
        super().__init__(wx.GetApp().panelManager.documentNotebook)
        self.textCtrl_name.SetValidator(GlyphNameValidator())

    @property
    def glyphname(self):
        if self.textCtrl_name.Value:
            return self.textCtrl_name.Value

    @property
    def unicodes(self):
        if self.textCtrl_unicode.Value:
            return [int(u, 16) for u in self.textCtrl_unicode.Value.split()]
        return []
