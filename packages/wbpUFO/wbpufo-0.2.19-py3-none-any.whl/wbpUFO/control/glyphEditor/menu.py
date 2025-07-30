"""
menu
===============================================================================
"""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

import wx
from booleanOperations import BooleanOperationManager as Boolean
from wbBase.scripting import MacroMenu
from wbDefcon import Anchor, Component, Font, Glyph, Guideline, Point
from wbDefcon.pens import ContourHit

from ...dialog.anchorDialog import AnchorDialog
from ...dialog.componentDialog import ComponentDialog
from ...dialog.findGlyphDialog import FindGlyphDialog
from ...dialog.guidelineDialog import GuidelineDialog
from ...glyphCommand.commandListDialog import CommandListDialog
from .drawing import LayerPlanes

if TYPE_CHECKING:
    from wbBase.application import App
log = logging.getLogger(__name__)

ID = wx.ID_ANY

getBitmap = lambda name: wx.ArtProvider.GetBitmap(name, wx.ART_MENU, (16, 16))


def makeGlyphEditMacroMenu():
    app: App = wx.GetApp()
    cfg = app.config
    macroFolderPath = [
        os.path.join(
            cfg.Read("/Application/SharedData/Dir", app.sharedDataDir),
            "Macro",
            "_system",
            "_glyph",
        ),
        os.path.join(
            cfg.Read("/Application/PrivateData/Dir", app.privateDataDir),
            "Macro",
            "_system",
            "_glyph",
        ),
    ]
    if any(os.path.isdir(p) for p in macroFolderPath):
        return MacroMenu(folderList=macroFolderPath)


glyphEditMacroMenu = makeGlyphEditMacroMenu()


class DefaultEditMenu(wx.Menu):
    def __init__(self, canvas, subject):
        super(DefaultEditMenu, self).__init__()
        self.canvas = canvas
        self.subject = subject
        self.x = None
        self.y = None

        # Ruler --------------------
        item = wx.MenuItem(self, ID, "Show Ruler", "", wx.ITEM_CHECK)
        self.Append(item)
        item.Check(self.canvas.Parent.rulerShown)
        self.Bind(wx.EVT_MENU, self.on_showRuler, id=item.GetId())

        # Metric --------------------
        item = wx.MenuItem(self, ID, "Show Metric", "", wx.ITEM_CHECK)
        self.Append(item)
        item.Check(self.canvas.Parent.metricShown)
        self.Bind(wx.EVT_MENU, self.on_showMetric, id=item.GetId())

        # Note --------------------
        item = wx.MenuItem(self, ID, "Edit Note", "", wx.ITEM_NORMAL)
        item.SetBitmap(getBitmap("NOTE"))
        self.Append(item)
        self.Bind(wx.EVT_MENU, self.on_editNote, id=item.GetId())

        # Command List --------------------
        item = wx.MenuItem(self, ID, "Command List ...", "", wx.ITEM_NORMAL)
        item.SetBitmap(getBitmap("COMMAND_LIST"))
        self.Append(item)
        self.Bind(wx.EVT_MENU, self.on_command_list, id=item.GetId())

        # Anchors --------------------
        self.AppendSeparator()
        if isinstance(self.subject, Anchor):
            # edit
            item = wx.MenuItem(self, ID, "Edit Anchor", "", wx.ITEM_NORMAL)
            self.Append(item)
            self.Bind(wx.EVT_MENU, self.on_editAnchor, id=item.GetId())
            # delete
            item = wx.MenuItem(self, ID, "Delete Anchor", "", wx.ITEM_NORMAL)
            self.Append(item)
            self.Bind(wx.EVT_MENU, self.on_deleteAnchor, id=item.GetId())
        else:
            # add new
            item = wx.MenuItem(self, ID, "Add Anchor", "", wx.ITEM_NORMAL)
            item.SetBitmap(getBitmap("ANCHOR_ADD"))
            self.Append(item)
            self.Bind(wx.EVT_MENU, self.on_addAnchor, id=item.GetId())
            if len(self.glyph.anchors) > 0:
                # clear Anchors
                clearAnchors = wx.MenuItem(
                    self, ID, "Delete All Anchors", "", wx.ITEM_NORMAL
                )
                self.Append(clearAnchors)
                self.Bind(wx.EVT_MENU, self.on_clearAnchors, id=clearAnchors.GetId())

        # Guidelines --------------------
        self.AppendSeparator()
        if isinstance(self.subject, Guideline):
            # edit
            item = wx.MenuItem(self, ID, "Edit Guideline", "", wx.ITEM_NORMAL)
            self.Append(item)
            self.Bind(wx.EVT_MENU, self.on_editGuideline, id=item.GetId())
            # delete
            item = wx.MenuItem(self, ID, "Delete Guideline", "", wx.ITEM_NORMAL)
            self.Append(item)
            self.Bind(wx.EVT_MENU, self.on_deleteGuideline, id=item.GetId())
            if isinstance(self.subject.glyph, Glyph):
                # convert to global guide
                item = wx.MenuItem(
                    self, ID, "Convert to global Guideline", "", wx.ITEM_NORMAL
                )
                self.Append(item)
                self.Bind(
                    wx.EVT_MENU, self.on_convertToGlobalGuideline, id=item.GetId()
                )
        else:
            # add new
            item = wx.MenuItem(self, ID, "Add Guideline", "", wx.ITEM_NORMAL)
            item.SetBitmap(getBitmap("GUIDELINE_ADD"))
            self.Append(item)
            self.Bind(wx.EVT_MENU, self.on_addGuideline, id=item.GetId())
            if len(self.glyph.guidelines) > 0:
                # clear Guidelines
                clearGuidelines = wx.MenuItem(
                    self, ID, "Delete All Guidelines", "", wx.ITEM_NORMAL
                )
                self.Append(clearGuidelines)
                self.Bind(
                    wx.EVT_MENU, self.on_clearGuidelines, id=clearGuidelines.GetId()
                )

        # Components --------------------
        self.AppendSeparator()
        # add new
        item = wx.MenuItem(self, ID, "Add Component", "", wx.ITEM_NORMAL)
        item.SetBitmap(getBitmap("COMPONENT_ADD"))
        self.Append(item)
        self.Bind(wx.EVT_MENU, self.on_addComponent, id=item.GetId())
        if isinstance(self.subject, Component):
            # edit
            item = wx.MenuItem(self, ID, "Edit Component", "", wx.ITEM_NORMAL)
            self.Append(item)
            self.Bind(wx.EVT_MENU, self.on_editComponent, id=item.GetId())
            # properties
            item = wx.MenuItem(self, ID, "Component Properties ...", "", wx.ITEM_NORMAL)
            self.Append(item)
            self.Bind(wx.EVT_MENU, self.on_componentProperties, id=item.GetId())
            # set index
            item = wx.MenuItem(self, ID, "Set Component Index", "", wx.ITEM_NORMAL)
            self.Append(item)
            self.Bind(wx.EVT_MENU, self.on_setComponentIndex, id=item.GetId())
            # decompose
            item = wx.MenuItem(self, ID, "Decompose Component", "", wx.ITEM_NORMAL)
            self.Append(item)
            self.Bind(wx.EVT_MENU, self.on_decomposeComponent, id=item.GetId())
            # delete
            item = wx.MenuItem(self, ID, "Remove Component", "", wx.ITEM_NORMAL)
            self.Append(item)
            self.Bind(wx.EVT_MENU, self.on_deleteComponent, id=item.GetId())
        else:
            if len(self.glyph.components) > 0:
                # decompose all
                item = wx.MenuItem(
                    self, ID, "Decompose All Components", "", wx.ITEM_NORMAL
                )
                self.Append(item)
                self.Bind(wx.EVT_MENU, self.on_decomposeAllComponents, id=item.GetId())
                # clear Components
                item = wx.MenuItem(
                    self, ID, "Remove All Components", "", wx.ITEM_NORMAL
                )
                self.Append(item)
                self.Bind(wx.EVT_MENU, self.on_clearComponents, id=item.GetId())

        # Points --------------------
        if isinstance(self.subject, Point):
            self.AppendSeparator()
            if self.subject.segmentType is not None:
                # Set Startpoint
                item = wx.MenuItem(self, ID, "Set Startpoint", "", wx.ITEM_NORMAL)
                item.SetBitmap(getBitmap("SET_STARTPOINT"))
                self.Append(item)
                self.Bind(wx.EVT_MENU, self.on_setStartPoint, id=item.GetId())
                # set smooth

        # Contours --------------------
        if len(self.glyph) > 0:
            self.AppendSeparator()
            item = wx.MenuItem(self, ID, "Reverse All Contours", "", wx.ITEM_NORMAL)
            item.SetBitmap(getBitmap("REVERSE_ALL_CONTOURS"))
            self.Append(item)
            self.Bind(wx.EVT_MENU, self.on_reverseAllContours, id=item.GetId())
            if isinstance(self.subject, (Point, ContourHit)):
                # change direction
                item = wx.MenuItem(self, ID, "Clockwise Direction", "", wx.ITEM_RADIO)
                self.Append(item)

                item = wx.MenuItem(
                    self, ID, "Counter-Clockwise Direction", "", wx.ITEM_RADIO
                )
                self.Append(item)
                # set index
                item = wx.MenuItem(self, ID, "Set Contour Index", "", wx.ITEM_NORMAL)
                self.Append(item)
                self.Bind(wx.EVT_MENU, self.on_setContourIndex, id=item.GetId())
                # substract
                item = wx.MenuItem(self, ID, "Substract Contour", "", wx.ITEM_NORMAL)
                self.Append(item)
                self.Bind(wx.EVT_MENU, self.on_substractContour, id=item.GetId())
                # get intersection
                item = wx.MenuItem(
                    self, ID, "Get Intersection with Contour", "", wx.ITEM_NORMAL
                )
                item.SetBitmap(getBitmap("GET_INTERSECTION"))
                self.Append(item)
                self.Bind(wx.EVT_MENU, self.on_getIntersection, id=item.GetId())
                # remove intersection
                item = wx.MenuItem(
                    self, ID, "Remove Intersection with Contour", "", wx.ITEM_NORMAL
                )
                item.SetBitmap(getBitmap("DELETE_INTERSECTION"))
                self.Append(item)
                self.Bind(wx.EVT_MENU, self.on_removeIntersection, id=item.GetId())

            item = wx.MenuItem(self, ID, "Remove Overlap", "", wx.ITEM_NORMAL)
            item.SetBitmap(getBitmap("MERGE_CONTOURS"))
            self.Append(item)
            self.Bind(wx.EVT_MENU, self.on_removeOverlap, id=item.GetId())
        # Macro Menu -------------------------------------
        if glyphEditMacroMenu:
            item = self.AppendSubMenu(glyphEditMacroMenu, "Macros")
            item.SetBitmap(wx.ArtProvider.GetBitmap("PYTHON", wx.ART_MENU, (16, 16)))
            item.SetFont(wx.GetApp().TopWindow.Font)

    @property
    def app(self):
        return wx.GetApp()

    @property
    def glyph(self) -> Glyph:
        planeStack = self.canvas.getActiveDrawingPlaneStack()
        if isinstance(planeStack, LayerPlanes):
            return planeStack.glyph
        else:
            return self.canvas.glyph

    @property
    def font(self):
        glyph = self.glyph
        if glyph is not None:
            return glyph.font

    # -------------------------------------------------------------------------
    # Event handler methods
    # -------------------------------------------------------------------------

    def on_showRuler(self, event):
        self.canvas.Parent.showRuler(not self.canvas.Parent.rulerShown)

    def on_showMetric(self, event):
        self.canvas.Parent.showMetric(not self.canvas.Parent.metricShown)

    def on_editNote(self, event):
        with wx.TextEntryDialog(
            self.canvas,
            'Glyph "%s" on layer "%s"' % (self.glyph.name, self.glyph.layer.name),
            "Glyph Note",
            self.glyph.note or "",
            wx.TextEntryDialogStyle | wx.TE_MULTILINE,
            wx.DefaultPosition,
        ) as noteDialog:
            if noteDialog.ShowModal() == wx.ID_OK:
                self.glyph.note = noteDialog.GetValue()
        self.canvas.SetFocus()

    def on_command_list(self, event):
        with CommandListDialog() as dialog:
            dialog.choice_target.SetSelection(0)  # current glyph
            if dialog.ShowModal() == wx.ID_OK:
                commandList = dialog.commandList
                if commandList:
                    dialog.executeCommandList()
        self.canvas.SetFocus()

    # Anchors --------------------

    def on_editAnchor(self, event):
        anchor = self.subject
        anchorDialog = AnchorDialog(self.canvas, anchor.asDict())
        if anchorDialog.ShowModal() == wx.ID_OK:
            d = anchorDialog.anchorDict
            anchor.x = d["x"]
            anchor.y = d["y"]
            anchor.name = d["name"]
            anchor.color = d["color"]
        anchorDialog.Destroy()

    def on_deleteAnchor(self, event):
        self.glyph.removeAnchor(self.subject)

    def on_addAnchor(self, event):
        with AnchorDialog(self.canvas) as anchorDialog:
            anchorDialog.spinCtrl_x.Value = round(self.x)
            anchorDialog.spinCtrl_y.Value = round(self.y)
            if anchorDialog.ShowModal() == wx.ID_OK:
                self.glyph.appendAnchor(anchorDialog.anchorDict)
        self.canvas.SetFocus()

    def on_clearAnchors(self, event):
        self.glyph.clearAnchors()

    # Guidelines --------------------

    def on_editGuideline(self, event):
        guideline = self.subject
        with GuidelineDialog(
            self.canvas, guideline.getDataForSerialization()
        ) as guidelineDialog:
            if guidelineDialog.ShowModal() == wx.ID_OK:
                d = guidelineDialog.guidelineDict
                guideline.x = d["x"]
                guideline.y = d["y"]
                guideline.name = d["name"]
                guideline.color = d["color"]
        self.canvas.SetFocus()

    def on_deleteGuideline(self, event):
        if self.subject.glyph is not None:
            self.glyph.removeGuideline(self.subject)
        else:
            self.font.removeGuideline(self.subject)

    def on_convertToGlobalGuideline(self, event):
        guideline = self.subject
        guidelineDict = guideline.getDataForSerialization()
        self.font.appendGuideline(guidelineDict)
        self.glyph.removeGuideline(self.subject)

    def on_addGuideline(self, event):
        with GuidelineDialog(self.canvas) as guidelineDialog:
            guidelineDialog.spinCtrl_x.Value = round(self.x)
            guidelineDialog.spinCtrl_y.Value = round(self.y)
            if guidelineDialog.ShowModal() == wx.ID_OK:
                self.glyph.appendGuideline(guidelineDialog.guidelineDict)
        self.canvas.SetFocus()

    def on_clearGuidelines(self, event):
        self.glyph.clearGuidelines()

    # Components --------------------

    def on_editComponent(self, event):
        self.subject.font[self.subject.baseGlyph].show()

    def on_componentProperties(self, event):
        component: Component = self.subject
        componentDialog = ComponentDialog(self.canvas, component)
        if componentDialog.ShowModal() == wx.ID_OK:
            component.baseGlyph = componentDialog.baseGlyph
            component.offset = componentDialog.offset
            component.scale = componentDialog.scale
        componentDialog.Destroy()

    def on_setComponentIndex(self, event):
        pointedComponent = self.subject
        glyph: Glyph = self.glyph
        pointedComponentIndex = glyph.componentIndex(pointedComponent)
        with wx.SingleChoiceDialog(
            self.Parent,
            "Select new Component Index",
            "Component Index",
            [str(i) for i in range(len(glyph.components))],
        ) as dialog:
            dialog.Selection = pointedComponentIndex
            if dialog.ShowModal() == wx.ID_OK:
                newComponentIndex = dialog.Selection
                if newComponentIndex != pointedComponentIndex:
                    glyph.undoManager
                    glyph.removeComponent(pointedComponent)
                    glyph.insertComponent(newComponentIndex, pointedComponent)
                    del glyph.undoManager._undoStack[-1]
        self.canvas.SetFocus()

    def on_decomposeComponent(self, event):
        self.glyph.decomposeComponent(self.subject)

    def on_deleteComponent(self, event):
        self.glyph.removeComponent(self.subject)

    def on_addComponent(self, event):
        findGlyphDialog = FindGlyphDialog(self.canvas, self.glyph.layer)
        # findGlyphDialog.layer = self.glyph.layer
        if (
            findGlyphDialog.ShowModal() == wx.ID_OK
            and findGlyphDialog.selctedGlyph is not None
        ):
            component = self.glyph.instantiateComponent()
            component.baseGlyph = findGlyphDialog.selctedGlyph
            self.glyph.appendComponent(component)
        findGlyphDialog.Destroy()

    def on_decomposeAllComponents(self, event):
        self.glyph.decomposeAllComponents()

    def on_clearComponents(self, event):
        self.glyph.clearComponents()

    # Points --------------------

    def on_setStartPoint(self, event):
        for contour in self.glyph:
            if self.subject in contour:
                contour.setStartPoint(contour.index(self.subject))

    # Contours --------------------

    def on_reverseAllContours(self, event):
        for contour in self.glyph:
            contour.reverse()

    def on_setContourIndex(self, event):
        glyph = self.glyph
        pointedContour = None
        if isinstance(self.subject, ContourHit):
            pointedContour = self.subject.contour
            pointedContourIndex = self.subject.contourIndex
        else:
            for contourIndex, contour in enumerate(glyph):
                if self.subject in contour:
                    pointedContour = contour
                    pointedContourIndex = contourIndex
                    break
        if pointedContour:
            with wx.SingleChoiceDialog(
                self.Parent,
                "Select new Contour Index",
                "Contour Index",
                [str(i) for i in range(len(glyph))],
            ) as dialog:
                dialog.Selection = pointedContourIndex
                if dialog.ShowModal() == wx.ID_OK:
                    newContourIndex = dialog.Selection
                    if newContourIndex != pointedContourIndex:
                        glyph.undoManager
                        glyph.removeContour(pointedContour)
                        glyph.insertContour(newContourIndex, pointedContour)
                        if len(glyph.undoManager._undoStack) >= 2:
                            del glyph.undoManager._undoStack[-1]
        self.canvas.SetFocus()

    def on_substractContour(self, event):
        font = self.font
        if font:
            font.holdNotifications()
        glyph = self.glyph
        contours = [c for c in glyph]
        glyph.disableNotifications()
        glyph.undoManager.saveState()
        glyph.clearContours()
        Boolean.difference(
            [c for c in contours if self.subject not in c],
            [c for c in contours if self.subject in c],
            glyph.getPointPen(),
        )
        glyph.round(roundAnchors=False, roundComponents=False)
        glyph.enableNotifications()
        glyph.postNotification("Glyph.ContoursChanged")
        if font:
            font.releaseHeldNotifications()

    def on_getIntersection(self, event):
        font = self.font
        if font:
            font.holdNotifications()
        glyph = self.glyph
        contours = list(glyph)
        glyph.disableNotifications()
        glyph.undoManager.saveState()
        glyph.clearContours()
        Boolean.intersection(
            [c for c in contours if self.subject not in c],
            [c for c in contours if self.subject in c],
            glyph.getPointPen(),
        )
        glyph.round(roundAnchors=False, roundComponents=False)
        glyph.enableNotifications()
        glyph.postNotification("Glyph.ContoursChanged")
        if font:
            font.releaseHeldNotifications()

    def on_removeIntersection(self, event):
        font = self.font
        if font:
            font.holdNotifications()
        glyph = self.glyph
        contours = [c for c in glyph]
        glyph.disableNotifications()
        glyph.undoManager.saveState()
        glyph.clearContours()
        Boolean.xor(
            [c for c in contours if self.subject not in c],
            [c for c in contours if self.subject in c],
            glyph.getPointPen(),
        )
        glyph.round(roundAnchors=False, roundComponents=False)
        glyph.enableNotifications()
        glyph.postNotification("Glyph.ContoursChanged")
        if font:
            font.releaseHeldNotifications()

    def on_removeOverlap(self, event):
        font = self.font
        if font:
            font.holdNotifications()
        glyph = self.glyph
        assert isinstance(glyph, Glyph)
        contours = [c for c in glyph]
        glyph.disableNotifications()
        glyph.clearContours()
        glyph.undoManager.saveState()
        Boolean.union(contours, glyph.getPointPen())
        glyph.round(roundAnchors=False, roundComponents=False)
        glyph.enableNotifications()
        glyph.postNotification("Glyph.ContoursChanged")
        if font:
            font.releaseHeldNotifications()
