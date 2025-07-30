"""
layer
===============================================================================
"""
import logging
import time
import wx
from wx import aui

from ..dialog.assignLayerDialog import AssignLayerDialog
from ..dialog.layerDialog import getLayerInfo
from ..view.glyph import UfoGlyphView
from ..view.font import UfoFontView
from . import BaseToolbar

log = logging.getLogger(__name__)

copy_to, copy_from, exchange, clear, assign = range(5)


class LayerToolbar(BaseToolbar):
    def __init__(self, parent):
        super().__init__(parent, "GlyphShowToolbar")

        tool = self.appendTool(
            "Copy to Layer",
            "LAYER_COPY_TO",
            "Copy glyph from current to other layer",
            copy_to,
        )
        self.SetToolDropDown(tool.Id, True)
        self.Bind(aui.EVT_AUITOOLBAR_TOOL_DROPDOWN, self.on_Tool, tool)

        tool = self.appendTool(
            "Copy from Layer",
            "LAYER_COPY_FROM",
            "Copy glyph from other layer to current layer",
            copy_from,
        )
        self.SetToolDropDown(tool.Id, True)
        self.Bind(aui.EVT_AUITOOLBAR_TOOL_DROPDOWN, self.on_Tool, tool)

        tool = self.appendTool(
            "Exchange with Layer",
            "LAYER_EXCHANGE",
            "Exchange glyph with other layer",
            exchange,
        )
        self.SetToolDropDown(tool.Id, True)
        self.Bind(aui.EVT_AUITOOLBAR_TOOL_DROPDOWN, self.on_Tool, tool)

        tool = self.appendTool(
            "Clear Layer",
            "LAYER_CLEAR",
            "Remove glyph from layer",
            clear,
        )
        self.SetToolDropDown(tool.Id, True)
        self.Bind(aui.EVT_AUITOOLBAR_TOOL_DROPDOWN, self.on_Tool, tool)

        self.AddSeparator()

        tool = self.appendTool(
            "Assign Layer",
            "LAYER_ASSIGN",
            "Assign layer from font",
            assign,
        )
        # self.Bind(aui.EVT_AUITOOLBAR_TOOL_DROPDOWN, self.on_Tool, tool)

    def _copy_glyph(self, glyphName, sourceLayerName, targetLayerName):
        view = self.currentView
        font = view.font
        if sourceLayerName not in font.layers:
            log.error("layer '%s' not found in font %r", sourceLayerName, font)
            return False
        sourceLayer = font.layers[sourceLayerName]
        if glyphName not in sourceLayer:
            log.warning(
                "glyph '%s' not found in layer '%s'", glyphName, sourceLayerName
            )
            return False
        sourceGlyph = sourceLayer[glyphName]
        if targetLayerName in font.layers:
            targetLayer = font.layers[targetLayerName]
        else:
            targetLayer = font.newLayer(targetLayerName)
        if glyphName in targetLayer:
            targetGlyph = targetLayer[glyphName]
        else:
            targetGlyph = targetLayer.newGlyph(glyphName)
        targetGlyph.copyDataFromGlyph(sourceGlyph)
        return True

    @staticmethod
    def _getNewLayerInfo(font):
        defaultName = "public.background"
        if defaultName in font.layers:
            defaultName = time.strftime("save %Y.%m.%d-%H:%M")
        return getLayerInfo(defaultName)

    def on_copy_to(self, event):
        targetLayerName = event.EventObject.FindItemById(event.Id).ItemLabelText
        view = self.currentView
        font = view.font
        targetLayerColor = None
        if targetLayerName == "<New Layer>":
            targetLayerName, targetLayerColor = self._getNewLayerInfo(font)
            if not targetLayerName:
                return
        if isinstance(view, UfoGlyphView):
            glyph = view.frame.canvas.glyph
            self._copy_glyph(glyph.name, glyph.layer.name, targetLayerName)
            planes = view.frame.canvas.getDrawingPlaneStack(targetLayerName)
            planes.visibleInactive = True
            view.frame.canvas.Refresh()
            view.frame.canvas.SetFocus()
        if isinstance(view, UfoFontView):
            for glyph in view.font.selectedGlyphs:
                self._copy_glyph(glyph.name, glyph.layer.name, targetLayerName)
        if targetLayerColor:
            font.layers[targetLayerName].color = targetLayerColor

    def on_copy_from(self, event):
        view = self.currentView
        sourceLayerName = event.EventObject.FindItemById(event.Id).ItemLabelText
        if isinstance(view, UfoGlyphView):
            glyph = view.frame.canvas.glyph
            glyph.undoManager.saveState()
            self._copy_glyph(glyph.name, sourceLayerName, glyph.layer.name)
            view.frame.canvas.Refresh()
            view.frame.canvas.SetFocus()
            return
        if isinstance(view, UfoFontView):
            for glyph in view.font.selectedGlyphs:
                self._copy_glyph(glyph.name, sourceLayerName, glyph.layer.name)

    def on_exchange(self, event):
        targetLayerName = event.EventObject.FindItemById(event.Id).ItemLabelText
        view = self.currentView
        font = view.font
        exchange_with_new = False
        targetLayerColor = None
        if targetLayerName == "<New Layer>":
            targetLayerName, targetLayerColor = self._getNewLayerInfo(font)
            if not targetLayerName:
                return
            exchange_with_new = True
        if not exchange_with_new:
            # move glyphs from target to temp layer
            temp_layer = time.strftime("__temp__%Y.%m.%d-%H:%M__")
            if isinstance(view, UfoGlyphView):
                glyph = view.frame.canvas.glyph
                self._copy_glyph(glyph.name, targetLayerName, temp_layer)
                font.layers[targetLayerName][glyph.name].clear()
            elif isinstance(view, UfoFontView):
                for glyphName in view.font.selectedGlyphNames:
                    self._copy_glyph(glyphName, targetLayerName, temp_layer)
                    font.layers[targetLayerName][glyphName].clear()
        # move glyphs from acvite to target layer
        if isinstance(view, UfoGlyphView):
            glyph = view.frame.canvas.glyph
            self._copy_glyph(glyph.name, glyph.layer.name, targetLayerName)
            glyph.clear()
        elif isinstance(view, UfoFontView):
            for glyph in view.font.selectedGlyphs:
                self._copy_glyph(
                    glyph.name, font.layers.defaultLayer.name, targetLayerName
                )
                glyph.clear()
        if not exchange_with_new:
            # move glyphs from temp to active layer
            if isinstance(view, UfoGlyphView):
                glyph = view.frame.canvas.glyph
                self._copy_glyph(glyph.name, temp_layer, glyph.layer.name)
                planes = view.frame.canvas.getDrawingPlaneStack(targetLayerName)
                planes.visibleInactive = True
                view.frame.canvas.Refresh()
                view.frame.canvas.SetFocus()
            elif isinstance(view, UfoFontView):
                for glyphName in view.font.selectedGlyphNames:
                    self._copy_glyph(
                        glyphName, temp_layer, font.layers.defaultLayer.name
                    )
            del font.layers[temp_layer]
        if targetLayerColor:
            font.layers[targetLayerName].color = targetLayerColor
        event.Skip()

    def on_clear(self, event):
        layerName = event.EventObject.FindItemById(event.Id).ItemLabelText
        view = self.currentView
        font = view.font
        layer = font.layers[layerName]
        if isinstance(view, UfoGlyphView):
            glyph = view.frame.canvas.glyph
            del layer[glyph.name]
            view.frame.canvas.Refresh()
            view.frame.canvas.SetFocus()
        if isinstance(view, UfoFontView):
            for glyphName in view.font.selectedGlyphNames:
                if glyphName in layer:
                    del layer[glyphName]
        if len(layer) == 0:
            del font.layers[layerName]

    def _on_assign(self, font):
        with AssignLayerDialog(self.currentView.frame) as dialog:
            dialog.target_font = font
            if dialog.ShowModal() == wx.ID_OK:
                targetLayerName = dialog.target_layer_name
                targetLayerColor = None
                if targetLayerName == "<New Layer>":
                    targetLayerName, targetLayerColor = self._getNewLayerInfo(font)
                    if not targetLayerName:
                        return
                sourceFont = dialog.source_font
                source_layer = sourceFont.layers[dialog.source_layer_name]
                target_font = dialog.target_font
                if targetLayerName in target_font.layers:
                    target_layer = target_font.layers[targetLayerName]
                else:
                    target_layer = target_font.newLayer(targetLayerName)
                for source_glyph in source_layer:
                    name = source_glyph.name
                    if name not in target_font:
                        if not dialog.create_new_glyphs:
                            continue
                        glyph = target_font.newGlyph(name)
                        glyph.unicodes = sourceFont[name].unicodes
                    if name in target_layer:
                        targetGlyph = target_layer[name]
                    else:
                        targetGlyph = target_layer.newGlyph(name)
                    targetGlyph.copyDataFromGlyph(source_glyph)
                if targetLayerColor:
                    font.layers[targetLayerName].color = targetLayerColor

    def on_Tool(self, event):
        self.SetToolSticky(event.Id, True)
        tool = self.FindTool(event.Id)
        i = tool.GetUserData()
        view = self.currentView
        if isinstance(view, UfoGlyphView):
            canvas = view.frame.canvas
            activeLayerName = canvas.getActiveDrawingPlaneStack().name
        elif isinstance(view, UfoFontView):
            activeLayerName = view.font.layers.defaultLayer.name
        if i == assign:
            self._on_assign(view.font)
            event.Skip()
            return
        menu = wx.Menu()
        if i == copy_to:
            for layer in view.font.layers:
                if layer.name != activeLayerName:
                    mnuItem = menu.Append(
                        wx.ID_ANY, layer.name, f"Copy to {layer.name}", wx.ITEM_NORMAL
                    )
                    self.Bind(wx.EVT_MENU, self.on_copy_to, mnuItem)
            menu.AppendSeparator()
            mnuItem = menu.Append(
                wx.ID_ANY, "<New Layer>", "Copy to New Layer", wx.ITEM_NORMAL
            )
            self.Bind(wx.EVT_MENU, self.on_copy_to, mnuItem)
        elif i == copy_from:
            for layer in view.font.layers:
                if layer.name != activeLayerName:
                    mnuItem = menu.Append(
                        wx.ID_ANY, layer.name, f"Copy from {layer.name}", wx.ITEM_NORMAL
                    )
                    self.Bind(wx.EVT_MENU, self.on_copy_from, mnuItem)
        elif i == exchange:
            for layer in view.font.layers:
                if layer.name != activeLayerName:
                    mnuItem = menu.Append(
                        wx.ID_ANY,
                        layer.name,
                        f"Exchange with {layer.name}",
                        wx.ITEM_NORMAL,
                    )
                    self.Bind(wx.EVT_MENU, self.on_exchange, mnuItem)
            menu.AppendSeparator()
            mnuItem = menu.Append(
                wx.ID_ANY, "<New Layer>", "Exchange with New Layer", wx.ITEM_NORMAL
            )
            self.Bind(wx.EVT_MENU, self.on_exchange, mnuItem)
        elif i == clear:
            for layer in view.font.layers:
                if layer.name not in (
                    activeLayerName,
                    view.font.layers.defaultLayer.name,
                ):
                    mnuItem = menu.Append(
                        wx.ID_ANY, layer.name, f"Clear {layer.name}", wx.ITEM_NORMAL
                    )
                    self.Bind(wx.EVT_MENU, self.on_clear, mnuItem)

        self.SetToolSticky(event.Id, False)
        self.PopupMenu(menu)
        menu.Destroy()
        event.Skip()

    def on_update_Tool(self, event):
        tool = self.FindTool(event.Id)
        i = tool.GetUserData()
        view = self.currentView
        if isinstance(view, UfoGlyphView):
            if i in (copy_from, clear):
                event.Enable(len(view.font.layers) > 1)
            else:
                event.Enable(True)
        elif isinstance(view, UfoFontView):
            if view.font is not None and view.font.selectedGlyphCount:
                if i in (copy_from, clear):
                    event.Enable(len(view.font.layers) > 1)
                else:
                    event.Enable(True)
            else:
                event.Enable(False)
        else:
            event.Enable(False)
