import os
import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin


class FontSelectListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.LC_REPORT | wx.LC_VIRTUAL,
        validator=wx.DefaultValidator,
        name="FontSelectListCtrl",
    ):
        wx.ListCtrl.__init__(self, parent, id, pos, size, style, validator, name)
        ListCtrlAutoWidthMixin.__init__(self)
        self.InsertColumn(0, "Font")
        self.InsertColumn(1, "Path")
        self.SetColumnWidth(0, 200)
        self.allFonts = self.Parent.allFonts
        self.SetItemCount(len(self.allFonts))

    @property
    def app(self):
        return wx.GetApp()

    def getSelectedFonts(self):
        fonts = []
        for i in range(self.ItemCount):
            if self.GetItemState(i, wx.LIST_STATE_SELECTED):
                fonts.append(self.allFonts[i])
        return fonts

    def OnGetItemText(self, item, col):
        font = self.allFonts[item]
        if col == 0:
            return f"{font.info.familyName} {font.info.styleName}"
        if col == 1:
            if font.path:
                return font.path
            return "Not saved yet"

