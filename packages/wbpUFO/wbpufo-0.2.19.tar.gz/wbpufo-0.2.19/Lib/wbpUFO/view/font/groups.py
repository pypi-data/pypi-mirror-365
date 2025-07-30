"""
groups
===============================================================================

"""
import pickle
import zlib

import wx
import wx.grid as gridlib
import wx.lib.mixins.gridlabelrenderer as glr
from wbBase.scripting import MacroButtonMixin
from wbDefcon import Font
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin, TextEditMixin

from .groupsStatusPanelUI import GroupsStatusPanelUI


class GroupsListDropTarget(wx.DropTarget):
    """
    DropTarget for GroupsListCtrl
    """

    def __init__(self, groupsListCtrl):
        super().__init__()
        self.groupsListCtrl = groupsListCtrl
        self.SetDataObject(wx.CustomDataObject("application.UFO-WB.glyphNames"))
        self.SetDefaultAction(wx.DragCopy)
        self.documentManager = wx.GetApp().documentManager
        self._font = None
        self._glyphs = []

    @property
    def font(self):
        return self._font

    @property
    def glyphs(self):
        return self._glyphs

    def OnEnter(self, x, y, defResult):
        if self.GetData():
            glyphNameData = self.DataObject.GetData()
            if glyphNameData:
                glyphNameDict = pickle.loads(glyphNameData)
                font = None
                for doc in self.documentManager.documents:
                    if (
                        doc.typeName == "UFO document"
                        and id(doc.font) == glyphNameDict["font"]
                    ):
                        font = doc.font
                        break
                if not font:
                    return wx.DragError
                if font != self.groupsListCtrl.font:
                    return wx.DragNone
                self._font = font
                self._glyphs = [font[g] for g in glyphNameDict["glyphs"] if g in font]
                self.groupsListCtrl.SetFocus()
                return defResult
        return wx.DragNone

    def OnDragOver(self, x, y, defResult):
        if self.font is None:
            return wx.DragNone
        itemIndex, flags = self.groupsListCtrl.HitTest(wx.Point(x, y))
        if flags & wx.LIST_HITTEST_ONITEM:
            self.groupsListCtrl.Select(itemIndex)
            self.groupsListCtrl.EnsureVisible(itemIndex)
        return defResult

    def OnLeave(self):
        self._font = None
        self._glyphs = []

    def OnData(self, x, y, defResult):
        if self.font is None:
            return wx.DragNone
        itemIndex, flags = self.groupsListCtrl.HitTest(wx.Point(x, y))
        if flags & wx.LIST_HITTEST_ONITEM:
            groupName = self.groupsListCtrl.GetItem(itemIndex).Text
            groups = self.font.groups
            groups[groupName] = groups[groupName] + [g.name for g in self.glyphs]
            self.groupsListCtrl.Select(itemIndex)
            self.groupsListCtrl.EnsureVisible(itemIndex)
            return defResult
        return wx.DragNone


class GroupsListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin, TextEditMixin):
    """
    ListCtrl of the Groups page
    """

    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_VIRTUAL,
        name="GroupsListCtrl",
    ):
        wx.ListCtrl.__init__(self, parent, id, pos, size, style, name=name)
        self._font = None
        # self._groupNames = []
        ListCtrlAutoWidthMixin.__init__(self)
        self.InsertColumn(0, "Group")
        self.SetItemCount(0)
        TextEditMixin.__init__(self)
        self.SetDropTarget(GroupsListDropTarget(self))

    @property
    def font(self):
        """The wbDefcon Font object of this FeatureTextCtrl"""
        return self._font

    @font.setter
    def font(self, value):
        assert self._font is None
        assert isinstance(value, Font)
        assert value == self.GrandParent._font
        self._font = value
        # self._groupNames = self._font.groups.sortedGroupNames
        self.SetItemCount(len(self.groupNames))
        if self.ItemCount:
            self.Select(0)

    @font.deleter
    def font(self):
        # self._groupNames = []
        self.SetItemCount(0)
        self._font = None

    @property
    def groupNames(self):
        if self._font is None:
            return []
        return self._font.groups.sortedGroupNames

    def OnGetItemText(self, item, column):
        return self.groupNames[item]

    def SetVirtualData(self, row, col, text):
        # todo: implement this
        wx.LogWarning(
            f"Method 'SetVirtualData' of GroupsListCtrl not yet implementd\n\n New name '{text}' not set"
        )


class GroupsStatusPanel(GroupsStatusPanelUI, MacroButtonMixin):
    """
    Status Panel of the Groups page
    """

    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.BORDER_NONE,
    ):
        super().__init__(parent, id, pos, size, style, name="GroupsStatusPanel")
        MacroButtonMixin.__init__(
            self, self.button_macro, "_groups", self.GrandParent.view
        )

    def on_choiceGroups(self, event):
        wx.LogWarning(
            "Method 'on_choiceGroups' of GroupsStatusPanel not yet implementd.\n\n Filter not set"
        )

    def update_choiceGroups(self, event):
        event.Skip()

    def on_button_New(self, event):
        newGroup = wx.GetTextFromUser(
            "Enter name for new group", "Add new Group", "", self
        )
        if newGroup:
            # todo: implement this
            wx.LogWarning(
                f"Method 'on_button_New' of GroupsStatusPanel not yet implementd\n\n New group '{newGroup}' not created"
            )

    def on_button_Delete(self, event):
        event.Skip()

    def update_button_Delete(self, event):
        event.Skip()


class GroupContentTable(gridlib.GridTableBase):
    """
    GroupContentTable of the Groups page
    """

    def __init__(self, group, font):
        super().__init__()
        self.group = group or []
        self.font = font
        self.colLabels = ("Name", "Left Margin", "Width", "Right Margin")
        self.dataTypes = (
            gridlib.GRID_VALUE_STRING,
            gridlib.GRID_VALUE_NUMBER,
            gridlib.GRID_VALUE_NUMBER,
            gridlib.GRID_VALUE_NUMBER,
        )

    def GetNumberCols(self):
        return len(self.colLabels)

    def GetNumberRows(self):
        return len(self.group)

    def GetColLabelValue(self, col):
        return self.colLabels[col]

    def GetRowLabelValue(self, row):
        return ""

    def CanGetValueAs(self, row, col, typeName):
        colType = self.dataTypes[col].split(":")[0]
        if typeName == colType:
            return True
        else:
            return False

    def CanSetValueAs(self, row, col, typeName):
        return self.CanGetValueAs(row, col, typeName)

    def GetValue(self, row, col):
        glyphName = self.group[row]
        if col == 0:
            return glyphName
        if glyphName in self.font:
            glyph = self.font[glyphName]
            if col == 1:
                return glyph.leftMargin
            if col == 2:
                return glyph.width
            if col == 3:
                return glyph.rightMargin
        return None

    def SetValue(self, row, col, value):
        glyphName = self.group[row]
        if glyphName in self.font:
            glyph = self.font[glyphName]
            if col == 1 and glyph.leftMargin is not None:
                glyph.leftMargin = int(value)
            if col == 2:
                glyph.width = int(value)
            if col == 3 and glyph.rightMargin is not None:
                glyph.rightMargin = int(value)
            self.View.Refresh()

    def GetAttr(self, row, col, kind):
        attr = gridlib.GridCellAttr()
        # todo: allow editing of lsb, rsb and width
        if col == 0:
            attr.SetReadOnly()
            attr.SetAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTER)
        if row % 2:
            attr.SetBackgroundColour(wx.Colour("WHITESMOKE"))
        else:
            attr.SetBackgroundColour(wx.Colour("WHITE"))
        if col > 0:
            attr.SetAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTER)
        return attr

    def IsEmptyCell(self, row, col):
        return self.GetValue(row, col) is None


class GlyphRowLabelRenderer(glr.GridLabelRenderer):
    """
    Show glyph image on Row label
    """
    def Draw(self, grid: gridlib.Grid, dc: wx.DC, rect: wx.Rect, row: int):
        w = rect.Width - 2
        h = rect.Height - 2
        bitmap = wx.Bitmap.FromRGBA(w, h)
        glyphName = grid.Table.GetValue(row, 0)
        font = grid.GrandParent.font
        if glyphName in font:
            glyph = font[glyphName]
            bitmapdata = zlib.decompress(
                glyph.getRepresentation("bitmap", width=w, height=h, captionHeight=0)
            )
            bitmap.CopyFromBuffer(bitmapdata, wx.BitmapBufferFormat_RGBA)
        dc.DrawBitmap(bitmap, rect.left + 1, rect.top + 1)
        self.DrawBorder(grid, dc, rect)


class GroupContentGrid(gridlib.Grid, glr.GridWithLabelRenderersMixin):
    """
    GroupContentGrid of the Groups page
    """

    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.WANTS_CHARS | wx.NO_BORDER | gridlib.Grid.GridSelectRows,
    ):
        super().__init__(parent, id, pos, size, style, name="GroupContentGrid")
        glr.GridWithLabelRenderersMixin.__init__(self)
        self.SetDefaultRowLabelRenderer(GlyphRowLabelRenderer())
        self.SetColLabelSize(20)
        self.SetRowLabelSize(28)
        self.SetDefaultRowSize(28)
        self.EnableDragRowSize(False)
        self.SetDefaultCellFitMode(gridlib.GridFitMode.Ellipsize(wx.ELLIPSIZE_MIDDLE))
        # bind events
        # self.Bind(gridlib.EVT_GRID_SELECT_CELL, self.on_selectCell)
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_DCLICK, self.on_CellLeftDoubleClick)

    # def SetTable(self, table, takeOwnership=False, selmode=gridlib.Grid.GridSelectCells):
    #     super().SetTable(table, takeOwnership, selmode)

    def on_CellLeftDoubleClick(self, event):
        col = event.Col
        if col == 0:
            row = event.Row
            glyphName = self.Table.GetValue(row, col)
            if glyphName in self.GrandParent.font:
                self.GrandParent.font.showGlyph(glyphName)
        event.Skip()


class GroupsPage(wx.Panel):
    """
    The Groups page
    """

    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.TAB_TRAVERSAL,
        name="GroupsPage",
    ):
        super().__init__(parent, id, pos, size, style, name)
        self._font = None
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.groupsPanel = wx.SplitterWindow(
            self,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.SP_3D | wx.SP_NOBORDER | wx.BORDER_NONE,
        )
        self.groupsListCtrl = GroupsListCtrl(self.groupsPanel)
        self.groupsContent = GroupContentGrid(self.groupsPanel)
        sizer.Add(self.groupsPanel, 1, wx.EXPAND, 0)
        self.groupsPanel.SetMinimumPaneSize(20)
        self.groupsPanel.SashGravity = 0.3
        self.groupsPanel.SplitVertically(self.groupsListCtrl, self.groupsContent, 200)
        # self.groupsPanel.Unsplit(self.groupsListCtrl)

        self.groupsStatusPanel = GroupsStatusPanel(self)
        sizer.Add(self.groupsStatusPanel, 0, wx.EXPAND, 0)

        self.SetSizer(sizer)
        self.Layout()
        # Connect Events
        self.groupsPanel.Bind(wx.EVT_IDLE, self.groupsPanelOnIdle)
        self.groupsListCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_GroupSelected)

    @property
    def font(self):
        """The wbDefcon Font object of this GroupsPage"""
        return self._font

    @font.setter
    def font(self, value: Font):
        assert self._font is None
        assert isinstance(value, Font)
        assert value == self.Parent.font
        self._font = value
        self.groupsListCtrl.font = value
        self._font.groups.addObserver(
            self,
            "handleNotification",
            notification=self._font.groups.changeNotificationName,
        )

    @font.deleter
    def font(self):
        del self.groupsListCtrl.font
        if self._font is not None and self._font.groups.hasObserver(
            self, self._font.groups.changeNotificationName
        ):
            self._font.groups.removeObserver(
                self, self._font.groups.changeNotificationName
            )
        self._font = None

    @property
    def currentGroupName(self):
        if self.groupsListCtrl.SelectedItemCount:
            itemIndex = self.groupsListCtrl.GetNextSelected(-1)
            return self.groupsListCtrl.GetItem(itemIndex).Text

    def handleNotification(self, notification):
        # print(notification)
        if self._font is not None:
            try:
                groupsListCtrl = self.groupsListCtrl
            except RuntimeError:
                return
            self.groupsListCtrl.SetItemCount(len(self._font.groups))
        if self.currentGroupName:
            self.setGroupsContentTable(self.currentGroupName)
        self.Refresh()

    def setGroupsContentTable(self, groupName):
        oldTable = self.groupsContent.Table
        if oldTable and hasattr(oldTable, "group"):
            for glyphName in oldTable.group:
                if glyphName in self.font:
                    glyph = self.font[glyphName]
                    if glyph.hasObserver(self, glyph.changeNotificationName):
                        glyph.removeObserver(self, glyph.changeNotificationName)
        newTabel = GroupContentTable(self.font.groups[groupName], self.font)
        for glyphName in newTabel.group:
            if glyphName in self.font:
                glyph = self.font[glyphName]
                if not glyph.hasObserver(self, glyph.changeNotificationName):
                    glyph.addObserver(
                        self,
                        "handleNotification",
                        notification=glyph.changeNotificationName,
                    )
        self.groupsContent.SetTable(
            newTabel,
            True,
            self.groupsContent.GridSelectRows,
        )
        self.groupsContent.Refresh()

    # -------------------------------------------------------------------------
    # Event handler methods
    # -------------------------------------------------------------------------

    def groupsPanelOnIdle(self, event):
        self.groupsPanel.SetSashPosition(200)
        self.groupsPanel.Unbind(wx.EVT_IDLE)

    def on_GroupSelected(self, event):
        self.setGroupsContentTable(self.font.groups.sortedGroupNames[event.Index])
        event.Skip()
