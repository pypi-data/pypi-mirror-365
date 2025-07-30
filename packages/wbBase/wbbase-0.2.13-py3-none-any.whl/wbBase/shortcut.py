from __future__ import annotations

from typing import TYPE_CHECKING

import wx
from wx.lib.agw.shortcuteditor import DISABLED_STRING, EVT_SHORTCUT_CHANGED
from wx.lib.agw.shortcuteditor import ListShortcut as ListShortcutBase
from wx.lib.agw.shortcuteditor import Shortcut

if TYPE_CHECKING:
    from wbBase.applicationWindow import ApplicationWindow


class ConflictDialog(wx.MessageDialog):
    """
    This class is used to resolve shortcut conflicts when the user assigns a shortcut
    that is already taken by another entry in the shortcut list.
    """

    def __init__(self, parent, conflict: Shortcut) -> None:
        message = f"Shortcut '{conflict.accelerator}' is already taken by '{conflict.label}' from the '{conflict.parent.label}' group."
        message += "\n\n"
        message += f"Reassigning the shortcut will cause it to be removed from '{conflict.label}'."
        style = wx.OK | wx.CANCEL | wx.ICON_WARNING
        super().__init__(
            parent, message, "Conflicting Shortcuts", style, wx.DefaultPosition
        )
        self.SetOKLabel("Reassign shortcut")


class ListShortcut(ListShortcutBase):
    """
    This class is used to display the shortcut label (with an optional bitmap next to it),
    its accelerator and the help string associated with it (if present).
    """

    manager: Shortcut

    def AcceptShortcut(self, shortcut: Shortcut, accelerator: str) -> bool:
        """
        Returns ``True`` if the input `accelerator` is a valid shortcut, ``False`` otherwise.

        :param `shortcut`: an instance of :class:`Shortcut`;
        :param string `accelerator`: the new accelerator to check.

        :note: Conflicting shortcuts are handled inside this method by presenting the user with
         a conflict dialog. At this point the user can decide to reassign an existing shortcut
         or to back away, in which case this method will return ``False``.
        """
        if not shortcut.menuItem:
            return False
        if isinstance(shortcut.menuItem, wx.Menu):
            return False
        if shortcut.menuItem.IsSubMenu():
            return False
        sortedAccel = accelerator.lower().split("+")
        sortedAccel.sort()

        conflict = self.manager.CheckAccelerator(self.manager, shortcut, sortedAccel)
        if conflict is None:
            return True

        with ConflictDialog(self.GetParent(), conflict) as dlg:
            dlg: ConflictDialog
            if dlg.ShowModal() == wx.ID_OK:
                self.DisableShortcut(conflict)
                return True
        return False


class ShortcutEditPanel(wx.Panel):
    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.TAB_TRAVERSAL,
        name="ShortcutEditPanel",
    ):
        wx.Panel.__init__(
            self, parent, id=id, pos=pos, size=size, style=style, name=name
        )
        self.manager = Shortcut()
        self._modified = False
        self.listShortcut = ListShortcut(self)
        self.listShortcut.manager = self.manager
        self.hiddenText = wx.TextCtrl(self, -1, "", style=wx.BORDER_THEME)
        w, h, d, e = self.hiddenText.GetFullTextExtent(
            "Ctrl+Shift+Alt+q+g+M", self.hiddenText.GetFont()
        )
        self.hiddenText.SetMinSize((w, h + d - e + 1))
        self.button_default = wx.Button(
            self, wx.ID_ANY, "Restore Defaults", wx.DefaultPosition, wx.DefaultSize, 0
        )
        self.DoLayout()
        self.listShortcut.Bind(EVT_SHORTCUT_CHANGED, self.on_shortcut_changed)
        self.button_default.Bind(wx.EVT_BUTTON, self.on_restore_defaults)
        self.Init()

    def DoLayout(self):
        """Lays out the widgets using sizers in a platform-independent way."""
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.listShortcut, 1, wx.EXPAND, 0)
        hiddenSizer = wx.BoxSizer(wx.HORIZONTAL)
        hiddenSizer.Add(
            self.hiddenText, 0, wx.LEFT | wx.RIGHT | wx.RESERVE_SPACE_EVEN_IF_HIDDEN, 10
        )
        hiddenSizer.Add((1, 0), 1, wx.EXPAND)
        hiddenSizer.Add(self.button_default, 0, wx.ALL, 5)
        sizer.Add(hiddenSizer, 0, wx.EXPAND | wx.BOTTOM, 5)
        self.hiddenText.Hide()
        self.SetSizer(sizer)
        sizer.Layout()

    def Init(self):
        """Common initialization procedures."""
        shortcutsFromMenuBar(self.manager)
        self.listShortcut.MakeImageList()
        self.listShortcut.RecreateTree()
        self.SetColumnWidths()

    def GetShortcutManager(self):
        return self.manager

    def SetColumnWidths(self):
        """
        Sets the :class:`ListShortcut` columns widths to acceptable and eye-pleasing
        numbers (in pixels).
        """

        for col in range(self.listShortcut.GetColumnCount()):
            self.listShortcut.SetColumnWidth(col, wx.LIST_AUTOSIZE)
            width = self.listShortcut.GetColumnWidth(col)

            if col == 0:
                width += 20
            elif col == 1:
                width += 5
            else:
                width = min(width, 200)

            width = max(50, width)
            self.listShortcut.SetColumnWidth(col, width)

    def on_shortcut_changed(self, event):
        self._modified = True
        event.Skip()

    def on_restore_defaults(self, event: wx.CommandEvent):
        """
        Handles the ``wx.EVT_BUTTON`` event for :class:`ShortcutEditor` when the user restores the
        original shortcuts.

        :param `event`: an instance of :class:`CommandEvent`.
        """
        self.manager.RestoreDefaults()
        self.listShortcut.RecreateTree()


def shortcutsFromMenuBar(shortcuts: Shortcut):
    """
    Builds the entire shortcut hierarchy starting from a :class:`TopLevelWindow`, containing the :class:`wx.MenuBar`.

    """
    topWindow: ApplicationWindow = wx.GetApp().TopWindow
    fileHistoryMenus = ()
    if topWindow.documentManager.fileHistory:
        fileHistoryMenus = topWindow.documentManager.fileHistory.Menus

    def MenuItemSearch(menu, item):
        for menuItem in list(menu.GetMenuItems()):
            label = menuItem.GetItemLabel()
            if not label:
                # It's a separator
                continue
            shortcutItem = Shortcut(menuItem=menuItem)
            shortcutItem.FromMenuItem()
            item.AppendItem(shortcutItem)
            subMenu = menuItem.GetSubMenu()
            if subMenu and subMenu not in fileHistoryMenus:
                MenuItemSearch(subMenu, shortcutItem)

    position = 0
    for menu, name in topWindow.GetMenuBar().GetMenus():
        shortcutItem = Shortcut(menuItem=menu)
        shortcutItem.topMenu = True
        shortcutItem.position = position
        shortcutItem.FromMenuItem()
        position += 1
        shortcuts.AppendItem(shortcutItem)
        MenuItemSearch(menu, item=shortcutItem)


def shortcutsToMenuBar(shortcuts: Shortcut):
    """
    Dumps the entire shortcut hierarchy (for shortcuts associated with a :class:`wx.MenuItem`), into
    a :class:`wx.MenuBar`, changing only the :class:`wx.Menu` / :class:`wx.MenuItem` labels (it does **not** rebuild
    the :class:`wx.MenuBar`).

    :param `topWindow`: an instance of :class:`TopLevelWindow`, containing the :class:`wx.MenuBar`
        we wish to repopulate.
    """

    def MenuItemSet(shortcut: Shortcut, menuBar: wx.MenuBar):
        child, cookie = shortcut.GetFirstChild(shortcut)
        while child:
            child.ToMenuItem(menuBar)
            MenuItemSet(child, menuBar)
            child, cookie = shortcut.GetNextChild(shortcut, cookie)

    topWindow: ApplicationWindow = wx.GetApp().TopWindow
    menuBar = topWindow.GetMenuBar()
    MenuItemSet(shortcuts, menuBar)


def shortcutsToConfig(shortcuts: Shortcut):
    """
    Write shortcuts to application config
    """

    def saveShortcut(shortcut: Shortcut, config: wx.ConfigBase, path: str):
        if (
            shortcut.menuItem
            and shortcut.accelerator
            and shortcut.accelerator != DISABLED_STRING
        ):
            config.SetPath(path)
            config.Write(shortcut.label, shortcut.accelerator)
        for child in shortcut.children:
            saveShortcut(child, config, path + f"/{shortcut.label}")

    topWindow: ApplicationWindow = wx.GetApp().TopWindow
    config: wx.ConfigBase = topWindow.config
    config.SetPath("/Application")
    if config.HasGroup("Shortcut"):
        config.DeleteGroup("Shortcut")
    saveShortcut(shortcuts, config, "/Application/Shortcut")


def clearAccelerator(shortcut: Shortcut):
    """
    Set accelerator to "Disabled" for all menuitems.
    """
    if (
        shortcut.menuItem
        and shortcut.accelerator
        and shortcut.accelerator != DISABLED_STRING
    ):
        shortcut.SetAccelerator(DISABLED_STRING)
    for child in shortcut.children:
        clearAccelerator(child)


def readAccelerator(shortcut: Shortcut, config: wx.ConfigBase, path: str):
    """
    Read accelerator from application config and apply it to shortcut
    """
    if shortcut.menuItem:
        config.SetPath(path)
        if config.HasEntry(shortcut.label):
            shortcut.SetAccelerator(config.Read(shortcut.label, DISABLED_STRING))
    for child in shortcut.children:
        readAccelerator(child, config, path + f"/{shortcut.label}")


def shortcutsFromConfig():
    """
    Read shortcuts from application config and apply these to the main menu bar.
    """
    topWindow: ApplicationWindow = wx.GetApp().TopWindow
    config: wx.ConfigBase = topWindow.config
    config.SetPath("/Application")
    if not config.HasGroup("Shortcut"):
        return
    shortcuts = Shortcut()
    shortcutsFromMenuBar(shortcuts)
    clearAccelerator(shortcuts)
    readAccelerator(shortcuts, config, "/Application/Shortcut")
    shortcutsToMenuBar(shortcuts)
    shortcutsToConfig(shortcuts)
