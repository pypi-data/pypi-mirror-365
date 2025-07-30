"""
This module implements the scriptability of Workbench application
"""
from __future__ import annotations

import os
from importlib import import_module
from typing import TYPE_CHECKING, Optional, List

import wx

from .document.manager import DOC_SILENT
from .shortcut import shortcutsFromConfig

if TYPE_CHECKING:
    from .application import App

def execsource(source, filename:str="<string>", global_vars=None, local_vars=None):
    """
    Execute python source code.
    """
    code = compile(source, filename, "exec")
    if not global_vars:
        main = import_module("__main__")
        global_vars = main.__dict__
    # prepare environment
    del_name = False
    if "__name__" not in global_vars:
        global_vars["__name__"] = "__main__"
        del_name = True
    # execute the code
    exec(code, global_vars, local_vars)
    # cleanup environment
    if del_name and "__name__" in global_vars:
        del global_vars["__name__"]


def execfile(filePath:str, global_vars=None, local_vars=None) -> None:
    """
    Execute a python script given by filePath
    """
    with open(filePath, "r", encoding="utf-8") as sourcefile:
        execsource(sourcefile.read(), filePath, global_vars, local_vars)


def makeMacroTree(folder, tree):
    if os.path.isdir(folder):
        for name in os.listdir(folder):
            if not name.startswith("_") and not name.startswith("."):
                fullPath = os.path.join(folder, name)
                if name.lower().endswith(".py"):
                    tree[name[:-3]] = fullPath
                elif os.path.isdir(fullPath):
                    if name in tree and isinstance(tree[name], dict):
                        subtree = tree[name]
                    elif name not in tree:
                        subtree = {}
                    subtree = makeMacroTree(fullPath, subtree)
                    if subtree:
                        tree[name] = subtree
    return tree


def makeMergedMacroTree(folderList):
    tree = {}
    for folder in folderList:
        tree = makeMacroTree(folder, tree)
    return tree


class MacroMenuItem(wx.MenuItem):
    def __init__(self, parentMenu, path, handler):
        name = os.path.splitext(os.path.basename(path))[0]
        wx.MenuItem.__init__(self, parentMenu, wx.ID_ANY, name)
        self.SetBitmap(
            wx.ArtProvider.GetBitmap("wxART_PYTHON_FILE", wx.ART_MENU, wx.Size(16, 16))
        )
        self.path = path
        handler.Bind(wx.EVT_MENU, handler.on_MenuSelection, self, self.Id)

    def __repr__(self):
        return f"<MacroMenuItem: {self.path}>"

    @property
    def app(self) -> App:
        return wx.GetApp()


class MacroMenu(wx.Menu):
    def __init__(self, handler=None, folderList=None):
        super().__init__()
        self.handler = handler or self
        self.folderList:list = folderList or []
        self._macroTree = None
        self._lastMacroPath:Optional[str] = None
        if folderList:
            self.folderList = folderList
            # repeat ---
            self.menuItem_repeat = wx.MenuItem(
                self, wx.ID_ANY, "Repeat: ", "Repeat the last used Macro"
            )
            self.menuItem_repeat.Enable(False)
            self.Bind(wx.EVT_MENU, self.on_macroRepeat, id=self.menuItem_repeat.Id)
            # update ---
            self.menuItem_update = wx.MenuItem(
                self, wx.ID_ANY, "Update Menu", "Rebuild this menu"
            )
            self.menuItem_update.SetBitmap(
                wx.ArtProvider.GetBitmap("RELOAD", wx.ART_MENU, wx.Size(16, 16))
            )
            self.Bind(wx.EVT_MENU, self.on_menuUpdate, id=self.menuItem_update.Id)
            self._updateMenue()

    def __repr__(self) -> str:
        return "<MacroMenu>"

    def _clearMenu(self) -> None:
        for menuItem in self.MenuItems:
            if menuItem in (self.menuItem_repeat, self.menuItem_update):
                self.Remove(menuItem)
            else:
                self.handler.Unbind(wx.EVT_MENU, id=menuItem.Id)
                self.DestroyItem(menuItem)

    def _updateMenue(self) -> None:
        self.Append(self.menuItem_repeat)
        self.Append(wx.MenuItem(self, wx.ID_SEPARATOR))
        self.addMacroTree(self.macroTree, self)
        self.Append(wx.MenuItem(self, wx.ID_SEPARATOR))
        self.Append(self.menuItem_update)

    # ==========================================================================
    # Properties
    # ==========================================================================

    @property
    def app(self) -> App:
        return wx.GetApp()

    @property
    def macroTree(self):
        if not self._macroTree and self.folderList:
            self._macroTree = makeMergedMacroTree(self.folderList)
        return self._macroTree

    # ==========================================================================
    # public methods
    # ==========================================================================

    def addMacroTree(self, macroTree, menu:wx.Menu) -> wx.Menu:
        bmpDir = wx.ArtProvider.GetBitmap("wxART_FOLDER", wx.ART_MENU, wx.Size(16, 16))
        for name in sorted(macroTree, key=str.lower):
            item = macroTree[name]
            if isinstance(item, dict):
                subMenu = MacroMenu(self.handler)
                subMenu.addMacroTree(item, subMenu)
                menuItem = menu.AppendSubMenu(subMenu, name)
                menuItem.SetBitmap(bmpDir)
            elif os.path.isfile(item):
                self.Append(MacroMenuItem(self, item, self.handler))
        return menu

    def rebuild(self) -> None:
        self._macroTree = None
        self._clearMenu()
        self._updateMenue()
        if self is self.app.TopWindow.scriptsMenu:
            shortcutsFromConfig()

    # =========================================================================
    # Event Handler
    # =========================================================================

    def on_macroRepeat(self, event):
        execfile(self._lastMacroPath)

    def on_MenuSelection(self, event):
        menuItem:MacroMenuItem = self.FindItemById(event.Id)
        if menuItem.path and os.path.isfile(menuItem.path):
            if wx.GetKeyState(wx.WXK_CONTROL):
                self.app.documentManager.CreateDocument(menuItem.path, DOC_SILENT)
            else:
                execfile(menuItem.path)
                self._lastMacroPath = menuItem.path
                self.menuItem_repeat.SetItemLabel(
                    f"Repeat: {os.path.splitext(os.path.basename(menuItem.path))[0]}"
                )
                self.menuItem_repeat.Enable(True)

    def on_menuUpdate(self, event):
        self.rebuild()

class MacroButtonMixin:
    def __init__(self, macroButton, folderName, view=None):
        self._folderName = folderName
        self.view = view
        self._macroFolderPath = []
        self._macroMenu = None
        macroButton.Bind(wx.EVT_BUTTON, self.on_macroButton)
        macroButton.Bind(wx.EVT_LEFT_DOWN, self.onLeftDown_macroButton)
        macroButton.Bind(wx.EVT_UPDATE_UI, self.onUpdate_macroButton)

    # ==========================================================================
    # Properties
    # ==========================================================================

    @property
    def macroFolderPath(self) -> List[str]:
        if not self._macroFolderPath:
            app: App = wx.GetApp()
            cfg = app.TopWindow.config
            self._macroFolderPath = [
                os.path.join(
                    cfg.Read("/Application/SharedData/Dir", app.sharedDataDir),
                    "Macro",
                    "_system",
                    self._folderName,
                ),
                os.path.join(
                    cfg.Read("/Application/PrivateData/Dir", app.privateDataDir),
                    "Macro",
                    "_system",
                    self._folderName,
                ),
            ]
        return self._macroFolderPath

    @property
    def isMacroFolderPath(self) -> bool:
        return any(os.path.isdir(p) for p in self.macroFolderPath)

    @property
    def macroMenu(self) -> MacroMenu:
        if not self._macroMenu and self.isMacroFolderPath:
            self._macroMenu = MacroMenu(folderList=self.macroFolderPath)
        return self._macroMenu

    # =========================================================================
    # Event Handler
    # =========================================================================

    def on_macroButton(self, event):
        if self.view:
            self.view.Activate()
        self.PopupMenu(self.macroMenu)

    def onLeftDown_macroButton(self, event):
        if event.ControlDown():
            self.macroMenu.on_update(event)
        event.Skip()

    def onUpdate_macroButton(self, event: wx.UpdateUIEvent):
        event.Enable(self.macroMenu is not None)
