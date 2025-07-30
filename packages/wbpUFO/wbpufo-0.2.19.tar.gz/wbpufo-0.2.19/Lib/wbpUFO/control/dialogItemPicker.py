"""
dialogItemPicker
===============================================================================
"""
import wx

from .dialogItemPickerUI import DialogItemPickerUI


class DialogItemPicker(DialogItemPickerUI):
    def __init__(
        self,
        parent,
        title="ItemPicker",
        message="Select options",
        options=None,
        selection=None,
        optionsLabel=None,
        selectionLabel=None,
        width = 500,
        height = 400
    ):
        DialogItemPickerUI.__init__(self, parent)
        self.Title = title
        self.label_message.LabelText = message
        if options:
            self.options = options
        if selection:
            self.selection = selection
        if optionsLabel:
            self.itemPicker.label_options.LabelText = optionsLabel
        if selectionLabel:
            self.itemPicker.label_selection.LabelText = selectionLabel

    @property
    def options(self):
        return self.itemPicker.listBox_options.Items

    @options.setter
    def options(self, value):
        self.itemPicker.listBox_options.Items = value

    @property
    def selection(self):
        return self.itemPicker.listBox_selection.Items

    @selection.setter
    def selection(self, value):
        self.itemPicker.listBox_selection.Items = value
