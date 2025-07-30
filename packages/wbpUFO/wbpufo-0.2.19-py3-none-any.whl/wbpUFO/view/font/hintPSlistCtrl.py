"""
hintPSlistCtrl
===============================================================================

"""
import wx


class ZoneListCtrl(wx.ListCtrl):
    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_VIRTUAL,
        name="ZoneListCtrl",
    ):
        wx.ListCtrl.__init__(
            self, parent, id=id, pos=pos, size=size, style=style, name=name
        )
        self.EnableAlternateRowColours()
        self.AppendColumn("")
        self.AppendColumn("Bottom", wx.LIST_FORMAT_RIGHT)
        self.AppendColumn("Top", wx.LIST_FORMAT_RIGHT)
        self.AppendColumn("Width", wx.LIST_FORMAT_RIGHT)
        self.SetColumnWidth(0, 0)
        self.SetColumnWidth(1, 90)
        self.SetColumnWidth(2, 90)
        self.SetColumnWidth(3, 90)
        self.SetItemCount(0)

        self.Bind(wx.EVT_SIZE, self.on_Size)

    @property
    def value(self):
        return self.Parent.Value

    def OnGetItemText(self, row, col):
        if col == 0:
            return ""
        if col == 1:
            return str(self.value[row * 2])
        if col == 2:
            return str(self.value[row * 2 + 1])
        if col == 3:
            return str(self.value[row * 2 + 1] - self.value[row * 2])

    def on_Size(self, event):
        self.SetColumnWidth(1, round(self.Size.Width / 3))
        self.SetColumnWidth(2, round(self.Size.Width / 3))
        self.SetColumnWidth(3, round(self.Size.Width / 3))
        event.Skip()


class StemListCtrl(wx.ListCtrl):
    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_VIRTUAL,
        name="StemListCtrl",
    ):
        wx.ListCtrl.__init__(
            self, parent, id=id, pos=pos, size=size, style=style, name=name
        )
        self.EnableAlternateRowColours()
        self.AppendColumn("Std Stem")
        self.AppendColumn("Width", wx.LIST_FORMAT_RIGHT)
        self.SetColumnWidth(0, 90)
        self.SetColumnWidth(1, 180)
        self.SetItemCount(0)
        self.EnableCheckBoxes()

        self.Bind(wx.EVT_LIST_ITEM_CHECKED, self.on_listItemChecked)
        # self.Bind(wx.EVT_LIST_ITEM_UNCHECKED, self.on_listItemUnChecked)
        self.Bind(wx.EVT_SIZE, self.on_Size)

    @property
    def value(self):
        return self.Parent.Value

    @value.setter
    def value(self, value):
        self.Parent.Value = value

    def OnGetItemText(self, row, col):
        if col == 0:
            return ""
        if col == 1:
            return str(self.value[row])

    def OnGetItemIsChecked(self, item):
        return item == 0

    def on_listItemChecked(self, event):
        # print(event.Index)
        stems = self.value[:]
        stdStem = stems.pop(event.Index)
        stems.sort()
        stems.insert(0, stdStem)
        self.value = stems
        # event.Skip()

    # def on_listItemUnChecked(self, event):
    #     event.Skip()

    def on_Size(self, event):
        self.SetColumnWidth(0, round(self.Size.Width / 3))
        self.SetColumnWidth(1, round(self.Size.Width / 3 * 2))
        event.Skip()
