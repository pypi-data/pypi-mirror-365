"""
libControl
===============================================================================
"""
import logging
from pprint import PrettyPrinter
import wx
from wbDefcon import Lib, Font, Layer, Glyph

log = logging.getLogger(__name__)
pp = PrettyPrinter(indent=2).pformat


class LibTree(wx.TreeCtrl):
    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.SP_LIVE_UPDATE | wx.SP_NOBORDER,
    ):
        wx.TreeCtrl.__init__(self, parent, id, pos, size, style)
        self.root = None
        self.lib = None
        # Connect Events
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_TREE_SEL_CHANGED)

    def updateLib(self, lib):
        if self.Count:
            self.DeleteAllItems()
        self.root = self.AddRoot("lib", data=lib)
        for libKey in sorted(lib.keys()):
            self.addLibData(self.root, libKey, lib[libKey])
        self.Expand(self.root)
        self.Refresh()

    def addLibData(self, parent, label, data):
        item = self.AppendItem(parent, label, data=data)
        if isinstance(data, (list, tuple)):
            for i, d in enumerate(data):
                self.addLibData(item, str(i), d)
        elif isinstance(data, dict):
            for libKey in sorted(data.keys()):
                self.addLibData(item, libKey, data[libKey])
        elif isinstance(data, (str, int, float, bool, bytes)):
            pass
        else:
            log.error("unhandled: %s, %r", label, data)
        return item

    # -------------------------------------------------------------------------
    # Event handler methods
    # -------------------------------------------------------------------------

    def on_TREE_SEL_CHANGED(self, event):
        itemID = event.GetItem()
        if itemID:
            item = self.GetItemData(itemID)
            value = f"Type:\n{type(item)}\n\n"
            value += f"Value:\n{pp(item)}\n"
            self.Parent.libValueCtrl.Value = value
        event.Skip()


class LibControl(wx.SplitterWindow):
    parentType = None

    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.SP_LIVE_UPDATE | wx.SP_NOBORDER,
    ):
        wx.SplitterWindow.__init__(self, parent, id, pos, size, style)
        self._lib = None
        self.SetSashGravity(0.5)
        self.SetMinimumPaneSize(100)
        self.libTreeCtrl = LibTree(
            parent=self,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.TR_DEFAULT_STYLE
            | wx.TR_HAS_BUTTONS
            | wx.TR_SINGLE
            | wx.TR_TWIST_BUTTONS
            | wx.NO_BORDER,
        )
        self.libValueCtrl = wx.TextCtrl(
            parent=self,
            id=wx.ID_ANY,
            value=wx.EmptyString,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.TE_MULTILINE | wx.TE_READONLY,
        )
        self.SplitVertically(self.libTreeCtrl, self.libValueCtrl, 100)
        self.Bind(wx.EVT_IDLE, self.on_IDLE)

    @property
    def lib(self):
        if not self._lib:
            self.lib = self.Validator.lib
        return self._lib

    @lib.setter
    def lib(self, lib):
        assert isinstance(lib, Lib)
        assert isinstance(lib.getParent(), self.parentType)
        del self.lib
        self._lib = lib
        self._lib.addObserver(self, "handleNotification", None)
        self.libTreeCtrl.updateLib(lib)

    @lib.deleter
    def lib(self):
        if isinstance(self._lib, Lib):
            self._lib.removeObserver(self, None)
        self._lib = None

    def on_IDLE(self, event):
        self.SetSashPosition(200)
        self.Unbind(wx.EVT_IDLE)

    def handleNotification(self, notification):
        log.debug("notification %r, %r, %r", self, notification.name, notification.data)
        if notification.name == self._lib.clearNotificationName:
            self.libTreeCtrl.DeleteAllItems()
        else:
            self.libTreeCtrl.updateLib(self.lib)
        self.libValueCtrl.Value = wx.EmptyString
        self.Refresh()

    def TransferDataToWindow(self):
        __ = self.lib
        return super().TransferDataToWindow()

class FontLibControl(LibControl):
    parentType = Font


class LayerLibControl(LibControl):
    parentType = Layer


class GlyphLibControl(LibControl):
    parentType = Glyph


class LibControlValidator(wx.Validator):
    def __init__(self, getLib):
        super().__init__()
        self._getLib = getLib
        self._lib = None

    @property
    def lib(self):
        if not self._lib:
            self._lib = self._getLib()
        return self._lib

    def Clone(self):
        return self.__class__(self._getLib)

    def Validate(self, win):
        return True

    def TransferToWindow(self):
        ctrl = self.GetWindow()
        ctrl.lib = self.lib
        return True

    def TransferFromWindow(self):
        return True
