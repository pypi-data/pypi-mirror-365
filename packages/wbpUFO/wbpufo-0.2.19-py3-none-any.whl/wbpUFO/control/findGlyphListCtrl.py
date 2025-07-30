"""
findGlyphListCtrl
===============================================================================
"""

import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin


class FindGlyphListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.LC_NO_HEADER
        | wx.LC_REPORT
        | wx.LC_SINGLE_SEL
        | wx.LC_SORT_ASCENDING
        | wx.LC_VIRTUAL,
        validator=wx.DefaultValidator,
        name="FindGlyphListCtrl",
    ):
        wx.ListCtrl.__init__(self, parent, id, pos, size, style, validator, name)
        self.InsertColumn(0, "Name")
        self.InsertColumn(1, "Unicode")
        ListCtrlAutoWidthMixin.__init__(self)
        self.setResizeColumn(0)
        self.SetItemCount(0)

    def OnGetItemText(self, item, col):
        return self.Parent.dataFind[item][col]

    def getColumnText(self, index, col):
        item = self.GetItem(index, col)
        return item.GetText()
