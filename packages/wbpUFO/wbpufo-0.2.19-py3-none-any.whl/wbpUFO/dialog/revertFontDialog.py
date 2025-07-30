"""
revertFontDialog
===============================================================================

This module provides the dialog which allows selective loading of external changes.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
import logging
import wx

from .revertFontDialogUI import RevertFontDialogUI, LayerPanelUI

if TYPE_CHECKING:
    from wbDefcon import Font

log = logging.getLogger(__name__)

class LayerPanel(LayerPanelUI):
    """
    Component for RevertFontDialog
    """
    def __init__(self, parent, name, info=False, glyphNames=None):
        super().__init__(
            parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.TAB_TRAVERSAL,
            name=name,
        )
        self.lbl_name.LabelText = f"Layer: {name}"
        self.checkBox_info.Value = info
        if glyphNames:
            assert isinstance(glyphNames, (list, tuple))
            self.checkList_glyphNames.SetItems(glyphNames)
            self.checkList_glyphNames.SetCheckedStrings(glyphNames)


class RevertFontDialog(RevertFontDialogUI):
    def __init__(self, parent, font:Font):
        super().__init__(parent)
        externalChanges = font.testForExternalChanges()
        log.debug("externalChanges: %r", externalChanges)
        self.checkBox_font_lib.Value = font.lib.dirty or externalChanges["lib"]
        self.checkBox_font_info.Value = font.info.dirty or externalChanges["info"]
        self.checkBox_groups.Value = font.groups.dirty or externalChanges["groups"]
        self.checkBox_kerning.Value = font.kerning.dirty or externalChanges["kerning"]
        self.checkBox_features.Value = (
            font.features.dirty or externalChanges["features"] or False
        )
        self.checkBox_images.Value = font.images.dirty
        self.checkBox_data.Value = font.data.dirty
        self.checkBox_defaultLayer.Value = externalChanges["layers"]["defaultLayer"]
        self.checkBox_layer_order.Value = externalChanges["layers"]["order"]
        self.layerPanels = []
        modifiedGlyphs = {}
        for layer in font.layers:
            for glyph in layer:
                if glyph.dirty:
                    if layer.name not in modifiedGlyphs:
                        modifiedGlyphs[layer.name] = []
                    modifiedGlyphs[layer.name].append(glyph.name)
        if modifiedGlyphs or externalChanges["layers"]["modified"]:
            sizer_layers_list = wx.BoxSizer(wx.VERTICAL)
            for layer in font.layers:
                externalModifiedGlyphs = []
                externalModifiedInfo = False
                if layer.name in externalChanges["layers"]["modified"]:
                    externalModifiedGlyphs = externalChanges["layers"]["modified"][
                        layer.name
                    ]["modified"]
                    externalModifiedInfo = externalChanges["layers"]["modified"][
                        layer.name
                    ]["info"]
                locallModifiedGlyphs = modifiedGlyphs.get(layer.name, [])
                if externalModifiedGlyphs or locallModifiedGlyphs:
                    allModifiedGlyphs = externalModifiedGlyphs + [
                        g
                        for g in locallModifiedGlyphs
                        if g not in externalModifiedGlyphs
                    ]
                    layerPanel = LayerPanel(
                        self.scrolledWindow_layers,
                        layer.name,
                        info=externalModifiedInfo,
                        glyphNames=allModifiedGlyphs,
                    )
                    sizer_layers_list.Add(
                        layerPanel, 0, wx.BOTTOM | wx.EXPAND | wx.TOP, 5
                    )
                    self.layerPanels.append(layerPanel)

            self.scrolledWindow_layers.SetSizer(sizer_layers_list)
            self.scrolledWindow_layers.Layout()
            sizer_layers_list.Fit(self.scrolledWindow_layers)
        self.Layout()

    @property
    def layerdata(self):
        data = dict(
            order=self.checkBox_layer_order.Value,
            default=self.checkBox_defaultLayer.Value,
        )
        if self.layerPanels:
            layers = {}
            for layerPanel in self.layerPanels:
                layers[layerPanel.Name] = dict(
                    info=layerPanel.checkBox_info.Value,
                    glyphNames=layerPanel.checkList_glyphNames.CheckedStrings,
                )
            data["layers"] = layers
        return data

    # -------------------------------------------------------------------------
    # Event handler methods
    # -------------------------------------------------------------------------

    def on_checkBox_all(self, event):
        for checkBox in (
            self.checkBox_font_lib,
            self.checkBox_font_info,
            self.checkBox_groups,
            self.checkBox_kerning,
            self.checkBox_features,
            self.checkBox_images,
            self.checkBox_data,
            self.checkBox_defaultLayer,
            self.checkBox_layer_order,
        ):
            checkBox.Value = event.IsChecked()
        event.Skip()

    def on_checkBox_single(self, event):
        if not event.IsChecked():
            self.checkBox_all.Value = False
        event.Skip()
