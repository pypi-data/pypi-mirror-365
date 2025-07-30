"""
template
===============================================================================

Document Templates for UFOs and imports to UFO WorkBench
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import wbDefcon
import wx
from fontTools.ufoLib import UFOFileStructure
from glyphsLib.builder import to_ufos
from glyphsLib.parser import load
from wbBase.document.template import (
    DEFAULT_TEMPLATE_FLAGS,
    TEMPLATE_NO_CREATE,
    DocumentTemplate,
)

from .document import UfoDocument
from .view.font import UfoFontView
from .view.fontinfo import UfoFontInfoView
from .view.glyph import UfoGlyphView

if TYPE_CHECKING:
    from wbBase.document.manager import DocumentManager


class UfoTemplate(DocumentTemplate):
    """
    Main Template for Unified Font Objects
    """

    def __init__(self, manager: DocumentManager):
        DocumentTemplate.__init__(
            self,
            manager=manager,
            description="UFO (Unified Font Object)",
            filter="*.ufo;*.ufoz",
            dir="",
            ext=".ufo",
            docTypeName="UFO document",
            # viewTypeName="UFO Font View",
            docType=UfoDocument,
            viewType=UfoFontView,
            flags=DEFAULT_TEMPLATE_FLAGS,
            icon=wx.ArtProvider.GetBitmap("UFO_FILE", wx.ART_FRAME_ICON),
        )
        self.viewTypes.append(UfoGlyphView)
        self.viewTypes.append(UfoFontInfoView)


class OTFTemplate(DocumentTemplate):
    """Template for OpenType OTF binary files - import only"""

    def __init__(self, manager: DocumentManager):
        DocumentTemplate.__init__(
            self,
            manager=manager,
            description="OpenType Font (import only)",
            filter="*.otf",
            dir="",
            ext=".ufo",
            docTypeName="UFO document",
            docType=UfoDocument,
            viewType=UfoFontView,
            flags=DEFAULT_TEMPLATE_FLAGS | TEMPLATE_NO_CREATE,
            icon=wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_FRAME_ICON),
        )
        self.viewTypes.append(UfoGlyphView)
        self.viewTypes.append(UfoFontInfoView)


class TTFTemplate(DocumentTemplate):
    """Template for OpenType TTF binary files - import only"""

    def __init__(self, manager: DocumentManager):
        DocumentTemplate.__init__(
            self,
            manager=manager,
            description="TrueType Font (import only)",
            filter="*.ttf",
            dir="",
            ext=".ufo",
            docTypeName="UFO document",
            docType=UfoDocument,
            viewType=UfoFontView,
            flags=DEFAULT_TEMPLATE_FLAGS | TEMPLATE_NO_CREATE,
            icon=wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_FRAME_ICON),
        )
        self.viewTypes.append(UfoGlyphView)
        self.viewTypes.append(UfoFontInfoView)


class VFBTemplate(DocumentTemplate):
    """Template for FontLab VFB files - import only"""

    def __init__(self, manager: DocumentManager):
        DocumentTemplate.__init__(
            self,
            manager=manager,
            description="FontLab file (import only)",
            filter="*.vfb",
            dir="",
            ext=".ufo",
            docTypeName="UFO document",
            docType=UfoDocument,
            viewType=UfoFontView,
            flags=DEFAULT_TEMPLATE_FLAGS | TEMPLATE_NO_CREATE,
            icon=wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_FRAME_ICON),
        )
        self.viewTypes.append(UfoGlyphView)
        self.viewTypes.append(UfoFontInfoView)


class GlyphsTemplate(DocumentTemplate):
    """Template for Glyphs App files - import only"""

    def __init__(self, manager: DocumentManager):
        DocumentTemplate.__init__(
            self,
            manager=manager,
            description="Glyphs App file (import only)",
            filter="*.glyphs",
            dir="",
            ext=".ufo",
            docTypeName="UFO document",
            docType=UfoDocument,
            viewType=UfoFontView,
            flags=DEFAULT_TEMPLATE_FLAGS | TEMPLATE_NO_CREATE,
            icon=wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_FRAME_ICON),
        )

    def CreateDocument(self, path: str, flags: int):
        """
        Creates a new instance of the associated document class (UfoDocument)
        for each master in the Glyphs file
        """
        result = None
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as glyphsFile:
                with wx.BusyInfo("Loading Glyphs File please wait"):
                    glyphsFont = load(glyphsFile)
                    ufos = to_ufos(glyphsFont, ufo_module=wbDefcon)
            result = []
            for font in ufos:
                font._ufoFormatVersion = 3
                font._ufoFileStructure = UFOFileStructure.ZIP
                doc = self._docType()
                doc.template = self.documentManager.FindTemplateByType(UfoTemplate)
                self.documentManager.AddDocument(doc)
                doc.font = font
                if doc.OnCreate(path, flags):
                    doc.set_modificationDate()
                    doc.saved = False
                    doc.modified = False
                    doc.UpdateAllViews(self, ("font loaded", True))
                    result.append(doc)
                else:
                    if doc in self.documentManager.documents:
                        doc.DeleteAllViews()
        return result
