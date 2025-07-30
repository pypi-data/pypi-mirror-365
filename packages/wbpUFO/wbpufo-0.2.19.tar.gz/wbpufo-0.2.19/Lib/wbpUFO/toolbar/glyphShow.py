"""
glyphShow
===============================================================================
"""
import wx
from wx import aui

from ..view.glyph import UfoGlyphView
from . import BaseToolbar

(
    margin,
    metric,
    anchor,
    zone,
    guide,
    fill,
    oncurve,
    offcurve,
    coordinates,
    redarraow,
    layer,
) = range(11)
fontLevel = (metric, zone, guide)
glyphLevel = (margin, anchor, fill, oncurve, offcurve, coordinates, redarraow, layer, guide)


class GlyphShowToolbar(BaseToolbar):
    itemType = wx.ITEM_CHECK

    def __init__(self, parent):
        super().__init__(parent, "GlyphShowToolbar")
        self.appendTool(
            "Show Margins",
            "MARGIN",
            "Show glyph margins in current glyph editor",
            margin,
        )
        self.appendTool(
            "Show Metric",
            "METRIC",
            "Show vertical font metric in current glyph editor",
            metric,
        )
        self.appendTool(
            "Show Zones", "ZONES", "Show alignment zones in current glyph editor", zone
        )
        self.appendTool(
            "Show Guides", "GUIDE", "Show guides in current glyph editor", guide
        )
        self.appendTool(
            "Show Anchors", "ANCHOR", "Show anchors in current glyph editor", anchor
        )
        self.tool_oncurve = self.appendTool(
            "Show On-Curve Points",
            "ONCURVE",
            "Show outline fill in current glyph editor",
            oncurve,
        )
        self.tool_offcurve = self.appendTool(
            "Show Off-Curve Points",
            "OFFCURVE",
            "Show outline fill in current glyph editor",
            offcurve,
        )
        self.tool_coordinates = self.appendTool(
            "Show Coordinates",
            "COORDINATES",
            "Show coordinates in current glyph editor",
            coordinates,
        )
        self.appendTool(
            "Show Red Arrow",
            "REDARROW",
            "Show red arraow hints in current glyph editor",
            redarraow,
        )
        self.appendTool(
            "Show Fill", "FILL", "Show outline fill in current glyph editor", fill
        )
        self.AddSeparator()
        tool = self.appendTool(
            "Show Layer",
            "LAYER_VIEW",
            "Show layer in current glyph editor",
            layer,
            wx.ITEM_NORMAL,
        )
        self.SetToolDropDown(tool.Id, True)
        self.Bind(aui.EVT_AUITOOLBAR_TOOL_DROPDOWN, self.on_Tool, tool)

    def on_menu(self, event):
        item = event.EventObject.FindItemById(event.Id)
        planeStack = self.currentView.frame.canvas.getDrawingPlaneStack(
            item.ItemLabelText
        )
        if planeStack:
            planeStack.visibleInactive = event.IsChecked()

    def on_Tool(self, event):
        tool = self.FindTool(event.Id)
        checked = event.IsChecked()
        i = tool.GetUserData()
        canvas = self.currentView.frame.canvas
        if i == layer:
            self.SetToolSticky(event.Id, True)
            menu = wx.Menu()
            for drawingPlane in canvas.layerPlanes:
                mnuItem = menu.Append(
                    wx.ID_ANY,
                    drawingPlane.name,
                    f"Show {drawingPlane.name} in current glyph editor",
                    wx.ITEM_CHECK,
                )
                mnuItem.Check(drawingPlane.visible)
                mnuItem.Enable(not drawingPlane.active)
                self.Bind(wx.EVT_MENU, self.on_menu, mnuItem)
            self.PopupMenu(menu)
            menu.Destroy()
            self.SetToolSticky(event.Id, False)
            event.Skip()
            return
        planes = []
        if i in fontLevel:
            fontPlanes = canvas.getDrawingPlaneStack("Font")
            if i == metric:
                planes.append(fontPlanes.get("VerticalMetric"))
            elif i == zone:
                planes.append(fontPlanes.get("AlignmentZones"))
            elif i == guide:
                planes.append(fontPlanes.get("FontGuide"))
            for plane in planes:
                plane.visible = event.IsChecked()
        planes = []
        activePlanes = canvas.getActiveDrawingPlaneStack()
        if i == margin:
            planes.append(activePlanes.get("GlyphMetric"))
        elif i == guide:
            planes.append(activePlanes.get("GlyphGuide"))
        elif i == anchor:
            planes.append(activePlanes.get("Anchors"))
            planes.append(activePlanes.get("AnchorLabels"))
        elif i == oncurve:
            planes.append(activePlanes.get("OnCurvePoints"))
            if (
                not checked
                or self.tool_coordinates.State & aui.AUI_BUTTON_STATE_CHECKED
            ):
                planes.append(activePlanes.get("OnCurvePointLabels"))
        elif i == offcurve:
            planes.append(activePlanes.get("OffCurvePoints"))
            if (
                not checked
                or self.tool_coordinates.State & aui.AUI_BUTTON_STATE_CHECKED
            ):
                planes.append(activePlanes.get("OffCurvePointLabels"))
        elif i == coordinates:
            if activePlanes.get("OnCurvePoints").visibleActive:
                planes.append(activePlanes.get("OnCurvePointLabels"))
            if activePlanes.get("OffCurvePoints").visibleActive:
                planes.append(activePlanes.get("OffCurvePointLabels"))
        elif i == redarraow:
            planes.append(activePlanes.get("RedArrows"))
        elif i == fill:
            planes.append(activePlanes.get("GlyphFill"))
        for plane in planes:
            plane.visibleActive = checked
        canvas.SetFocus()

    def on_update_Tool(self, event):
        view = self.currentView
        if isinstance(view, UfoGlyphView):
            canvas = view.frame.canvas
            tool = self.FindTool(event.Id)
            i = tool.GetUserData()
            if i == layer:
                event.Enable(len(canvas.layerPlanes) > 1)
                return
            plane = None
            if i in fontLevel:
                event.Enable(True)
                fontPlanes = canvas.getDrawingPlaneStack("Font")
                if i == metric:
                    plane = fontPlanes.get("VerticalMetric")
                elif i == zone:
                    plane = fontPlanes.get("AlignmentZones")
                elif i == guide:
                    plane = fontPlanes.get("FontGuide")
                if plane:
                    event.Check(plane.visible)
            plane = None
            activePlanes = canvas.getActiveDrawingPlaneStack()
            if i == margin:
                plane = activePlanes.get("GlyphMetric")
            elif i == guide:
                plane = activePlanes.get("GlyphGuide")
            elif i == anchor:
                plane = activePlanes.get("Anchors")
            elif i == oncurve:
                plane = activePlanes.get("OnCurvePoints")
            elif i == offcurve:
                plane = activePlanes.get("OffCurvePoints")
            elif i == redarraow:
                plane = activePlanes.get("RedArrows")
            elif i == fill:
                plane = activePlanes.get("GlyphFill")
            if plane:
                event.Check(plane.visibleActive)
            elif i == coordinates:
                event.Check(
                    activePlanes.get("OnCurvePointLabels").visibleActive
                    or activePlanes.get("OffCurvePointLabels").visibleActive
                )
            event.Enable(True)
            return
        event.Enable(False)
