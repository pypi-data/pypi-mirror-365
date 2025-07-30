"""
editTool
===============================================================================

Implementation of the Glyph Edit Toolbar
"""
import logging
import time

import wx
from wx import aui

from ..dialog.layerDialog import getLayerInfo
from ..view.glyph import UfoGlyphView
from . import BaseToolbar

log = logging.getLogger(__name__)

(
    edit,
    erase,
    knife,
    meter,
    startpoint,
    reversecontour,
    draw,
    rotate,
    scale,
    rectangle,
    ellipse,
    layer,
) = range(12)


class GlyphEditToolbar(BaseToolbar):
    """Glyph Edit Toolbar"""

    itemType = wx.ITEM_RADIO
    tools = {
        edit: "ToolEdit",
        erase: "ToolErase",
        knife: "ToolKnife",
        meter: "ToolMeter",
        startpoint: "ToolStartpoint",
        reversecontour: "ToolReverse",
        draw: "ToolDraw",
        rectangle: "AddRectangle",
        ellipse: "AddEllipse",
        rotate: "ToolRotate",
        scale: "ToolScale",
        # "ToolZoom",
        # "ToolPan",
        # "MagicWand",
    }

    def __init__(self, parent):
        super().__init__(parent, "GlyphEditToolbar")
        self.appendTool("Edit", "TOOL_EDIT", commandIndex=edit)
        self.appendTool("Erase (Q)", "ERASER", commandIndex=erase)
        self.appendTool("Knife (W)", "TOOL_KNIFE", commandIndex=knife)
        self.appendTool("Meter (T)", "TOOL_METER", commandIndex=meter)
        self.appendTool("Startpoint", "SET_STARTPOINT", commandIndex=startpoint)
        self.appendTool("Reverse", "REVERSE_CONTOUR", commandIndex=reversecontour)
        self.appendTool("Draw (D)", "TOOL_DRAW", commandIndex=draw)
        self.appendTool("Rectangle (R)", "TOOL_RECTANGLE", commandIndex=rectangle)
        self.appendTool("Ellipse (E)", "TOOL_ELLIPSE", commandIndex=ellipse)
        self.appendTool("Rotate", "TOOL_ROTATE", commandIndex=rotate)
        self.appendTool("Scale", "TOOL_SCALE", commandIndex=scale)
        self.AddSeparator()
        layer_tool = self.appendTool(
            "Layer", "LAYER_EDIT", "Edit Layer", layer, wx.ITEM_NORMAL
        )
        self.SetToolDropDown(layer_tool.Id, True)
        self.Bind(aui.EVT_AUITOOLBAR_TOOL_DROPDOWN, self.on_Tool, layer_tool)

    def on_activate_layer(self, event):
        layerName = event.EventObject.FindItemById(event.Id).ItemLabelText
        view = self.app.documentManager.currentView
        if layerName == view.frame.canvas.getActiveDrawingPlaneStack().name:
            return
        font = view.font
        layerColor = None
        if layerName == "<New Layer>":
            defaultName = "public.background"
            if defaultName in font.layers:
                defaultName = time.strftime("save %Y.%m.%d-%H:%M")
            layerName, layerColor = getLayerInfo(defaultName)
            if not layerName:
                return
        glyph = view.frame.canvas.glyph
        if layerName in font.layers:
            layer = font.layers[layerName]
        else:
            layer = font.newLayer(layerName)
        if layerColor:
            layer.color = layerColor
        if glyph.name not in layer:
            newGlyph = layer.newGlyph(glyph.name)
            newGlyph.width = glyph.width
        for layerPlane in view.frame.canvas.layerPlanes:
            layerPlane.active = layerPlane.name == layerName
        view.frame.canvas.glyph = layer[glyph.name]
        view.frame.metric.glyph = layer[glyph.name]
        view.frame.SetFocus()
        event.Skip()

    def on_Tool(self, event):
        tool = self.FindTool(event.Id)
        i = tool.GetUserData()
        view = self.app.documentManager.currentView
        if i == layer:
            self.SetToolSticky(event.Id, True)
            menu = wx.Menu()
            activeLayerName = view.frame.canvas.getActiveDrawingPlaneStack().name
            for _layer in view.font.layers:
                name = _layer.name
                mnuItem = menu.Append(wx.ID_ANY, name, name, wx.ITEM_RADIO)
                mnuItem.Check(name == activeLayerName)
                self.Bind(wx.EVT_MENU, self.on_activate_layer, mnuItem)
            menu.AppendSeparator()
            mnuItem = menu.Append(
                wx.ID_ANY, "<New Layer>", "Switch to New Layer", wx.ITEM_NORMAL
            )
            self.Bind(wx.EVT_MENU, self.on_activate_layer, mnuItem)
            self.SetToolSticky(event.Id, False)
            self.PopupMenu(menu)
            menu.Destroy()
        elif isinstance(i, int) and i >= 0:
            view.frame.canvas.selectTool(self.tools[i])
        event.Skip()

    def on_update_Tool(self, event):
        view = self.app.documentManager.currentView
        if view and view.document:
            if isinstance(view, UfoGlyphView):
                event.Enable(True)
            else:
                event.Enable(False)
        else:
            event.Enable(False)
