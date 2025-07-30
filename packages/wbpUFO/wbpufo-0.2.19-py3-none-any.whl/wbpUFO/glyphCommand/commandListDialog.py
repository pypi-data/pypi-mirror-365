"""
commandListDialog
===============================================================================
"""
from __future__ import annotations

import os
from typing import TYPE_CHECKING

import wx
from wx.lib.dialogs import textEntryDialog

from .commandListDialogUI import CommandListDialogUI
from ..glyphCommand import (
    GlyphCommand,
    glyphCommandRegistry,
    saveCommandList,
    loadCommandList,
)
from . import executeCommandList

if TYPE_CHECKING:
    from wbBase.application import App

commandListCache = []
glyphNameListCache = []


class CommandListDialog(CommandListDialogUI):
    def __init__(self):
        CommandListDialogUI.__init__(self, wx.GetApp().TopWindow)
        self.sizer_dialog_buttonsOK.SetDefault()
        self.currentTreeCommand = None
        self.listCtrl_commands.SetItemCount(len(self.commandList))
        self.listCtrl_commands.Refresh()
        self._currentListCommand = None

    # ==========================================================================
    # Properties
    # ==========================================================================

    @property
    def app(self) -> App:
        return wx.GetApp()

    @property
    def currentGlyph(self):
        view = self.app.documentManager.currentView
        if view:
            if view.typeName == "UFO Font View":
                glyph = view.frame.glyphGridPanel.currentGlyph
                if glyph is not None:
                    return view.document.font[glyph.name]
            elif view.typeName == "UFO Glyph View":
                return view.document.font[view.glyph.name]

    @property
    def currentFont(self):
        doc = self.app.documentManager.currentDocument
        if doc and doc.typeName == "UFO document":
            return doc.font

    @property
    def allFonts(self):
        return [
            doc.font
            for doc in self.app.documentManager.documents
            if doc.typeName == "UFO document"
        ]

    @property
    def glyphs(self):
        result = []
        target = self.target
        if target == "Current Glyph":
            return [self.currentGlyph]
        if target == "Selected Glyphs in Current Font":
            return self.currentFont.selectedGlyphs
        if target == "All Glyphs in Current Font":
            return self.font
        if target == "All Glyphs in all open Fonts":
            for font in self.allFonts:
                result.extend([glyph for glyph in font])
            return result
        if target == "Glyphs from List in Current Font":
            return [g for g in self.currentFont if g.name in self.glyphNameList]
        if target == "Glyphs from List in all open Fonts":
            for font in self.allFonts:
                result.extend([g for g in font if g.name in self.glyphNameList])
            return result

    @property
    def commandList(self):
        return commandListCache

    @commandList.setter
    def commandList(self, value):
        global commandListCache
        commandListCache = value

    @property
    def commandListPath(self):
        privateDataPath = self.app.config.Read(
            "/Application/PrivateData/Dir", self.app.privateDataDir
        )
        cmdLstFolder = os.path.join(privateDataPath, "CommandList")
        if not os.path.isdir(cmdLstFolder):
            os.makedirs(cmdLstFolder)
        return cmdLstFolder

    @property
    def currentListCommandIndex(self):
        if self._currentListCommand in self.commandList:
            return self.commandList.index(self._currentListCommand)

    @property
    def currentListCommand(self):
        return self._currentListCommand

    @currentListCommand.setter
    def currentListCommand(self, command):
        if command is None:
            del self.currentListCommand
            return
        if command != self._currentListCommand:
            self._currentListCommand = command
            self.listCtrl_commands.SetItemState(
                self.currentListCommandIndex,
                wx.LIST_STATE_SELECTED,
                wx.LIST_STATE_SELECTED,
            )
            self.label_current_command.LabelText = (
                "Current command is: %s" % command.name
            )
            self.parameterGrid.Clear()
            for prop in command.pgProperties:
                self.parameterGrid.Append(prop)
            self.parameterGrid.SetPropertyAttributeAll("UseCheckbox", True)
        self.listCtrl_commands.SetItemState(
            self.currentListCommandIndex, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED
        )

    @currentListCommand.deleter
    def currentListCommand(self):
        if self._currentListCommand is not None:
            self._currentListCommand = None
            self.parameterGrid.Clear()
            self.label_current_command.LabelText = "Current command is: "

    @property
    def target(self):
        return self.choice_target.StringSelection

    @property
    def glyphNameList(self):
        return glyphNameListCache

    @glyphNameList.setter
    def glyphNameList(self, value):
        if isinstance(value, (list, tuple)) and all(isinstance(n, str) for n in value):
            glyphNameListCache[:] = value[:]
        if isinstance(value, str):
            items = (
                value.replace(",", ", ").replace("/", " /").replace("  ", " ").split()
            )
            items = [i[1:] if i.startswith("/") else i for i in items]
            glyphNameListCache[:] = items[:]

    # ==========================================================================
    # Public Methods
    # ==========================================================================

    def executeCommandList(self):
        if self.commandList:
            executeCommandList(self.commandList, self.glyphs)

    def addCurrentTreeCommand(self):
        if self.currentTreeCommand is not None:
            command = self.currentTreeCommand()
            if self.currentListCommandIndex is None:
                self.commandList.append(command)
            else:
                self.commandList.insert(self.currentListCommandIndex, command)
            self.listCtrl_commands.SetItemCount(len(self.commandList))
            self.currentListCommand = command
            self.listCtrl_commands.Refresh()
            wx.CallAfter(self.listCtrl_commands.SetFocus)

    def removeCurrentListCommand(self):
        if self.currentListCommand is not None:
            i = self.currentListCommandIndex
            self.commandList.pop(i)
            self.listCtrl_commands.SetItemCount(len(self.commandList))
            if i < len(self.commandList):
                self.currentListCommand = self.commandList[i]
            self.listCtrl_commands.Refresh()
            wx.CallAfter(self.listCtrl_commands.SetFocus)

    # ==========================================================================
    # Event Handler
    # ==========================================================================

    def on_InitDialog(self, event):
        # load registered commands in tree ctrl
        tree = self.treeCtrl_commands_available
        tree.DeleteAllItems()
        root = tree.AddRoot("Commands")
        tree.SetItemData(root, None)
        for group in sorted(glyphCommandRegistry):
            groupID = tree.AppendItem(root, group)
            tree.SetItemData(groupID, None)
            for cmd in sorted(glyphCommandRegistry[group]):
                cmdID = tree.AppendItem(groupID, cmd)
                tree.SetItemData(cmdID, glyphCommandRegistry[group][cmd])
        # load saved command lists
        self.choice_saved_lists.Clear()
        for name in sorted(os.listdir(self.commandListPath)):
            if name.endswith(".cmdlst"):
                self.choice_saved_lists.Append(
                    name.replace(".cmdlst", ""),
                    os.path.join(self.commandListPath, name),
                )
        event.Skip()

    def on_choice_target(self, event):
        if self.choice_target.StringSelection in (
            "Glyphs from List in Current Font",
            "Glyphs from List in all open Fonts",
        ):
            glyphListResult = textEntryDialog(
                self,
                message="Enter Glyph Names",
                title="Glyph List",
                defaultText=" ".join(["/" + n for n in glyphNameListCache]),
                style=wx.TE_MULTILINE | wx.OK | wx.CANCEL | wx.RESIZE_BORDER,
            )
            if glyphListResult.returned == wx.ID_OK:
                self.glyphNameList = glyphListResult.text
        event.Skip()

    def on_choice_saved_lists(self, event):
        del self.currentListCommand
        self.commandList = loadCommandList(event.ClientData)
        self.listCtrl_commands.SetItemCount(len(self.commandList))
        self.listCtrl_commands.Refresh()

    def on_TreeCommandActivated(self, event):
        self.currentTreeCommand = self.treeCtrl_commands_available.GetItemData(
            event.Item
        )
        self.addCurrentTreeCommand()
        event.Skip()

    def on_TreeCommandSelChanged(self, event):
        try:
            self.currentTreeCommand = self.treeCtrl_commands_available.GetItemData(
                event.Item
            )
        except RuntimeError:
            self.currentTreeCommand = None

    def on_button_add(self, event):
        self.addCurrentTreeCommand()

    def onUpdate_button_add(self, event):
        event.Enable(
            self.currentTreeCommand is not None
            and issubclass(self.currentTreeCommand, GlyphCommand)
        )

    def on_button_remove(self, event):
        self.removeCurrentListCommand()

    def onUpdate_button_remove(self, event):
        event.Enable(self.currentListCommand is not None)

    def on_button_open(self, event):
        filename = wx.FileSelector(
            "Open Command List",
            self.commandListPath,
            "",
            ".cmdlst",
            "UFO WorkBench Command List (*.cmdlst)|*.cmdlst|Any File (*.*)|*.*",
            wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
            self,
        )
        if filename:
            del self.currentListCommand
            self.commandList = loadCommandList(filename)
            self.listCtrl_commands.SetItemCount(len(self.commandList))
            self.listCtrl_commands.Refresh()

    def on_button_save(self, event):
        filename = wx.FileSelector(
            "Save Command List",
            self.commandListPath,
            "new comman list.cmdlst",
            ".cmdlst",
            "UFO WorkBench Command List (*.cmdlst)|*.cmdlst|Any File (*.*)|*.*",
            wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
            self,
        )
        if filename:
            saveCommandList(self.commandList, filename)
            self.choice_saved_lists.Clear()
            for name in sorted(os.listdir(self.commandListPath)):
                if name.endswith(".cmdlst"):
                    self.choice_saved_lists.Append(
                        name.replace(".cmdlst", ""),
                        os.path.join(self.commandListPath, name),
                    )

    def onUpdate_button_save(self, event):
        event.Enable(len(self.commandList) > 0)

    def on_listCtrl_commands_Activated(self, event):
        self.currentListCommand = self.commandList[event.Index]
        self.removeCurrentListCommand()
        event.Skip()

    def on_listCtrl_commands_Selected(self, event):
        self.currentListCommand = self.commandList[event.Index]

    def onUpdate_listCtrl_commands(self, event):
        if not self.listCtrl_commands.GetSelectedItemCount():
            del self.currentListCommand

    def on_button_up(self, event):
        i = self.currentListCommandIndex
        command = self.commandList.pop(i)
        self.commandList.insert(i - 1, command)
        self.currentListCommand = command
        self.listCtrl_commands.Refresh()
        wx.CallAfter(self.listCtrl_commands.SetFocus)

    def onUpdate_button_up(self, event):
        event.Enable(
            self.currentListCommandIndex is not None
            and self.currentListCommandIndex > 0
        )

    def on_button_down(self, event):
        i = self.currentListCommandIndex
        command = self.commandList.pop(i)
        self.commandList.insert(i + 1, command)
        self.currentListCommand = command
        self.listCtrl_commands.Refresh()
        wx.CallAfter(self.listCtrl_commands.SetFocus)

    def onUpdate_button_down(self, event):
        event.Enable(
            self.currentListCommandIndex is not None
            and self.currentListCommandIndex < len(self.commandList) - 1
        )

    def on_button_clear(self, event):
        self.commandList = []
        del self.currentListCommand
        self.listCtrl_commands.SetItemCount(0)
        self.listCtrl_commands.Refresh()

    def onUpdate_button_clear(self, event):
        event.Enable(len(self.commandList) > 0)

    def on_propertyGrid_Changed(self, event):
        if self.currentListCommand:
            setattr(
                self.currentListCommand,
                event.GetPropertyName(),
                event.GetPropertyValue(),
            )
            self.listCtrl_commands.RefreshItem(self.currentListCommandIndex)
        event.Skip()
