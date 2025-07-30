from __future__ import annotations

import logging
import os
import time
from typing import (
    TYPE_CHECKING,
    Dict,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
    Iterable,
)

import wx
import wx.aui as aui

from ..dialog.multiSaveModifiedDialog import MultiSaveModifiedDialog
from . import (
    DOC_NEW,
    DOC_NO_VIEW,
    DOC_OPEN_ONCE,
    DOC_SILENT,
    Document,
    FileNameFromPath,
    dbg,
)
from .template import DocumentTemplate

if TYPE_CHECKING:
    from types import ModuleType

    from ..application import App
    from ..applicationWindow import ApplicationWindow
    from .notebook import DocumentNotebook
    from .view import View

log = logging.getLogger(__name__)


def OpenDocument(documentPath: str):
    if os.path.exists(documentPath):
        app: App = wx.GetApp()
        app.TopWindow.documentManager.CreateDocument(documentPath, DOC_SILENT)


class DocumentManager(wx.EvtHandler):
    def __init__(self, parent: ApplicationWindow) -> None:
        wx.EvtHandler.__init__(self)
        self.TopLevelParent: ApplicationWindow = parent
        self._templates: List[DocumentTemplate] = []
        self.initTemplates()
        self._defaultDocumentNameCounter: int = 1
        self._flags: int = DOC_OPEN_ONCE
        self._currentView: Optional[View] = None
        self._lastActiveView: Optional[View] = None
        self._menu: Optional[wx.Menu] = None
        self._toolbar: Optional[aui.AuiToolBar] = None
        self._docs: List[Document] = []
        self._maxDocsOpen: int = 10000
        if self.templates:
            self._fileHistory: wx.FileHistory = wx.FileHistory()
            self._fileHistoryMenu: wx.Menu = wx.Menu()
            self._fileHistory.UseMenu(self._fileHistoryMenu)
        self.log = logging.getLogger("documentLog")
        self._setupLogging()

        self.loadConfig()

        self.Bind(wx.EVT_MENU, self.on_file_quit, id=wx.ID_EXIT)
        if self.templates:
            self.Bind(wx.EVT_MENU, self.on_file_new, id=wx.ID_NEW)
            self.Bind(wx.EVT_MENU, self.on_file_open, id=wx.ID_OPEN)
            self.Bind(wx.EVT_MENU, self.on_file_close, id=wx.ID_CLOSE)
            self.Bind(wx.EVT_MENU, self.on_file_closeall, id=wx.ID_CLOSE_ALL)
            self.Bind(wx.EVT_MENU, self.on_file_save, id=wx.ID_SAVE)
            self.Bind(wx.EVT_MENU, self.on_file_saveall, id=self.menu.FindItem("Save All"))
            self.Bind(wx.EVT_MENU, self.on_file_saveas, id=wx.ID_SAVEAS)
            self.Bind(wx.EVT_MENU, self.on_file_revert, id=wx.ID_REVERT)
            self.Bind(
                wx.EVT_MENU,
                self.on_file_ext_canges,
                id=self.menu.FindItem("External Changes"),
            )
            self.Bind(
                wx.EVT_MENU_RANGE, self.on_file_recent, id=wx.ID_FILE1, id2=wx.ID_FILE9
            )

            self.Bind(wx.EVT_UPDATE_UI, self.on_update_file_new, id=wx.ID_NEW)
            self.Bind(wx.EVT_UPDATE_UI, self.on_update_file_open, id=wx.ID_OPEN)
            self.Bind(wx.EVT_UPDATE_UI, self.on_update_file_close, id=wx.ID_CLOSE)
            self.Bind(wx.EVT_UPDATE_UI, self.on_update_file_closeall, id=wx.ID_CLOSE_ALL)
            self.Bind(wx.EVT_UPDATE_UI, self.on_update_file_save, id=wx.ID_SAVE)
            self.Bind(
                wx.EVT_UPDATE_UI,
                self.on_update_file_saveall,
                id=self.menu.FindItem("Save All"),
            )
            self.Bind(wx.EVT_UPDATE_UI, self.on_update_file_saveas, id=wx.ID_SAVEAS)
            self.Bind(wx.EVT_UPDATE_UI, self.on_update_file_revert, id=wx.ID_REVERT)
            self.Bind(
                wx.EVT_UPDATE_UI,
                self.on_update_file_ext_canges,
                id=self.menu.FindItem("External Changes"),
            )

            # make the OpenDocument function available in the global namespace
            import __main__ as main

            name = "OpenDocument"
            if name not in main.__dict__ and name not in self.app.globalObjects:
                main.__dict__[name] = OpenDocument
                self.app.globalObjects.append(name)

    def __repr__(self):
        return '<%s of "%s">' % (self.__class__.__name__, wx.GetApp().GetAppName())

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
    def documentNotebook(self) -> DocumentNotebook:
        """
        The main notebook control which holds the views of all open documents.
        """
        return self.TopLevelParent._panelManager._documentNotebook

    @property
    def flags(self) -> int:
        """
        The document manager's flags.
        """
        return self._flags

    @property
    def plugins(self) -> Dict[str, ModuleType]:
        """
        The plugins loaded by the PluginManager
        """
        return self.app.pluginManager

    @property
    def currentView(self) -> Optional[View]:
        """
        The currently active view, may be None.
        """
        if self._currentView:
            if self._currentView.document:
                return self._currentView
            self._currentView = None
        if len(self._docs) == 1:
            self._currentView = self._docs[0].firstView
            return self._currentView
        return None

    @property
    def lastActiveView(self) -> Optional[View]:
        """
        The last active view. This is used in the SDI framework where dialogs
        can be mistaken for a view and causes the framework to deactivete the
        current view. This happens when something like a custom dialog box used
        to operate on the current view is shown.
        """
        if len(self._docs) >= 1:
            return self._lastActiveView
        else:
            return None

    @property
    def maxDocsOpen(self) -> int:
        """
        Number of documents that can be open at the same time.
        """
        return self._maxDocsOpen

    @maxDocsOpen.setter
    def maxDocsOpen(self, maxDocsOpen: int) -> None:
        self._maxDocsOpen = maxDocsOpen

    @property
    def documents(self) -> Tuple[Document, ...]:
        """
        The collection of managed documents.
        """
        return tuple(self._docs)

    @property
    def documentCount(self) -> int:
        """
        Number of managed documents.
        """
        return len(self._docs)

    @property
    def modifiedDocumentsCount(self) -> int:
        """
        Number of modified documents.
        """
        return len([d for d in self._docs if d.modified])

    @property
    def templates(self) -> Tuple[DocumentTemplate, ...]:
        """
        The collection of associated document templates.
        """
        return tuple(self._templates)

    @property
    def templateCount(self) -> int:
        """
        Number of associated document templates.
        """
        return len(self._templates)

    @property
    def visibleTemplates(self) -> Tuple[DocumentTemplate, ...]:
        """
        The collection of visible document templates.
        """
        return tuple(t for t in self._templates if t.visible)

    @property
    def newableTemplates(self) -> Tuple[DocumentTemplate, ...]:
        """
        The collection of newable document templates.
        """
        return tuple(t for t in self.visibleTemplates if t.newable)

    @property
    def currentDocument(self) -> Optional[Document]:
        """
        The document associated with the currently active view (if any).
        """
        view = self.currentView
        if view:
            return view.document
        return None

    @property
    def fileHistory(self) -> Optional[wx.FileHistory]:
        """
        The file history.
        """
        if hasattr(self, "_fileHistory"):
            return self._fileHistory
        return None

    @property
    def fileWildcard(self) -> str:
        if (
            wx.Platform == "__WXMSW__"
            or wx.Platform == "__WXGTK__"
            or wx.Platform == "__WXMAC__"
        ):
            wildcard = ""
            for template in self.visibleTemplates:
                if len(wildcard) > 0:
                    wildcard += "|"
                wildcard = (
                    wildcard
                    + template.description
                    + " ("
                    + template.fileFilter
                    + ") |"
                    + template.fileFilter
                )  # spacing is important, make sure there is no space after the "|", it causes a bug on wx_gtk
            wildcard = "All|*.*|%s" % wildcard
        else:
            wildcard = "*.*"
        return wildcard

    @property
    def defaultFolder(self) -> str:
        """default folder for file open/save dialog"""
        # use folder of last open/save action
        if self._fileHistory.Count:
            return os.path.dirname(self._fileHistory.GetHistoryFile(0))
        return ""

    @property
    def menu(self) -> wx.Menu:
        """
        The File menu of the main application window.
        """
        if not self._menu:
            self._menu = mnu = wx.Menu()
            if self.templates:
                item = wx.MenuItem(
                    mnu, wx.ID_NEW, "New\tCtrl+N", "Create new document", wx.ITEM_NORMAL
                )
                item.SetBitmap(wx.ArtProvider.GetBitmap("FILE_NEW", wx.ART_MENU))
                mnu.Append(item)

                item = wx.MenuItem(
                    mnu, wx.ID_OPEN, "Open\tCtrl+O", "Open file", wx.ITEM_NORMAL
                )
                item.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_MENU))
                mnu.Append(item)

                item = wx.MenuItem(
                    mnu, wx.ID_CLOSE, "Close", "Close current file", wx.ITEM_NORMAL
                )
                item.SetBitmap(wx.ArtProvider.GetBitmap("FILE_CLOSE", wx.ART_MENU))
                mnu.Append(item)

                item = wx.MenuItem(
                    mnu, wx.ID_CLOSE_ALL, "Close All", "Close all files", wx.ITEM_NORMAL
                )
                item.SetBitmap(wx.ArtProvider.GetBitmap("FILE_CLOSE_ALL", wx.ART_MENU))
                mnu.Append(item)

                mnu.AppendSeparator()

                item = wx.MenuItem(
                    mnu, wx.ID_SAVE, "Save\tCtrl+S", "Save current file", wx.ITEM_NORMAL
                )
                item.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_MENU))
                mnu.Append(item)

                item = wx.MenuItem(
                    mnu, wx.ID_ANY, "Save All", "Save all files", wx.ITEM_NORMAL
                )
                item.SetBitmap(wx.ArtProvider.GetBitmap("FILE_SAVE_ALL", wx.ART_MENU))
                mnu.Append(item)

                item = wx.MenuItem(
                    mnu, wx.ID_SAVEAS, "Save As ...", "Save files as ...", wx.ITEM_NORMAL
                )
                item.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE_AS, wx.ART_MENU))
                mnu.Append(item)

                item = wx.MenuItem(
                    mnu, wx.ID_REVERT, "Revert", "Reload last saved version", wx.ITEM_NORMAL
                )
                item.SetBitmap(wx.ArtProvider.GetBitmap("REVERT_TO_SAVED", wx.ART_MENU))
                mnu.Append(item)

                item = wx.MenuItem(
                    mnu,
                    wx.ID_ANY,
                    "External Changes",
                    "Check current document for external changes",
                    wx.ITEM_NORMAL,
                )
                mnu.Append(item)

                mnu.AppendSeparator()
                mnu.AppendSubMenu(self._fileHistoryMenu, "Recent")
                mnu.AppendSeparator()

            item = wx.MenuItem(
                mnu, wx.ID_EXIT, "&Quit\tCtrl+Q", "Quit programm", wx.ITEM_NORMAL
            )
            item.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_QUIT, wx.ART_MENU))
            mnu.Append(item)

        return self._menu

    @property
    def toolbar(self) -> Optional[aui.AuiToolBar]:
        """
        The File toolbar of the main application window.
        """
        if not self.templates:
            return None
        if not self._toolbar:
            menu = self.menu
            self._toolbar = tb = aui.AuiToolBar(
                self.TopLevelParent,
                wx.ID_ANY,
                wx.DefaultPosition,
                wx.DefaultSize,
                aui.AUI_TB_HORZ_LAYOUT | aui.AUI_TB_PLAIN_BACKGROUND | wx.NO_BORDER,
            )
            tb.SetName("File")
            tb.SetToolBitmapSize(wx.Size(16, 16))
            lastItem: wx.MenuItem = menu.MenuItems[0]
            item: wx.MenuItem
            for item in menu.MenuItems:
                if item.IsSeparator() and not lastItem.IsSeparator():
                    pass
                elif item.IsSubMenu():
                    continue
                elif item.Bitmap.IsOk() and item.Id != wx.ID_EXIT:
                    if lastItem.IsSeparator():
                        tb.AddSeparator()
                    tb.AddTool(
                        item.Id,
                        item.ItemLabelText,
                        item.Bitmap,
                        item.Help,
                        wx.ITEM_NORMAL,
                    )
                lastItem = item
            tb.Realize()
        return self._toolbar

    @property
    def config(self) -> wx.ConfigBase:
        cfg = self.TopLevelParent.config
        cfg.SetPath("/document/")
        return cfg

    # -----------------------------------------------------------------------------
    # public methods
    # -----------------------------------------------------------------------------

    def loadConfig(self) -> None:
        config = self.config
        if self.templates and self._fileHistory:
            self._fileHistory.Load(config)

    def saveConfig(self) -> None:
        config = self.config
        if self.templates and self._fileHistory:
            self._fileHistory.Save(config)

    def initTemplates(self) -> None:
        self.app.splashMessage("init templates")
        plugins = self.plugins
        for name in plugins:
            plugin = plugins[name]
            if hasattr(plugin, "doctemplates"):
                for doctemplate in plugin.doctemplates:
                    doctemplate(self)

    def MakeDefaultName(self) -> str:
        """
        Returns a suitable default name. This is implemented by appending an
        integer counter to the string "Untitled" and incrementing the counter.
        """
        name = "Untitled %d" % self._defaultDocumentNameCounter
        self._defaultDocumentNameCounter += 1
        return name

    def AssociateTemplate(self, docTemplate: DocumentTemplate) -> None:
        """
        Adds the template to the document manager's template list.
        """
        if docTemplate not in self._templates:
            self._templates.append(docTemplate)

    def DisassociateTemplate(self, docTemplate: DocumentTemplate) -> None:
        """
        Removes the template from the list of templates.
        """
        if docTemplate in self._templates:
            self._templates.remove(docTemplate)

    def AddDocument(self, document: Document):
        """
        Adds the document to the list of documents.
        """
        dbg(f"DocumentManager.AddDocument({document})", indent=1)
        if document not in self._docs:
            self._docs.append(document)
            dbg(f"Document() {document} added")
        dbg(indent=0)

    def RemoveDocument(self, document: Document):
        """
        Removes the document from the list of documents.
        """
        dbg("DocumentManager.RemoveDocument()")
        if document in self._docs:
            docPath = document.path
            self._docs.remove(document)
            self.log.info("document closed: %s", docPath)

    def CreateDocument(self, path: str = "", flags: int = 0) -> Optional[Document]:
        """
        Creates a new document in a manner determined by the flags parameter,
        which can be:

        * DOC_NEW Creates a fresh document.
        * DOC_SILENT Silently loads the given document file.

        If DOC_NEW is present, a new document will be
        created and returned, possibly after asking the user for a template to
        use if there is more than one document template.

        If DOC_SILENT is present, a new document will be created
        and the given file loaded into it. If neither of these flags is
        present, the user will be presented with a file selector for the file
        to load, and the template to use will be determined by the extension
        (Windows) or by popping up a template choice list (other platforms).
        """
        dbg(f'DocumentManager.CreateDocument(path="{path}", flags={flags})', indent=1)
        if not self.visibleTemplates:
            return None

        temp: Optional[DocumentTemplate] = None
        if flags & DOC_NEW:
            newableTemplates = self.newableTemplates
            if not newableTemplates:
                return None
            elif len(newableTemplates) == 1:
                temp = newableTemplates[0]
            else:
                temp = self.SelectDocumentType(newableTemplates)
            if isinstance(temp, DocumentTemplate):
                newDoc = temp.CreateDocument(path, flags)
                if isinstance(newDoc, Document):
                    newDoc.OnNewDocument()
                    dbg(f"DocumentManager.CreateDocument() -> done {newDoc}", indent=0)
                    wx.LogStatus(f"Document created: {newDoc.printableName}")
                    return newDoc
            dbg("DocumentManager.CreateDocument() -> done NO NEW DOC", indent=0)
            return None

        if path and flags & DOC_SILENT:
            temp = self.FindTemplateForPath(path)
        elif not path:
            temp, path = self.SelectDocumentPath(self.visibleTemplates, flags)

        # Existing document
        if path and self.flags & DOC_OPEN_ONCE:
            for document in self._docs:
                if document.path and os.path.normcase(
                    document.path
                ) == os.path.normcase(path):
                    # check for file modification outside of application
                    if not document.modificationDateCorrect:
                        msgTitle = self.app.AppName
                        shortName = document.printableName
                        res = wx.MessageBox(
                            "'%s' has been modified outside of %s.  Reload '%s' from file system?"
                            % (shortName, msgTitle, shortName),
                            msgTitle,
                            wx.YES_NO | wx.ICON_QUESTION,
                            self.FindSuitableParent(),
                        )
                        if res == wx.YES:
                            if not self.CloseDocument(document, False):
                                wx.MessageBox(
                                    "Couldn't reload '%s'.  Unable to close current '%s'."
                                    % (shortName, shortName)
                                )
                                dbg(
                                    "DocumentManager.CreateDocument() -> done NO EXISTING DOC",
                                    indent=0,
                                )
                                return None
                            newDoc = self.CreateDocument(path, flags)
                            if isinstance(newDoc, Document):
                                dbg(
                                    f"DocumentManager.CreateDocument() -> done {newDoc}",
                                    indent=0,
                                )
                                wx.LogStatus(
                                    f"Document reloaded: {newDoc.printableName}"
                                )
                                return newDoc
                        elif res == wx.NO:  # don't ask again
                            document.set_modificationDate()

                    firstView = document.firstView
                    if not firstView and not flags & DOC_NO_VIEW:
                        document.template.CreateView(document, flags)
                        document.UpdateAllViews()
                        firstView = document.firstView

                    if firstView and firstView.frame and not flags & DOC_NO_VIEW:
                        firstView.frame.SetFocus()  # Not in wxWindows code but useful nonetheless
                    dbg(
                        "DocumentManager.CreateDocument() -> done EXISTING DOC",
                        indent=0,
                    )
                    return None

        if isinstance(temp, DocumentTemplate) and path:
            newDoc = temp.CreateDocument(path, flags)
            if newDoc:
                if not newDoc.OnOpenDocument(path):
                    frame = None
                    if newDoc.firstView:
                        frame = newDoc.firstView.frame
                    newDoc.DeleteAllViews()  # Implicitly deleted by DeleteAllViews
                    if frame:
                        frame.Destroy()  # DeleteAllViews doesn't get rid of the frame, so we'll explicitly destroy it.
                    dbg(
                        "DocumentManager.CreateDocument() -> done NO EXISTING DOC",
                        indent=0,
                    )
                    return None
                wx.LogStatus(f"Document opened: {newDoc.printableName}")
                self.log.info("document opened: %s", path)
                self._fileHistory.AddFileToHistory(path)
                self.saveConfig()
                dbg(f"DocumentManager.CreateDocument() -> done {newDoc}", indent=0)
                return newDoc
        dbg("DocumentManager.CreateDocument() -> done NO DOC", indent=0)
        return None

    def openDocuments(self, filenames: Sequence[str]):
        """
        Opens Documents by calling :meth:`CreateDocument` for every filename.
        """
        fileCount = len(filenames)
        if fileCount == 1:
            self.CreateDocument(filenames[0], DOC_SILENT)
            return
        with wx.ProgressDialog(
            "Open Documents",
            f"Opening {fileCount} Documents",
            fileCount,
            self.app.TopWindow,
            wx.PD_APP_MODAL
            | wx.PD_ESTIMATED_TIME
            | wx.PD_ELAPSED_TIME
            | wx.PD_REMAINING_TIME
            | wx.PD_SMOOTH
            | wx.PD_AUTO_HIDE,
        ) as progress:
            progress: wx.ProgressDialog
            for name in filenames:
                progress.Update(progress.Value, os.path.basename(name))
                self.CreateDocument(name, DOC_SILENT)
                progress.Update(progress.Value + 1)
                self.app.Yield(True)

    def SelectDocumentPath(
        self, templates: Sequence[DocumentTemplate], flags: int
    ) -> Union[Tuple[DocumentTemplate, str], Tuple[None, None]]:
        """
        Under Windows, pops up a file selector with a list of filters
        corresponding to document templates. The wxDocTemplate corresponding
        to the selected file's extension is returned.

        On other platforms, if there is more than one document template a
        choice list is popped up, followed by a file selector.

        This function is used in :meth:`DocManager.CreateDocument`.
        """
        path = ""
        with wx.FileDialog(
            self.FindSuitableParent(),
            "Select a File",
            wildcard=self.fileWildcard,
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_CHANGE_DIR,
        ) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()

        if path:
            template = self.FindTemplateForPath(path)
            if template:
                return (template, path)
        return (None, None)

    def SelectDocumentType(
        self, templates: Sequence[DocumentTemplate]
    ) -> Optional[DocumentTemplate]:
        """
        Returns a document template by asking the user (if there is more than
        one template). This function is used in :meth:`CreateDocument`.

        :param templates: list of templates from which to choose a desired template.
        """
        if len(templates) == 0:
            return None
        elif len(templates) == 1:
            return templates[0]
        else:
            choices = [t.description for t in templates]
            res = wx.GetSingleChoice(
                "Select a document type:",
                "Documents",
                choices,
                self.FindSuitableParent(),
            )
            if res == "":
                return None
            return templates[choices.index(res)]

    def FindTemplateForPath(self, path: str) -> Optional[DocumentTemplate]:
        """
        Given a path, try to find template that matches the extension. This is
        only an approximate method of finding a template for creating a
        document.

        Note this wxPython verson looks for and returns a default template
        if no specific template is found.
        """
        dbg(f"DocumentManager.FindTemplateForPath(path={path})")
        generic = []
        templates = []
        for temp in self._templates:
            if temp.FileMatchesTemplate(path):
                templates.append(temp)
            if "*.*" in temp.fileFilter:
                generic.append(temp)
        if templates:
            if len(templates) == 1:
                return templates[0]
            else:
                return self.SelectDocumentType(templates)
        if generic:
            if len(generic) == 1:
                return generic[0]
            else:
                return self.SelectDocumentType(generic)
        return None

    def FindTemplateByType(
        self, templateType: type[DocumentTemplate]
    ) -> Optional[DocumentTemplate]:
        for template in self._templates:
            if isinstance(template, templateType):
                return template
        return None

    def FindTemplateByDocumentTypeName(
        self, documentTypeName: str
    ) -> Optional[DocumentTemplate]:
        for template in self._templates:
            if template.documentTypeName == documentTypeName:
                return template
        return None

    def FindTemplateByDescription(self, description: str) -> Optional[DocumentTemplate]:
        for template in self._templates:
            if template.description == description:
                return template
        return None

    def getDocumentsByTypeName(self, documentTypeName: str) -> Iterable[Document]:
        """
        :return: All open documents with the given documentTypeName.
        """
        for doc in self.documents:
            if doc.typeName == documentTypeName:
                yield doc

    def getDocumentsByType(self, documentType: type[Document]) -> Iterable[Document]:
        """
        :return: All open documents of the given documentType.
        """
        for doc in self.documents:
            if isinstance(doc, documentType):
                yield doc

    def ActivateView(
        self, view: View, activate: bool = True, deleting: bool = False
    ) -> None:
        """
        Sets the current view.

        :param deleting: Currently not used

        """
        dbg(f"DocumentManager.ActivateView(view={view}, activate={activate})")
        if activate:
            self._currentView = view
            self._lastActiveView = view
        else:
            self._currentView = None

    def FindSuitableParent(self) -> wx.Window:
        """
        :return:  A parent frame or dialog, either the frame with the current
            focus or if there is no current focus the application's top frame.
        """
        parent = self.TopLevelParent
        focusWindow = wx.Window.FindFocus()
        if focusWindow:
            while (
                focusWindow
                and not isinstance(focusWindow, wx.Dialog)
                and not isinstance(focusWindow, wx.Frame)
            ):
                focusWindow = focusWindow.GetParent()
            if focusWindow:
                parent = focusWindow
        return parent

    def AddFileToHistory(self, fileName: str) -> None:
        """
        Adds a file to the file history list, if we have a pointer to an
        appropriate file menu.
        """
        if self._fileHistory:
            self._fileHistory.AddFileToHistory(fileName)

    def RemoveFileFromHistory(self, i: int) -> None:
        """
        Removes a file from the file history list, if we have a pointer to an
        appropriate file menu.
        """
        if self._fileHistory:
            self._fileHistory.RemoveFileFromHistory(i)

    def testForExternalChanges(self, testAll: bool = False) -> None:
        if testAll:
            for doc in self.documents:
                if doc and doc.canReload and doc.saved and os.path.exists(doc.path):
                    if not doc.modificationDateCorrect:
                        if doc.askForReload():
                            doc.revert()
                        else:
                            doc.set_modificationDate()
                            doc.modified = True
        elif self.currentDocument is not None:
            doc = self.currentDocument
            if doc.canReload and doc.saved and os.path.exists(doc.path):
                if doc.modificationDateCorrect:
                    wx.LogStatus("No external changes detected for %r" % doc)
                else:
                    if doc.askForReload():
                        doc.revert()
                    else:
                        doc.set_modificationDate()
                        doc.modified = True

    def CloseDocument(self, doc: Document, force: bool = True) -> bool:
        """
        Closes the specified document.
        """
        dbg(f"DocumentManager.CloseDocument(doc={doc}, force={force})")
        if doc.Close() or force:
            doc.DeleteAllViews()
            if doc in self._docs:
                doc.Destroy()
            return True
        return False

    def CloseDocuments(self, force: bool = True) -> bool:
        """
        Closes all open documents by calling :meth:`CloseDocument`
        for every document.
        """
        dbg("DocumentManager.CloseDocuments()")
        if not force and self.modifiedDocumentsCount > 1:
            with MultiSaveModifiedDialog(self) as dlg:
                dlg.ShowModal()
                return True
        for document in self._docs[::-1]:
            # Close in lifo (reverse) order.  We clone the list to make sure we go through all docs even as they are deleted
            if not self.CloseDocument(document, force):
                return False
            if document:
                document.DeleteAllViews()  # Implicitly delete the document when the last view is removed
        return True

    def Clear(self, force: bool = True) -> bool:
        """
        Closes all currently opened document by calling :meth:`CloseDocuments`
        and clears the document manager's templates.
        """
        dbg("DocumentManager.Clear()")
        if not self.CloseDocuments(force):
            return False
        self._templates = []
        self.saveConfig()
        return True

    def Destroy(self) -> None:
        """
        Destructor.
        """
        dbg("Destroy")
        self.Clear()
        wx.EvtHandler.Destroy(self)

    def OnOpenFileFailure(self) -> None:
        """
        Called when there is an error opening a file.
        currently not used - remove?
        """
        wx.LogWarning("There is an error opening a file.")

    def _setupLogging(self) -> None:
        self.log.propagate = False
        logFolder = os.path.dirname(self.app.Traits.StandardPaths.UserLocalDataDir)
        now = time.localtime()
        logFileFolder = os.path.join(
            logFolder, f"{now.tm_year}", f"{now.tm_year}.{now.tm_mon:02}"
        )
        if not os.path.isdir(logFileFolder):
            os.makedirs(logFileFolder)
        logFileName = f"{now.tm_year}.{now.tm_mon:02}.{now.tm_mday:02}-documentLog.txt"
        logFilePath = os.path.join(logFileFolder, logFileName)
        docLogHandler = logging.FileHandler(logFilePath, encoding="utf-8", delay=True)
        formatter = logging.Formatter(
            f"%(asctime)s\t{self.app.AppName}\t%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        docLogHandler.setFormatter(formatter)
        self.log.addHandler(docLogHandler)
        self.log.setLevel(logging.INFO)
        self.log.info("application started")

    # -----------------------------------------------------------------------------
    # Event handler
    # -----------------------------------------------------------------------------

    # menu events

    def on_file_new(self, event: wx.CommandEvent):
        """
        Creates a new blank document by calling :meth:`CreateDocument`.
        """
        dbg("DocumentManager.on_file_new()", indent=1)
        self.CreateDocument("", DOC_NEW)
        dbg("DocumentManager.on_file_new() - done", indent=0)

    def on_file_open(self, event: wx.CommandEvent):
        """
        Event handler for menu :menuselection:`File --> Open`

        Creates new documents by showing a File-Open-Dialog
        and calling :meth:`openDocuments` with the selected file names.
        """
        dbg("DocumentManager.on_file_open()")
        with wx.FileDialog(
            self.FindSuitableParent(),
            message="Select a File",
            defaultDir=self.defaultFolder,
            wildcard=self.fileWildcard,
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE,
        ) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self.openDocuments(dlg.Paths)

    def on_file_save(self, event: wx.CommandEvent) -> None:
        """
        Event handler for menu :menuselection:`File --> Save`

        Saves the currrent document by calling :meth:`.Document.Save` method of the document.
        """
        dbg("DocumentManager.on_file_save()", indent=1)
        doc = self.currentDocument
        if doc:
            doc.Save()
        # event.Skip()
        dbg("DocumentManager.on_file_save() -> done", indent=0)

    def on_file_saveall(self, event: wx.CommandEvent) -> None:
        """
        Event handler for menu :menuselection:`File --> Save All`

        Saves all documents by calling :meth:`.Document.Save` method
        of every open document.
        """
        dbg("DocumentManager.on_file_saveall()")
        modifiedDocs = [d for d in self.documents if d.modified]
        documentCount = len(modifiedDocs)

        with wx.ProgressDialog(
            "Save Documents",
            f"Saving {documentCount} Documents",
            documentCount,
            self.app.TopWindow,
            wx.PD_APP_MODAL
            | wx.PD_ESTIMATED_TIME
            | wx.PD_ELAPSED_TIME
            | wx.PD_REMAINING_TIME
            | wx.PD_SMOOTH
            | wx.PD_AUTO_HIDE,
        ) as progress:
            progress: wx.ProgressDialog
            for document in modifiedDocs:
                progress.Update(progress.Value, os.path.basename(document.title))
                document.Save()
                progress.Update(progress.Value + 1)
                self.app.Yield(True)
            # event.Skip()

    def on_file_saveas(self, event: wx.CommandEvent) -> None:
        doc = self.currentDocument
        if doc:
            doc.SaveAs()

    def on_file_close(self, event: wx.CommandEvent):
        """
        Closes and deletes the currently active document.
        """
        dbg("DocumentManager.on_file_close()")
        doc = self.currentDocument
        if doc:
            self.CloseDocument(doc)
            # doc.Close()

    def on_file_closeall(self, event: wx.CommandEvent):
        """
        Closes and deletes all the currently opened documents.
        """
        return self.CloseDocuments(force=False)

    def on_file_revert(self, event: wx.CommandEvent):
        doc = self.currentDocument
        if doc:
            doc.revert()

    def on_file_ext_canges(self, event):
        self.testForExternalChanges()

    def on_file_recent(self, event: wx.CommandEvent):
        n = event.Id - wx.ID_FILE1
        filename = self._fileHistory.GetHistoryFile(n)
        if filename and os.path.exists(filename):
            self.CreateDocument(filename, DOC_SILENT)
        else:
            self.RemoveFileFromHistory(n)
            msgTitle = self.app.AppName
            if not msgTitle:
                msgTitle = "File Error"
            wx.MessageBox(
                "The file '%s' doesn't exist and couldn't be opened.\nIt has been removed from the most recently used files list"
                % FileNameFromPath(filename),
                msgTitle,
                wx.OK | wx.ICON_EXCLAMATION,
                self.TopLevelParent,
            )

    def on_file_quit(self, event: wx.CommandEvent):
        self.TopLevelParent.Close()

    # update UI events

    def on_update_file_new(self, event: wx.UpdateUIEvent):
        event.Enable(len(self.newableTemplates) > 0)

    def on_update_file_open(self, event: wx.UpdateUIEvent):
        event.Enable(len(self.visibleTemplates) > 0)

    def on_update_file_save(self, event: wx.UpdateUIEvent):
        event.Enable(self.currentDocument is not None and self.currentDocument.modified)

    def on_update_file_saveall(self, event: wx.UpdateUIEvent):
        enable = False
        for doc in self.documents:
            if doc.modified:
                enable = True
                break
        event.Enable(enable)

    def on_update_file_saveas(self, event: wx.UpdateUIEvent):
        event.Enable(self.currentDocument is not None)

    def on_update_file_close(self, event: wx.UpdateUIEvent):
        event.Enable(self.currentDocument is not None)

    def on_update_file_closeall(self, event: wx.UpdateUIEvent):
        event.Enable(self.documentCount > 0)

    def on_update_file_revert(self, event: wx.UpdateUIEvent):
        enable = False
        doc = self.currentDocument
        if (
            doc
            and doc.path
            and doc.canReload
            and doc.modified
            and os.path.exists(doc.path)
        ):
            enable = True
        event.Enable(enable)

    def on_update_file_ext_canges(self, event: wx.UpdateUIEvent):
        doc = self.currentDocument
        if doc and doc.canReload:
            event.Enable(True)
        else:
            event.Enable(False)
