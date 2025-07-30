"""
assignLayerDialog
===============================================================================
"""
import os

import wx
from .assignLayerDialogUI import AssignLayerDialogUI


class AssignLayerDialog(AssignLayerDialogUI):
    def __init__(self, parent):
        super().__init__(parent)
        self.button_sizerOK.SetDefault()
        self._fonts = None
        self.choice_source_font.Set([f[0] for f in self.fonts])
        self.choice_source_font.Selection = 0
        self.choice_source_layer.Set([l.name for l in self.source_font.layers])
        self.choice_source_layer.Selection = 0
        self.choice_target_font.Set([f[0] for f in self.fonts])
        self.choice_target_font.Selection = 0
        self.choice_target_layer.Set(
            [l.name for l in self.target_font.layers if l.name != "public.default"]
        )
        self.choice_target_layer.Append("<New Layer>")
        self.choice_target_layer.Selection = 0

    @property
    def app(self):
        return wx.GetApp()

    @property
    def fonts(self):
        if not self._fonts:
            self._fonts = []
            for doc in self.app.documentManager.documents:
                if doc.typeName == "UFO document":
                    self._fonts.append((self._getFontDisplayName(doc.font), doc.font))
        return self._fonts

    @property
    def source_font(self):
        return self.fonts[self.choice_source_font.Selection][1]

    @property
    def source_layer_name(self):
        return self.choice_source_layer.StringSelection

    @property
    def target_font(self):
        return self.fonts[self.choice_target_font.Selection][1]

    @target_font.setter
    def target_font(self, font):
        for i, f in enumerate(self.fonts):
            if f[1] == font:
                self.choice_target_font.Selection = i
                break
        self.choice_target_layer.Set(
            [l.name for l in self.target_font.layers if l.name != "public.default"]
        )
        self.choice_target_layer.Append("<New Layer>")
        self.choice_target_layer.Selection = 0

    @property
    def target_layer_name(self):
        return self.choice_target_layer.StringSelection

    @property
    def create_new_glyphs(self):
        return self.checkBox_new_glyphs.Value

    @staticmethod
    def _getFontDisplayName(font):
        name = f"{font.info.familyName} {font.info.styleName}"
        if font.path:
            path = os.path.basename(font.path)
        else:
            path = "Not saved yet"
        return f"{name} | {path}"

    # =========================================================================
    # Event Handler
    # =========================================================================

    def on_choice_source_font(self, event):
        self.choice_source_layer.Set([l.name for l in self.source_font.layers])
        self.choice_source_layer.Selection = 0
        event.Skip()

    def on_choice_source_layer(self, event):
        event.Skip()

    def on_choice_target_font(self, event):
        self.choice_target_layer.Set(
            [l.name for l in self.target_font.layers if l.name != "public.default"]
        )
        self.choice_target_layer.Append("<New Layer>")
        self.choice_target_layer.Selection = 0
        event.Skip()

    def on_choice_target_layer(self, event):
        event.Skip()
