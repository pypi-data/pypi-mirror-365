"""
deleteGlyphsDialog
===============================================================================
"""
import wx

from .deleteGlyphsDialogUI import DeleteGlyphsDialogUI


class DeleteGlyphsDialog(DeleteGlyphsDialogUI):
    def __init__(self, glyphCount):
        super().__init__(parent=wx.GetApp().TopWindow)
        self.lbl_message.SetLabelMarkup(
            f"Delete {glyphCount} selected glyphs - No Undo!"
        )

    @property
    def component_handling(self):
        if self.radioBtn_decompose.Value:
            return "decompose"
        return "remove"
