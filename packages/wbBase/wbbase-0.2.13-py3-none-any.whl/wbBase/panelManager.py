from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional, Sequence

import wx
import wx.aui as aui

from .document.notebook import DocumentNotebook

if TYPE_CHECKING:
    from types import ModuleType

    from .application import App
    from .applicationWindow import ApplicationWindow
    from .document.manager import DocumentManager

PANE_MAXIMIZED = 2**16


def toolbarPaneInfo(name) -> aui.AuiPaneInfo:
    """Returns a aui.AuiPaneInfo for toolbars"""
    info = aui.AuiPaneInfo()
    info.ToolbarPane()
    info.Name(name)
    info.Caption(name)
    info.Dock()
    info.Top()
    return info


class PanelManager(aui.AuiManager):
    ManagedWindow: ApplicationWindow
    ArtProvider: aui.AuiDockArt
    AllPanes: Sequence[aui.AuiPaneInfo]

    def __init__(self, managed_wnd=None, flags=aui.AUI_MGR_DEFAULT):
        self._menu = wx.Menu()
        self._workspace: Dict[str, str] = {}
        self._panel_icons = {}
        self._workspaceCurrent: str = ""
        self._tempPerspective: str = ""
        self.mnu_workspace = wx.Menu()
        self.ID_WORKSPACE_SAVE = None
        aui.AuiManager.__init__(self, managed_wnd, flags)
        self._toolbar = aui.AuiToolBar(
            self.ManagedWindow,
            style=aui.AUI_TB_HORZ_LAYOUT | aui.AUI_TB_PLAIN_BACKGROUND | wx.NO_BORDER,
        )
        self._documentNotebook = DocumentNotebook(self.ManagedWindow)
        self.loadConfig()
        # Bind events
        self.Bind(aui.EVT_AUI_PANE_BUTTON, self.on_PANE_BUTTON)
        # 		self.Bind(aui.EVT_AUI_PANE_MAXIMIZE, self.on_PANE_MAXIMIZE)
        self.Bind(aui.EVT_AUI_PANE_RESTORE, self.on_PANE_RESTORE)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} of "{self.app.AppName}">'

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
    def documentNotebook(self) -> DocumentNotebook:
        return self._documentNotebook

    @property
    def config(self) -> wx.ConfigBase:
        cfg = self.app.config
        cfg.SetPath("/Window/Panels/")
        return cfg

    @property
    def plugins(self) -> Dict[str, ModuleType]:
        return self.app.pluginManager

    @property
    def documentManager(self) -> DocumentManager:
        return self.ManagedWindow.documentManager

    @property
    def menu(self) -> wx.Menu:
        """
        The 'View' menu of the main application window.
        """
        if not self._menu.MenuItemCount:
            mnu = self._menu
            # === Menu View:Toolbars
            mnu_toolbar = wx.Menu()
            item = wx.MenuItem(
                mnu_toolbar,
                wx.ID_ANY,
                "Panels",
                'Show/Hide "Panels" toolbar',
                wx.ITEM_CHECK,
            )
            mnu_toolbar.Append(item)
            self.Bind(wx.EVT_MENU, self.on_menu_panel, id=item.GetId())
            self.Bind(wx.EVT_UPDATE_UI, self.update_menu_panel, id=item.GetId())
            # === Menu View:Panels
            mnu_panel = wx.Menu()
            for pane in self.AllPanes:
                if pane.IsToolbar():
                    item = wx.MenuItem(
                        mnu_toolbar,
                        wx.ID_ANY,
                        pane.caption,
                        'Show/Hide "%s" toolbar' % pane.caption,
                        wx.ITEM_CHECK,
                    )
                    mnu_toolbar.Append(item)
                elif pane.dock_direction != aui.AUI_DOCK_CENTER:
                    item = wx.MenuItem(
                        mnu_panel,
                        wx.ID_ANY,
                        pane.caption,
                        'Show/Hide "%s" panel' % pane.caption,
                        wx.ITEM_CHECK,
                    )
                    mnu_panel.Append(item)
                self.Bind(wx.EVT_MENU, self.on_menu_panel, id=item.Id)
                self.Bind(wx.EVT_UPDATE_UI, self.update_menu_panel, id=item.Id)
            mnu.AppendSubMenu(mnu_toolbar, "Toolbars")
            mnu.AppendSubMenu(mnu_panel, "Panels")
            # === Menu View:Workspaces
            # self.mnu_workspace = wx.Menu()
            item = wx.MenuItem(
                self.mnu_workspace,
                wx.ID_ANY,
                "Save current ...",
                "Save current workspace",
                wx.ITEM_NORMAL,
            )
            self.mnu_workspace.Append(item)
            self.ID_WORKSPACE_SAVE = item.GetId()
            self.Bind(
                wx.EVT_MENU, self.on_menu_workspace_save, id=self.ID_WORKSPACE_SAVE
            )
            self.mnu_workspace.AppendSeparator()
            self.updateWorkspaceMenu()
            mnu.AppendSubMenu(self.mnu_workspace, "Workspaces")

            mnu.AppendSeparator()
            item = wx.MenuItem(
                mnu, wx.ID_ANY, "Tooltips", "Show/Hide Tooltips ", wx.ITEM_CHECK
            )
            mnu.Append(item)
            self.Bind(wx.EVT_MENU, self.on_menu_tooltip, id=item.Id)
            self.Bind(wx.EVT_UPDATE_UI, self.update_menu_tooltip, id=item.Id)

            item = wx.MenuItem(
                mnu, wx.ID_ANY, "Statusbar", "Show/Hide Statusbar ", wx.ITEM_CHECK
            )
            mnu.Append(item)
            self.Bind(wx.EVT_MENU, self.on_menu_statusbar, id=item.Id)
            self.Bind(wx.EVT_UPDATE_UI, self.update_menu_statusbar, id=item.Id)
        return self._menu

    @property
    def toolbar(self) -> aui.AuiToolBar:
        """
        :return: The Panels Toolbar
        """
        if not self._toolbar.GetToolCount():
            menu = self.menu
            tb = self._toolbar
            tb.SetName("Panels")
            tb.SetToolBitmapSize(wx.Size(16, 16))
            getBitmap = lambda artID: wx.ArtProvider.GetBitmap(
                artID, wx.ART_TOOLBAR, wx.Size(16, 16)
            )
            # add full screen check-tool
            tool = tb.AddTool(
                wx.ID_ANY,
                "Full Screen",
                getBitmap("FULLSCREEN"),
                "Toggle Full-Screen mode",
                wx.ITEM_CHECK,
            )
            self.Bind(wx.EVT_TOOL, self.on_tool_fullscreen, id=tool.Id)
            self.Bind(wx.EVT_UPDATE_UI, self.update_tool_fullscreen, id=tool.Id)
            # add Expand Center Panel check-tool
            tool = tb.AddTool(
                wx.ID_ANY,
                "Expand Center Panel",
                getBitmap("EXPAND_CENTER_PANEL"),
                "Expand Center Panel",
                wx.ITEM_CHECK,
            )
            self.Bind(wx.EVT_TOOL, self.on_tool_expandCenterPanel, id=tool.Id)
            self.Bind(wx.EVT_UPDATE_UI, self.update_tool_expandCenterPanel, id=tool.Id)

            tb.AddSeparator()
            # add check-tool for all panes
            for pane in self.AllPanes:
                if (
                    not pane.IsToolbar()
                    and pane.icon.IsOk()
                    and pane.dock_direction != aui.AUI_DOCK_CENTER
                ):
                    id = menu.FindItem(pane.caption)
                    label = pane.caption
                    bitmap = pane.icon
                    short_help_string = 'Show/Hide "%s" panel' % pane.caption
                    kind = wx.ITEM_CHECK
                    tb.AddTool(id, label, bitmap, short_help_string, kind)
            tb.Realize()
        return self._toolbar

    @property
    def centerPane(self) -> Optional[aui.AuiPaneInfo]:
        for pane in self.AllPanes:
            if pane.dock_direction == aui.AUI_DOCK_CENTER and pane.IsDocked():
                return pane
        return None

    @property
    def centerPaneMaximized(self):
        panes = [
            p
            for p in self.AllPanes
            if p.IsShown() and p.IsDocked() and not p.IsToolbar()
        ]
        return len(panes) == 1 and panes[0].dock_direction == aui.AUI_DOCK_CENTER

    # -----------------------------------------------------------------------------
    # Public Methods
    # -----------------------------------------------------------------------------

    def LoadPerspective(self, perspective, update=True) -> None:
        super().LoadPerspective(perspective, update)
        pane: aui.AuiPaneInfo
        for pane in self.AllPanes:
            # restore pane icons
            if pane.name in self._panel_icons:
                icon = self._panel_icons[pane.name]
                if icon.IsOk():
                    pane.Icon(icon)
        self.checkToolBars()

    def loadConfig(self) -> None:
        config = self.config
        config.SetPath("/Window/")
        self._workspaceCurrent = config.Read("workspace", "default")
        config.SetPath("/Window/workspace/")
        more, name, index = config.GetFirstEntry()
        while more:
            self._workspace[name] = config.Read(name)
            more, name, index = config.GetNextEntry(index)
        config.SetPath("/Window/Panels/")
        self.Flags = config.ReadInt("AUI_MGR_FLAGS", aui.AUI_MGR_DEFAULT)
        setMetric = self.ArtProvider.SetMetric
        setMetric(aui.AUI_DOCKART_SASH_SIZE, config.ReadInt("AUI_DOCKART_SASH_SIZE", 4))
        setMetric(
            aui.AUI_DOCKART_CAPTION_SIZE, config.ReadInt("AUI_DOCKART_CAPTION_SIZE", 17)
        )
        setMetric(
            aui.AUI_DOCKART_GRIPPER_SIZE, config.ReadInt("AUI_DOCKART_GRIPPER_SIZE", 9)
        )
        setMetric(
            aui.AUI_DOCKART_PANE_BORDER_SIZE,
            config.ReadInt("AUI_DOCKART_PANE_BORDER_SIZE", 1),
        )
        setMetric(
            aui.AUI_DOCKART_PANE_BUTTON_SIZE,
            config.ReadInt("AUI_DOCKART_PANE_BUTTON_SIZE", 14),
        )
        setMetric(
            aui.AUI_DOCKART_GRADIENT_TYPE,
            config.ReadInt("AUI_DOCKART_GRADIENT_TYPE", 0),
        )
        setColour = self.ArtProvider.SetColour
        getColour = lambda ColourIndex: wx.SystemSettings.GetColour(
            ColourIndex
        ).GetRGB()
        colour = wx.Colour(
            config.ReadInt(
                "AUI_DOCKART_BACKGROUND_COLOUR", getColour(wx.SYS_COLOUR_BACKGROUND)
            )
        )
        setColour(aui.AUI_DOCKART_BACKGROUND_COLOUR, colour)
        self.ManagedWindow.SetBackgroundColour(colour)
        self.ManagedWindow.StatusBar.SetBackgroundColour(colour)
        setColour(
            aui.AUI_DOCKART_BORDER_COLOUR,
            wx.Colour(
                config.ReadInt(
                    "AUI_DOCKART_BORDER_COLOUR", getColour(wx.SYS_COLOUR_ACTIVEBORDER)
                )
            ),
        )
        setColour(
            aui.AUI_DOCKART_SASH_COLOUR,
            wx.Colour(
                config.ReadInt(
                    "AUI_DOCKART_SASH_COLOUR", getColour(wx.SYS_COLOUR_BTNFACE)
                )
            ),
        )
        setColour(
            aui.AUI_DOCKART_GRIPPER_COLOUR,
            wx.Colour(
                config.ReadInt(
                    "AUI_DOCKART_GRIPPER_COLOUR", getColour(wx.SYS_COLOUR_BTNFACE)
                )
            ),
        )
        setColour(
            aui.AUI_DOCKART_ACTIVE_CAPTION_COLOUR,
            wx.Colour(
                config.ReadInt(
                    "AUI_DOCKART_ACTIVE_CAPTION_COLOUR",
                    getColour(wx.SYS_COLOUR_ACTIVECAPTION),
                )
            ),
        )
        setColour(
            aui.AUI_DOCKART_ACTIVE_CAPTION_GRADIENT_COLOUR,
            wx.Colour(
                config.ReadInt(
                    "AUI_DOCKART_ACTIVE_CAPTION_GRADIENT_COLOUR",
                    getColour(wx.SYS_COLOUR_GRADIENTACTIVECAPTION),
                )
            ),
        )
        setColour(
            aui.AUI_DOCKART_ACTIVE_CAPTION_TEXT_COLOUR,
            wx.Colour(
                config.ReadInt(
                    "AUI_DOCKART_ACTIVE_CAPTION_TEXT_COLOUR",
                    getColour(wx.SYS_COLOUR_CAPTIONTEXT),
                )
            ),
        )
        setColour(
            aui.AUI_DOCKART_INACTIVE_CAPTION_COLOUR,
            wx.Colour(
                config.ReadInt(
                    "AUI_DOCKART_INACTIVE_CAPTION_COLOUR",
                    getColour(wx.SYS_COLOUR_INACTIVECAPTION),
                )
            ),
        )
        setColour(
            aui.AUI_DOCKART_INACTIVE_CAPTION_GRADIENT_COLOUR,
            wx.Colour(
                config.ReadInt(
                    "AUI_DOCKART_INACTIVE_CAPTION_GRADIENT_COLOUR",
                    getColour(wx.SYS_COLOUR_GRADIENTINACTIVECAPTION),
                )
            ),
        )
        setColour(
            aui.AUI_DOCKART_INACTIVE_CAPTION_TEXT_COLOUR,
            wx.Colour(
                config.ReadInt(
                    "AUI_DOCKART_INACTIVE_CAPTION_TEXT_COLOUR",
                    getColour(wx.SYS_COLOUR_INACTIVECAPTIONTEXT),
                )
            ),
        )
        self.Update()

    def saveConfig(self) -> None:
        config = self.config
        config.SetPath("/Window/")
        config.Write("workspace", self._workspaceCurrent)
        self._workspace[self._workspaceCurrent] = self.SavePerspective()
        config.SetPath("/Window/workspace/")
        for name, value in self._workspace.items():
            config.Write(name, value)
        config.SetPath("/Window/Panels/")
        config.WriteInt("AUI_MGR_FLAGS", self.Flags)

    def initPanels(self) -> None:
        if self.documentManager.toolbar:
            self.AddPane(self.documentManager.toolbar, toolbarPaneInfo("File"))
        self.AddPane(self.ManagedWindow.editToolbar, toolbarPaneInfo("Edit"))

        panels = []
        toolbars = []
        plugins = self.plugins
        for name in plugins:
            plugin = plugins[name]
            if hasattr(plugin, "panels"):
                panels.extend(plugin.panels)
            if hasattr(plugin, "toolbars"):
                toolbars.extend(plugin.toolbars)
        for frame, info in panels:
            self.app.splashMessage(f"adding panel {info.name}")
            self.AddPane(frame(self.ManagedWindow), info)
            if info.icon.IsOk():
                # save pane icons to be restored on LoadPrespective
                self._panel_icons[info.name] = info.icon
        for toolbar, info in toolbars:
            self.app.splashMessage(f"adding toolbar {info.name}")
            self.AddPane(toolbar(self.ManagedWindow), info)

        info = aui.AuiPaneInfo()
        info.CenterPane()
        info.Name("DocumentNotebook")
        info.Caption("DocumentNotebook")
        info.PaneBorder(False)
        self.AddPane(self._documentNotebook, info)

        self.AddPane(self.toolbar, toolbarPaneInfo("Panels"))
        workspace = self._workspace.get(self._workspaceCurrent)
        if workspace:
            self.LoadPerspective(workspace)
        self.Update()

    def getPaneByCaption(self, caption) -> Optional[aui.AuiPaneInfo]:
        for pane in self.AllPanes:
            if pane.caption == caption:
                return pane
        return None

    def getWindowByCaption(self, caption):
        pane = self.getPaneByCaption(caption)
        if pane and pane.IsOk():
            return pane.window

    def updateWorkspaceMenu(self) -> None:
        if self.mnu_workspace is not None:
            IDs_keep = (wx.ID_SEPARATOR, self.ID_WORKSPACE_SAVE)
            IDs = [i.Id for i in self.mnu_workspace.MenuItems if i.Id not in IDs_keep]
            for id in IDs:
                self.Unbind(wx.EVT_MENU, id=id)
                self.mnu_workspace.DestroyItem(id)
            for name in sorted(self._workspace):
                item = wx.MenuItem(
                    self.mnu_workspace,
                    wx.ID_ANY,
                    name,
                    f'Select workspace "{name}"',
                    wx.ITEM_RADIO,
                )
                self.mnu_workspace.Append(item)
                self.Bind(wx.EVT_MENU, self.on_menu_workspace_select, id=item.GetId())
                if name == self._workspaceCurrent:
                    item.Check(True)

    def maximizeCenterPane(self) -> None:
        pane = self.centerPane
        event = aui.AuiManagerEvent()
        event.Manager = self
        event.Button = aui.AUI_BUTTON_MAXIMIZE_RESTORE
        event.Pane = pane
        self.QueueEvent(event)

    def checkToolBars(self) -> None:
        """
        Ensure that all shown toolbars are placed inside the visible area of
        the main window.
        """
        needUpdate = False
        toolbars = [p for p in self.AllPanes if p.IsToolbar() and p.IsShown()]
        for toolbar in sorted(toolbars, key=lambda t: (t.dock_row, t.dock_pos)):
            if toolbar.best_size.width < toolbar.rect.width:
                toolbar.Position(toolbar.dock_pos -1)
                needUpdate = True
            elif toolbar.best_size.width > toolbar.rect.width:
                toolbar.Row(toolbar.dock_row + 1)
                toolbar.Position(0)
                needUpdate = True
        if needUpdate:
            self.Update()
            self.checkToolBars()


    def _restoreTempPerspective(self) -> None:
        if self._tempPerspective:
            self.LoadPerspective(self._tempPerspective)
            self._tempPerspective = ""

    # -----------------------------------------------------------------------------
    # Event handler
    # -----------------------------------------------------------------------------

    def on_PANE_BUTTON(self, event:aui.AuiManagerEvent):
        if (
            event.Button == aui.AUI_BUTTON_MAXIMIZE_RESTORE
            and not self._tempPerspective
        ):
            self._tempPerspective = self.SavePerspective()
        event.Skip()

    def on_PANE_RESTORE(self, event:aui.AuiManagerEvent):
        self._restoreTempPerspective()

    def on_tool_fullscreen(self, event:aui.AuiToolBarEvent):
        self.ManagedWindow.ShowFullScreen(event.IsChecked(), wx.FULLSCREEN_ALL)

    def update_tool_fullscreen(self, event: wx.UpdateUIEvent):
        event.Check(self.ManagedWindow.IsFullScreen())

    def on_tool_expandCenterPanel(self, event:aui.AuiToolBarEvent):
        pane = self.centerPane
        if pane and pane.IsOk():
            if event.IsChecked():
                self._tempPerspective = self.SavePerspective()
                for pane in self.AllPanes:
                    if (
                        pane.IsShown()
                        and pane.IsDocked()
                        and not pane.IsToolbar()
                        and not pane.dock_direction == aui.AUI_DOCK_CENTER
                    ):
                        pane.Hide()
                self.Update()
            else:
                self._restoreTempPerspective()

    def update_tool_expandCenterPanel(self, event: wx.UpdateUIEvent):
        event.Check(self.centerPaneMaximized)

    def on_menu_panel(self, event: wx.CommandEvent):
        eventObject = event.EventObject
        paneInfo = aui.AuiPaneInfo()
        if isinstance(eventObject, wx.Menu):
            menuItem = eventObject.FindItemById(event.Id)
            if menuItem:
                paneInfo = self.getPaneByCaption(menuItem.ItemLabelText)
        elif isinstance(eventObject, aui.AuiToolBar):
            tool = eventObject.FindTool(event.Id)
            if tool:
                paneInfo = self.getPaneByCaption(tool.Label)
        if paneInfo and paneInfo.IsOk():
            paneInfo.Show(event.IsChecked())
            self.Update()

    def update_menu_panel(self, event: wx.UpdateUIEvent):
        eventObject = event.EventObject
        paneInfo = aui.AuiPaneInfo()
        if isinstance(eventObject, wx.Menu):
            menuItem = eventObject.FindItemById(event.Id)
            if menuItem:
                paneInfo = self.getPaneByCaption(menuItem.ItemLabelText)
        elif isinstance(eventObject, aui.AuiToolBar):
            tool = eventObject.FindTool(event.Id)
            if tool:
                paneInfo = self.getPaneByCaption(tool.Label)
        if paneInfo and paneInfo.IsOk():
            event.Check(paneInfo.IsShown())
        else:
            event.Check(False)

    def on_menu_workspace_save(self, event: wx.CommandEvent):
        if self._workspaceCurrent:
            name = self._workspaceCurrent
        else:
            name = "default"
        dlg = wx.TextEntryDialog(
            self.ManagedWindow,
            "Enter name for workspace",
            "Save workspace",
            name,
            wx.OK | wx.CANCEL | wx.CENTRE,
        )
        dlg.CenterOnParent()
        if dlg.ShowModal() == wx.ID_OK and dlg.GetValue():
            self._workspaceCurrent = dlg.GetValue()
            self.saveConfig()
            self.updateWorkspaceMenu()
        dlg.Destroy()

    def on_menu_workspace_select(self, event: wx.CommandEvent):
        item = self.mnu_workspace.FindItemById(event.Id)
        if item and item.ItemLabelText in self._workspace:
            self._workspaceCurrent = item.ItemLabelText
            self.updateWorkspaceMenu()
            self.LoadPerspective(self._workspace[self._workspaceCurrent])
            self.Update()

    def on_menu_tooltip(self, event: wx.CommandEvent):
        self.app.TopWindow.showTooltip = event.IsChecked()

    def update_menu_tooltip(self, event: wx.UpdateUIEvent):
        event.Check(self.app.TopWindow.showTooltip)

    def on_menu_statusbar(self, event: wx.CommandEvent):
        self.app.TopWindow.StatusBar.Show(event.IsChecked())
        self.app.TopWindow.SendSizeEvent()
        self.app.TopWindow.Refresh()

    def update_menu_statusbar(self, event: wx.UpdateUIEvent):
        event.Check(self.app.TopWindow.StatusBar.IsShown())