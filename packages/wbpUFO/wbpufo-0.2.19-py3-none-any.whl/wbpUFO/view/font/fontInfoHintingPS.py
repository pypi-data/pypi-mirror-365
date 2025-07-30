"""
fontInfoHintingPS
===============================================================================

"""

import wx

from .fontInfoHintingPSUI import FontInfoHintingPSUI


class FontInfoHintingPS(FontInfoHintingPSUI):
    """
    Font Info page for PostScript hinting
    """

    def __init__(
        self,
        parent: wx.Window,
        id: int = wx.ID_ANY,
        pos: wx.Point = wx.DefaultPosition,
        size: wx.Size = wx.DefaultSize,
        style: int = wx.TAB_TRAVERSAL,
        name: str = "FontInfoHintingPS",
    ):
        style = style | wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.HSCROLL | wx.VSCROLL
        super().__init__(parent, id, pos, size, style, name)
        self.panel_postscriptBlueValues._maxValueLen = 14
        self.panel_postscriptOtherBlues._maxValueLen = 10
        self.panel_postscriptFamilyBlues._maxValueLen = 14
        self.panel_postscriptFamilyOtherBlues._maxValueLen = 10

    def on_button_copy_localZones(self, event):
        self.panel_postscriptFamilyBlues.Value = self.panel_postscriptBlueValues.Value
        self.panel_postscriptFamilyOtherBlues.Value = (
            self.panel_postscriptOtherBlues.Value
        )

    def on_button_copy_familyZones(self, event):
        from ... import AllFonts, SelectFonts

        fonts = [f for f in AllFonts() if f != self.Parent.font]
        selectedFonts = SelectFonts(
            "Select fonts to copy family zones to", "Copy Family Zones", fonts
        )
        if selectedFonts:
            for font in selectedFonts:
                info = font.info
                info.postscriptFamilyBlues = self.panel_postscriptFamilyBlues.Value
                info.postscriptFamilyOtherBlues = (
                    self.panel_postscriptFamilyOtherBlues.Value
                )

    def onUpdate_button_copy_familyZones(self, event):
        from ... import AllFonts

        event.Enable(len(AllFonts()) > 1)
