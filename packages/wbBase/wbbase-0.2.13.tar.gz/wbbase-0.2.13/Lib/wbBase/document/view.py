from __future__ import annotations
from typing import Optional, TYPE_CHECKING

import wx

# from . import dbg
from .template import DocumentTemplate

if TYPE_CHECKING:
    from ..application import App
    # from ..panelManager import PanelManager
    from . import Document
    from .manager import DocumentManager

class View:
    """
    The view class can be used to model the viewing and editing component of
    an application's file-based data.
    """

    typeName:str = "View"
    frameType = wx.Window

    def __init__(self):
        self._document:Optional[Document] = None
        self._frame:Optional[wx.Window] = None

    def __repr__(self) -> str:
        if self._document:
            return '<%s of %s "%s">' % (
                self.__class__.__name__,
                self._document.__class__.__name__,
                self._document.printableName,
            )
        return "<%s of %s>" % (
            self.__class__.__name__,
            self._document.__class__.__name__,
        )

    @staticmethod
    def getIcon() -> wx.Bitmap:
        """
        UI icon for this type of view.
        """
        return wx.NullBitmap

    # -----------------------------------------------------------------------------
    # properties
    # -----------------------------------------------------------------------------

    @property
    def app(self) -> App:
        """The main application object"""
        return wx.GetApp()

    @property
    def document(self) -> Optional[Document]:
        """
        The document this view belongs to.
        """
        return self._document

    @document.setter
    def document(self, document:Document):
        self._document = document
        if document:
            document.AddView(self)

    @document.deleter
    def document(self) -> None:
        self._document = None

    @property
    def documentTemplate(self) -> Optional[DocumentTemplate]:
        """
        The document template this view belongs to.
        """
        if self._document is not None:
            return self._document.template
        return None

    @property
    def frame(self) -> Optional[wx.Window]:
        """
        The frame this view belongs to.
        """
        return self._frame

    @property
    def documentManager(self) -> DocumentManager:
        """
        The document manager instance for which this view was
        created.
        """
        return self.app.documentManager

    @property
    def documentNotebook(self):
        return self.documentManager.documentNotebook

    @property
    def pageIndex(self):
        if self._frame:
            i = self.documentNotebook.GetPageIndex(self._frame)
            if i != wx.NOT_FOUND:
                return i
        return None

    # -----------------------------------------------------------------------------
    # internal methods
    # -----------------------------------------------------------------------------

    def OnCreate(self, doc:Document, flags:int) -> bool:
        """
        :class:`DocManager` or :class:`Document` creates a :class:`View` via
        a :class:`DocTemplate`. Just after the :class:`DocTemplate` creates
        the :class:`View`, it calls :meth:`xView.OnCreate`. In its ``OnCreate``
        member function, the ``View`` can create a :class:`DocChildFrame` or
        a derived class. This :class:`DocChildFrame` provides user
        interface elements to view and/or edit the contents of the wxDocument.

        By default, simply returns true. If the function returns false, the
        view will be deleted.
        """
        if self.frameType is None:
            return False
        template = doc.template
        assert isinstance(template, DocumentTemplate)
        documentNotebook = self.documentNotebook
        documentNotebook.Freeze()
        self._frame = self.frameType(documentNotebook, doc, self)
        documentNotebook.AddPage(self._frame, doc.printableName, True, template.icon)
        documentNotebook.Thaw()
        return True

    def OnClose(self, deleteWindow:bool=True) -> bool:
        """
        Implements closing behaviour. The default implementation calls
        :meth:`Document.Close` to close the associated document. Does not delete the
        view. The application may wish to do some cleaning up operations in
        this function, if a call to :meth:`Document::Close` succeeded. For example,
        if your application's all share the same window, you need to
        disassociate the window from the view and perhaps clear the window. If
        deleteWindow is true, delete the frame associated with the view.
        """
        result = False
        if (
            self.document
            and len(self.document.views) == 1
            and not self.document.OnSaveModified()
        ):
            return result
        if self.document is None or self.document.RemoveView(self):
            self.Activate(False)
            if self.frame and deleteWindow:
                index = self.pageIndex
                # self.frame.Unlink()
                if index is not None:
                    self.documentNotebook.DeletePage(index)
                else:
                    self.frame.Destroy()
            self.Destroy()
            result = True
        return result

    def OnActivateView(self, activate, activeView, deactiveView):
        """
        Called when a view is activated by means of :meth:`View.Activate`.
        """
        i = self.pageIndex
        if i is not None and i != self.documentNotebook.Selection:
            self.documentNotebook.Selection = i

    def OnClosingDocument(self):
        """
        Override this to clean up the view when the document is being closed.
        The default implementation does nothing.
        """
        self.OnClose(deleteWindow=True)

    def OnUpdate(self, sender, hint) -> bool:
        """
        Called when the view should be updated. sender is a pointer to the
        view that sent the update request, or None if no single view requested
        the update (for instance, when the document is opened). hint is as yet
        unused but may in future contain application-specific information for
        making updating more efficient.
        """
        if hint:
            if hint[0] == "modify":
                # if dirty flag changed, update the view's displayed title
                frame = self._frame
                if frame and hasattr(frame, "OnTitleIsModified"):
                    frame.OnTitleIsModified()
                    return True
        return False


    def OnChangeFilename(self) -> None:
        """
        Called when the filename has changed. The default implementation
        constructs a suitable title and sets the title of the view frame (if
        any).
        """
        frame = self._frame
        if frame:
            if self._document:
                frame.title = self._document.printableName

    # -----------------------------------------------------------------------------
    # public methods
    # -----------------------------------------------------------------------------

    def Close(self, deleteWindow:bool=True) -> bool:
        """
        Closes the view by calling :meth:`OnClose`. If deleteWindow is true, this
        function should delete the window associated with the view.
        """
        result = self.OnClose(deleteWindow=deleteWindow)
        return result

    def Activate(self, activate:bool=True):
        """
        Call this from your view frame's OnActivate member to tell the
        framework which view is currently active. If your windowing system
        doesn't call OnActivate, you may need to call this function from
        OnMenuCommand or any place where you know the view must be active, and
        the framework will need to get the current view.
        """
        if self.document and self.documentManager:
            self.OnActivateView(activate, self, self.documentManager.currentView)
            self.documentManager.ActivateView(self, activate)

    def Destroy(self):
        """
        Destructor. Removes itself from the document's list of views.
        """
        if self._document:
            self._document.RemoveView(self)
