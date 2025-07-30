"""
glyphGrid
===============================================================================

"""

from __future__ import annotations

import logging
import os
import pickle
import zlib
from math import sqrt
from multiprocessing import Pool, cpu_count
from typing import TYPE_CHECKING, List, Optional

import wx
from defcon import registerRepresentationFactory
from fontTools.misc.transform import Transform
from fontTools.pens.boundsPen import ControlBoundsPen
from fontTools.pens.transformPen import TransformPen
from wbBase.scripting import MacroMenu
from wbDefcon import Font, Glyph
from wbDefcon.pens import graphicsPen
from wbDefcon.tools.glyph import deleteGlyph, getSaveKeepName, renameGlyph

from ...control.glyphGridStatusPanelUI import GlyphGridStatusPanelUI
from ...dialog.deleteGlyphsDialog import DeleteGlyphsDialog
from ...dialog.findGlyphDialog import FindGlyphDialog
from ...dialog.newGlyphDialog import NewGlyphDialog
from ...dialog.renameGlyphDialog import RenameGlyphDialog
from ...glyphCommand.commandListDialog import CommandListDialog
from ..fontinfo import UfoFontInfoView

if TYPE_CHECKING:
    from wbBase.application import App
    from . import UfoFontWindow, UfoFontView
    from ...document import UfoDocument

log = logging.getLogger(__name__)


def glyphBitmapRepresentationFactory(
    glyph: Glyph, width: int = 72, height: int = 88, captionHeight: int = 16
) -> bytes:
    imageHeight = height - captionHeight
    font = glyph.font
    info = font.info
    scale = imageHeight / (info.unitsPerEm * 1.7)
    bitmap = wx.Bitmap.FromRGBA(width, height)
    dc = wx.MemoryDC(bitmap)
    gc: wx.GraphicsContext = wx.GraphicsContext.Create(dc)

    # draw background
    if glyph.markColor:
        gc.SetBrush(wx.TheBrushList.FindOrCreateBrush(glyph.markColor.wx, wx.SOLID))
    else:
        gc.SetBrush(wx.WHITE_BRUSH)
    gc.DrawRectangle(0, captionHeight, width - 1, imageHeight - 1)

    # draw glyph
    graphicsPen.glyphSet = font._glyphSet
    graphicsPen.path = gc.CreatePath()
    boundsPen = ControlBoundsPen(font._glyphSet)
    glyph.draw(boundsPen)
    bounds = boundsPen.bounds
    if bounds:
        x0, y0, x1, y1 = bounds
    else:
        x0, y0, x1, y1 = (0, 0, 0, 0)
    dx = ((width / scale) - (x0 + x1)) / 2
    dy = -info.unitsPerEm * 1.2 - captionHeight / scale
    transformation = Transform().scale(scale, -scale).translate(dx, dy)
    pen = TransformPen(graphicsPen, transformation)
    glyph.draw(pen)
    gc.SetBrush(wx.BLACK_BRUSH)
    gc.FillPath(graphicsPen.path, wx.WINDING_RULE)

    # draw caption
    if captionHeight > 0:
        gc.SetBrush(
            wx.TheBrushList.FindOrCreateBrush(wx.Colour(230, 230, 230, 255), wx.SOLID)
        )
        gc.DrawRectangle(0, 0, width - 1, captionHeight)
        font = wx.Font(
            10,
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_NORMAL,
            False,
            "Segoe UI",
        )
        font.PixelSize = wx.Size(0, captionHeight - 2)
        gc.SetFont(font, wx.BLACK)
        name = glyph.name
        text = glyph.name
        cut = round(len(text) / 2) - 1
        w, h = gc.GetTextExtent(text)
        while w >= width - 1:
            text = "%s…%s" % (name[:cut], name[-cut:])
            w, h = gc.GetTextExtent(text)
            cut -= 1
        tx = (width - w) / 2
        ty = -1
        gc.DrawText(text, tx, ty)

    # draw border
    gc.SetPen(wx.ThePenList.FindOrCreatePen(wx.Colour(245, 245, 245, 255), 2, wx.SOLID))
    border: wx.GraphicsPath = gc.CreatePath()
    border.MoveToPoint(width, 0)
    border.AddLineToPoint(width, height)
    border.AddLineToPoint(0, height)
    gc.StrokePath(border)

    # return the bitmap as zlib compressed bytes
    dc.SelectObject(wx.NullBitmap)
    buffer = bytes(bitmap.Width * bitmap.Height * 4)
    bitmap.CopyToBuffer(buffer, wx.BitmapBufferFormat_RGBA)
    return zlib.compress(buffer)


registerRepresentationFactory(
    Glyph,
    name="bitmap",
    factory=glyphBitmapRepresentationFactory,
    destructiveNotifications=(
        "Glyph.Changed",
        "Glyph.NameChanged",
        "Glyph.MarkColorChanged",
        "Glyph.ContoursChanged",
        "Glyph.ComponentsChanged",
        "Glyph.ComponentBaseGlyphDataChanged",
    ),
)


class GlyphGridContextMenu(wx.Menu):
    """Context Menu for GlyphGrid"""

    def __init__(self, parent, title=""):
        wx.Menu.__init__(self, title, style=0)
        self.glyphGrid: GlyphGrid = parent
        self._macroFolderPath = []
        app = wx.GetApp()
        item = wx.MenuItem(self, wx.ID_ANY, "Open New Glyph Window")
        self.Append(item)
        self.Bind(wx.EVT_MENU, self.on_OPEN_NEW_GLYPHWINDOW, item, item.Id)

        item = wx.MenuItem(self, wx.ID_ANY, "Rename Glyph ...")
        self.Append(item)
        self.Bind(wx.EVT_MENU, self.on_RENAME_GLYPH, item, item.Id)

        item = wx.MenuItem(self, wx.ID_ANY, "New Glyph ...")
        self.Append(item)
        self.Bind(wx.EVT_MENU, self.on_NEW_GLYPH, item, item.Id)

        item = wx.MenuItem(self, wx.ID_ANY, "Dublicate Glyph ...")
        self.Append(item)
        self.Bind(wx.EVT_MENU, self.on_DUBLICATE_GLYPH, item, item.Id)

        item = wx.MenuItem(self, wx.ID_ANY, "Show Tooltips")
        item.SetBitmap(wx.ArtProvider.GetBitmap("INFORMATION", wx.ART_MENU, (16, 16)))
        # item.SetFont(app.TopWindow.Font)
        self.Append(item)
        self.Bind(wx.EVT_MENU, self.on_SHOW_TOOLTIPS, item, item.Id)

        item = wx.MenuItem(self, wx.ID_ANY, "Delete selected Glyphs ...\tDel")
        item.SetBitmap(wx.ArtProvider.GetBitmap("DELETE", wx.ART_MENU, (16, 16)))
        # item.SetFont(app.TopWindow.Font)
        self.Append(item)
        self.glyphGrid.Bind(wx.EVT_MENU, self.on_DELETE_SELECTED, item, item.Id)
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_DELETE_SELECTED, item)
        self.glyphGrid.SetAcceleratorTable(
            wx.AcceleratorTable(
                [wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_DELETE, item.Id, item)]
            )
        )

        item = wx.MenuItem(self, wx.ID_ANY, "Command List ...")
        item.SetBitmap(wx.ArtProvider.GetBitmap("COMMAND_LIST", wx.ART_MENU, (16, 16)))
        # item.SetFont(app.TopWindow.Font)
        self.Append(item)
        self.Bind(wx.EVT_MENU, self.on_COMMAND_LIST, item, item.Id)

        if any(os.path.isdir(p) for p in self.macroFolderPath):
            macroMenu = MacroMenu(folderList=self.macroFolderPath)
            item = self.AppendSubMenu(macroMenu, "Macros")
            item.SetBitmap(wx.ArtProvider.GetBitmap("PYTHON", wx.ART_MENU, (16, 16)))
            item.SetFont(app.TopWindow.Font)

    @property
    def app(self) -> App:
        return wx.GetApp()

    @property
    def font(self) -> Font:
        return self.glyphGrid.font

    @property
    def macroFolderPath(self):
        if not self._macroFolderPath:
            cfg = self.app.TopWindow.config
            self._macroFolderPath = [
                os.path.join(
                    cfg.Read("/Application/SharedData/Dir", self.app.sharedDataDir),
                    "Macro",
                    "_system",
                    "_font",
                ),
                os.path.join(
                    cfg.Read("/Application/PrivateData/Dir", self.app.privateDataDir),
                    "Macro",
                    "_system",
                    "_font",
                ),
            ]
        return self._macroFolderPath

    def on_OPEN_NEW_GLYPHWINDOW(self, event):
        win = self.glyphGrid
        self.font.showGlyph(win.glyphNames[win.selectedIndex], True)

    def on_RENAME_GLYPH(self, event):
        glyph = self.glyphGrid.currentGlyph
        with RenameGlyphDialog(self.glyphGrid, glyph) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                # print(f"Glyph Name: {dialog.glyphname}, Unicodes: {dialog.unicodes}")
                if dialog.glyphname != glyph.name:
                    if dialog.replaceExisting:
                        if dialog.keepReplaced:  # rename replaced
                            replacedGlyph = self.font[dialog.glyphname]
                            replacedName = getSaveKeepName(replacedGlyph)
                            renameGlyph(
                                glyph=replacedGlyph,
                                newName=replacedName,
                                inComponents=dialog.inComposites,
                                inGroups=dialog.inGroups,
                                inKerning=dialog.inKerning,
                                inFeatures=dialog.inFeatures,
                                allLayers=dialog.allLayers,
                            )
                        else:  # delete replaced
                            deleteGlyph(
                                glyph=self.font[dialog.glyphname],
                                inComponents="delete",
                                inGroups=True,
                                inKerning=True,
                                allLayers=True,
                            )
                    renameGlyph(
                        glyph=glyph,
                        newName=dialog.glyphname,
                        inComponents=dialog.inComposites,
                        inGroups=dialog.inGroups,
                        inKerning=dialog.inKerning,
                        inFeatures=dialog.inFeatures,
                        allLayers=dialog.allLayers,
                    )
                if dialog.unicodes != glyph.unicodes:
                    glyph.unicodes = dialog.unicodes

    def on_NEW_GLYPH(self, event: wx.CommandEvent):
        with NewGlyphDialog() as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                newGlyph = self.font.newGlyph(dialog.glyphname)
                newGlyph.unicodes = dialog.unicodes
                self.font.selectedGlyphNames = [newGlyph.name]

    def on_DUBLICATE_GLYPH(self, event: wx.CommandEvent):
        glyph: Glyph = self.glyphGrid.currentGlyph
        if isinstance(glyph, Glyph) and glyph.name:
            with NewGlyphDialog() as dialog:
                dialog: NewGlyphDialog
                dialog.textCtrl_name.Value = getSaveKeepName(glyph)
                if dialog.ShowModal() == wx.ID_OK:
                    if dialog.glyphname and dialog.glyphname not in self.font:
                        newGlyph: Glyph = self.font.newGlyph(dialog.glyphname)
                        newGlyph.name = dialog.glyphname
                        newGlyph.unicodes = dialog.unicodes
                        newGlyph.width = glyph.width
                        newGlyph.markColor = glyph.markColor
                        newGlyph.lib = glyph.lib.copy()
                        for anchor in glyph.anchors:
                            newGlyph.appendAnchor(anchor)
                        for guideline in glyph.guidelines:
                            newGlyph.appendGuideline(guideline)
                        glyph.draw(newGlyph.getPen())
                        self.font.selectedGlyphs = [newGlyph]
                        self.glyphGrid.ScrollToSelected()
                    else:
                        wx.LogWarning(f"Glyph '{glyph.name}' already exist!")

    def on_SHOW_TOOLTIPS(self, event):
        win = self.glyphGrid
        win.showTooltip = not win.showTooltip

    def on_DELETE_SELECTED(self, event):
        self.glyphGrid.deleteSelectedGlyphs()

    def on_update_DELETE_SELECTED(self, event):
        event.Enable(self.font.selectedGlyphCount > 0)

    def on_COMMAND_LIST(self, event):
        with CommandListDialog() as dialog:
            dialog.choice_target.SetSelection(1)  # selected glyphs
            if dialog.ShowModal() == wx.ID_OK:
                commandList = dialog.commandList
                if commandList:
                    dialog.executeCommandList()
                    # self.glyphGrid.Refresh()


class GlyphGridStatusPanel(GlyphGridStatusPanelUI):
    """Status Panel for GlyphGrid"""

    def __init__(
        self,
        parent: GlyphGridPage,
        id: int = wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style: int = 0,
        name="GlyphGridStatusPanel",
    ):
        super().__init__(parent, id, pos, size, style, name)
        self.searchCtrl.SetHint("filter glyphs")

    @property
    def font(self) -> Font:
        return self.glyphGrid.font

    @property
    def glyphGrid(self) -> GlyphGrid:
        return self.GrandParent.glyphGridPanel

    # -------------------------------------------------------------------------
    # event handler
    # -------------------------------------------------------------------------

    def on_button_fontinfo(self, event):
        with wx.BusyCursor():
            window = wx.GetApp().TopWindow.panelManager.centerPane.window
            window.Freeze()
            doc = self.font.document
            view = None
            for v in doc.views:
                if v.typeName == "UFO Font Info View":
                    view = v
                    break
            if not view:
                view = UfoFontInfoView()
                if view.OnCreate(doc, None):
                    doc.AddView(view)
                    view.frame.font = self.font
                else:
                    wx.LogError(f"Can not create view for {self.font}")
                    view.Destroy()
                    window.Thaw()
                    return
            view.Activate()
            window.Thaw()

    def onSearchCancel(self, event: wx.CommandEvent):
        del self.glyphGrid.searchText
        event.Skip()

    def onSearchText(self, event: wx.CommandEvent):
        self.glyphGrid.searchText = event.GetString()

    def update_current(self, event):
        if self.glyphGrid.selectedIndex >= 0:
            try:
                label = self.glyphGrid.glyphNames[self.glyphGrid.selectedIndex]
            except IndexError:
                label = ""
        else:
            label = ""
        if label != self.text_current.Label:
            self.text_current.SetLabel(label)

    def update_unicodes(self, event):
        if self.font and self.glyphGrid.selectedIndex >= 0:
            try:
                glyph = self.font[
                    self.glyphGrid.glyphNames[self.glyphGrid.selectedIndex]
                ]
                label = " ".join("%04X" % u for u in glyph.unicodes)
            except IndexError:
                label = ""
        else:
            label = ""
        if label != self.text_unicodes.Label:
            self.text_unicodes.SetLabel(label)

    def update_selected_count(self, event):
        if self.font:
            label = str(self.font.selectedGlyphCount)
        else:
            label = "0"
        # log.debug(f"update_selected_count: {label}")
        if label != self.text_selected_count.Label:
            self.text_selected_count.SetLabel(label)

    def update_total_count(self, event):
        if self.font:
            label = str(len(self.font))
        else:
            label = "0"
        if label != self.text_total_count.Label:
            self.text_total_count.SetLabel(label)


class GlyphGrid(wx.ScrolledWindow):
    """The main GlyphGrid"""

    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.HSCROLL | wx.VSCROLL | wx.WANTS_CHARS | wx.TAB_TRAVERSAL,
        name="GlyphGrid",
    ):
        super().__init__(parent, id, pos, size, style, name)
        self.SetMinSize(wx.Size(256, 256))
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_LISTBOX))
        self._imageSize = 48
        self._cellCaption = "name"
        self._cellCaptionHeight = 12
        self._visibleGlyphs = set()
        self._observedGlyphs = set()
        self._font = None
        self._glyphNames: List[str] = []
        # self._cells = []
        self._pointed = -1
        self._selector = None
        self._currenter = None
        self._skipExportMarker = None
        self._selectedIndex = -1
        self._mouseeventhandled = False
        self._searchText = ""

        self._showTooltip = False
        self._tooltipWin = None
        self._menu = None
        self._notifications = ("Glyph.Changed", "Glyph.NameChanged")

        self.brushBackground = wx.TheBrushList.FindOrCreateBrush(
            self.GetBackgroundColour(), wx.SOLID
        )

        # Connect Events
        #  Window
        self.Bind(wx.EVT_SET_FOCUS, self.on_SET_FOCUS)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_LEAVE_WINDOW)
        self.Bind(wx.EVT_PAINT, self.on_PAINT)
        self.Bind(wx.EVT_SIZE, self.on_SIZE)
        #  Mouse
        self.Bind(wx.EVT_LEFT_DCLICK, self.on_LEFT_DCLICK)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_LEFT_DOWN)
        self.Bind(wx.EVT_LEFT_UP, self.on_LEFT_UP)
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_RIGHT_DOWN)
        self.Bind(wx.EVT_MOTION, self.on_MOTION)
        # Keyboard
        self.Bind(wx.EVT_KEY_DOWN, self.on_KEY_DOWN)
        self.Bind(wx.EVT_CHAR, self.on_CHAR)

        # hack: force the contextMenu to be build, enable del key to delete glyphs
        self.contextMenu

    def __repr__(self):
        return f"<GlyphGrid of {self.document.title}>"

    def __len__(self):
        return len(self.glyphNames)

    def __del__(self):
        print("GlyphGrid.__del__")
        self.contextMenu.glyphGrid = None
        self.contextMenu.Destroy()

    # -------------------------------------------------------------------------
    # properties
    # -------------------------------------------------------------------------

    @property
    def app(self):
        """
        The running workbench application
        """
        return wx.GetApp()

    @property
    def fontWindow(self) -> UfoFontWindow:
        return self.GrandParent

    @property
    def font(self) -> Font:
        """
        The font shown in this GlyphGrid.
        """
        return self._font

    @font.setter
    def font(self, value: Font):
        assert self._font is None
        assert isinstance(value, Font)
        assert (
            value == self.document.font
        ), f"expected {self.document.font}, got {value}"
        self._font = value
        self._font.addObserver(self, "handleNotification", "Font.GlyphOrderChanged")
        for notification in (
            "Layer.GlyphAdded",
            "Layer.GlyphDeleted",
            "Layer.GlyphSelectionChanged",
            "Layer.GlyphNameChanged",
        ):
            self._font._glyphSet.addObserver(self, "handleNotification", notification)
        # with Pool(processes=round(cpu_count() * 0.6)) as pool:
        #     for glyph in self._font:
        #         pool.apply_async(
        #             glyph.getRepresentation,
        #             (
        #                 "bitmap",
        #                 self.cellWidth,
        #                 self.cellHeight,
        #                 self.captionHeight,
        #             ),
        #         )
        #     pool.close()
        #     pool.join()
        self.updateProp()
        self.SendSizeEvent()
        self.Refresh()
        # wx.CallLater(1000, self._generateBitmaps)

    @font.deleter
    def font(self):
        if self._font is not None:
            for notification in (
                "Layer.GlyphAdded",
                "Layer.GlyphDeleted",
                "Layer.GlyphSelectionChanged",
                "Layer.GlyphNameChanged",
            ):
                self._font._glyphSet.removeObserver(self, notification)
            self._font.removeObserver(self, "Font.GlyphOrderChanged")
            self._font = None

    # def _generateBitmaps(self) -> None:
    #     with Pool(processes=round(cpu_count() * 0.6)) as pool:
    #         for glyph in self._font:
    #             pool.apply_async(
    #                 glyph.getRepresentation,
    #                 (
    #                     "bitmap",
    #                     self.cellWidth,
    #                     self.cellHeight,
    #                     self.captionHeight,
    #                 ),
    #             )
    #         pool.close()
    #         pool.join()

    @property
    def document(self) -> UfoDocument:
        return self.fontWindow.document

    @property
    def view(self) -> UfoFontView:
        return self.fontWindow.view

    # @property
    # def cells(self):
    #     return self._cells

    @property
    def glyphNames(self) -> List[str]:
        font = self.font
        if not font:
            return []
        if not self._glyphNames:
            names = [g for g in set(font.glyphOrder) if g in font]
            names.sort(key=font.glyphOrder.index)
            other = list(font.keys() - set(names))
            other.sort()
            self._glyphNames = names + other
        if self._searchText:
            self._glyphNames = [g for g in self._glyphNames if self._searchText in g]
        return self._glyphNames

    @property
    def selectedIndex(self):
        return self._selectedIndex

    @selectedIndex.setter
    def selectedIndex(self, index):
        if self._selectedIndex != index:
            if 0 > index >= len(self.glyphNames):
                raise IndexError
            old = self._selectedIndex
            self._selectedIndex = index
            self.refreshCellIndex(old)
            self.refreshCellIndex(self._selectedIndex)

    @property
    def currentGlyph(self) -> Optional[Glyph]:
        if self._font:
            index = self._selectedIndex
            if index >= 0:
                name = self.glyphNames[index]
                if name in self._font:
                    return self._font[name]

    @property
    def cellWidth(self) -> int:
        return self._imageSize

    @property
    def cellHeight(self) -> int:
        if self._cellCaption is None:
            return self._imageSize
        else:
            return self._imageSize + self._cellCaptionHeight

    @property
    def captionHeight(self) -> int:
        return self._cellCaptionHeight

    @property
    def collCount(self) -> int:
        cols = int(self.GetClientSize().GetWidth() / self.cellWidth)
        if cols == 0:
            cols = 1
        return cols

    @property
    def rowCount(self) -> int:
        cols = self.collCount
        count = len(self.glyphNames)
        rows = int(count / cols)
        if cols * rows < count:
            rows += 1
        return rows

    @property
    def pointed(self):
        """Index of cell the mouse cursor is in"""
        return self._pointed

    @pointed.setter
    def pointed(self, index):
        if index != self._pointed:
            self._pointed = index

    @pointed.deleter
    def pointed(self) -> int:
        self._pointed = -1

    @property
    def selector(self) -> wx.Bitmap:
        """Bitmap used to mark selected cells."""
        if self._selector is None:
            r, g, b, __ = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT).Get()
            blend = lambda a: wx.Colour(r, g, b, alpha=a)
            w = self.cellWidth - 1
            h = self.cellHeight - 1
            bitmap = wx.Bitmap.FromRGBA(w, h)
            dc = wx.MemoryDC(bitmap)
            gc = wx.GraphicsContext.Create(dc)
            x = w / 2
            y = h - w + x
            radius = sqrt(x**2 + y**2)
            stops = wx.GraphicsGradientStops(blend(0), blend(220))
            stops.Add(blend(10), 0.2)
            stops.Add(blend(180), 0.8)
            brush = gc.CreateRadialGradientBrush(x, y, x, y, radius, stops)
            gc.SetBrush(brush)
            gc.DrawRectangle(0, 0, w, h)
            dc.SelectObject(wx.NullBitmap)
            self._selector = bitmap
        return self._selector

    @property
    def currentMarker(self) -> wx.Bitmap:
        """Bitmap used to mark the current cell."""
        if self._currenter is None:
            self._currenter = wx.Bitmap.FromRGBA(self.cellWidth, self.cellHeight)
            dc = wx.MemoryDC(self._currenter)
            gc = wx.GraphicsContext.Create(dc)
            c = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)
            gc.SetPen(
                wx.ThePenList.FindOrCreatePen(
                    wx.Colour(c.red, c.green, c.blue, alpha=220), 1, wx.SOLID
                )
            )
            border = gc.CreatePath()
            border.AddRectangle(0, 0, self.cellWidth - 2, self.cellHeight - 2)
            gc.StrokePath(border)
            dc.SelectObject(wx.NullBitmap)
        return self._currenter

    @property
    def skipExportMarker(self) -> wx.Bitmap:
        """Bitmap used to mark the cells of glyphs which are skiped for export."""
        if self._skipExportMarker is None:
            size = 12
            self._skipExportMarker = wx.Bitmap.FromRGBA(size, size)
            dc = wx.MemoryDC(self._skipExportMarker)
            gc = wx.GraphicsContext.Create(dc)
            gc.SetPen(
                wx.ThePenList.FindOrCreatePen(
                    wx.Colour(255, 0, 0, alpha=200), 2, wx.SOLID
                )
            )
            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.DrawEllipse(1, 1, size - 2, size - 2)
            gc.DrawLines([(1, size / 2), (size - 1, size / 2)])
            dc.SelectObject(wx.NullBitmap)
        return self._skipExportMarker

    @property
    def showTooltip(self) -> bool:
        return self._showTooltip

    @showTooltip.setter
    def showTooltip(self, value):
        assert isinstance(value, bool)
        self._showTooltip = value
        if value and self._tooltipWin is None:
            self._tooltipWin = wx.ToolTip(" " * 100 + "\n" * 50)
            self._tooltipWin.SetDelay(1000)
            self.SetToolTip(self._tooltipWin)
        if self._tooltipWin is not None:
            self._tooltipWin.Enable(value)

    @property
    def contextMenu(self) -> GlyphGridContextMenu:
        if self._menu is None:
            self._menu = GlyphGridContextMenu(self)
        return self._menu

    @property
    def paintRect(self) -> wx.Rect:
        """
        Returns The Paint Bounding Rect For The on_PAINT() Method.
        """
        size = self.GetClientSize()
        rect = wx.Rect(0, 0, size.GetWidth(), size.GetHeight())
        rect.x, rect.y = self.GetViewStart()
        xu, yu = self.GetScrollPixelsPerUnit()
        rect.x = rect.x * xu
        rect.y = rect.y * yu
        return rect

    @property
    def searchText(self) -> str:
        return self._searchText

    @searchText.setter
    def searchText(self, text: str) -> None:
        del self.font.selectedGlyphs
        self._searchText = text
        self._glyphNames = []
        self.SendSizeEvent()
        # self.Refresh()

    @searchText.deleter
    def searchText(self):
        self._searchText = ""
        self._glyphNames = []
        self.SendSizeEvent()
        # self.Refresh()

    # -------------------------------------------------------------------------
    # notification handling
    # -------------------------------------------------------------------------

    def updateObservation(self):
        font = self.font
        for glyphName in self._observedGlyphs - self._visibleGlyphs:
            if glyphName in font:
                for notification in self._notifications:
                    font[glyphName].removeObserver(self, notification)
        for glyphName in self._visibleGlyphs - self._observedGlyphs:
            if glyphName in font:
                for notification in self._notifications:
                    font[glyphName].addObserver(
                        self, "handleNotification", notification
                    )
        self._observedGlyphs = set(self._visibleGlyphs)

    def handleNotification(self, notification):
        if notification.name == "Layer.GlyphSelectionChanged":
            for name in [
                n for n in notification.data["unselected"] if n in self._observedGlyphs
            ]:
                self.refreshGlyphName(name)
            for name in [
                n for n in notification.data["selected"] if n in self._observedGlyphs
            ]:
                self.refreshGlyphName(name)
        elif notification.name in ("Layer.GlyphAdded", "Layer.GlyphDeleted"):
            self._glyphNames = []
            self.updateProp()
            self.SendSizeEvent()
        elif notification.name == "Glyph.NameChanged":
            old = notification.data["oldValue"]
            new = notification.data["newValue"]
            if old in self._visibleGlyphs:
                self._visibleGlyphs.remove(old)
                self._visibleGlyphs.add(new)
            if old in self._observedGlyphs:
                self._observedGlyphs.remove(old)
                self._observedGlyphs.add(new)
            self._glyphNames = []
        elif notification.name == "Glyph.Changed":
            self.refreshGlyphName(notification.object.name)
        elif notification.name == "Layer.GlyphNameChanged":
            self._glyphNames = []
        elif notification.name == "Font.GlyphOrderChanged":
            self._glyphNames = []
        else:
            print(f"unhandled notification: {notification}")
        if not self._glyphNames:
            self.Refresh()

    # -------------------------------------------------------------------------
    # Public methods
    # -------------------------------------------------------------------------

    def CanCopy(self) -> bool:
        """
        Return True if something can be copied to the clipboard
        """
        if self.font is not None and self.font.selectedGlyphNames:
            return True
        return False

    def Copy(self) -> None:
        """
        Copy names of selected glyphs to the clipboard
        """
        glyphNames = [g for g in self.glyphNames if g in self.font.selectedGlyphNames]
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(" ".join(glyphNames)))
            wx.TheClipboard.Close()
        else:
            wx.LogError("Unable to open the clipboard")

    def CanFind(self) -> bool:
        return self.font is not None

    def doFind(self) -> None:
        glyphName = None
        dlg = FindGlyphDialog(self, self.font, allowSelection=True)
        if dlg.ShowModal() == wx.ID_OK:
            glyphName = dlg.selctedGlyph
        dlg.Destroy()
        if glyphName:
            self.font.selectedGlyphNames = [glyphName]
            self.selectedIndex = self.glyphNames.index(glyphName)
            self.ScrollToSelected()

    def deleteSelectedGlyphs(self):
        font = self.font
        with DeleteGlyphsDialog(font.selectedGlyphCount) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                for glyph in font.selectedGlyphs:
                    for notification in self._notifications:
                        glyph.removeObserver(self, notification)
                    name = glyph.name
                    if name in self._observedGlyphs:
                        self._observedGlyphs.remove(name)
                    if name in font.componentReferences:
                        for compositeName in font.componentReferences[name]:
                            if compositeName in font:
                                composite = font[compositeName]
                                for component in composite.components:
                                    if component.baseGlyph == name:
                                        if dlg.component_handling == "decompose":
                                            composite.decomposeComponent(component)
                                        else:
                                            composite.removeComponent(component)
                    del font[name]

    def getCellIndex(self, x: int, y: int) -> int:
        """
        Returns The Cell Index At Position (x, y).
        """
        col = int(x / self.cellWidth)
        if col >= self.collCount:
            return -1
        row = -1
        while y > 0:
            row = row + 1
            y = y - self.cellHeight
        if row < 0:
            row = 0
        index = row * self.collCount + col
        if index >= len(self):
            index = -1
        # log.debug("getCellIndex -> %s", index)
        return index

    def updateProp(self, checkSize: bool = True):
        width = self.GetClientSize().GetWidth()
        self.SetVirtualSize(
            (self.collCount * self.cellWidth, self.rowCount * self.cellHeight)
        )
        self.SetScrollRate(self.cellWidth, self.cellHeight)
        self.SetSizeHints(self.cellWidth, self.cellHeight)
        if checkSize and width != self.GetClientSize().GetWidth():
            self.updateProp(False)

    def IsSelected(self, index) -> bool:
        """Returns Whether A Cell Is Selected Or Not."""
        return self.font[self.glyphNames[index]].selected

    def SelectAll(self) -> None:
        with wx.BusyCursor():
            self.font.selectedGlyphNames = self.glyphNames

    def refreshCellIndex(self, index: int):
        """refresh cell with given index"""
        width = self.cellWidth
        height = self.cellHeight
        col = index % self.collCount
        row = int(index / self.collCount)
        tx = col * width
        ty = row * height
        tx, ty = self.CalcScrolledPosition(tx, ty)
        rect = wx.Rect(tx, ty, width, height)
        if self.ClientRect.Intersects(rect):
            self.RefreshRect(rect)

    def refreshGlyphName(self, name: str):
        """refresh cell with given glyph name"""
        if name in self.glyphNames:
            self.refreshCellIndex(self.glyphNames.index(name))

    def GetSelection(self, selIndex: int = -1):
        """Returns The Selected Cell."""
        return (
            selIndex == -1 and [self.selectedIndex] or [self._selectedarray[selIndex]]
        )[0]

    def ScrollToSelected(self) -> None:
        """Scrolls The wx.ScrolledWindow To The Cell Selected."""
        if self.GetSelection() == -1:
            return
        # get row
        row = int(self.GetSelection() / self.collCount)
        # calc position to scroll view
        paintRect = self.paintRect
        y1 = row * self.cellHeight
        y2 = y1 + self.cellHeight
        if y1 < paintRect.GetTop():
            sy = y1  # scroll top
        elif y2 > paintRect.GetBottom():
            sy = y2 - paintRect.height  # scroll bottom
        else:
            return
        # scroll view
        xu, yu = self.GetScrollPixelsPerUnit()
        sy = sy / yu + (sy % yu and [1] or [0])[0]  # convert sy to scroll units
        x, y = self.GetViewStart()
        self.Scroll(x, round(sy))

    def startDragOperation(self):
        # create a composite object to hold multiple data representations
        dataObject = wx.DataObjectComposite()
        dataObject.Add(wx.TextDataObject(repr(self.font.selectedGlyphNames)))
        glyphNameObject = wx.CustomDataObject("application.UFO-WB.glyphNames")
        glyphNameObject.Data = pickle.dumps(
            {"font": id(self.font), "glyphs": self.font.selectedGlyphNames}
        )
        dataObject.Add(glyphNameObject)
        dropSource = wx.DropSource(self)
        dropSource.SetData(dataObject)
        dropSource.DoDragDrop(wx.Drag_CopyOnly)

    # -------------------------------------------------------------------------
    # Event handler methods
    # -------------------------------------------------------------------------

    def on_SET_FOCUS(self, event):
        if self.app.documentManager.currentView != self.view:
            wx.LogDebug(
                "%r on_SET_FOCUS: %r %r"
                % (self, self.app.documentManager.currentView, self.view)
            )
            self.view.Activate()
        event.Skip()

    def on_PAINT(self, event):
        """
        Handles The wx.EVT_PAINT Event For FontWindow.
        """
        if self.IsShown():
            dc = wx.PaintDC(self)
            self.PrepareDC(dc)
            row = -1
            self._visibleGlyphs.clear()
            skipExportGlyphs = []
            if self.font is not None:
                skipExportGlyphs = self.font.lib.get("public.skipExportGlyphs", [])
            for index in range(len(self)):
                col = index % self.collCount
                if col == 0:
                    row += 1
                tx = col * self.cellWidth
                ty = row * self.cellHeight
                # visible?
                if not self.paintRect.Intersects(
                    wx.Rect(tx, ty, self.cellWidth, self.cellHeight)
                ):
                    continue
                glyphName = self.glyphNames[index]
                log.debug("Glyph: %r", glyphName)
                glyph = self.font[glyphName]
                bitmap = wx.Bitmap.FromRGBA(self.cellWidth, self.cellHeight)
                bitmapdata = zlib.decompress(
                    glyph.getRepresentation(
                        "bitmap",
                        width=self.cellWidth,
                        height=self.cellHeight,
                        captionHeight=self.captionHeight,
                    )
                )
                bitmap.CopyFromBuffer(bitmapdata, wx.BitmapBufferFormat_RGBA)
                dc.DrawBitmap(bitmap, tx, ty)
                if glyph.dirty:
                    dc.SetBrush(wx.BLACK_BRUSH)
                    dc.DrawRectangle(tx, ty + self.captionHeight, self.cellWidth - 1, 2)
                if glyphName in skipExportGlyphs:
                    x = tx + self.cellWidth - self.skipExportMarker.GetWidth() - 2
                    y = ty + self.captionHeight + 2
                    dc.DrawBitmap(self.skipExportMarker, x, y)
                if glyph.selected:
                    memDC = wx.MemoryDC()
                    memDC.SelectObjectAsSource(self.selector)
                    dc.Blit(
                        xdest=tx,
                        ydest=ty,
                        width=self.selector.GetWidth(),
                        height=self.selector.GetHeight(),
                        source=memDC,
                        xsrc=0,
                        ysrc=0,
                        # logicalFunc=wx.INVERT,
                        useMask=True,
                    )
                    # dc.DrawBitmap(self.selector, tx, ty)
                if index == self.selectedIndex:
                    dc.DrawBitmap(self.currentMarker, tx, ty)
                self._visibleGlyphs.add(glyphName)
            self.updateObservation()

    def on_SIZE(self, event):
        """
        Handles The wx.EVT_SIZE Event For FontWindow.
        """
        self.updateProp()
        if self.IsShown():
            self.ScrollToSelected()
            self.Refresh()

    def on_LEFT_DCLICK(self, event):
        """
        Handles The wx.EVT_LEFT_DCLICK Events For ThumbnailCtrl.
        """
        if self.app.documentManager.currentView != self.view:
            self.view.Activate()
        x, y = self.CalcUnscrolledPosition(event.GetX(), event.GetY())
        self.selectedIndex = self.getCellIndex(x, y)
        if self.selectedIndex >= 0:
            self.font.showGlyph(self.glyphNames[self.selectedIndex])

    def on_LEFT_DOWN(self, event):
        """
        Handles The wx.EVT_LEFT_DOWN Events For ThumbnailCtrl.
        """
        wx.LogDebug("%r on_LEFT_DOWN" % self)
        if self.app.documentManager.currentView != self.view:
            self.view.Activate()
        x, y = self.CalcUnscrolledPosition(event.GetX(), event.GetY())
        # get item number to select
        lastselected = self.selectedIndex
        self.selectedIndex = self.getCellIndex(x, y)
        self._mouseeventhandled = False
        selection = [self.glyphNames.index(g) for g in self.font.selectedGlyphNames]
        update = False
        if event.ControlDown():
            if self.selectedIndex == -1:
                self._mouseeventhandled = True
            elif self.IsSelected(self.selectedIndex):
                selection.remove(self.selectedIndex)
                update = True
                self._mouseeventhandled = True
            elif not self.IsSelected(self.selectedIndex):
                selection.append(self.selectedIndex)
                update = True
                self._mouseeventhandled = True
        elif event.ShiftDown():
            if self.selectedIndex != -1:
                begindex = self.selectedIndex
                endindex = lastselected
                if lastselected < self.selectedIndex:
                    begindex = lastselected
                    endindex = self.selectedIndex
                selection = []
                for ii in range(begindex, endindex + 1):
                    selection.append(ii)
                update = True
            self.selectedIndex = lastselected
            self._mouseeventhandled = True
        else:
            # print(
            #     f"selectedIndex: {self.selectedIndex}, {self.glyphNames[self.selectedIndex]}"
            # )
            if self.selectedIndex == -1:
                update = len(selection) > 0
                selection = []
                self._mouseeventhandled = True
            elif self.selectedIndex in selection:
                self.startDragOperation()
            elif len(selection) <= 1:
                update = len(selection) == 0 or selection[0] != self.selectedIndex
                # try:
                #     update = len(selection) == 0 or selection[0] != self.selectedIndex
                # except:
                #     update = True
                selection = [self.selectedIndex]
                self._mouseeventhandled = True
        if update:
            self.ScrollToSelected()
            self.font.selectedGlyphNames = [self.glyphNames[i] for i in selection]
        self.SetFocus()

    def on_LEFT_UP(self, event):
        """
        Handles The wx.EVT_LEFT_UP Events For ThumbnailCtrl.
        """
        # get item number to select
        x, y = self.CalcUnscrolledPosition(event.GetX(), event.GetY())
        lastselected = self.selectedIndex
        self.selectedIndex = self.getCellIndex(x, y)
        if not self._mouseeventhandled:
            selection = [self.glyphNames.index(g) for g in self.font.selectedGlyphNames]
            if event.ControlDown():
                if self.selectedIndex in selection:
                    selection.remove(self.selectedIndex)
                self.selectedIndex = -1
            else:
                selection = [self.selectedIndex]
            self.ScrollToSelected()
            self.font.selectedGlyphNames = [
                self.glyphNames[i] for i in selection if i >= 0
            ]
        if event.ShiftDown():
            self.selectedIndex = lastselected

    def on_RIGHT_DOWN(self, event):
        wx.LogDebug("on_RIGHT_DOWN")
        self.contextMenu.UpdateUI()
        self.PopupMenu(self.contextMenu)

    def on_MOTION(self, event):
        """
        Handles The wx.EVT_MOTION Event For ThumbnailCtrl.
        """
        x, y = self.CalcUnscrolledPosition(event.GetX(), event.GetY())
        sel = self.getCellIndex(x, y)
        if sel == self.pointed:
            if self.showTooltip and sel >= 0:
                self._tooltipWin.SetTip(
                    "Glyph Index: %d\nGlyph Name: %s" % (sel, self.glyphNames[sel])
                )
            event.Skip()
            return
            # update cell
        self.pointed = sel
        if event.LeftIsDown():
            lastselected = self.selectedIndex
            if self.selectedIndex != -1:
                begindex = sel
                endindex = lastselected
                if lastselected < sel:
                    begindex = lastselected
                    endindex = sel
                selection = range(begindex, endindex + 1)
                self.font.selectedGlyphNames = [self.glyphNames[i] for i in selection]
            self.selectedIndex = lastselected
            self._mouseeventhandled = True
        event.Skip()

    def on_LEAVE_WINDOW(self, event):
        del self.pointed

    def on_KEY_DOWN(self, event):
        should_skip_event = True
        unicodeKey = event.GetUnicodeKey()
        isCharacter = False
        if unicodeKey == wx.WXK_NONE:
            key = event.KeyCode
        else:
            key = chr(unicodeKey)
            isCharacter = True
        # print(f"key: {key}, isCharacter: {isCharacter}, unicodeKey: {unicodeKey}")
        if isCharacter:
            if unicodeKey == wx.WXK_RETURN:
                self.font.showGlyph(self.glyphNames[self.selectedIndex])
                self.SetFocus()
                event.Skip()
                return
            glyphNames = self.font.unicodeData.get(unicodeKey)
            if glyphNames:
                glyphName = glyphNames[0]
                self.font.selectedGlyphNames = [glyphName]
                self.selectedIndex = self.glyphNames.index(glyphName)
                self.ScrollToSelected()
        else:
            new_index = None
            if key == wx.WXK_RIGHT:
                new_index = self.selectedIndex + 1
            elif key == wx.WXK_LEFT:
                new_index = self.selectedIndex - 1
            elif key == wx.WXK_DOWN:
                new_index = self.selectedIndex + self.collCount
            elif key == wx.WXK_UP:
                new_index = self.selectedIndex - self.collCount
            # else:
            #     print(key)
            if new_index is not None:
                old_index = self.selectedIndex
                try:
                    self.selectedIndex = new_index
                except IndexError:
                    wx.Bell()
                if event.ShiftDown():
                    idx = [old_index, new_index]
                    idx.sort()
                    self.font.selectedGlyphNames += self.glyphNames[idx[0] : idx[1] + 1]
                else:
                    self.font.selectedGlyphNames = [self.glyphNames[self.selectedIndex]]
                self.ScrollToSelected()
                should_skip_event = False
        if should_skip_event:
            event.Skip()

    def on_CHAR(self, event):
        event.Skip()


class GlyphGridPage(wx.Panel):
    """
    Implementation of the main Glyphs page.
    Contains:
    - GlyphGrid
    - GlyphGridStatusPanel
    """

    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.TAB_TRAVERSAL,
        name="GlyphGridPage",
    ):
        super().__init__(parent, id, pos, size, style, name)
        self._font = None
        self.Freeze()
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.glyphGridPanel = GlyphGrid(self)
        sizer.Add(self.glyphGridPanel, 1, wx.EXPAND, 0)
        self.glyphGridStatus = GlyphGridStatusPanel(self)
        sizer.Add(self.glyphGridStatus, 0, wx.EXPAND, 0)
        self.SetSizer(sizer)
        self.Layout()
        sizer.Fit(self)
        self.Thaw()
        self.Bind(wx.EVT_SET_FOCUS, self.on_SET_FOCUS)

    @property
    def font(self):
        """The wbDefcon Font object of this InfoPage"""
        return self._font

    @font.setter
    def font(self, value):
        assert self._font is None
        assert isinstance(value, Font)
        assert value == self.Parent.font
        self._font = value
        log.debug("Font %r set for %r", self._font, self)
        self.glyphGridPanel.font = value

    @font.deleter
    def font(self):
        del self.glyphGridPanel.font
        self._font = None

    def on_SET_FOCUS(self, event):
        self.glyphGridPanel.SetFocus()
        event.Skip()
