"""
panelItemPicker
===============================================================================
"""
import wx

from .panelItemPickerUI import PanelItemPickerUI


class PanelItemPicker(PanelItemPickerUI):
    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.TAB_TRAVERSAL,
    ):
        PanelItemPickerUI.__init__(
            self, parent, id=id, pos=pos, size=size, style=style, name="PanelItemPicker"
        )

    @property
    def options(self):
        return self.listBox_options.Items

    @options.setter
    def options(self, value):
        self.listBox_options.Items = value

    @property
    def selection(self):
        return self.listBox_selection.Items

    @selection.setter
    def selection(self, value):
        self.listBox_selection.Items = value

    def _moveItems(self, source, dest):
        selections = source.GetSelections()
        selectedItems = list(map(source.GetString, selections))
        dest.SetItems(dest.GetItems() + selectedItems)
        selections = set(selections)
        source.SetItems(
            [item for i, item in enumerate(source.GetItems()) if i not in selections]
        )

    # -------------------------------------------------------------------------
    # Event handler methods
    # -------------------------------------------------------------------------

    def on_listBox_dblclick(self, event):
        listBox = event.GetEventObject()
        selections = listBox.GetSelections()
        if len(selections) != 1:
            return  # DCLICK only works on one item
        if event.GetSelection() != selections[0]:
            # this can happen using ^DCLICK when two items are selected
            return
        if listBox == self.listBox_options:
            self.on_select(event)
        else:
            self.on_unselect(event)

    def on_select(self, event):
        self._moveItems(self.listBox_options, self.listBox_selection)

    def update_button_select(self, event):
        event.Enable(len(self.listBox_options.Selections) > 0)

    def on_unselect(self, event):
       self._moveItems(self.listBox_selection, self.listBox_options)

    def update_button_unselect(self, event):
        event.Enable(len(self.listBox_selection.Selections) > 0)

    def on_button_move_up(self, event):
        event.Skip()

    def update_button_move_up(self, event):
        event.Skip()

    def on_button_move_down(self, event):
        event.Skip()

    def update_button_move_down(self, event):
        event.Skip()

    def on_button_clear(self, event):
        self.options = self.options + self.selection
        self.selection = []

    def update_button_clear(self, event):
        event.Enable(len(self.selection)>0)

