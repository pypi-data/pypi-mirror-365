"""
applyGlyphConstructionDialog
===============================================================================
"""
import wx

from wbDefcon import Color

from .applyGlyphConstructionDialogUI import ApplyGlyphConstructionDialogUI


class ApplyGlyphConstructionDialog(ApplyGlyphConstructionDialogUI):
    def __init__(self):
        super().__init__(wx.GetApp().TopWindow)

    def update_SaveOutline(self, event):
        event.Enable(self.checkBox_ReplaceOutline.Value)

    def update_Mark(self, event):
        event.Enable(self.checkBox_Mark.Value)

    @property
    def constructionPath(self):
        return self.filePicker_ConstructionPath.GetPath()

    @property
    def newGlyphs(self):
        return self.checkBox_NewGlyphs.Value

    @property
    def replaceOutline(self):
        return self.checkBox_ReplaceOutline.Value

    @property
    def saveOutline(self):
        return self.checkBox_ReplaceOutline.Value and self.checkBox_SaveOutline.Value

    @property
    def replaceComposite(self):
        return self.checkBox_ReplaceComposite.Value

    @property
    def markColor(self):
        if self.checkBox_Mark.Value:
            return Color.from_wx(self.colourPicker_Mark.Colour)
