from __future__ import annotations

from typing import TYPE_CHECKING

import wx
import wx.aui as aui

from . import dbg

if TYPE_CHECKING:
    from ..application import App
    from . import Document
    from .view import View


class DocumentNotebook(aui.AuiNotebook):
    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=aui.AUI_NB_DEFAULT_STYLE,
    ):
        """DocumentNotebook(parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=aui.AUI_NB_DEFAULT_STYLE)"""
        aui.AuiNotebook.__init__(self, parent, id, pos, size, style)
        self.Name = "DocumentNotebook"
        self.loadConfig()
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.on_PAGE_CLOSE)
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.on_PAGE_CHANGED)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} of "{self.app.AppName}">'

    @property
    def app(self) -> App:
        """
        The running Workbench application.
        """
        return wx.GetApp()

    @property
    def config(self) -> wx.ConfigBase:
        cfg = self.app.config
        cfg.SetPath("/Window/Panels/")
        return cfg

    def loadConfig(self) -> None:
        self.SetWindowStyleFlag(
            self.config.ReadInt("AUI_NB_FLAGS", aui.AUI_NB_DEFAULT_STYLE)
        )

    def AddPage(self, page, caption:str, select:bool=False, bitmap=None) -> bool:
        result: bool = aui.AuiNotebook.AddPage(self, page, caption, select, bitmap)
        if result and page.document and page.document.path:
            pageIndex = self.GetPageIndex(page)
            self.SetPageToolTip(pageIndex, page.document.path)
        return result

    # -----------------------------------------------------------------------------
    #: Event handler
    # -----------------------------------------------------------------------------

    def on_PAGE_CLOSE(self, event):
        dbg("DocumentNotebook.on_PAGE_CLOSE()", indent=1)
        page = self.GetPage(event.Selection)
        if page.view and page.view.Close(deleteWindow=False):
            dbg("DocumentNotebook.on_PAGE_CLOSE() - > page.view closed")
            event.Skip()
        else:
            dbg("DocumentNotebook.on_PAGE_CLOSE() - > page.view NOT closed")
            event.Veto()
        dbg(indent=0)

    def on_PAGE_CHANGED(self, event):
        dbg("DocumentNotebook.on_PAGE_CHANGED()", indent=1)
        page = self.GetPage(event.GetSelection())
        if page and page.view:
            page.view.Activate()
            page.SetFocus()
        event.Skip()
        dbg(indent=0)


class DocumentPageMixin:
    """
    Mixin Class for DocumentNotebook pages
    """
    Parent: DocumentNotebook
    def __init__(self, document: Document, view: View):
        self._document: Document = document
        self._view: View = view

    # -----------------------------------------------------------------------------
    # properties
    # -----------------------------------------------------------------------------

    @property
    def app(self) -> App:
        """
        The running Workbench application.
        """
        return wx.GetApp()

    @property
    def document(self) -> Document:
        """
        The document associated with this page.
        """
        return self._document

    @property
    def view(self) -> View:
        """
        The view associated with this page.
        """
        return self._view

    @property
    def title(self) -> str:
        """
        The visible title of this page.
        """
        return self.Parent.GetPageText(self.Parent.GetPageIndex(self))

    @title.setter
    def title(self, title: str):
        pageIndex = self.Parent.GetPageIndex(self)
        self.Parent.SetPageText(pageIndex, title)
        if self.document and self.document.path:
            self.Parent.SetPageToolTip(pageIndex, self.document.path)
        else:
            self.Parent.SetPageToolTip(pageIndex, "")

    def OnTitleIsModified(self):
        """
        Add/remove to the frame's title an indication that the document is dirty.
        If the document is dirty, an '*' is appended to the title
        This method has been added to wxPython and is not in wxWindows.
        """
        title = self.title
        if title:
            if self.document.modified:
                if title.endswith("*"):
                    return
                else:
                    title += "*"
                    self.title = title
            else:
                if title.endswith("*"):
                    title = title[:-1]
                    self.title = title
                else:
                    return
