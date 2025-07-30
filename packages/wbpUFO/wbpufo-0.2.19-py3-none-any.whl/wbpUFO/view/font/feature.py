"""
feature
===============================================================================

"""
from __future__ import annotations

import logging
from typing import Optional

import wx
from feaASTools.inspect import isFeatureAutomatic, setFeatureAutomatic
from fontTools.feaLib import ast
from wbBase.control.textEditControl import STCfindReplaceMixin
from wbBase.scripting import MacroButtonMixin
from wbDefcon import Features, Font
from wx import stc

log = logging.getLogger(__name__)

feaKeywords = """
anchor anchorDef anon anonymous by contour cursive device 
enum enumerate excludeDFLT exclude_dflt feature featureNames from 
ignore IgnoreBaseGlyphs IgnoreLigatures IgnoreMarks 
MarkAttachmentType UseMarkFilteringSet include includeDFLT 
include_dflt language languagesystem lookup lookupflag 
markClass nameid NULL parameters pos position required 
RightToLeft rsub reversesub script sub substitute subtable 
table useExtension valueRecordDef
""".split()

# style IDs for Feature Lexer
STC_FEA_DEFAULT = 0
STC_FEA_COMMENTLINE = 1
STC_FEA_NUMBER = 2
STC_FEA_WORD = 5
STC_FEA_CLASSNAME = 8


class FeatureTextLexer:
    """Lexer for the FeatureTextCtrl"""

    def styleText(self, event):
        buffer = event.EventObject
        lastStyled = buffer.GetEndStyled()
        startPos = max(lastStyled, 0)
        endPos = event.GetPosition()
        curWord = ""
        comment = False
        while startPos < endPos:
            c = chr(buffer.GetCharAt(startPos))
            curWord += c
            if c == "#":
                comment = True
            elif c in ("\n", "\r"):
                comment = False

            if comment:
                # buffer.StartStyling(startPos, 0x1F)
                buffer.StartStyling(startPos)
                buffer.SetStyling(1, STC_FEA_COMMENTLINE)
                curWord = ""
            elif c.isspace() or c in "()[]{};'":
                curWord = curWord.strip()
                if curWord.startswith("@"):
                    style = STC_FEA_CLASSNAME
                elif curWord in feaKeywords:
                    style = STC_FEA_WORD
                else:
                    style = STC_FEA_DEFAULT

                wordStart = max(0, startPos - len(curWord))
                # buffer.StartStyling(wordStart, 0x1F)
                buffer.StartStyling(wordStart)
                buffer.SetStyling(len(curWord), style)
                buffer.SetStyling(1, STC_FEA_DEFAULT)
                curWord = ""
            startPos += 1
            # else:
            # 	startPos += 1


class FeatureTextCtrl(stc.StyledTextCtrl, STCfindReplaceMixin):
    """
    StyledTextCtrl to display the Feature Code.
    """

    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.BORDER_NONE,
        name="FeatureTextCtrl",
    ):
        super().__init__(parent, id, pos, size, style, name)
        STCfindReplaceMixin.__init__(self, "Find in Features", "Replace in Features")
        self._font = None
        self._lexer = FeatureTextLexer()
        self.SetUseTabs(False)
        self.SetTabWidth(4)
        self.SetIndent(4)
        self.SetTabIndents(True)
        self.SetBackSpaceUnIndents(True)
        self.SetViewEOL(False)
        self.SetViewWhiteSpace(False)
        self.SetMarginWidth(2, 0)
        self.SetIndentationGuides(True)
        self.SetReadOnly(False)
        self.SetMarginType(1, stc.STC_MARGIN_SYMBOL)
        self.SetMarginMask(1, stc.STC_MASK_FOLDERS)
        self.SetMarginWidth(1, 16)
        self.SetMarginSensitive(1, True)
        self.SetProperty("fold", "1")
        self.SetFoldFlags(
            stc.STC_FOLDFLAG_LINEBEFORE_CONTRACTED
            | stc.STC_FOLDFLAG_LINEAFTER_CONTRACTED
        )
        self.SetMarginType(0, stc.STC_MARGIN_NUMBER)
        self.SetMarginWidth(0, self.TextWidth(stc.STC_STYLE_LINENUMBER, "_99999"))
        self.MarkerDefine(stc.STC_MARKNUM_FOLDER, stc.STC_MARK_BOXPLUS)
        self.MarkerSetBackground(stc.STC_MARKNUM_FOLDER, wx.BLACK)
        self.MarkerSetForeground(stc.STC_MARKNUM_FOLDER, wx.WHITE)
        self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN, stc.STC_MARK_BOXMINUS)
        self.MarkerSetBackground(stc.STC_MARKNUM_FOLDEROPEN, wx.BLACK)
        self.MarkerSetForeground(stc.STC_MARKNUM_FOLDEROPEN, wx.WHITE)
        self.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB, stc.STC_MARK_EMPTY)
        self.MarkerDefine(stc.STC_MARKNUM_FOLDEREND, stc.STC_MARK_BOXPLUS)
        self.MarkerSetBackground(stc.STC_MARKNUM_FOLDEREND, wx.BLACK)
        self.MarkerSetForeground(stc.STC_MARKNUM_FOLDEREND, wx.WHITE)
        self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_BOXMINUS)
        self.MarkerSetBackground(stc.STC_MARKNUM_FOLDEROPENMID, wx.BLACK)
        self.MarkerSetForeground(stc.STC_MARKNUM_FOLDEROPENMID, wx.WHITE)
        self.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_EMPTY)
        self.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL, stc.STC_MARK_EMPTY)
        # line wrap
        self.SetWrapMode(stc.STC_WRAP_WORD)
        self.SetWrapIndentMode(stc.STC_WRAPINDENT_INDENT)
        self.SetWrapVisualFlags(stc.STC_WRAPVISUALFLAG_START)
        # selection
        self.SetSelBackground(
            True, wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)
        )
        self.SetSelForeground(
            True, wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT)
        )
        self.SetLexer(stc.STC_LEX_CONTAINER)
        self.StyleSetSpec(
            STC_FEA_DEFAULT, "fore:black,back:white,face:Consolas,size:11"
        )
        self.StyleSetSpec(STC_FEA_WORD, "fore:#0000FF,face:Consolas,size:11")
        self.StyleSetSpec(STC_FEA_CLASSNAME, "fore:#009900,face:Consolas,size:11")
        self.StyleSetSpec(
            STC_FEA_COMMENTLINE, "fore:#808080,back:#E0FCF0,face:Consolas,size:11"
        )

        self.updateFont = False
        self.reloadFeatureText = True

        self.Bind(stc.EVT_STC_CHANGE, self.on_CHANGE)
        self.Bind(stc.EVT_STC_STYLENEEDED, self.on_STYLENEEDED)

    @property
    def font(self):
        """The wbDefcon Font object of this FeatureTextCtrl"""
        return self._font

    @font.setter
    def font(self, value):
        assert self._font is None
        assert isinstance(value, Font)
        assert value == self.GrandParent._font
        self._font = value
        self.updateFont = False
        if value.features and value.features.text:
            self.SetText(value.features.text)
        else:
            self.SetText("")
        self.SetModified(False)
        value.features.addObserver(self, "handleNotification", "Features.TextChanged")
        log.debug("FeatureTextCtrl.@font.setter: %s", self._font)
        self.updateFont = True

    @font.deleter
    def font(self):
        if self._font is not None:
            self._font.features.removeObserver(self, "Features.TextChanged")
            self._font = None
        log.debug("FeatureTextCtrl.@font.deleter")

    @property
    def features(self):
        if self._font:
            return self._font.features

    def handleNotification(self, notification):
        if notification.name == "Features.TextChanged" and self.reloadFeatureText:
            newText = notification.data["newValue"]
            if self.GetText() != newText:
                self.SetText(newText)
                print("reloadFeatureText done")

    def on_CHANGE(self, event):
        if self.updateFont:
            wx.LogDebug("FeatureTextCtrl.on_CHANGE")
            text = self.GetText()
            features = self.features
            if text != features.text:
                self.reloadFeatureText = False
                features.text = text
                self.reloadFeatureText = True
                self.SetFocus()

    def on_STYLENEEDED(self, event):
        self._lexer.styleText(event)


class FeatureCtxMenue(wx.Menu):
    """Context Menu for feature items in the tree control"""

    def __init__(self, feature, treeCtrl):
        super().__init__()
        self.feature = feature
        self.treeCtrl = treeCtrl
        self.font = treeCtrl.font
        automatic = isFeatureAutomatic(feature)
        self.mnu_auto = wx.MenuItem(
            self, wx.ID_ANY, "Automatic", "Automatc generated feature", wx.ITEM_CHECK
        )
        self.Append(self.mnu_auto)
        self.mnu_auto.Check(automatic)
        self.mnu_delete = wx.MenuItem(
            self, wx.ID_ANY, "Delete Feature", wx.EmptyString, wx.ITEM_NORMAL
        )
        self.Append(self.mnu_delete)
        self.mnu_insert = wx.MenuItem(
            self, wx.ID_ANY, "Insert Feature", wx.EmptyString, wx.ITEM_NORMAL
        )
        self.Append(self.mnu_insert)
        self.mnu_update = wx.MenuItem(
            self, wx.ID_ANY, "Update Feature", "Regenerate feature code", wx.ITEM_NORMAL
        )
        self.Append(self.mnu_update)
        self.mnu_update.Enable(automatic)
        # Connect Events
        self.Bind(wx.EVT_MENU, self.on_menuSelection, id=self.mnu_auto.Id)
        self.Bind(wx.EVT_MENU, self.on_menuSelection, id=self.mnu_delete.Id)
        self.Bind(wx.EVT_MENU, self.on_menuSelection, id=self.mnu_insert.Id)
        self.Bind(wx.EVT_MENU, self.on_menuSelection, id=self.mnu_update.Id)

    def on_menuSelection(self, event):
        print(dir(event))
        print(event.EventObject)
        if event.Id == self.mnu_auto.Id:
            print("mnu_auto")
            print(event.IsChecked())
            setFeatureAutomatic(self.feature, event.IsChecked())
            self.font.features.setSyntaxtree(
                self.font.features.getSyntaxtree(useGlyphNames=False)
            )
            self.treeCtrl.buildTree()
        elif event.Id == self.mnu_update.Id:
            if not isFeatureAutomatic(self.feature):
                answer = wx.MessageBox(
                    f"Feature '{self.feature.name}' is not automatc generated!\n\nUpdate aynway?",
                    "Update Feature",
                    wx.YES_NO,
                    wx.GetApp().TopWindow,
                )
                if answer == wx.NO:
                    return
        event.Skip()


class FeatureTreeCtrl(wx.TreeCtrl):
    """
    Tree Control in the Feature Panel
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
        super().__init__(parent, id, pos, size, style, name="FeatureTreeCtrl")
        size = 16
        imagelist = wx.ImageList(size, size)
        self.imgLangSys = imagelist.Add(
            wx.Bitmap.FromRGBA(
                size, size, red=0x02, green=0x4F, blue=0x73, alpha=wx.ALPHA_OPAQUE
            )
        )
        self.imgFeature = imagelist.Add(
            wx.Bitmap.FromRGBA(
                size, size, red=0xAC, green=0x02, blue=0x13, alpha=wx.ALPHA_OPAQUE
            )
        )
        self.imgLookup = imagelist.Add(
            wx.Bitmap.FromRGBA(
                size, size, red=0xAC, green=0xA4, blue=0x02, alpha=wx.ALPHA_OPAQUE
            )
        )
        self.imgClass = imagelist.Add(
            wx.Bitmap.FromRGBA(
                size, size, red=0x03, green=0x72, blue=0x30, alpha=wx.ALPHA_OPAQUE
            )
        )
        self.SetImageList(imagelist)

        self.imagelist = imagelist
        self._font = None
        self.root = None

        # Connect Events
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_selectionChanged)
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_rightDown)
        self.Bind(wx.EVT_RIGHT_UP, self.on_rightUp)

    @property
    def font(self) -> Font:
        """The wbDefcon Font object of this FeatureTextCtrl"""
        return self._font

    @font.setter
    def font(self, value: Font):
        assert self._font is None
        assert isinstance(value, Font)
        assert value == self.GrandParent._font
        self._font = value
        self._font.features.addObserver(
            self, "handleNotification", Features.changeNotificationName
        )
        self.buildTree()

    @font.deleter
    def font(self):
        if isinstance(self._font, Font):
            self._font.features.removeObserver(self, Features.changeNotificationName)
        self._font = None

    @property
    def syntaxtree(self) -> Optional[ast.FeatureFile]:
        if self._font:
            return self._font.features.getSyntaxtree(useGlyphNames=False)

    @property
    def textCtrl(self):
        return self.GrandParent.featureTextCtrl

    def appendStatement(self, parent, statement):
        if isinstance(statement, ast.LanguageSystemStatement):
            treeItemId = self.AppendItem(
                parent,
                f"{statement.script}-{statement.language}",
                self.imgLangSys,
                data=statement,
            )
        elif isinstance(statement, ast.FeatureBlock):
            treeItemId = self.AppendItem(
                parent, statement.name, self.imgFeature, data=statement
            )
            for s in statement.statements:
                self.appendStatement(treeItemId, s)
        elif isinstance(statement, ast.LookupBlock):
            treeItemId = self.AppendItem(
                parent, statement.name, self.imgLookup, data=statement
            )
            for s in statement.statements:
                self.appendStatement(treeItemId, s)
        elif isinstance(statement, ast.GlyphClassDefinition):
            treeItemId = self.AppendItem(
                parent, statement.name, self.imgClass, data=statement
            )

    def buildTree(self):
        self.Freeze()
        log.debug("FeatureTreeCtrl.buildTree")
        self.DeleteAllItems()
        tree = self.syntaxtree
        if tree:
            self.root = self.AddRoot("features")
            for statement in tree.statements:
                self.appendStatement(self.root, statement)
            # self.ExpandAllChildren(self.root)
        else:
            log.debug("No syntaxtree")
        self.Thaw()

    def handleNotification(self, notification):
        if self.syntaxtree:
            self.buildTree()

    # --------------------------------------------------------------------------
    # Event handler
    # --------------------------------------------------------------------------

    def on_selectionChanged(self, event):
        if self.FindFocus() != self:
            # event.Skip()
            return
        if self.IsFrozen():
            return
        try:
            data = self.GetItemData(event.Item)
        except RuntimeError:
            return
        if data:
            ctrl = self.textCtrl
            # print(self.FindFocus())
            # print(f"line before {ctrl.GetCurrentLine()}")
            ctrl.GotoLine(data.location[1] + int(ctrl.LinesOnScreen() / 2))
            ctrl.GotoLine(data.location[1])
            ctrl.Home()
            # ctrl.GotoPos(ctrl.PositionFromLine(ctrl.GetCurrentLine()))
            ctrl.LineUpExtend()
            ctrl.SetFocus()
            # print(f"line after {ctrl.GetCurrentLine()}")
        # event.Skip()

    def on_rightDown(self, event):
        position = event.GetPosition()
        item, __ = self.HitTest(position)
        if item:
            self.SelectItem(item)

    def on_rightUp(self, event):
        position = event.GetPosition()
        item, __ = self.HitTest(position)
        if item:
            data = self.GetItemData(item)
            lineNo = data.location[1]
            if isinstance(data, ast.FeatureBlock):
                menu = FeatureCtxMenue(data, self)
                self.PopupMenu(menu)
                menu.Destroy()
            wx.CallAfter(self.textCtrl.ShowLines, lineNo - 5, lineNo + 5)
        # item, __ = self.HitTest(position)
        # if item:
        #     wx.CallAfter(self.SelectItem, item)


class FeatureStatusPanel(wx.Panel, MacroButtonMixin):
    """
    Tree Status Panel in the Feature Panel
    """

    Parent: FeaturePage

    def __init__(
        self,
        parent: FeaturePage,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.BORDER_NONE,
    ):
        super().__init__(parent, id, pos, size, style, name="FeatureStatusPanel")
        sizer_outer = wx.BoxSizer(wx.VERTICAL)
        self.staticline = wx.StaticLine(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL
        )
        sizer_outer.Add(self.staticline, 0, wx.EXPAND, 0)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonSplit = wx.BitmapButton(
            self,
            wx.ID_ANY,
            wx.ArtProvider.GetBitmap(wx.ART_GOTO_LAST, wx.ART_BUTTON),
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.BU_AUTODRAW | 0,
        )
        sizer.Add(self.buttonSplit, 0, wx.ALL, 5)
        sizer.Add((0, 0), 1, wx.EXPAND, 5)
        self.button_macro = wx.Button(
            self, wx.ID_ANY, "▼", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT
        )
        self.button_macro.SetBitmap(wx.ArtProvider.GetBitmap("PYTHON", wx.ART_BUTTON))
        sizer.Add(self.button_macro, 0, wx.ALL, 5)
        sizer_outer.Add(sizer, 1, wx.EXPAND, 5)
        self.SetSizer(sizer_outer)
        self.Layout()

        MacroButtonMixin.__init__(
            self, self.button_macro, "_features", self.GrandParent.view
        )
        # Connect Events
        self.buttonSplit.Bind(wx.EVT_BUTTON, self.on_buttonSplit)
        self.buttonSplit.Bind(wx.EVT_UPDATE_UI, self.update_buttonSplit)

    @property
    def featurePanel(self):
        return self.Parent.featurePanel

    def on_buttonSplit(self, event):
        if self.featurePanel.IsSplit():
            self.featurePanel.Unsplit(self.Parent.featureTreeCtrl)
            self.buttonSplit.SetBitmap(
                wx.ArtProvider.GetBitmap("GO_LAST", wx.ART_BUTTON)
            )
        else:
            self.featurePanel.SplitVertically(
                self.Parent.featureTreeCtrl, self.Parent.featureTextCtrl, 200
            )
            self.buttonSplit.SetBitmap(
                wx.ArtProvider.GetBitmap("GO_FIRST", wx.ART_BUTTON)
            )

    def update_buttonSplit(self, event):
        event.Skip()


class FeaturePage(wx.Panel):
    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.BORDER_NONE | wx.TAB_TRAVERSAL,
    ):
        super().__init__(parent, id, pos, size, style, name="FeaturePage")
        self._font = None
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.featurePanel = wx.SplitterWindow(
            self,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.SP_3D | wx.SP_NOBORDER | wx.BORDER_NONE,
        )
        self.featureTreeCtrl = FeatureTreeCtrl(self.featurePanel)
        self.featureTextCtrl = FeatureTextCtrl(self.featurePanel)

        sizer.Add(self.featurePanel, 1, wx.EXPAND, 0)
        self.featurePanel.SetMinimumPaneSize(20)
        self.featurePanel.SashGravity = 0.5
        self.featurePanel.SplitVertically(self.featureTreeCtrl, self.featureTextCtrl, 0)
        self.featurePanel.Unsplit(self.featureTreeCtrl)

        self.featureStatusPanel = FeatureStatusPanel(self)
        sizer.Add(self.featureStatusPanel, 0, wx.EXPAND, 0)

        self.SetSizer(sizer)
        self.Layout()

        # Connect Events
        self.featurePanel.Bind(wx.EVT_IDLE, self.featurePanelOnIdle)
        self.featurePanel.Bind(wx.EVT_SPLITTER_UNSPLIT, self.on_Unsplit)

    @property
    def font(self):
        """The wbDefcon Font object of this FeaturePage"""
        return self._font

    @font.setter
    def font(self, value):
        assert self._font is None
        assert isinstance(value, Font)
        # assert value == self.Parent._document._data
        assert value == self.Parent.font
        self._font = value
        self.featureTextCtrl.font = value
        self.featureTreeCtrl.font = value

    @font.deleter
    def font(self):
        del self.featureTextCtrl.font
        del self.featureTreeCtrl.font
        self._font = None

    def featurePanelOnIdle(self, event):
        self.featurePanel.SetSashPosition(0)
        self.featurePanel.Unbind(wx.EVT_IDLE)

    def on_Unsplit(self, event):
        self.featureStatusPanel.buttonSplit.SetBitmap(
            wx.ArtProvider.GetBitmap(wx.ART_GOTO_LAST, wx.ART_BUTTON)
        )
