import logging

import wx

from wbDefcon import Font
from wbBase.document import dbg
from wbBase.document.notebook import DocumentPageMixin
from wbBase.document.view import View

from .glyphGrid import GlyphGridPage

log = logging.getLogger(__name__)


class UfoFontWindow(wx.Notebook, DocumentPageMixin):
    """
    The main Document Window for UFO Documents
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

        # GlyphGrid page
        self.glyphGridPage = GlyphGridPage(self)
        self.glyphGridPanel = self.glyphGridPage.glyphGridPanel
        self.AddPage(self.glyphGridPage, "Glyphs", True)
        icon = wx.ArtProvider.GetBitmap("VIEW_ICON", wx.ART_FRAME_ICON)
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
        assert self._font is None
        assert isinstance(
            value, Font
        ), f"Expected Font, got {value}, type {type(value)}"
        assert value == self._document.font
        self._font = value
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


class UfoFontView(View):
    frameType = UfoFontWindow
    typeName = "UFO Font View"

    def __repr__(self):
        if self._document:
            return '<%s of "%s">' % (
                self.__class__.__name__,
                self._document.printableName,
            )
        return "<%s of %s>" % (
            self.__class__.__name__,
            self._document.__class__.__name__,
        )

    @staticmethod
    def getIcon() -> wx.Bitmap:
        return wx.ArtProvider.GetBitmap("F", wx.ART_FRAME_ICON)

    @property
    def font(self):
        return self.document.font

    def OnCreate(self, doc, flags):
        dbg(f'UfoFontView.OnCreate(doc="{doc}", flags={flags})', indent=1)
        self._document = doc
        self._typeName = doc.template.viewTypeName
        self._frame: UfoFontWindow = self.frameType(self.documentNotebook, doc, self)
        documentNotebook = self.documentNotebook
        documentNotebook.Freeze()
        documentNotebook.AddPage(
            self._frame,
            doc.printableName,
            True,
            self.getIcon()
        )
        documentNotebook.Thaw()
        dbg(indent=0)
        return True

    def OnUpdate(self, sender, hint):
        dbg(f"UfoFontView.OnUpdate(sender={sender}, hint={hint})", indent=1)
        super().OnUpdate(sender, hint)
        if hint and hint[0] == "font loaded":
            frame = self._frame
            if frame.font is None:
                frame.font = self.document.font
            frame.title = self._document.title
            if frame and hasattr(frame, "OnTitleIsModified"):
                frame.OnTitleIsModified()
            frame.TransferDataToWindow()
            frame.glyphGridPanel.SendSizeEvent()
        dbg(indent=0)

    def OnClose(self, deleteWindow=True):
        dbg(f"UfoFontView.OnClose(deleteWindow={deleteWindow})", indent=1)
        result = False
        for view in self._document.views:
            if view is not self:
                dbg(f"UfoFontView.OnClose() closing child view {view}")
                if not view.Close(deleteWindow=True):
                    dbg(
                        f"UfoFontView.OnClose() returns {result}, can not close {view}",
                        indent=0,
                    )
                    return result
                dbg("UfoFontView.OnClose() closing child view done")
        result = super().OnClose(deleteWindow=deleteWindow)
        dbg(indent=0)
        return result
