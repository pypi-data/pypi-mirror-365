"""
selectFontsDialog
===============================================================================
"""
import wx
from .. import CurrentFont, AllFonts

from .selectFontsDialogUI import SelectFontsDialogUI


class SelectFontsDialog(SelectFontsDialogUI):
    def __init__(self, message="Select fonts:", title="UFO Workbench", allFonts=None):
        if allFonts is None:
            allFonts = AllFonts()
        self.allFonts = allFonts
        super().__init__(wx.GetApp().TopWindow)
        self.Title = title
        self.label_message.Label = message
        self.sdbSizerOK.SetDefault()
        fontList = self.listCtrl_fonts
        currentFont = CurrentFont()
        for i in range(fontList.ItemCount):
            if fontList.allFonts[i] == currentFont:
                fontList.SetItemState(i, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
        
    @property
    def selectedFonts(self):
        return self.listCtrl_fonts.getSelectedFonts()

    def on_KEY_DOWN(self, event):
        unicodeKey = event.GetUnicodeKey()
        if unicodeKey != wx.WXK_NONE:
            key = chr(unicodeKey)
            if key == "A" and (event.ControlDown() or event.CmdDown()):
                fontList = self.listCtrl_fonts
                for i in range(fontList.ItemCount):
                    fontList.SetItemState(
                        i, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED
                    )
                self.sdbSizerOK.SetFocus()
            else:
                event.Skip()
        else:
            event.Skip()

