"""
fontInfoBase
===============================================================================

"""
import wx


class FontInfoBasePage(wx.ScrolledWindow):
    def __init__(
        self,
        parent: wx.Window,
        id: int = wx.ID_ANY,
        pos: wx.Point = wx.DefaultPosition,
        size: wx.Size = wx.DefaultSize,
        style: int = wx.TAB_TRAVERSAL,
        name: str = wx.EmptyString,
    ):
        style = style | wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.HSCROLL | wx.VSCROLL
        super().__init__(parent, id, pos, size, style, name)
        self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)
        self.SetScrollRate(5, 5)

    def __repr__(self):
        return f"<{self.__class__.__name__} of {self.Parent}>"
