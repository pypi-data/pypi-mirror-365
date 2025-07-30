import wx
from wx import aui
# from wbDefcon import Glyph
# from wbFontParts import RGlyph

from .glyphViewPanelUI import GlyphViewPanelUI

name = "GlyphViewPanel"


class GlyphViewPanel(GlyphViewPanelUI):
    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.TAB_TRAVERSAL,
        name=name,
    ):
        super().__init__(parent, id=id, pos=pos, size=size, style=style, name=name)

    @property
    def fontsize(self):
        return self.spinCtrl_font_size.Value

    @fontsize.setter
    def fontsize(self, value):
        self.spinCtrl_font_size.Value = value
        self.glyphViewCanvas.Refresh()

    @property
    def linespace(self):
        return self.spinCtrl_line_space.Value

    @property
    def glyphs(self):
        return self.glyphViewCanvas.glyphs

    def insertGlyph(self, index, glyph):
        self.glyphViewCanvas.insertGlyph(index, glyph)

    def appendGlyph(self, glyph):
        self.glyphViewCanvas.insertGlyph(self.glyphViewCanvas.glyphCount, glyph)

    def clearGlyphs(self):
        self.glyphViewCanvas.clearGlyphs()

    # =================================================================
    # event handlers
    # =================================================================
    def on_spinCtrl_font_size(self, event):
        self.glyphViewCanvas.Refresh()

    def on_spinCtrl_line_space(self, event):
        self.glyphViewCanvas.Refresh()

    def on_checkBox_showKerning(self, event):
        self.glyphViewCanvas.Refresh()

    def on_btn_clear(self, event):
        self.clearGlyphs()


glyphViewPanelInfo = aui.AuiPaneInfo()
glyphViewPanelInfo.Name(name)
glyphViewPanelInfo.Caption(name)
glyphViewPanelInfo.Dock()
glyphViewPanelInfo.Bottom()
glyphViewPanelInfo.Resizable()
glyphViewPanelInfo.MaximizeButton(True)
glyphViewPanelInfo.MinimizeButton(True)
glyphViewPanelInfo.CloseButton(False)
glyphViewPanelInfo.FloatingSize(wx.Size(300, 200))
glyphViewPanelInfo.BestSize(wx.Size(800, 400))
glyphViewPanelInfo.MinSize(wx.Size(300, 100))
glyphViewPanelInfo.Icon(wx.ArtProvider.GetBitmap("VIEW", wx.ART_FRAME_ICON))
