from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, List, Optional, Union

import wx

if TYPE_CHECKING:
    from ..application import App
    from . import Document
    from .manager import DocumentManager
    from .view import View

log = logging.getLogger(__name__)

# ----------------------------------------------------------------------
# document template globals
# ----------------------------------------------------------------------

TEMPLATE_VISIBLE = 1
TEMPLATE_INVISIBLE = 2
TEMPLATE_NO_CREATE = 4 | TEMPLATE_VISIBLE
DEFAULT_TEMPLATE_FLAGS = TEMPLATE_VISIBLE


def FindExtension(path):
    """
    Returns the extension of a filename for a full path.
    """
    return os.path.splitext(path)[1].lower()


class DocumentTemplate:
    def __init__(
        self,
        manager: DocumentManager,
        description: str,
        filter: str,
        dir: str,
        ext: str,
        docTypeName: str,
        docType: type[Document],
        viewType: type[View],
        flags: int = DEFAULT_TEMPLATE_FLAGS,
        icon=None,
    ):
        self._docManager = manager
        self._description: str = description
        self._fileFilter: str = filter or ""
        self._directory: str = dir or ""
        self._defaultExt: str = ext or ""
        self._docTypeName: str = docTypeName
        self._docType: type[Document] = docType
        self._viewTypes: List[type[View]] = [
            viewType,
        ]
        self._flags: int = flags
        self._icon = icon

        self._docManager.AssociateTemplate(self)

    def __repr__(self):
        return '<DocumentTemplate for "%s">' % self._docTypeName

    # -----------------------------------------------------------------------------
    # properties
    # -----------------------------------------------------------------------------

    @property
    def app(self) -> App:
        """The main application object"""
        return wx.GetApp()

    @property
    def documentManager(self) -> DocumentManager:
        """
        The document manager instance for which this template was
        created.
        """
        return self._docManager

    @documentManager.setter
    def documentManager(self, manager: DocumentManager):
        self._docManager = manager

    @property
    def defaultExtension(self) -> str:
        """
        The default file extension for the document data,
        as passed to the document template constructor.
        """
        return self._defaultExt

    @property
    def description(self) -> str:
        """
        The text description of this template,
        as passed to the document template constructor.
        """
        return self._description

    @property
    def directory(self) -> str:
        """
        The default directory, as passed to the document template
        constructor.
        """
        return self._directory

    @property
    def fileFilter(self) -> str:
        """
        Returns the file filter,
        as passed to the document template constructor.
        """
        return self._fileFilter

    @property
    def flags(self) -> int:
        """
        Returns the flags, as passed to the document template constructor.
        (see the constructor description for more details).
        """
        return self._flags

    @property
    def icon(self) -> wx.Bitmap:
        """
        The icon, as passed to the document template constructor.
        """
        return self._icon

    @property
    def documentType(self) -> type[Document]:
        """
        Returns the Python document class, as passed to the document template
        constructor.
        """
        return self._docType

    @property
    def viewType(self) -> type[View]:
        """
        Returns the Python class for the default view, 
        as passed to the document template
        constructor.
        """
        return self._viewTypes[0]

    @property
    def viewTypes(self) -> List[type[View]]:
        """
        List of view types available for this document template.
        """
        return self._viewTypes

    @property
    def visible(self) -> bool:
        """
        Returns true if the document template can be shown in user dialogs,
        false otherwise.
        """
        return (self._flags & TEMPLATE_VISIBLE) == TEMPLATE_VISIBLE

    @property
    def newable(self) -> bool:
        """
        Returns true if the document template can be shown in "New" dialogs,
        false otherwise.
        """
        return (self._flags & TEMPLATE_NO_CREATE) != TEMPLATE_NO_CREATE

    @property
    def documentTypeName(self) -> str:
        """
        The document type name, as passed to the document template constructor.
        """
        return self._docTypeName

    @property
    def viewTypeName(self) -> str:
        """
        The view type name.
        """
        return self.viewType.typeName

    @property
    def plugin(self) -> str:
        """
        :return: Name of the plugin from which this document template was loaded
        """
        for name, module in self.app.pluginManager.items():
            if (
                hasattr(module, "doctemplates")
                and self.__class__ in module.doctemplates
            ):
                return name
        return ""

    @property
    def config(self) -> Optional[wx.ConfigBase]:
        if self.plugin:
            cfg = self.app.config
            cfg.SetPath("/Plugin/%s/%s/" % (self.plugin, self._docTypeName))
            return cfg
        return None

    # -----------------------------------------------------------------------------
    # public methods
    # -----------------------------------------------------------------------------
    def GetViewType(self, viewTypeName: str) -> Optional[type[View]]:
        for viewType in self._viewTypes:
            if viewType.typeName == viewTypeName:
                return viewType
        return None

    def CreateView(
        self,
        doc: Document,
        flags: int,
        viewType: Optional[Union[str, type[View]]] = None,
    ) -> Optional[View]:
        """
        Creates a new instance of the associated document view. If you have
        not supplied a class to the template constructor, you will need to
        override this function to return an appropriate view instance.
        """
        result = None
        if isinstance(viewType, str):
            viewType = self.GetViewType(viewType)
        if not viewType:
            viewType = self._viewTypes[0]
        view: View = viewType()
        view.document = doc
        try:
            if view.OnCreate(doc, flags) and view.frame:
                view.frame.Refresh()
                result = view
            else:
                view.Destroy()
        except Exception:
            log.exception("CreateView failed:")
            view.Destroy()
        return result

    def CreateDocument(self, path:str, flags: int, **kwds) -> Optional[Document]:
        """
        Creates a new instance of the associated document class. If you have
        not supplied a class to the template constructor, you will need to
        override this function to return an appropriate document instance.
        """
        result = None
        doc: Document = self._docType(self)
        doc.path = path
        self.documentManager.AddDocument(doc)
        if doc.OnCreate(path, flags, **kwds):
            result = doc
        else:
            if doc in self.documentManager.documents:
                doc.DeleteAllViews()
        return result

    def FileMatchesTemplate(self, path: str) -> bool:
        """
        Returns True if the path's extension matches one of this template's
        file filter extensions.
        """
        ext = FindExtension(path)
        if not ext:
            return False

        extList = self._fileFilter.replace("*", "").split(";")
        return ext in extList

    def AddViewType(self, viewType: type[View]):
        if viewType not in self._viewTypes:
            self._viewTypes.append(viewType)
