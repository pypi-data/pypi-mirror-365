"""
info
===============================================================================

Font Info
"""
from __future__ import annotations
import logging
import re

import wx
from fontTools.ufoLib import fontInfoAttributesVersion3ValueData
from wbDefcon import Font, Info
from wbBase.scripting import MacroButtonMixin

from ...control.libControl import FontLibControl, LibControlValidator
from .fontInfoCaret import FontInfoCaret
from .fontInfoCodepage import FontInfoCodepage
from .fontInfoControl import BitList
from .fontInfoClassification import FontInfoClassification
from .fontInfoEmbedding import FontInfoEmbedding
from .fontInfoEncoding import FontInfoEncoding
from .fontInfoHinting import FontInfoHinting
from .fontInfoHintingPS import FontInfoHintingPS
from .fontInfoIdentification import FontInfoIdentification
from .fontInfoLegal import FontInfoLegal
from .fontInfoLine import FontInfoLine
from .fontInfoMetric import FontInfoMetric
from .fontInfoName import FontInfoName
from .fontInfoNote import FontInfoNote
from .fontInfoSuperSubscript import FontInfoSuperSubscript
from .fontInfoUnicode import FontInfoUnicode
from .fontInfoValidator import (
    FontInfoBitListValidator,
    FontInfoCheckBoxValidator,
    FontInfoIntlistTextCtrlValidator,
    FontInfoTextCtrlValidator,
    FontInfoPShintCtrlValidator,
)
from .fontInfoNaviagtionPanelUI import FontInfoNaviagtionPanelUI
from .hintPSpanel import ZonePanel, StemPanel

log = logging.getLogger(__name__)

FontInfoAttributes = Info._properties.keys()
# pattern for Bit-List FontInfoAttributes
bitPattern = re.compile(r"^\w+ \d$")


class InfoTreeCtrl(wx.TreeCtrl):
    """
    Tree control with FontInfo
    """

    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.BORDER_NONE
        | wx.TR_HIDE_ROOT
        | wx.TR_LINES_AT_ROOT
        | wx.TR_HAS_BUTTONS
        | wx.TR_TWIST_BUTTONS
        | wx.TR_NO_LINES
        | wx.TR_FULL_ROW_HIGHLIGHT,
    ):
        super().__init__(parent, id, pos, size, style, name="InfoTreeCtrl")
        self._font = None
        self.root = self.AddRoot("FontInfo")
        itemID = self.AppendItem(self.root, "Names", data=0)
        identID = self.AppendItem(self.root, "Identification", data=1)
        itemID = self.AppendItem(identID, "Classification", data=2)
        legalID = self.AppendItem(self.root, "Legal", data=3)
        itemID = self.AppendItem(legalID, "Embedding", data=4)
        metricID = self.AppendItem(self.root, "Metric", data=5)
        itemID = self.AppendItem(metricID, "Super- and Subscript", data=6)
        itemID = self.AppendItem(metricID, "Line", data=7)
        itemID = self.AppendItem(metricID, "Caret", data=8)
        encodingID = self.AppendItem(self.root, "Encoding", data=9)
        itemID = self.AppendItem(encodingID, "Codepage", data=10)
        itemID = self.AppendItem(encodingID, "Unicode", data=11)
        hintingID = self.AppendItem(self.root, "Hinting", data=12)
        itemID = self.AppendItem(hintingID, "PostScript Hinting", data=13)
        itemID = self.AppendItem(self.root, "Note", data=14)
        itemID = self.AppendItem(self.root, "Lib", data=15)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_selectionChanged)
        self.Bind(wx.EVT_TREE_SEL_CHANGING, self.on_selectionChanging)

    @property
    def infoBookCtrl(self) -> InfoBookCtrl:
        return self.GrandParent.infoBookCtrl

    def on_selectionChanged(self, event):
        if self:
            pageNum = self.GetItemData(event.Item)
            self.infoBookCtrl.ChangeSelection(pageNum)
            self.infoBookCtrl.CurrentPage.TransferDataToWindow()
            # self.infoBookCtrl.CurrentPage.Validator.TransferToWindow()
        event.Skip()

    def on_selectionChanging(self, event):
        if self:
            pageNum = self.GetItemData(event.Item)
            log.debug("on_selectionChanging %r", pageNum)
            if pageNum is not None:
                page = self.infoBookCtrl.GetPage(pageNum)
                if not page.Validate():
                    log.debug("on_selectionChanging %r.Validate() failed", page)
                    event.Veto()
                    return
        event.Skip()


class InfoBookCtrl(wx.Simplebook):
    """
    Book control with FontInfo pages
    """

    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.BORDER_NONE,
    ):
        super().__init__(parent, id, pos, size, style, name="InfoBookCtrl")
        self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)
        self._font = None
        self.fontInfoControls = {}
        pages = (
            ("Name", FontInfoName),
            ("Identification", FontInfoIdentification),
            ("Classification", FontInfoClassification),
            ("Legal", FontInfoLegal),
            ("Embedding", FontInfoEmbedding),
            ("Metric", FontInfoMetric),
            ("Super- and Subscript", FontInfoSuperSubscript),
            ("Line", FontInfoLine),
            ("Caret", FontInfoCaret),
            ("Encoding", FontInfoEncoding),
            ("Codepage", FontInfoCodepage),
            ("Unicode", FontInfoUnicode),
            ("Hinting", FontInfoHinting),
            ("HintingPS", FontInfoHintingPS),
            ("Note", FontInfoNote),
            ("Lib", FontLibControl),
        )
        self.Freeze()
        for name, page in pages:
            self.AddPage(page(self), name)

        self._collectControls(self)
        self._setControlAttributes()
        self._bindControlEvents()
        self.ChangeSelection(0)
        self.Thaw()
        self.Bind(wx.EVT_BOOKCTRL_PAGE_CHANGING, self.on_pageChanging)
        self.Bind(wx.EVT_BOOKCTRL_PAGE_CHANGED, self.on_pageChanged)

    def __repr__(self):
        return f"<{self.__class__.__name__} of {self.Parent}>"

    @property
    def font(self):
        """The wbDefcon Font object of this InfoPage"""
        return self._font

    @font.setter
    def font(self, value):
        assert self._font is None
        assert isinstance(value, Font)
        assert value == self.GrandParent._font
        self._font = value
        for child in self.Children:
            child.TransferDataToWindow()
        self._font.info.addObserver(self, "handleNotification", "Info.ValueChanged")
        log.debug("Font %r set for %r", self._font, self)
        self.CurrentPage.TransferDataToWindow()

    @font.deleter
    def font(self):
        self._font.info.removeObserver(self, "Info.ValueChanged")
        self._font = None

    def getFontInfo(self):
        if self._font is not None:
            return self._font.info

    def getFontLib(self):
        if self._font is not None:
            return self._font.lib

    def _collectControls(self, win):
        if win.Children:
            for child in win.Children:
                if isinstance(child, FontLibControl):
                    child.Validator = LibControlValidator(self.getFontLib)
                if child.Name in FontInfoAttributes:
                    self.fontInfoControls[child.Name] = child
                elif (
                    bitPattern.match(child.Name)
                    and child.Name.split(" ", 1)[0] in FontInfoAttributes
                ):
                    self.fontInfoControls[child.Name] = child
                self._collectControls(child)

    def _getControlValueType(self, controlName):
        if controlName in fontInfoAttributesVersion3ValueData:
            return fontInfoAttributesVersion3ValueData[controlName]["type"]

    def _setControlAttributes(self):
        for name, control in self.fontInfoControls.items():
            control.ToolTip = f"info.{name}"
            valueType = self._getControlValueType(name)
            if isinstance(control, wx.TextCtrl):
                if valueType == "integerList":
                    control.Validator = FontInfoIntlistTextCtrlValidator(
                        self.getFontInfo
                    )
                else:
                    control.Validator = FontInfoTextCtrlValidator(self.getFontInfo)
                    if valueType in (int, float, (int, float), (float, int)):
                        control.WindowStyle |= wx.TE_RIGHT
                    control.WindowStyle |= wx.TE_NOHIDESEL
                    if control.IsSingleLine():
                        control.SetHint("None")
            elif isinstance(control, (wx.CheckBox, wx.RadioButton)):
                control.Validator = FontInfoCheckBoxValidator(self.getFontInfo)
            elif isinstance(control, BitList):
                control.Validator = FontInfoBitListValidator(self.getFontInfo)
            elif isinstance(control, (ZonePanel, StemPanel)):
                control.Validator = FontInfoPShintCtrlValidator(self.getFontInfo)

    def _bindControlEvents(self):
        for control in self.fontInfoControls.values():
            control.Bind(wx.EVT_KILL_FOCUS, self.on_controlKillFocus)

    def handleNotification(self, notification):
        if notification.name == "Info.ValueChanged":
            log.debug("InfoBookCtrl.handleNotification(%r)", notification.data)
            attribute = notification.data["attribute"]
            if attribute in ("openTypeOS2Selection",):
                for controlName, control in self.fontInfoControls.items():
                    if controlName.startswith(attribute + " "):
                        control.Validator.TransferToWindow()
            else:
                control = self.fontInfoControls.get(attribute)
                if control and control.Validator:
                    control.Validator.TransferToWindow()

    # -----------------------------------------------------------------------------
    # Event handler
    # -----------------------------------------------------------------------------

    def on_pageChanging(self, event):
        page = self.GetPage(event.OldSelection)
        if page.Validate():
            if page.TransferDataFromWindow():
                event.Skip()
            else:
                log.debug("TransferDataFromWindow failed for %r", page)
                event.Veto()
        else:
            log.debug("page Validate failed for %r", page)
            event.Veto()

    def on_pageChanged(self, event):
        event.Skip()

    def on_controlKillFocus(self, event):
        log.debug("on_controlKillFocus %r", event.EventObject.Name)
        control = event.EventObject
        if control.Validator and control.Validator.Validate(control.Parent):
            log.debug("%r valid", event.EventObject.Name)
            control.Validator.TransferFromWindow()
        else:
            if hasattr(control, "SelectAll"):
                control.SelectAll()
            wx.CallAfter(control.SetFocus)
        event.Skip()


class FontInfoNaviagtionPanel(FontInfoNaviagtionPanelUI, MacroButtonMixin):
    """
    Naviagtion Panel of InfoPage
    """

    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.TAB_TRAVERSAL,
        name="FontInfoNaviagtionPanel",
    ):
        FontInfoNaviagtionPanelUI.__init__(
            self, parent, id=id, pos=pos, size=size, style=style, name=name
        )
        MacroButtonMixin.__init__(
            self, self.button_macro, "_fontInfo", self.GrandParent.view
        )

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def font(self):
        return self.Parent.font

    @property
    def currentPage(self):
        """Active page of InfoBookCtrl"""
        return self.Parent.infoBookCtrl.CurrentPage

    @property
    def currentAttributes(self):
        attributes = []

        def _collectAttributes(control):
            if control.Children:
                for child in control.Children:
                    if child.Name in FontInfoAttributes:
                        attributes.append(child.Name)
                    elif bitPattern.match(child.Name):
                        childName = child.Name.split(" ", 1)[0]
                        if (
                            childName in FontInfoAttributes
                            and childName not in attributes
                        ):
                            attributes.append(childName)
                    _collectAttributes(child)

        _collectAttributes(self.currentPage)
        return attributes

    @property
    def currentInfo(self):
        info = {}
        fontInfo = self.font.info
        for attr in self.currentAttributes:
            info[attr] = getattr(fontInfo, attr)
        return info

    # =========================================================================
    # Event Handler
    # =========================================================================

    def on_button_copy(self, event):
        from ... import AllFonts, CurrentFont, SelectFonts

        info = self.currentInfo
        name = self.currentPage.Name
        for font in SelectFonts(
            f"Select fonts to copy {name} to:",
            f"Copy {name}",
            [f for f in AllFonts() if f is not CurrentFont()],
        ):
            fontInfo = font.info.naked()
            for attrName, value in info.items():
                setattr(fontInfo, attrName, value)

    def onUpdate_button_copy(self, event):
        invalidNames = ("splitterWindow",)
        fontCount = len(
            [
                d
                for d in wx.GetApp().documentManager.documents
                if d.typeName == "UFO document"
            ]
        )
        event.Enable(self.currentPage.Name not in invalidNames and fontCount > 1)


class InfoPage(wx.Panel):
    """
    Main Font InfoPage with
        - InfoTreeCtrl
        - InfoBookCtrl
        - FontInfoNaviagtionPanel
    """

    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.BORDER_NONE | wx.TAB_TRAVERSAL,
    ):
        super().__init__(parent, id, pos, size, style, name="InfoPage")
        self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)
        self._font = None
        self.Freeze()
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.infoPanel = wx.SplitterWindow(
            self,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.SP_3D | wx.SP_NOBORDER | wx.BORDER_NONE,
        )
        self.infoPanel.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)
        self.infoTreeCtrl = InfoTreeCtrl(self.infoPanel)
        self.infoBookCtrl = InfoBookCtrl(self.infoPanel)

        sizer.Add(self.infoPanel, 1, wx.EXPAND, 0)
        self.infoPanel.SetMinimumPaneSize(20)
        self.infoPanel.SashGravity = 0.3
        self.infoPanel.SplitVertically(self.infoTreeCtrl, self.infoBookCtrl, 200)

        self.infoStatusPanel = FontInfoNaviagtionPanel(self)
        sizer.Add(self.infoStatusPanel, 0, wx.EXPAND, 0)

        self.SetSizer(sizer)
        self.Layout()
        self.Thaw()

        # Connect Events
        self.infoPanel.Bind(wx.EVT_IDLE, self.infoPanelOnIdle)

    def __repr__(self):
        return f"<{self.__class__.__name__} of {self.Parent}>"

    @property
    def font(self):
        """The wbDefcon Font object of this InfoPage"""
        return self._font

    @font.setter
    def font(self, value):
        if value == self._font:
            return
        assert self._font is None
        assert isinstance(value, Font)
        assert value == self.Parent.font
        self._font = value
        log.debug("Font %r set for %r", self._font, self)
        self.infoBookCtrl.font = value

    @font.deleter
    def font(self):
        del self.infoBookCtrl.font
        self._font = None

    def infoPanelOnIdle(self, event):
        self.infoPanel.SetSashPosition(200)
        self.infoPanel.Unbind(wx.EVT_IDLE)

    def Destroy(self):
        del self.font
        return super().Destroy()

    # def TransferDataFromWindow(self):
    #     value = super().TransferDataFromWindow()
    #     log.debug("TransferDataFromWindow for %r returns %r", self, value)
    #     return value
