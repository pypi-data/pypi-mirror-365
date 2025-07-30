"""
markColor
===============================================================================
"""
import logging
import wx
import wx.aui as aui
from wx.lib.colourdb import updateColourDB, getColourList

from wbDefcon.objects.color import Color, mark

from ..view.font import UfoFontView
from ..view.font.groups import GroupsPage
from ..view.fontinfo import UfoFontInfoView
from ..view.glyph import UfoGlyphView

log = logging.getLogger(__name__)

updateColourDB()


class ColorMixin:
    @property
    def app(self):
        return wx.GetApp()

    @property
    def font(self):
        return self.app.documentManager.currentView.font

    @staticmethod
    def bitmap(color):
        return wx.Bitmap.FromRGBA(16, 16, *wx.Colour(color))

    @property
    def glyphs(self):
        view = self.app.documentManager.currentView
        if isinstance(view, UfoFontView):
            return self.font.selectedGlyphs
        if isinstance(view, UfoFontInfoView):
            return [self.font[g] for g in self.font.groups[view.frame.CurrentPage.currentGroupName]]
        if isinstance(view, UfoGlyphView):
            return [view.glyph]

    def markSelectedGlyphs(self, color):
        log.debug("color: %r", color)
        font = self.font
        font.holdNotifications()
        if color in ("WHITE", "No Color"):
            c = None
        else:
            c = Color(wx.Colour(color))
        for glyph in self.glyphs:
            glyph.markColor = c
        font.releaseHeldNotifications()


class ColorMenu(wx.Menu, ColorMixin):
    def __init__(self):
        super().__init__()
        for color in getColourList():
            if (
                " " not in color
                and color[-1] not in "01234567899"
                and color not in ("WHITE", "BLACK")
            ):
                item = wx.MenuItem(self, wx.ID_ANY, color)
                item.SetBitmap(self.bitmap(color))
                self.Append(item)
                self.Bind(wx.EVT_MENU, self.on_menu, id=item.GetId())

    def on_menu(self, event):
        self.markSelectedGlyphs(self.GetLabelText(event.Id))


class GlyphMarkToolbar(aui.AuiToolBar, ColorMixin):
    def __init__(self, parent):
        id = wx.ID_ANY
        pos = wx.DefaultPosition
        size = wx.DefaultSize
        style = (
            wx.aui.AUI_TB_HORZ_LAYOUT | wx.aui.AUI_TB_PLAIN_BACKGROUND | wx.NO_BORDER
        )
        aui.AuiToolBar.__init__(self, parent, id, pos, size, style)
        self.SetToolBitmapSize(wx.Size(16, 16))
        tool = self.AddTool(
            wx.ID_ANY, "No Color", self.bitmap("WHITE"), "No Color", wx.ITEM_NORMAL
        )
        self.Bind(wx.EVT_TOOL, self.on_Tool, tool)
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_Tool, tool)
        for color in ("RED", "ORANGE", "YELLOW", "GREEN", "CYAN", "BLUE", "MAGENTA"):
            tool = self.AddTool(
                wx.ID_ANY, color, self.bitmap(color), color, wx.ITEM_NORMAL
            )
            self.Bind(wx.EVT_TOOL, self.on_Tool, tool)
            self.Bind(wx.EVT_UPDATE_UI, self.on_update_Tool, tool)
        self.AddSeparator()
        # add ColorMenu
        tool = self.AddTool(
            wx.ID_ANY,
            "Select Color",
            self.bitmap("GREY"),
            "Select Color",
            wx.ITEM_NORMAL,
        )
        tool.SetHasDropDown(True)
        self.Bind(aui.EVT_AUITOOLBAR_TOOL_DROPDOWN, self.on_ColorMenu, tool)
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_Tool, tool)
        self.menu = ColorMenu()

    def on_Tool(self, event):
        self.markSelectedGlyphs(self.GetToolLabel(event.Id))

    def on_ColorMenu(self, event):
        eventID = event.Id
        self.SetToolSticky(eventID, True)
        rect = self.GetToolRect(eventID)
        pt = self.ClientToScreen(rect.GetBottomLeft())
        pt = self.ScreenToClient(pt)
        self.PopupMenu(self.menu, pt)
        self.SetToolSticky(eventID, False)

    def on_update_Tool(self, event):
        view = self.app.documentManager.currentView
        if view:
            if isinstance(view, UfoFontView):
                event.Enable(True)
            elif isinstance(view, UfoFontInfoView):
                if isinstance(view.frame.CurrentPage, GroupsPage) and view.frame.CurrentPage.currentGroupName:
                    event.Enable(True)
                else:
                    event.Enable(False)
            elif isinstance(view, UfoGlyphView):
                event.Enable(True)
        else:
            event.Enable(False)
