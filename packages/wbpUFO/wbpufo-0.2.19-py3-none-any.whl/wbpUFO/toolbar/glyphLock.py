"""
glyphLock
===============================================================================
"""
import wx
from wx import aui

from ..view.glyph import UfoGlyphView
from . import BaseToolbar

contour, component, margin, metric, anchor, zone, guide = range(7)
fontLevel = (metric, zone, guide)
glyphLevel = (margin, anchor, contour, component, guide)


class GlyphLockToolbar(BaseToolbar):
    itemType = wx.ITEM_CHECK

    def __init__(self, parent):
        super().__init__(parent, "GlyphLockToolbar")
        self.appendTool(
            "Lock Margins",
            "MARGIN_LOCK",
            "Lock glyph margins in current glyph editor",
            margin,
        )
        self.appendTool(
            "Lock Metric",
            "METRIC_LOCK",
            "Lock vertical font metric in current glyph editor",
            metric,
        )
        self.appendTool(
            "Lock Zones",
            "ZONES_LOCK",
            "Lock alignment zones in current glyph editor",
            zone,
        )
        self.appendTool(
            "Lock Guides",
            "GUIDE_LOCK",
            "Lock guides in current glyph editor",
            guide,
        )
        self.appendTool(
            "Lock Anchors",
            "ANCHOR_LOCK",
            "Lock anchors in current glyph editor",
            anchor,
        )
        self.appendTool(
            "Lock Contours",
            "OUTLINE_LOCK",
            "Lock contours in current glyph editor",
            contour,
        )
        self.appendTool(
            "Lock Components",
            "COMPONENT_LOCK",
            "Lock components in current glyph editor",
            component,
        )

    def on_Tool(self, event):
        tool:aui.AuiToolBarItem = self.FindTool(event.Id)
        i = tool.GetUserData()
        planes = []
        if i in fontLevel:
            fontPlanes = self.currentView.frame.canvas.getDrawingPlaneStack("Font")
            if i == metric:
                planes.append(fontPlanes.get("VerticalMetric"))
            elif i == zone:
                planes.append(fontPlanes.get("AlignmentZones"))
            elif i == guide:
                planes.append(fontPlanes.get("FontGuide"))
        if i in glyphLevel:
            activePlanes = self.currentView.frame.canvas.getActiveDrawingPlaneStack()
            if i == margin:
                planes.append(activePlanes.get("GlyphMetric"))
            elif i == guide:
                planes.append(activePlanes.get("GlyphGuide"))
            elif i == anchor:
                planes.append(activePlanes.get("Anchors"))
            elif i == contour:
                planes.append(activePlanes.get("OnCurvePoints"))
                planes.append(activePlanes.get("OffCurvePoints"))
                planes.append(activePlanes.get("GlyphOutline"))
            elif i == component:
                planes.append(activePlanes.get("GlyphComponent"))
        for plane in planes:
            plane.locked = event.IsChecked()

    def on_update_Tool(self, event):
        view = self.currentView
        if isinstance(view, UfoGlyphView) and view.document:
            canvas = view.frame.canvas
            tool:aui.AuiToolBarItem = self.FindTool(event.Id)
            i = tool.GetUserData()
            not_yet_supported = (margin, metric, zone)
            planes = []
            if i in not_yet_supported:
                event.Check(True)
                event.Enable(False)
                return
            event.Enable(True)
            if i in fontLevel:
                planes = canvas.getDrawingPlaneStack("Font")
                if i == guide:
                    event.Check(planes.get("FontGuide").locked)
            elif i in glyphLevel:
                planes = canvas.getActiveDrawingPlaneStack()
                if i == metric:
                    event.Check(planes.get("VerticalMetric").locked)
                elif i == zone:
                    event.Check(planes.get("AlignmentZones").locked)
                elif i == margin:
                    event.Check(planes.get("GlyphMetric").locked)
                elif i == guide:
                    event.Check(planes.get("GlyphGuide").locked)
                elif i == anchor:
                    event.Check(planes.get("Anchors").locked)
                elif i == contour:
                    event.Check(planes.get("GlyphOutline").locked)
                elif i == component:
                    event.Check(planes.get("GlyphComponent").locked)
            return
        event.Enable(False)
