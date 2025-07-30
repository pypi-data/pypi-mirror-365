from __future__ import annotations

import logging
import os
import sys
from functools import partial
from typing import TYPE_CHECKING, Optional, ClassVar

import wx
from wx import aui
from wx import adv
from wx.lib.dialogs import ScrolledMessageDialog

from .dialog.preferences import PreferencesDialog
from .document.manager import DocumentManager
from .panelManager import PanelManager
from .pluginManager import PluginManager
from .scripting import MacroMenu  # , makeMergedMacroTree
# from .shortcut import shortcutsFromConfig

if TYPE_CHECKING:
    from .application import App

log = logging.getLogger(__name__)


class FileDropTarget(wx.FileDropTarget):
    @property
    def app(self) -> App:
        """
        The running Workbench application.
        """
        return wx.GetApp()

    def OnDropFiles(self, x, y, filenames):
        wx.CallAfter(self.app.TopWindow.documentManager.openDocuments, filenames)
        return True


class ApplicationWindow(wx.Frame):
    """
    Implementation of the main application window
    """

    panelManagerClass: ClassVar[type[PanelManager]] = PanelManager
    documentManagerClass: ClassVar[type[DocumentManager]] = DocumentManager

    MenuBar: wx.MenuBar

    def __init__(self, iconName: str = ""):
        self._toolbarEdit: Optional[aui.AuiToolBar] = None
        self._showTooltip: bool = False
        app: App = wx.GetApp()
        wx.Frame.__init__(
            self,
            parent=None,
            id=wx.ID_ANY,
            title=app.info.AppDisplayName,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL,
            name="ApplicationWindow",
        )
        self.SetIcon(iconName)
        self._externalTools = []
        self._menubar = wx.MenuBar()
        self.CreateStatusBar(3, wx.STB_SIZEGRIP, wx.ID_ANY)
        self.loadConfig()
        self._documentManager: DocumentManager = self.documentManagerClass(self)
        self._panelManager: PanelManager = self.panelManagerClass(self)
        app.splashMessage("building menus")
        self.PushEventHandler(self._documentManager)
        self.editMenu = wx.Menu()
        self.buildEditMenu()
        self.scriptsMenu = None
        self.buildScriptsMenu()
        self.extraMenu = wx.Menu()
        self.buildExtraMenu()
        self.helpMenu = wx.Menu()
        self.buildHelpMenu()
        app.splashMessage("init panels")
        self.panelManager.initPanels()
        self._menubar.Append(self.documentManager.menu, "&File")
        self._menubar.Append(self.editMenu, "&Edit")
        self._menubar.Append(self.panelManager.menu, "&View")
        self._menubar.Append(self.scriptsMenu, "&Scripts")
        self._menubar.Append(self.extraMenu, "E&xtra")
        self._menubar.Append(self.helpMenu, "&Help")
        app.splashMessage("init menu bar")
        self.SetMenuBar(self._menubar)
        # shortcutsFromConfig()

        # =================================================================================
        self.SetDropTarget(FileDropTarget())
        # =================================================================================

        # --- Connect Events ---
        # Window Events
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_SIZE, self.on_resize)
        self.Bind(wx.EVT_SYS_COLOUR_CHANGED, self.on_sys_colour_chnaged)
        # Menu Events
        self.Bind(wx.EVT_MENU, self.on_edit_undo, id=wx.ID_UNDO)
        self.Bind(wx.EVT_MENU, self.on_edit_redo, id=wx.ID_REDO)
        self.Bind(wx.EVT_MENU, self.on_edit_copy, id=wx.ID_COPY)
        self.Bind(wx.EVT_MENU, self.on_edit_cut, id=wx.ID_CUT)
        self.Bind(wx.EVT_MENU, self.on_edit_paste, id=wx.ID_PASTE)
        self.Bind(wx.EVT_MENU, self.on_edit_select_all, id=wx.ID_SELECTALL)
        self.Bind(wx.EVT_MENU, self.on_find, id=wx.ID_FIND)
        self.Bind(
            wx.EVT_MENU, self.on_find_next, id=self.editMenu.FindItem("Find Next")
        )
        self.Bind(wx.EVT_MENU, self.on_replace, id=wx.ID_REPLACE)
        self.Bind(wx.EVT_MENU, self.on_edit_preferences, id=wx.ID_PREFERENCES)
        self.Bind(wx.EVT_MENU, self.on_help_about, id=wx.ID_ABOUT)
        self.Bind(
            wx.EVT_MENU,
            self.on_help_about_plugin,
            id=self.helpMenu.FindItem("About Plugins"),
        )
        # Update UI Events
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_edit_undo, id=wx.ID_UNDO)
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_edit_redo, id=wx.ID_REDO)
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_edit_copy, id=wx.ID_COPY)
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_edit_cut, id=wx.ID_CUT)
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_edit_paste, id=wx.ID_PASTE)
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_edit_select_all, id=wx.ID_SELECTALL)
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_find, id=wx.ID_FIND)
        self.Bind(
            wx.EVT_UPDATE_UI,
            self.on_update_find_next,
            id=self.editMenu.FindItem("Find Next"),
        )
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_replace, id=wx.ID_REPLACE)

        app.splashMessage("main application window created")

    def __repr__(self):
        return f'<Application Window of {self.app.info.AppName}">'

    # -----------------------------------------------------------------------------
    # Properties
    # -----------------------------------------------------------------------------

    @property
    def app(self) -> App:
        """
        The running Workbench application.
        """
        return wx.GetApp()

    @property
    def config(self) -> wx.ConfigBase:
        return self.app.config

    @property
    def pluginManager(self) -> PluginManager:
        """
        The plugin manager of the running application.
        """
        return self.app.pluginManager

    @property
    def panelManager(self) -> PanelManager:
        """
        The panel manager of the running application.
        """
        return self._panelManager

    @property
    def documentManager(self) -> DocumentManager:
        """
        The document manager of the running application.
        """
        return self._documentManager

    @property
    def editToolbar(self) -> aui.AuiToolBar:
        if not self._toolbarEdit:
            menu = self.editMenu
            self._toolbarEdit = tb = aui.AuiToolBar(
                self.TopLevelParent,
                wx.ID_ANY,
                wx.DefaultPosition,
                wx.DefaultSize,
                aui.AUI_TB_HORZ_LAYOUT | aui.AUI_TB_PLAIN_BACKGROUND | wx.NO_BORDER,
            )
            tb.SetName("Edit")
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
        return self._toolbarEdit

    @property
    def showTooltip(self) -> bool:
        return self._showTooltip

    @showTooltip.setter
    def showTooltip(self, value):
        self._showTooltip = bool(value)
        wx.ToolTip.Enable(self._showTooltip)

    @property
    def externalTools(self):
        return self._externalTools

    # -----------------------------------------------------------------------------
    # public methods
    # -----------------------------------------------------------------------------

    def SetIcon(self, iconName: str = "") -> None:
        if iconName:
            super().SetIcon(wx.ArtProvider.GetIcon(iconName, wx.ART_FRAME_ICON))

    def buildEditMenu(self) -> None:
        mnu = self.editMenu
        menuItem = partial(
            wx.MenuItem,
            parentMenu=mnu,
            text=wx.EmptyString,
            helpString=wx.EmptyString,
            kind=wx.ITEM_NORMAL,
        )
        getBitmap = partial(wx.ArtProvider.GetBitmap, client=wx.ART_MENU)
        # undo/redo
        item = menuItem(id=wx.ID_UNDO)
        item.SetBitmap(getBitmap(wx.ART_UNDO))
        mnu.Append(item)

        item = menuItem(id=wx.ID_REDO)
        item.SetBitmap(getBitmap(wx.ART_REDO))
        mnu.Append(item)

        # copy/cut/paste
        mnu.AppendSeparator()

        item = menuItem(id=wx.ID_COPY)
        item.SetBitmap(getBitmap(wx.ART_COPY))
        mnu.Append(item)

        item = menuItem(id=wx.ID_CUT)
        item.SetBitmap(getBitmap(wx.ART_CUT))
        mnu.Append(item)

        item = menuItem(id=wx.ID_PASTE)
        item.SetBitmap(getBitmap(wx.ART_PASTE))
        mnu.Append(item)

        # select all
        mnu.AppendSeparator()

        item = menuItem(id=wx.ID_SELECTALL)
        item.SetBitmap(getBitmap("SELECT_ALL"))
        mnu.Append(item)

        # find/replace
        mnu.AppendSeparator()

        item = menuItem(id=wx.ID_FIND)
        item.SetBitmap(getBitmap(wx.ART_FIND))
        mnu.Append(item)

        item = wx.MenuItem(mnu, wx.ID_ANY, "Find Next\tF3", "Find next", wx.ITEM_NORMAL)
        item.SetBitmap(getBitmap("FIND_NEXT"))
        mnu.Append(item)

        item = menuItem(id=wx.ID_REPLACE)
        item.SetBitmap(getBitmap("REPLACE"))
        mnu.Append(item)

        # preferences
        mnu.AppendSeparator()

        self.menu_edit_preferences = menuItem(id=wx.ID_PREFERENCES)
        mnu.Append(self.menu_edit_preferences)

    def buildScriptsMenu(self) -> None:
        macroFolders = []
        cfg = self.config
        with wx.ConfigPathChanger(cfg, "/Application/"):
            macroFolders.append(
                os.path.join(
                    cfg.Read("SharedData/Dir", self.app.sharedDataDir),
                    "Macro",
                )
            )
            macroFolders.append(
                os.path.join(
                    cfg.Read("PrivateData/Dir", self.app.privateDataDir),
                    "Macro",
                ),
            )
        for macroFolder in macroFolders:
            if not os.path.isdir(macroFolder):
                os.makedirs(macroFolder)
            modulesPath = os.path.join(macroFolder, "_Modules")
            if not os.path.isdir(modulesPath):
                os.makedirs(modulesPath)
            if modulesPath not in sys.path:
                sys.path.insert(0, modulesPath)
        self.scriptsMenu = MacroMenu(folderList=macroFolders)

    def buildExtraMenu(self) -> None:
        mnu = self.extraMenu
        if mnu.MenuItemCount == 0:
            mnu.AppendSeparator()
            item = wx.MenuItem(
                mnu, wx.ID_ANY, "Configure", "Configure external tools", wx.ITEM_NORMAL
            )
            mnu.Append(item)
            self.Bind(wx.EVT_MENU, self.on_externalToolConfigure, item, item.Id)
        if mnu.MenuItemCount > 2:
            for i in reversed(range(0, mnu.MenuItemCount - 2)):
                item = mnu.MenuItems[i]
                self.Unbind(wx.EVT_MENU, item, item.Id)
                mnu.DestroyItem(item)
        for i, tool in enumerate(self.externalTools):
            item = wx.MenuItem(
                mnu, wx.ID_ANY, tool["name"], tool["name"], wx.ITEM_NORMAL
            )
            mnu.Insert(i, item)
            self.Bind(wx.EVT_MENU, self.on_externalTool, item, item.Id)

    def buildHelpMenu(self) -> None:
        mnu = self.helpMenu
        self.menu_help_about = wx.MenuItem(
            mnu, wx.ID_ABOUT, wx.EmptyString, wx.EmptyString, wx.ITEM_NORMAL
        )
        self.menu_help_about.SetBitmap(wx.ArtProvider.GetBitmap("ABOUT", wx.ART_MENU))
        mnu.Append(self.menu_help_about)
        about_plugins = wx.MenuItem(mnu, wx.ID_ANY, "About Plugins")
        mnu.Append(about_plugins)

    def loadConfig(self) -> None:
        cfg = self.config
        with wx.ConfigPathChanger(cfg, "/Window/"):
            x = cfg.ReadInt("x", -1)
            y = cfg.ReadInt("y", -1)
            self.Position = (x, y)
            width = cfg.ReadInt("width", 800)
            height = cfg.ReadInt("height", 600)
            self.Size = (width, height)
            self.showTooltip = cfg.ReadBool("showTooltip", True)
            self.StatusBar.Show(cfg.ReadBool("showStatusBar", True))
        with wx.ConfigPathChanger(cfg, "/Application/"):
            self._externalTools = eval(cfg.Read("ExternalTools", "[]"))

    def saveConfig(self) -> None:
        cfg = self.config
        with wx.ConfigPathChanger(cfg, "/Window/"):
            x, y = self.Position
            cfg.WriteInt("x", x)
            cfg.WriteInt("y", y)
            width, height = self.Size
            cfg.WriteInt("width", width)
            cfg.WriteInt("height", height)
            cfg.WriteBool("showTooltip", self.showTooltip)
            cfg.WriteBool("showStatusBar", self.StatusBar.IsShown())
        self.panelManager.saveConfig()
        self.documentManager.saveConfig()

    # -----------------------------------------------------------------------------
    # Event handler
    # -----------------------------------------------------------------------------

    def on_sys_colour_chnaged(self, event):
        """
        Prevent colour changes if screenpresso is used to make a screenshot
        """
        dockArtColours = (
            "AUI_DOCKART_BACKGROUND_COLOUR",
            "AUI_DOCKART_BORDER_COLOUR",
            "AUI_DOCKART_SASH_COLOUR",
            "AUI_DOCKART_GRIPPER_COLOUR",
            "AUI_DOCKART_ACTIVE_CAPTION_COLOUR",
            "AUI_DOCKART_ACTIVE_CAPTION_GRADIENT_COLOUR",
            "AUI_DOCKART_ACTIVE_CAPTION_TEXT_COLOUR",
            "AUI_DOCKART_INACTIVE_CAPTION_COLOUR",
            "AUI_DOCKART_INACTIVE_CAPTION_GRADIENT_COLOUR",
            "AUI_DOCKART_INACTIVE_CAPTION_TEXT_COLOUR",
        )
        cfg = self.app.config
        with wx.ConfigPathChanger(cfg, "/Window/Panels/"):
            setColour = self.panelManager.ArtProvider.SetColour
            for artColour in dockArtColours:
                setColour(getattr(aui, artColour), wx.Colour(cfg.ReadInt(artColour)))
            self.panelManager.Update()

    def on_resize(self, event: wx.SizeEvent) -> None:
        self._panelManager.checkToolBars()
        event.Skip()

    def on_close(self, event: wx.CommandEvent):
        if self._documentManager.Clear():
            self.saveConfig()
            self._panelManager.UnInit()
            self.PopEventHandler(True)
            self.app.SetAssertMode(wx.APP_ASSERT_SUPPRESS)
            self.Destroy()

    # === Undo/Redo ===
    def on_edit_undo(self, event: wx.CommandEvent):
        self.FindFocus().Undo()

    def on_update_edit_undo(self, event: wx.UpdateUIEvent):
        widget = self.FindFocus()
        if widget:
            if widget.Name == "wxWebView":
                event.Enable(False)
                return
            if widget and hasattr(widget, "CanUndo"):
                try:
                    event.Enable(widget.CanUndo())
                except:
                    event.Enable(False)
                return
        event.Enable(False)

    def on_edit_redo(self, event: wx.CommandEvent):
        self.FindFocus().Redo()

    def on_update_edit_redo(self, event: wx.UpdateUIEvent):
        widget = self.FindFocus()
        if widget:
            if widget.Name == "wxWebView":
                event.Enable(False)
                return
            if hasattr(widget, "CanRedo"):
                try:
                    event.Enable(widget.CanRedo())
                except:
                    event.Enable(False)
                return
        event.Enable(False)

    # === Copy/Cut/Paste ===
    def on_edit_copy(self, event: wx.CommandEvent):
        self.FindFocus().Copy()

    def on_update_edit_copy(self, event: wx.UpdateUIEvent):
        widget = self.FindFocus()
        if widget:
            if widget.Name == "wxWebView":
                event.Enable(False)
                return
            if hasattr(widget, "CanCopy"):
                event.Enable(widget.CanCopy())
                return
        event.Enable(False)

    def on_edit_cut(self, event: wx.CommandEvent):
        self.FindFocus().Cut()

    def on_update_edit_cut(self, event: wx.UpdateUIEvent):
        widget = self.FindFocus()
        if widget:
            if widget.Name == "wxWebView":
                event.Enable(False)
                return
            if hasattr(widget, "CanCut"):
                event.Enable(widget.CanCut())
                return
        event.Enable(False)

    def on_edit_paste(self, event: wx.CommandEvent):
        self.FindFocus().Paste()

    def on_update_edit_paste(self, event: wx.UpdateUIEvent):
        widget = self.FindFocus()
        if widget:
            if widget.Name == "wxWebView":
                event.Enable(False)
                return
            if hasattr(widget, "CanPaste"):
                event.Enable(widget.CanPaste())
                return
        event.Enable(False)

    def on_edit_select_all(self, event: wx.CommandEvent):
        widget = self.FindFocus()
        widget.SelectAll()
        event.Skip()

    def on_update_edit_select_all(self, event: wx.UpdateUIEvent):
        widget = self.FindFocus()
        if widget and hasattr(widget, "SelectAll"):
            event.Enable(True)
        else:
            event.Enable(False)

    # === Find/Replace ===
    def on_find(self, event: wx.CommandEvent):
        widget = self.FindFocus()
        widget.doFind()

    def on_update_find(self, event: wx.UpdateUIEvent):
        widget = self.FindFocus()
        if widget and hasattr(widget, "CanFind"):
            event.Enable(widget.CanFind())
        else:
            event.Enable(False)

    def on_find_next(self, event: wx.CommandEvent):
        widget = self.FindFocus()
        widget.doFindNext()

    def on_update_find_next(self, event: wx.UpdateUIEvent):
        widget = self.FindFocus()
        if widget and hasattr(widget, "CanFindNext"):
            event.Enable(widget.CanFindNext())
        else:
            event.Enable(False)

    def on_replace(self, event: wx.CommandEvent):
        widget = self.FindFocus()
        widget.doReplace()

    def on_update_replace(self, event: wx.UpdateUIEvent):
        widget = self.FindFocus()
        if widget and hasattr(widget, "CanReplace"):
            event.Enable(widget.CanReplace())
        else:
            event.Enable(False)

    def on_edit_preferences(self, event: wx.CommandEvent):
        prefDlg: PreferencesDialog
        with PreferencesDialog(self) as prefDlg:
            prefDlg.ShowModal()

    def on_externalTool(self, event: wx.CommandEvent):
        menuItem: wx.MenuItem = self.MenuBar.FindItemById(event.GetId())
        for tool in self.externalTools:
            if tool["name"] == menuItem.ItemLabelText:
                from .tools import startfile  # The wx.App object must be created first!

                oldDir = os.getcwd()
                if os.path.isdir(tool["folder"]):
                    os.chdir(tool["folder"])
                startfile(tool["cmd"])
                os.chdir(oldDir)
                return
        wx.LogError(f"Tool not found {menuItem.ItemLabelText}")

    def on_externalToolConfigure(self, event: wx.CommandEvent):
        prefDlg: PreferencesDialog
        with PreferencesDialog(self) as prefDlg:
            for i in range(prefDlg.book.PageCount):
                if prefDlg.book.GetPageText(i) == "External Tools":
                    prefDlg.book.SetSelection(i)
                    break
            prefDlg.ShowModal()

    def on_help_about(self, event: wx.CommandEvent):
        appInfo = self.app.info
        info = adv.AboutDialogInfo()
        info.Name = appInfo.AppDisplayName
        info.Version = self.app.version
        info.Description = appInfo.Description
        info.Copyright = appInfo.Copyright
        adv.AboutBox(info)

    def on_help_about_plugin(self, event: wx.CommandEvent):
        message = "Plugin version info\n============================\n"
        for pluginName in sorted(self.pluginManager, key=str.lower):
            plugin = self.pluginManager[pluginName]
            if hasattr(plugin, "__version__"):
                message += f"{pluginName:30}\t{plugin.__version__}\n"
        with ScrolledMessageDialog(self, message, "About Plugins") as dlg:
            dlg.ShowModal()
