from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import wx
from wx import aui

if TYPE_CHECKING:
    from wbBase.application import App
    from wbBase.document.view import View


class BaseToolbar(aui.AuiToolBar):
    """
    Base class for all toolbars of the wbpUfo plugin.
    """

    itemType = wx.ITEM_NORMAL

    def __init__(self, parent, name=None):
        id = wx.ID_ANY
        pos = wx.DefaultPosition
        size = wx.DefaultSize
        style = aui.AUI_TB_HORZ_LAYOUT | aui.AUI_TB_PLAIN_BACKGROUND | wx.NO_BORDER
        super().__init__(parent, id, pos, size, style)
        if isinstance(name, str):
            self.Name = name
        self.SetToolBitmapSize(wx.Size(16, 16))

    @property
    def app(self) -> App:
        """
        The running Workbench application.
        """
        return wx.GetApp()

    @property
    def currentView(self) -> Optional[View]:
        """
        The currently active view, may be None.
        """
        return self.app.documentManager.currentView

    @staticmethod
    def bitmap(name) -> wx.Bitmap:
        return wx.ArtProvider.GetBitmap(name, wx.ART_TOOLBAR)

    def appendTool(
        self,
        label: str,
        bitmapName: str,
        helpText: str = wx.EmptyString,
        commandIndex: int = -1,
        kind = None
    ) -> aui.AuiToolBarItem:
        if not helpText:
            helpText = label
        if kind is None:
            kind = self.itemType
        tool: aui.AuiToolBarItem = self.AddTool(
            toolId=wx.ID_ANY,
            label=label,
            bitmap=self.bitmap(bitmapName),
            short_help_string=helpText,
            kind=kind,
        )
        tool.SetUserData(commandIndex)
        self.Bind(wx.EVT_TOOL, self.on_Tool, tool)
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_Tool, tool)
        return tool

    def on_Tool(self, event):
        event.Skip()

    def on_update_Tool(self, event):
        event.Skip()
