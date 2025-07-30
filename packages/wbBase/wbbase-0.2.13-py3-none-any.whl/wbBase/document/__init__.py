"""
This package implements the document/view framework.
It uses the concept of the docview package which comes with wxPython but not
the code.
"""

from __future__ import annotations
import os
import logging
import shutil
import sys
from typing import TYPE_CHECKING, List, Optional, Tuple, IO

import wx
from wx.tools.dbg import Logger
from .view import View

if TYPE_CHECKING:
    from ..application import App
    from .template import DocumentTemplate
    from .manager import DocumentManager

log = logging.getLogger(__name__)

dbg = Logger("doc")
if hasattr(sys, "frozen") and sys.frozen:
    dbg(enable=0)
else:
    app = wx.GetApp()
    if app and hasattr(app, "_debug"):
        dbg._dbg = app._debug
    else:
        dbg(enable=int(sys.argv[0].endswith("py")))


# ----------------------------------------------------------------------
# document globals
# ----------------------------------------------------------------------

DOC_SDI = 1
DOC_MDI = 2
DOC_NEW = 4
DOC_SILENT = 8
DOC_OPEN_ONCE = 16
DOC_NO_VIEW = 32
DEFAULT_DOCMAN_FLAGS = DOC_MDI | DOC_OPEN_ONCE

MAX_FILE_HISTORY = 9


def FileNameFromPath(path:str) -> str:
    """
    Returns the filename for a full path.
    """
    return os.path.split(path)[1]


class Document:
    """
    Base class for all document classes
    """

    binaryData = False
    canReload = False

    def __init__(self, template:DocumentTemplate):
        self._template: DocumentTemplate = template
        self._saved:bool = False
        self._writeable:bool = True
        self._title: str = ""
        self._path: str = ""
        self._typeName:str = template.documentTypeName
        self._modified: bool = False
        self._modificationDate: Optional[float] = None
        self._views:List[View] = []
        self._currentView:Optional[View] = None
        self._data = None

    def __repr__(self):
        return '<%s "%s">' % (self.__class__.__name__, self.printableName)

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
    def template(self) -> DocumentTemplate:
        """
        The template that created the document.
        """
        return self._template

    @template.setter
    def template(self, template:DocumentTemplate):
        self._template = template
        self._typeName = template.documentTypeName

    @property
    def path(self) -> str:
        """
        The full path associated with this document, or an empty string.
        """
        return self._path

    @path.setter
    def path(self, filePath:str) -> None:
        if filePath != self._path:
            dbg(f'Document.path.setter(filePath="{filePath}")')
            self._path = filePath
            for view in self._views:
                view.OnChangeFilename()

    @property
    def title(self) -> str:
        """
        The title of this document.
        """
        return self._title

    @title.setter
    def title(self, title:str) -> None:
        if title == self._title:
            return
        self._title = title
        if not self._path:
            for view in self._views:
                view.OnChangeFilename()

    @property
    def printableName(self) -> str:
        """
        The default function uses the title, or if there is no title, uses the
        filename; or if no filename, the string 'Untitled'.
        """
        if self._title:
            return self._title
        if self._path:
            return FileNameFromPath(self._path)
        return "Untitled"

    @property
    def typeName(self) -> str:
        """
        The document type name given to the DocumentTemplate constructor,
        copied to this document when the document is created. If several
        document templates are created that use the same document type, this
        variable is used in :meth:`DocManager.CreateView` to collate a list of
        alternative view types that can be used on this kind of document.
        """
        return self._typeName

    @property
    def saved(self) -> bool:
        """
        True if the document has been saved.
        """
        return self._saved

    @saved.setter
    def saved(self, saved):
        self._saved = bool(saved)

    @property
    def modified(self) -> bool:
        """
        True if the document has been saved.
        """
        return self._modified

    @modified.setter
    def modified(self, modified):
        _modified = bool(modified)
        if _modified != self._modified:
            self._modified = _modified
            self.UpdateAllViews(self, ("modify", self, self._modified))

    @property
    def modificationDate(self):
        """
        The file's modification date when it was loaded from disk.
        This is used to check if the file has been modified outside of the application.
        """
        return self._modificationDate

    @property
    def modificationDateCorrect(self):
        """
        False if the file has been modified outside of the application.
        """
        if not self._path or not os.path.exists(
            self._path
        ):  # document must be in memory only and can't be out of date
            return True
        return self._modificationDate == os.path.getmtime(self._path)

    @property
    def views(self) -> Tuple[View, ...]:
        """
        Tuple of views for this document
        """
        return tuple(self._views)

    @property
    def firstView(self) -> Optional[View]:
        """
        List of views for this document
        """
        if self._views:
            return self._views[0]
        return None

    @property
    def manager(self) -> DocumentManager:
        """
        The associated document manager.
        """
        return self._template.documentManager
        # if self._template:
        #     return self._template.documentManager
        # return None

    @property
    def frame(self) -> Optional[wx.Window]:
        """
        Intended to return a suitable window for using as a parent for
        document-related dialog boxes. By default, uses the frame associated
        with the first view.
        """
        view = self.firstView
        if view:
            return view.frame
        else:
            return self.app.TopWindow

    @property
    def modeRead(self) -> str:
        if self.binaryData:
            return "rb"
        else:
            return "r"

    @property
    def modeWrite(self) -> str:
        if self.binaryData:
            return "wb"
        else:
            return "w"

    # -----------------------------------------------------------------------------
    # internal methods
    # -----------------------------------------------------------------------------

    def OnCreate(self, path, flags) -> bool:
        dbg(f'Document.OnCreate(path="{path}", flags={flags})', indent=1)
        result = False
        if flags & DOC_NO_VIEW:
            result = True
        elif isinstance(self.template.CreateView(self, flags), View):
            result = True
        dbg(f"Document.OnCreate() done -> {result}", indent=0)
        return result

    def OnNewDocument(self):
        """
        The default implementation calls OnSaveModified and DeleteContents,
        makes a default title for the document, and notifies the views that
        the filename (in fact, the title) has changed.
        """
        dbg("Document.OnNewDocument()", indent=1)
        # if not self.OnSaveModified():
        #     return False
        # self.DeleteContents()
        self.modified = False
        self.saved = False
        self.title = self.manager.MakeDefaultName()
        dbg("Document.OnNewDocument() - done", indent=0)
        # self.path = name

    def OnOpenDocument(self, filename:str) -> bool:
        """
        Constructs an input file for the given filename (which must not
        be empty), and calls :meth:`LoadObject`. If LoadObject returns true, the
        document is set to unmodified; otherwise, an error message box is
        displayed. The document's views are notified that the filename has
        changed, to give windows an opportunity to update their titles. All of
        the document's views are then updated.
        """
        dbg('Document.OnOpenDocument(filename="{filename}")', indent=1)
        if not self.OnSaveModified():
            dbg('Document.OnOpenDocument(") -> done', indent=0)
            return False

        try:
            with open(filename, self.modeRead) as fileObject:
                self.LoadObject(fileObject)
        except Exception:
            log.exception("Could not open '%s'.", FileNameFromPath(filename))
            wx.MessageBox(
                "Could not open '%s'." % FileNameFromPath(filename),
                self.app.AppName,
                wx.OK | wx.ICON_EXCLAMATION,
                self.frame,
            )
            dbg("Document.OnOpenDocument() -> Could not open", indent=0)
            return False
        dbg("Document.OnOpenDocument() object loaded ")
        self.set_modificationDate()
        self.path = filename
        self.title = FileNameFromPath(filename)
        self.saved = True
        self.modified = False
        dbg("Document.OnOpenDocument() -> done", indent=0)
        return True

    def OnSaveModified(self) -> bool:
        """
        If the document has been modified, prompts the user to ask if the
        changes should be changed. If the user replies Yes, the Save function
        is called. If No, the document is marked as unmodified and the
        function succeeds. If Cancel, the function fails.
        """
        dbg("Document.OnSaveModified()", indent=1)
        if not self.modified:
            dbg("Document.OnSaveModified() not modified, return True", indent=0)
            return True

        # check for file modification outside of application
        if not self.modificationDateCorrect:
            res = wx.MessageBox(
                "'%s' has been modified outside of %s.  Overwrite '%s' with current changes?"
                % (self.printableName, self.app.AppName, self.printableName),
                self.app.AppName,
                wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION,
                self.frame,
            )

            if res == wx.NO:
                self.modified = False
                return True
            if res == wx.YES:
                return self.Save()
            return False

        res = wx.MessageBox(
            "Save changes to '%s'?" % self.printableName,
            self.app.AppName,
            wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION,
            self.frame,
        )

        if res == wx.NO:
            self.modified = False
            dbg("user do not want to save, return True", indent=0)
            return True
        if res == wx.YES:
            return self.Save()
        dbg("saving canceled by user, return False", indent=0)
        return False

    def OnSaveDocument(self, filename:str) -> bool:
        """
        Constructs an output file for the given filename (which must
        not be empty), and calls SaveObject. If SaveObject returns true, the
        document is set to unmodified; otherwise, an error message box is
        displayed.
        """
        dbg(f"Document.OnSaveDocument(filename={filename})", indent=1)
        if not filename:
            dbg("Document.OnSaveDocument() no filename return False", indent=0)
            return False

        msgTitle = self.app.AppName
        if not msgTitle:
            msgTitle = "File Error"

        backupFilename = None
        fileObject = None
        copied = False
        saved = False
        try:
            # if current file exists, move it to a safe place temporarily
            if os.path.exists(filename):

                # Check if read-only.
                if not os.access(filename, os.W_OK):
                    wx.LogError(
                        "Could not save '%s'.\n\nNo write permission to overwrite existing file."
                        % FileNameFromPath(filename),
                    )
                    dbg(
                        "Document.OnSaveDocument() No write permission return False",
                        indent=0,
                    )
                    return False

                i = 1
                backupFilename = "%s.bak%s" % (filename, i)
                while os.path.exists(backupFilename):
                    i += 1
                    backupFilename = "%s.bak%s" % (filename, i)
                shutil.copy(filename, backupFilename)
                copied = True

            with open(filename, self.modeWrite) as fileObject:
                saved = self.SaveObject(fileObject)

            if backupFilename:
                os.remove(backupFilename)
        except Exception:
            # save failed, remove copied file
            if backupFilename and copied:
                os.remove(backupFilename)
            log.exception("Could not save '%s'", FileNameFromPath(filename))
            wx.LogError(
                "Could not save '%s'.\n\n%s"
                % (FileNameFromPath(filename), sys.exc_info()[1]),
            )
            dbg("Document.OnSaveDocument() save failed return False", indent=0)
            return False
        if saved:
            self.path = filename
            self.set_modificationDate()
            self.modified = False
            self.saved = True
            # if wx.Platform == '__WXMAC__':  # Not yet implemented in wxPython
            #    wx.FileName(file).MacSetDefaultTypeAndCreator()
            dbg("Document.OnSaveDocument() -> done return True", indent=0)
            wx.LogStatus(f"Document saved: {self.printableName}")
            self.manager.log.info("document saved: %s", self.path)
            return True
        dbg("Document.OnSaveDocument() -> not saved return False", indent=0)
        return False

    def NotifyClosing(self) -> None:
        """
        Notifies the views that the document is going to close.
        """
        dbg("Document.NotifyClosing()", indent=1)
        for view in self._views:
            view.OnClosingDocument()
        dbg("Document.NotifyClosing() - done", indent=0)

    def OnCloseDocument(self) -> bool:
        """
        The default implementation calls :meth:`DeleteContents` (an empty
        implementation) sets the modified flag to false. Override this to
        supply additional behaviour when the document is closed with Close.
        """
        dbg("Document.OnCloseDocument()", indent=1)
        self.NotifyClosing()
        self.DeleteContents()
        self.modified = False
        dbg("Document.OnCloseDocument done", indent=0)
        return True

    def OnChangedViewList(self) -> None:
        """
        Called when a view is added to or deleted from this document. The
        default implementation saves and deletes the document if no views
        exist (the last one has just been removed).
        """
        dbg("Document.OnChangedViewList()")
        if not self._views:
            self.Destroy()

    # -----------------------------------------------------------------------------
    # public methods
    # -----------------------------------------------------------------------------

    def LoadObject(self, fileObject:IO) -> bool:
        """
        Override this function and call it from your own ``LoadObject`` before
        loading your own data. ``LoadObject`` is called by the framework
        automatically when the document contents need to be loaded.

        Note that the wxPython version simply sends you a Python file object,
        so you can use pickle.
        """
        dbg(f"Document.LoadObject({fileObject})", indent=1)
        self._data = fileObject.read()
        self.UpdateAllViews(self, ["load"])
        dbg(indent=0)
        return True

    def SaveObject(self, fileObject:IO) -> bool:
        fileObject.write(self._data)
        dbg("Document.SaveObject() -> done")
        return True

    def set_modificationDate(self) -> None:
        """
        Saves the file's last modification date.
        This is used to check if the file has been modified outside of
        the application.
        """
        if self.path and os.path.exists(self.path):
            self._modificationDate = os.path.getmtime(self.path)
        else:
            self._modificationDate = None
            self.saved = False

    def revert(self) -> None:
        """
        Revert document to last saved version
        by reloading the data from file.
        """
        if self.canReload and self.path and os.path.exists(self.path):
            with open(self.path, self.modeRead) as fileObject:
                self.LoadObject(fileObject)
            self.set_modificationDate()
            self.UpdateAllViews(self, ["load"])
            self.saved = True
            self.modified = False

    def Save(self) -> bool:
        """
        Saves the document by calling OnSaveDocument if there is an associated
        filename, or SaveAs if there is no filename.
        """
        dbg("Document.Save()", indent=1)
        if not self.modified:
            dbg("Document.Save() -> not modified, return True", indent=0)
            return True
        # check for file modification outside of application
        if not self.modificationDateCorrect:
            msgTitle = self.app.AppName
            if not msgTitle:
                msgTitle = "Application"
            res = wx.MessageBox(
                "'%s' has been modified outside of %s.  Overwrite '%s' with current changes?"
                % (self.printableName, msgTitle, self.printableName),
                msgTitle,
                wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION,
                self.frame,
            )
            if res == wx.NO:
                return True
            elif res == wx.YES:
                pass
            else:  # elif res == wx.CANCEL:
                return False
        if not self.path or not self.saved:
            return self.SaveAs()
        result = self.OnSaveDocument(self.path)
        dbg(indent=0)
        return result

    def SaveAs(self) -> bool:
        """
        Prompts the user for a file to save to, and then calls OnSaveDocument.
        """
        dbg("Document.SaveAs()")
        template = self.template
        if not template:
            return False

        descr = (
            template.description
            + " ("
            + template.fileFilter
            + ") |"
            + template.fileFilter
        )  # spacing is important, make sure there is no space after the "|", it causes a bug on wx_gtk
        if self.path:
            folder, filename = os.path.split(self.path)
        else:
            folder = self.manager.defaultFolder
            filename = self.printableName + template.defaultExtension

        filename = wx.FileSelector(
            message="Save As",
            default_path=folder,
            default_filename=filename,
            default_extension=template.defaultExtension,
            wildcard=descr,
            flags=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
            parent=self.frame,
        )
        if filename == "":
            return False

        ext = os.path.splitext(filename)[1]
        if ext == "":
            filename += "." + template.defaultExtension

        if not self.OnSaveDocument(filename):
            return False

        self.path = filename
        self.title = FileNameFromPath(filename)

        for view in self._views:
            view.OnChangeFilename()

        if template.FileMatchesTemplate(filename):
            self.manager.AddFileToHistory(filename)
        return True

    def Close(self) -> bool:
        """
        Closes the document, by calling :meth:`OnSaveModified` and then (if this true)
        :meth:`OnCloseDocument`. This does not normally delete the document object:
        use :meth:`DeleteAllViews` to do this implicitly.
        """
        dbg("Document.Close()", indent=1)
        result = False
        if self.OnSaveModified():
            result = self.OnCloseDocument()
        dbg("Document.Close() -> {result}")
        dbg(indent=0)
        return result

    def AddView(self, view:View) -> bool:
        """
        If the view is not already in the list of views, adds the view and
        calls :meth:`OnChangedViewList`.
        """
        dbg(f"Document.AddView(view={view})", indent=1)
        if not view in self._views:
            self._views.append(view)
            self.OnChangedViewList()
        dbg(indent=0)
        return True

    def RemoveView(self, view:View) -> bool:
        """
        Removes the view from the document's list of views, and calls
        :meth:`OnChangedViewList`.
        """
        dbg(f"Document.RemoveView(view={view})", indent=1)
        if view in self._views:
            self._views.remove(view)
            del view.document
            self.OnChangedViewList()
        dbg(indent=0)
        return True

    def UpdateAllViews(self, sender=None, hint=None) -> None:
        """
        Updates all views. If sender is non-NULL, does not update this view.
        hint represents optional information to allow a view to optimize its
        update.
        """
        dbg(f"Document.UpdateAllViews(sender={sender}, hint={hint})", indent=1)
        for view in self._views:
            if view != sender:
                view.OnUpdate(sender, hint)
        dbg(indent=0)
        dbg("Document.UpdateAllViews() -> done")

    def askForReload(self, message:str="") -> bool:
        if self.canReload:
            if not message:
                message = (
                    "External changes in %s detected\nDo you want to reload the data from disk?"
                    % self.title
                )
            answer = wx.MessageBox(
                message, "Reload", wx.YES_NO | wx.YES_DEFAULT, self.app.TopWindow
            )
            if answer == wx.YES:
                return True
        return False

    def DeleteAllViews(self) -> bool:
        """
        Calls :meth:`View.Close` and deletes each view. Deleting the final view will
        implicitly delete the document itself, because the wxView destructor
        calls RemoveView. This in turn calls :meth:`Document.OnChangedViewList`,
        whose default implemention is to save and delete the document if no
        views exist.
        """
        dbg("Document.DeleteAllViews()")
        manager = self.manager
        for view in self._views:
            if not view.Close():
                return False
        if self in manager.documents:
            self.Destroy()
        return True

    def DeleteContents(self) -> bool:
        """
        Deletes the contents of the document.  Override this method as
        necessary.
        """
        dbg("Document.DeleteContents()")
        self._data = None
        return True

    def Destroy(self) -> None:
        """
        Destructor. Removes itself from the document manager.
        """
        dbg("Document.Destroy", indent=1)
        self.DeleteContents()
        self._modificationDate = None
        if self.manager:
            self.manager.RemoveDocument(self)
        wx.LogStatus(f"Document closed: {self.printableName}")
        dbg(indent=0)
