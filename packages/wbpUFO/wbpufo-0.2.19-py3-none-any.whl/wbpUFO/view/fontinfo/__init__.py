import logging

import wx

from wbDefcon import Font
from wbBase.document.notebook import DocumentPageMixin
from wbBase.document.view import View

from ..font.feature import FeaturePage
from ..font.groups import GroupsPage
from ..font.info import InfoPage
from ..font.kerning import KerningPage

log = logging.getLogger(__name__)


class UfoFontInfoWindow(wx.Notebook, DocumentPageMixin):
    """
    Document Window for UFO Font Info
    """

    def __init__(self, parent, doc, view):
        ID = wx.ID_ANY
        pos = wx.DefaultPosition
        size = wx.DefaultSize
        wx.Notebook.__init__(
            self,
            parent,
            ID,
            pos,
            size,
            style=wx.NB_FIXEDWIDTH | wx.NO_BORDER,
            name="UfoFontWindow",
        )
        DocumentPageMixin.__init__(self, doc, view)
        self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)
        self._font = None
        notebookIndex = 0
        tabIcons = wx.ImageList(16, 16)
        self.AssignImageList(tabIcons)

        # Info page
        self.infoPage = InfoPage(self)
        self.AddPage(self.infoPage, "Info", False)
        icon = wx.ArtProvider.GetBitmap("VIEW_INFO", wx.ART_FRAME_ICON)
        if icon.IsOk():
            tabIcons.Add(icon)
            self.SetPageImage(notebookIndex, notebookIndex)
            notebookIndex += 1

        # Feature page
        self.featurePage = FeaturePage(self)
        self.AddPage(self.featurePage, "Feature", False)
        icon = wx.ArtProvider.GetBitmap("BLANK", wx.ART_FRAME_ICON)
        if icon.IsOk():
            tabIcons.Add(icon)
            self.SetPageImage(notebookIndex, notebookIndex)
            notebookIndex += 1

        # Groups page
        self.groupsPage = GroupsPage(self)
        self.AddPage(self.groupsPage, "Groups", False)
        icon = wx.ArtProvider.GetBitmap("VIEW_GROUP", wx.ART_FRAME_ICON)
        if icon.IsOk():
            tabIcons.Add(icon)
            self.SetPageImage(notebookIndex, notebookIndex)
            notebookIndex += 1

        # Kerning page
        self.kerningPage = KerningPage(self)
        self.AddPage(self.kerningPage, "Kerning", False)
        icon = wx.ArtProvider.GetBitmap("VIEW_KERNING", wx.ART_FRAME_ICON)
        if icon.IsOk():
            tabIcons.Add(icon)
            self.SetPageImage(notebookIndex, notebookIndex)
            notebookIndex += 1

        # # Connect Events
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.on_PAGE_CHANGING)
        #  Window
        self.Bind(wx.EVT_SET_FOCUS, self.on_SET_FOCUS)

    def __repr__(self):
        return f"<{self.__class__.__name__} of {self._font}>"

    # -------------------------------------------------------------------------
    # properties
    # -------------------------------------------------------------------------

    @property
    def font(self):
        """The wbDefcon Font object of this UfoFontWindow"""
        return self._font

    @font.setter
    def font(self, value):
        if value == self._font:
            return
        assert self._font is None
        assert isinstance(
            value, Font
        ), f"Expected Font, got {value}, type {type(value)}"
        assert value == self._document.font
        self._font = value
        self.title = self._document.title.replace("Font", "Info", 1)
        log.debug("Font %r set for %r", self._font, self)
        for page in self.Children:
            page.font = value

    @font.deleter
    def font(self):
        for page in self.Children:
            del page.font

    def Destroy(self):
        del self.font
        return super().Destroy()

    # -------------------------------------------------------------------------
    # event handler
    # -------------------------------------------------------------------------

    def on_PAGE_CHANGING(self, event):
        page = self.GetPage(event.OldSelection)
        if page.Validate():
            if not page.TransferDataFromWindow():
                log.debug("page %r TransferDataFromWindow failed", page)
            event.Skip()
        else:
            log.debug("page %r Validate failed", page)
            event.Veto()

    def on_SET_FOCUS(self, event):
        self.CurrentPage.SetFocus()
        event.Skip()


class UfoFontInfoView(View):
    frameType = UfoFontInfoWindow
    typeName = "UFO Font Info View"

    def __repr__(self):
        if self._document:
            return f'<{self.__class__.__name__} of "{self._document.printableName}">'
        return f"<{self.__class__.__name__} of {self._document.__class__.__name__}>"

    @staticmethod
    def getIcon() -> wx.Bitmap:
        return wx.ArtProvider.GetBitmap("I", wx.ART_FRAME_ICON)

    @property
    def font(self):
        return self.document.font

    def OnCreate(self, doc, flags):
        self._document = doc
        self._frame = self.frameType(self.documentNotebook, doc, self)
        self.documentNotebook.AddPage(
            self._frame,
            doc.printableName.replace("Font", "Info", 1),
            True,
            self.getIcon()
        )
        return True

    def OnUpdate(self, sender, hint):
        super().OnUpdate(sender, hint)
        if hint and hint[0] == "font loaded":
            frame = self._frame
            if frame.font is None:
                frame.font = self.document.font
            frame.title = self._document.title.replace("Font", "Info", 1)
            if frame and hasattr(frame, "OnTitleIsModified"):
                frame.OnTitleIsModified()
            frame.TransferDataToWindow()
