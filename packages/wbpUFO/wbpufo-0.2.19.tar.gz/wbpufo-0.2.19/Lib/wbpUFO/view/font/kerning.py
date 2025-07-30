"""
kerning
===============================================================================

"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional, Tuple

import wx
import wx.grid as gridlib
from wbBase.scripting import MacroButtonMixin
from wbDefcon import Font

from .kerningStatusPanelUI import KerningStatusPanelUI

if TYPE_CHECKING:
    from wbDefcon import Kerning

    from ..fontinfo import UfoFontInfoWindow

log = logging.getLogger(__name__)


class KerningStatusPanel(KerningStatusPanelUI, MacroButtonMixin):
    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.BORDER_NONE,
    ):
        super().__init__(parent, id, pos, size, style, name="KerningStatusPanel")
        MacroButtonMixin.__init__(
            self, self.button_macro, "_kerning", self.GrandParent.view
        )

    # -------------------------------------------------------------------------
    # Event handler methods
    # -------------------------------------------------------------------------

    def on_button_New(self, event):
        event.Skip()

    def on_button_Delete(self, event):
        event.Skip()

    def update_button_Delete(self, event):
        event.Skip()


class KerningTable(gridlib.GridTableBase):
    def __init__(self, kerning: Kerning):
        super().__init__()
        self.kerning = kerning
        self.colLabels = ("Side 1", "Side 2", "Value")
        self.dataTypes = (
            gridlib.GRID_VALUE_STRING,
            gridlib.GRID_VALUE_STRING,
            gridlib.GRID_VALUE_NUMBER,
        )

    def GetNumberCols(self) -> int:
        return 3

    def GetNumberRows(self) -> int:
        return len(self.kerning)

    def GetColLabelValue(self, col: int) -> str:
        return self.colLabels[col]

    def GetRowLabelValue(self, row: int) -> str:
        return ""

    def CanGetValueAs(self, row: int, col: int, typeName) -> bool:
        colType = self.dataTypes[col].split(":")[0]
        if typeName == colType:
            return True
        else:
            return False

    def CanSetValueAs(self, row: int, col: int, typeName):
        return self.CanGetValueAs(row, col, typeName)

    def GetValue(self, row: int, col: int):
        try:
            pair: Tuple[str, str] = self.kerning.sortedPairList[row]
        except IndexError:
            return
        if col == 0:
            return pair[0].replace("public.kern1.", "@", 1)
        if col == 1:
            return pair[1].replace("public.kern2.", "@", 1)
        if col == 2:
            return self.kerning[pair]
        # return ("A", "V", -10)[col]

    def SetValue(self, row: int, col: int, value):
        if col == 2:
            kernValue = int(value)
            pair = self.kerning.sortedPairList[row]
            self.kerning[pair] = kernValue

    def GetAttr(self, row: int, col: int, kind) -> gridlib.GridCellAttr:
        attr = gridlib.GridCellAttr()
        if row % 2:
            attr.SetBackgroundColour(wx.Colour("WHITESMOKE"))
        else:
            attr.SetBackgroundColour(wx.Colour("WHITE"))
        if col in (0, 1):
            attr.SetReadOnly()
            if self.GetValue(row, col).startswith("@"):
                attr.SetTextColour("MEDIUM BLUE")
        elif col == 2:
            attr.SetAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTER)
        return attr

    def IsEmptyCell(self, row: int, col: int) -> bool:
        try:
            __ = self.kerning.sortedPairList[row]
            return False
        except IndexError:
            return True


class KerningGrid(gridlib.Grid):
    Table: KerningTable

    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.WANTS_CHARS | wx.NO_BORDER | gridlib.Grid.GridSelectRows,
    ):
        super().__init__(parent, id, pos, size, style, name="KerningGrid")
        self.SetColLabelSize(20)
        self.SetRowLabelSize(0)
        # self.UseNativeColHeader(True)
        self.SetDefaultCellFitMode(gridlib.GridFitMode.Ellipsize(wx.ELLIPSIZE_MIDDLE))
        # self.SetSortingColumn(0)
        # bind events
        self.Bind(gridlib.EVT_GRID_SELECT_CELL, self.on_selectCell)

    @property
    def kerning(self):
        return self.Table.kerning

    # -------------------------------------------------------------------------
    # Event handler methods
    # -------------------------------------------------------------------------

    def on_selectCell(self, event):
        pair = self.kerning.sortedPairList[event.GetRow()]
        log.debug("%r: %r", pair, self.kerning[pair])
        event.Skip()


class KerningPage(wx.Panel):
    Parent: UfoFontInfoWindow

    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.TAB_TRAVERSAL,
    ):
        super().__init__(parent, id, pos, size, style, name="KerningPage")
        self._font: Optional[Font] = None
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.kerningPanel = wx.SplitterWindow(
            self,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.SP_3D | wx.SP_NOBORDER | wx.BORDER_NONE,
        )
        self.kerningGrid = KerningGrid(self.kerningPanel)
        self.kerningViewPanel = wx.Panel(self.kerningPanel)
        sizer.Add(self.kerningPanel, 1, wx.EXPAND, 0)
        self.kerningPanel.SetMinimumPaneSize(20)
        self.kerningPanel.SashGravity = 0.3
        self.kerningPanel.SplitVertically(self.kerningGrid, self.kerningViewPanel, 200)

        self.kerningStatusPanel = KerningStatusPanel(self)
        sizer.Add(self.kerningStatusPanel, 0, wx.EXPAND, 0)
        self.SetSizer(sizer)
        self.Layout()
        # Connect Events
        self.kerningPanel.Bind(wx.EVT_IDLE, self.kerningPanelOnIdle)

    @property
    def font(self) -> Optional[Font]:
        """The wbDefcon Font object of this KerningPage"""
        return self._font

    @font.setter
    def font(self, value: Font) -> None:
        assert self._font is None
        assert isinstance(value, Font)
        assert value == self.Parent.font
        self._font = value
        self.kerningGrid.SetTable(
            KerningTable(self._font.kerning), True, self.kerningGrid.GridSelectRows
        )
        self._font.kerning.addObserver(
            self,
            "handleNotification",
            notification=self._font.kerning.changeNotificationName,
        )
        # self.kerningGrid.SetSortingColumn(0)

    @font.deleter
    def font(self) -> None:
        if self._font is not None and self._font.kerning.hasObserver(
            self, self._font.kerning.changeNotificationName
        ):
            self._font.kerning.removeObserver(
                self, self._font.kerning.changeNotificationName
            )
        self._font = None

    def handleNotification(self, notification):
        self.Refresh()

    # -------------------------------------------------------------------------
    # Event handler methods
    # -------------------------------------------------------------------------

    def kerningPanelOnIdle(self, event):
        self.kerningPanel.SetSashPosition(200)
        self.kerningPanel.Unbind(wx.EVT_IDLE)
