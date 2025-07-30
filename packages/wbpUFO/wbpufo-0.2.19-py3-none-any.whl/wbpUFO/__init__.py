from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Tuple

import wbFontParts
import wx
from fontParts import world
from wbBase.document import DOC_NEW, DOC_NO_VIEW, DOC_SILENT
from wbBase.panelManager import toolbarPaneInfo
from wbFontParts import (
    RAnchor,
    RComponent,
    RContour,
    RFeatures,
    RGlyph,
    RGroups,
    RGuideline,
    RImage,
    RInfo,
    RKerning,
    RLayer,
    RLib,
    RPoint,
    RSegment,
    mark,
)

from .dialog.findGlyphDialog import FindGlyphDialog
from .document import UfoDocument
from .panel.glyphViewPanel import GlyphViewPanel, glyphViewPanelInfo
from .template import GlyphsTemplate, OTFTemplate, UfoTemplate, VFBTemplate, TTFTemplate
from .toolbar.command import GlyphCommandToolbar
from .toolbar.editTool import GlyphEditToolbar
from .toolbar.glyphLock import GlyphLockToolbar
from .toolbar.glyphShow import GlyphShowToolbar
from .toolbar.layer import LayerToolbar
from .toolbar.markColor import GlyphMarkToolbar
from .view.font import UfoFontView
from .view.glyph import UfoGlyphView

if TYPE_CHECKING:
    from wbBase.application import App

__version__ = "0.2.19"


def getApp() -> App:
    """
    The currently running Workbench application.
    """
    return wx.GetApp()


# add wbFontParts objects to the world
world.dispatcher["RAnchor"] = RAnchor
world.dispatcher["RComponent"] = RComponent
world.dispatcher["RContour"] = RContour
world.dispatcher["RFeatures"] = RFeatures
world.dispatcher["RGlyph"] = RGlyph
world.dispatcher["RGroups"] = RGroups
world.dispatcher["RGuideline"] = RGuideline
world.dispatcher["RImage"] = RImage
world.dispatcher["RInfo"] = RInfo
world.dispatcher["RKerning"] = RKerning
world.dispatcher["RLayer"] = RLayer
world.dispatcher["RLib"] = RLib
world.dispatcher["RPoint"] = RPoint


def dispatchUItools(app: App) -> None:
    uitools = app.pluginManager.get("uitools")
    if uitools:
        for attr in ("AskString", "AskYesNoCancel", "GetFile", "Message", "PutFile"):
            if hasattr(uitools, attr):
                world.dispatcher[attr] = getattr(uitools, attr)


def CurrentFont() -> Optional[wbFontParts.RFont]:
    doc = getApp().documentManager.currentDocument
    if isinstance(doc, UfoDocument):
        return doc.RFont


world.dispatcher["CurrentFont"] = CurrentFont


def CurrentGlyph() -> Optional[RGlyph]:
    view = getApp().documentManager.currentView
    if view:
        if view.typeName == "UFO Font View":
            glyph = view.frame.glyphGridPanel.currentGlyph
            if glyph is not None:
                return view.document.RFont[glyph.name]
        elif view.typeName == "UFO Glyph View":
            return view.document.RFont.getLayer(view.frame.canvas.glyph.layer.name)[
                view.glyph.name
            ]


world.dispatcher["CurrentGlyph"] = CurrentGlyph


def CurrentAnchors() -> Tuple[RAnchor, ...]:
    """
    :return: Selected anchors in the current glyph.
    """
    glyph = CurrentGlyph()
    if glyph is None:
        return ()
    return glyph.selectedAnchors


world.dispatcher["CurrentAnchors"] = CurrentAnchors


def CurrentComponents() -> Tuple[RComponent, ...]:
    """
    :return: Selected components in the current glyph.
    """
    glyph = CurrentGlyph()
    if glyph is None:
        return ()
    return glyph.selectedComponents


world.dispatcher["CurrentComponents"] = CurrentComponents


def CurrentContours() -> Tuple[RContour, ...]:
    """
    :return: Selected contours in the current glyph.
    """
    glyph = CurrentGlyph()
    if glyph is None:
        return ()
    return glyph.selectedContours


world.dispatcher["CurrentContours"] = CurrentContours


def CurrentPoints() -> Tuple[RPoint, ...]:
    """
    :return: Selected points in the current glyph.
    """
    glyph = CurrentGlyph()
    if glyph is None:
        return ()
    points = []
    for contour in glyph:
        points.extend(contour.selectedPoints)
    return tuple(points)


world.dispatcher["CurrentPoints"] = CurrentPoints


def CurrentSegments() -> Tuple[RSegment, ...]:
    """
    :return: Selected segments in the current glyph.
    """
    glyph = CurrentGlyph()
    if glyph is None:
        return ()
    segments = []
    for contour in glyph:
        segments.extend(contour.selectedSegments)
    return tuple(segments)


world.dispatcher["CurrentSegments"] = CurrentSegments


def CurrentGuidelines() -> Tuple[RGuideline, ...]:
    guidelines = []
    font = CurrentFont()
    if font is not None:
        guidelines.extend(font.selectedGuidelines)
    glyph = CurrentGlyph()
    if glyph is not None:
        guidelines.extend(glyph.selectedGuidelines)
    return tuple(guidelines)


world.dispatcher["CurrentGuidelines"] = CurrentGuidelines


def CurrentLayer() -> Optional[RLayer]:
    view = getApp().documentManager.currentView
    if isinstance(view, UfoFontView):
        return view.document.RFont.defaultLayer
    elif isinstance(view, UfoGlyphView):
        return view.document.RFont.getLayer(view.frame.canvas.glyph.layer.name)


world.dispatcher["CurrentLayer"] = CurrentLayer


def AllFonts(sortOptions=None):
    fontlist = [
        doc.RFont
        for doc in getApp().documentManager.getDocumentsByTypeName("UFO document")
    ]
    fontlist = world.FontList(fontlist)
    if sortOptions is not None:
        fontlist.sortBy(sortOptions)
    return fontlist


world.dispatcher["AllFonts"] = AllFonts


def NewFont(familyName=None, styleName=None, showInterface=True) -> wbFontParts.RFont:
    app = getApp()
    ufoTemplate = None
    for template in app.documentManager.templates:
        if isinstance(template, UfoTemplate):
            ufoTemplate = template
            break
    if ufoTemplate:
        if showInterface:
            flags = DOC_NEW
        else:
            flags = DOC_NEW | DOC_NO_VIEW
        newDoc = ufoTemplate.CreateDocument("", flags)
        if isinstance(newDoc, UfoDocument):
            # newDoc._typeName = ufoTemplate.documentTypeName
            # newDoc.template = ufoTemplate
            newDoc.OnNewDocument()
            font = newDoc.RFont
            title = []
            if familyName is not None:
                font.info.familyName = familyName
                title.append(str(familyName).strip())
            if styleName is not None:
                font.info.styleName = styleName
                title.append(str(styleName).strip())
            if title:
                newDoc.title = "-".join(title)
            return font


world.dispatcher["NewFont"] = NewFont


def OpenFont(path: str, showInterface: bool = True) -> Optional[wbFontParts.RFont :]:
    app = getApp()
    documentManager = app.TopWindow.documentManager
    template = documentManager.FindTemplateForPath(path)
    if isinstance(template, UfoTemplate):
        if showInterface:
            flags = DOC_SILENT
        else:
            flags = DOC_SILENT | DOC_NO_VIEW
        newDoc = documentManager.CreateDocument(path, flags)
        if isinstance(newDoc, UfoDocument):
            return newDoc.RFont


world.dispatcher["OpenFont"] = OpenFont


def RFont(pathOrObject=None, showInterface=True) -> Optional[wbFontParts.RFont :]:
    if pathOrObject is None:
        return NewFont(showInterface=showInterface)
    return OpenFont(pathOrObject, showInterface=showInterface)


world.dispatcher["RFont"] = RFont

# ============================================================================
# fontParts.ui
# ============================================================================


def FindGlyph(aFont, message="Search for a glyph:", title="UFO Workbench"):
    glyphName = None
    with FindGlyphDialog(wx.GetApp().TopWindow, aFont) as dialog:
        if dialog.ShowModal() == wx.ID_OK:
            glyphName = dialog.selctedGlyph
    if glyphName:
        return aFont[glyphName]


def SelectFonts(message="Select fonts:", title="UFO Workbench", allFonts=None):
    result = []
    if allFonts is None:
        allFonts = AllFonts()
    if allFonts:
        from .dialog.selectFontsDialog import SelectFontsDialog

        with SelectFontsDialog(message, title, allFonts) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                result = dialog.selectedFonts
    else:
        wx.LogWarning("Can not select fonts!\n\nNo fonts open.")
    return result


# ============================================================================
# additional stuff
# ============================================================================


def SelectSingleFont(message="Select font:", title="UFO Workbench", allFonts=None):
    result = None
    if allFonts is None:
        allFonts = AllFonts()
    if allFonts:
        from .dialog.selectFontsDialog import SelectFontsDialog

        with SelectFontsDialog(message, title, allFonts) as dialog:
            dialog.listCtrl_fonts.WindowStyle |= wx.LC_SINGLE_SEL
            if dialog.ShowModal() == wx.ID_OK:
                if dialog.selectedFonts:
                    result = dialog.selectedFonts[0]
    else:
        wx.LogWarning("Can not select font!\n\nNo fonts open.")
    return result


def ShowFont(font) -> Optional[UfoDocument]:
    app = getApp()
    ufoTemplate = None
    for template in app.documentManager.templates:
        if isinstance(template, UfoTemplate):
            ufoTemplate = template
            break
    if isinstance(ufoTemplate, UfoTemplate):
        doc = ufoTemplate.CreateDocument("", DOC_NEW)
        if isinstance(doc, UfoDocument):
            doc.font = font
            doc.beginObservation()
            doc.UpdateAllViews(doc, ("font loaded", True))
            return doc
    return None


doctemplates = [UfoTemplate, VFBTemplate, GlyphsTemplate, OTFTemplate, TTFTemplate]

toolbars = [
    (GlyphCommandToolbar, toolbarPaneInfo("Glyph Commands")),
    (GlyphEditToolbar, toolbarPaneInfo("Glyph Tools")),
    (GlyphLockToolbar, toolbarPaneInfo("Glyph Lock")),
    (GlyphMarkToolbar, toolbarPaneInfo("Glyph MarkColor")),
    (GlyphShowToolbar, toolbarPaneInfo("Glyph Show")),
    (LayerToolbar, toolbarPaneInfo("Layer")),
]

panels = [(GlyphViewPanel, glyphViewPanelInfo)]

globalObjects = [
    "AllFonts",
    "AskString",
    "AskYesNoCancel",
    "CurrentAnchors",
    "CurrentComponents",
    "CurrentContours",
    "CurrentFont",
    "CurrentGlyph",
    "CurrentGuidelines",
    "CurrentLayer",
    "CurrentPoints",
    "CurrentSegments",
    "FindGlyph",
    "getCheckList",
    "GetFile",
    "mark",
    "Message",
    "NewFont",
    "OpenFont",
    "PutFile",
    "RFont",
    "RGlyph",
    "SelectFonts",
    "SelectSingleFont",
    "ShowFont",
]

getApp().AddPostInitAction(dispatchUItools)
