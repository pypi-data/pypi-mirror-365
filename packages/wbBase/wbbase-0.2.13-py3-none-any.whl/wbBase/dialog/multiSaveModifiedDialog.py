from __future__ import annotations

from typing import TYPE_CHECKING

from .multiSaveModifiedDialogUI import MultiSaveModifiedDialogUI

if TYPE_CHECKING:
    from wbBase.document import DocumentManager


class MultiSaveModifiedDialog(MultiSaveModifiedDialogUI):
    def __init__(self, documentManager: DocumentManager):
        self.documentManager = documentManager
        for doc in self.documentManager.documents:
            if not doc.modified:
                self.documentManager.CloseDocument(doc)
        self.documents = list(self.documentManager.documents)
        super().__init__(documentManager.app.TopWindow)
        self.Title = documentManager.app.AppName
        self.lbl_path.Label = self.documents[0].path or self.documents[0].printableName

    # -----------------------------------------------------------------------------
    # Event handler
    # -----------------------------------------------------------------------------

    def on_btn_yes_to_all(self, event):
        """Save and close all documents"""
        while self.documents:
            doc = self.documents.pop(0)
            if doc.Save():
                self.documentManager.CloseDocument(doc, False)
        self.EndModal(0)

    def on_btn_no_to_all(self, event):
        """Close all documents without saving"""
        while self.documents:
            doc = self.documents.pop(0)
            doc.modified = False
            self.documentManager.CloseDocument(doc)
        self.EndModal(0)

    def on_btn_cancel(self, event):
        """Keep current document unsaved open"""
        self.documents.pop(0)
        if self.documents:
            self.lbl_path.Label = (
                self.documents[0].path or self.documents[0].printableName
            )
        else:
            self.EndModal(0)

    def on_btn_no(self, event):
        """Close current document without saving"""
        doc = self.documents.pop(0)
        doc.modified = False
        self.documentManager.CloseDocument(doc)
        if self.documents:
            self.lbl_path.Label = (
                self.documents[0].path or self.documents[0].printableName
            )
        else:
            self.EndModal(0)

    def on_btn_yes(self, event):
        """Save and close current document"""
        doc = self.documents.pop(0)
        if doc.Save():
            self.documentManager.CloseDocument(doc, False)
        if self.documents:
            self.lbl_path.Label = (
                self.documents[0].path or self.documents[0].printableName
            )
        else:
            self.EndModal(0)
