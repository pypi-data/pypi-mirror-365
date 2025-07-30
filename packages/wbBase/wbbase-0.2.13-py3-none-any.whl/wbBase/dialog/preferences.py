from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import wx
import wx.aui as aui
import wx.propgrid as pg

from ..control.externalToolConfig import ExternalToolConfig
from ..shortcut import ShortcutEditPanel, shortcutsToMenuBar, shortcutsToConfig

if TYPE_CHECKING:
    from types import ModuleType
    from ..application import App
    from ..document.manager import DocumentManager


class PreferencesDialog(wx.Dialog):
    def __init__(
        self,
        parent,
        id: int = wx.ID_ANY,
        title: str = "Preferences",
        pos: wx.Point = wx.DefaultPosition,
        size: wx.Size = wx.Size(600, 400),
        style: int = wx.CAPTION | wx.CLOSE_BOX | wx.RESIZE_BORDER,
    ):
        wx.Dialog.__init__(self, parent, id, title, pos, size, style)
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.book = wx.Treebook(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LB_DEFAULT
        )
        self.addPages()
        sizer.Add(self.book, 1, wx.EXPAND, 0)

        buttonSizer = wx.StdDialogButtonSizer()
        self.buttonSizerOK = wx.Button(self, wx.ID_OK)
        buttonSizer.AddButton(self.buttonSizerOK)
        self.buttonSizerApply = wx.Button(self, wx.ID_APPLY)
        buttonSizer.AddButton(self.buttonSizerApply)
        self.buttonSizerCancel = wx.Button(self, wx.ID_CANCEL)
        buttonSizer.AddButton(self.buttonSizerCancel)
        buttonSizer.Realize()
        sizer.Add(buttonSizer, 0, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(sizer)
        self.Layout()
        self.Centre(wx.BOTH)

        # Connect Events
        self.buttonSizerApply.Bind(wx.EVT_BUTTON, self.on_apply)
        self.buttonSizerOK.Bind(wx.EVT_BUTTON, self.on_ok)

    @property
    def app(self) -> App:
        return wx.GetApp()

    def addPages(self):
        self.book.AddPage(AppPreferences(self.book), "Application")
        self.book.AddSubPage(PanelPreferences(self.book), "Panels")
        self.book.AddSubPage(ExternalToolPreferences(self.book), "External Tools")
        self.book.AddSubPage(ShortcutPreferences(self.book), "Shortcuts")
        for name, module in self.app.pluginManager.items():
            if hasattr(module, "preferencepages"):
                for i, page in enumerate(module.preferencepages):
                    if i == 0:
                        self.book.AddPage(page(self.book), "Plugin - %s" % name)
                    else:
                        self.book.AddSubPage(page(self.book), page.name)

    # -----------------------------------------------------------------------------
    # Event handler
    # -----------------------------------------------------------------------------

    def on_apply(self, event):
        for page in [
            p for p in self.book.Children if isinstance(p, PreferencesPageFacade)
        ]:
            if page.IsAnyModified():
                page.applyValues()
            # print(page)
        event.Skip()

    def on_ok(self, event):
        doFlush = False
        for page in [
            p for p in self.book.Children if isinstance(p, PreferencesPageFacade)
        ]:
            if page.IsAnyModified():
                page.applyValues()
                page.saveValues()
                doFlush = True
        if doFlush:
            self.Parent.config.Flush()
        event.Skip()


class PreferencesPageFacade:
    Parent: wx.Treebook

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"

    @property
    def app(self) -> App:
        return wx.GetApp()

    @property
    def documentManager(self) -> DocumentManager:
        return self.app.TopWindow.documentManager

    def applyValues(self):
        wx.LogWarning(
            'Method "applyValues" not implemented in class "%s"'
            % self.__class__.__name__
        )

    def saveValues(self):
        wx.LogWarning(
            'Method "saveValues" not implemented in class "%s"'
            % self.__class__.__name__
        )


class PreferencesPageBase(PreferencesPageFacade, pg.PropertyGrid):
    """
    Base class for Preferences page
    """

    # info = {}

    def __init__(self, parent: wx.Treebook):
        id = wx.ID_ANY
        pos = wx.DefaultPosition
        size = wx.DefaultSize
        style = pg.PG_SPLITTER_AUTO_CENTER
        pg.PropertyGrid.__init__(self, parent, id, pos, size, style)
        self.CaptionBackgroundColour = wx.Colour(200, 250, 200)
        self.MarginColour = wx.Colour(20, 150, 20)

    @property
    def plugin(self) -> str:
        """
        :return: Name of the plugin to which this Preferences Page belongs to.
        """
        for name, module in self.app.pluginManager.items():
            if hasattr(module, "preferencepages"):
                for page in module.preferencepages:
                    if page == self.__class__:
                        return name
        return ""

    @property
    def config(self) -> wx.ConfigBase:
        result = self.app.config
        path = "/Application/"
        plugin = self.plugin
        if plugin:
            path = f"/Plugin/{plugin}/"
        result.SetPath(path)
        return result


class AppPreferences(PreferencesPageBase):
    def __init__(self, parent: wx.Treebook):
        PreferencesPageBase.__init__(self, parent)
        cfg = self.config

        # --- Startup -------------------------
        self.Append(pg.PropertyCategory("Startup"))
        self.Append(
            pg.BoolProperty(
                "Show Splashscreen",
                "show_splash",
                cfg.ReadBool("Start/showSplashScreen", True),
            )
        )
        self.Append(
            pg.BoolProperty(
                "Show tip of the day",
                "show_tip",
                cfg.ReadBool("Start/showTipOfTheDay", True),
            )
        )
        self.Append(
            pg.BoolProperty(
                "Allow multiple instances",
                "MultipleInstances",
                self.app.allowMultipleInstances,
            )
        )
        self.Append(
            pg.EnumProperty(
                "Check for external changes",
                "ExtChangesMode",
                ["On Request", "On App activation", "On Timer"],
                [
                    self.app.EXT_CHANGE_TEST_ON_REQUEST,
                    self.app.EXT_CHANGE_TEST_ON_ACTIVATE,
                    self.app.EXT_CHANGE_TEST_ON_TIMER,
                ],
                self.app.extChangeMode,
            )
        )
        self.Append(
            pg.IntProperty(
                "External changes timer interval",
                "ExtChangesTimer",
                self.app.extChangeTimerInterval,
            )
        )
        self.SetPropertyEditor("ExtChangesTimer", "SpinCtrl")

        # --- startup script -------------------------
        self.Append(
            pg.FileProperty(
                "Startup script",
                "start_script_path",
                cfg.Read("Start/Script/path", ""),
            )
        )
        self.Append(
            pg.BoolProperty(
                "Execute startup script",
                "start_script_exec",
                cfg.ReadBool("Start/Script/execute", False),
            )
        )

        # --- Shared Data -------------------------
        self.Append(pg.PropertyCategory("Shared Data"))
        self.Append(
            pg.DirProperty(
                "Folder",
                "sharedDataDir",
                cfg.Read("SharedData/Dir", self.app.sharedDataDir),
            )
        )
        self.Append(pg.StringProperty("Git URL", "url", cfg.Read("SharedData/URL", "")))
        self.Append(
            pg.BoolProperty(
                "Pull Shared Data from Git repository on start",
                "pull_on_start",
                cfg.ReadBool("SharedData/PullOnStart", False),
            )
        )

        # --- Private Data -------------------------
        self.Append(pg.PropertyCategory("Private Data"))
        self.Append(
            pg.DirProperty(
                "Folder",
                "privateDataDir",
                cfg.Read("PrivateData/Dir", self.app.privateDataDir),
            )
        )

        self.SetPropertyAttributeAll("UseCheckbox", True)

    def applyValues(self):
        values = self.GetPropertyValues()
        app = self.app
        app.allowMultipleInstances = values["MultipleInstances"]
        app.extChangeMode = values["ExtChangesMode"]
        app.extChangeTimerInterval = values["ExtChangesTimer"]
        val = values["sharedDataDir"]
        if app.sharedDataDir != val:
            app.sharedDataDir = val
            app.prepareSharedDataFolder()

    def saveValues(self):
        values = self.GetPropertyValues()
        cfg = self.config
        cfg.WriteBool("Start/showSplashScreen", values["show_splash"])
        cfg.WriteBool("Start/showTipOfTheDay", values["show_tip"])
        cfg.WriteBool("Start/MultipleInstances", values["MultipleInstances"])
        cfg.Write("Start/Script/path", values["start_script_path"])
        cfg.WriteBool("Start/Script/execute", values["start_script_exec"])
        cfg.WriteInt("ExtChanges/Mode", values["ExtChangesMode"])
        cfg.WriteInt("ExtChanges/Timer", values["ExtChangesTimer"])
        cfg.Write("SharedData/Dir", values["sharedDataDir"])
        cfg.Write("SharedData/URL", values["url"])
        cfg.WriteBool("SharedData/PullOnStart", values["pull_on_start"])
        cfg.Write("PrivateData/Dir", values["privateDataDir"])


class PanelPreferences(PreferencesPageBase):
    draggingStyles = (
        (
            aui.AUI_MGR_ALLOW_FLOATING,
            "Allow floating panes",
            "Allow floating of panes.",
        ),
        (
            aui.AUI_MGR_ALLOW_ACTIVE_PANE,
            "Highlight active panes",
            'If a pane becomes active, "highlight" it in the interface.',
        ),
        (
            aui.AUI_MGR_TRANSPARENT_DRAG,
            "Transparent floating panes",
            "If the platform supports it, set transparency on a floating pane while it is dragged by the user.",
        ),
        (
            aui.AUI_MGR_TRANSPARENT_HINT,
            "Transparent hint on docking",
            "If the platform supports it, show a transparent hint window when the user is about to dock a floating pane.",
        ),
        (
            aui.AUI_MGR_VENETIAN_BLINDS_HINT,
            "Venetian blind hint on docking",
            'Show a "venetian blind" effect when the user is about to dock a floating pane.',
        ),
        (
            aui.AUI_MGR_RECTANGLE_HINT,
            "Rectangle hint on docking",
            "Show a rectangle hint effect when the user is about to dock a floating pane.",
        ),
        (
            aui.AUI_MGR_HINT_FADE,
            "Hint fade",
            "If the platform supports it, the hint window will fade in and out.",
        ),
        (
            aui.AUI_MGR_NO_VENETIAN_BLINDS_FADE,
            "No venetian blind hint fade",
            'Disables the "venetian blind" fade in and out.',
        ),
        (
            aui.AUI_MGR_LIVE_RESIZE,
            "Live resize",
            "Live resize when the user drag a sash.",
        ),
    )

    dockArtMetrics = (
        ("AUI_DOCKART_SASH_SIZE", "Sash size", "Customizes the sash size."),
        ("AUI_DOCKART_CAPTION_SIZE", "Caption size", "Customizes the caption size."),
        ("AUI_DOCKART_GRIPPER_SIZE", "Gripper size", "Customizes the gripper size."),
        (
            "AUI_DOCKART_PANE_BORDER_SIZE",
            "Pane border size",
            "Customizes the pane border size.",
        ),
        (
            "AUI_DOCKART_PANE_BUTTON_SIZE",
            "Pane button size",
            "Customizes the pane button size.",
        ),
        (
            "AUI_DOCKART_GRADIENT_TYPE",
            "Gradient type",
            "Customizes the gradient type (no gradient, vertical or horizontal).",
        ),
    )

    dockArtColours = (
        (
            "AUI_DOCKART_BACKGROUND_COLOUR",
            "Background colour",
            "Customizes the background colour.",
        ),
        ("AUI_DOCKART_BORDER_COLOUR", "Border colour", "Customizes the border colour."),
        ("AUI_DOCKART_SASH_COLOUR", "Sash colour", "Customizes the sash colour."),
        (
            "AUI_DOCKART_GRIPPER_COLOUR",
            "Gripper colour",
            "Customizes the gripper colour.",
        ),
        (
            "AUI_DOCKART_ACTIVE_CAPTION_COLOUR",
            "Active caption colour",
            "Customizes the active caption colour colour.",
        ),
        (
            "AUI_DOCKART_ACTIVE_CAPTION_GRADIENT_COLOUR",
            "Active caption gradient colour",
            "Customizes the active caption gradient colour.",
        ),
        (
            "AUI_DOCKART_ACTIVE_CAPTION_TEXT_COLOUR",
            "Active caption text colour",
            "Customizes the active caption text colour.",
        ),
        (
            "AUI_DOCKART_INACTIVE_CAPTION_COLOUR",
            "Inactive caption colour",
            "Customizes the inactive caption colour colour.",
        ),
        (
            "AUI_DOCKART_INACTIVE_CAPTION_GRADIENT_COLOUR",
            "Inactive caption gradient colour",
            "Customizes the inactive caption gradient colour.",
        ),
        (
            "AUI_DOCKART_INACTIVE_CAPTION_TEXT_COLOUR",
            "Inactive caption text colour",
            "Customizes the inactive caption text colour.",
        ),
    )

    notebookFlags = (
        (
            "AUI_NB_TOP",
            "Tabs at top",
            "With this style, tabs are drawn along the top of the notebook.",
        ),
        (
            "AUI_NB_BOTTOM",
            "Tabs at bottom",
            "With this style, tabs are drawn along the bottom of the notebook.",
        ),
        (
            "AUI_NB_TAB_SPLIT",
            "Allows splitting",
            "Allows the tab control to be split by dragging a tab.",
        ),
        (
            "AUI_NB_TAB_MOVE",
            "Allow tab move",
            "Allows a tab to be moved horizontally by dragging.",
        ),
        (
            "AUI_NB_TAB_EXTERNAL_MOVE",
            "Allow tab move to other control",
            "Allows a tab to be moved to another tab control.",
        ),
        (
            "AUI_NB_TAB_FIXED_WIDTH",
            "Fixed tab width",
            "With this style, all tabs have the same width.",
        ),
        (
            "AUI_NB_SCROLL_BUTTONS",
            "Show scroll buttons",
            "With this style, left and right scroll buttons are displayed.",
        ),
        (
            "AUI_NB_WINDOWLIST_BUTTON",
            "Show window list",
            "With this style, a drop-down list of windows is available.",
        ),
        (
            "AUI_NB_CLOSE_BUTTON",
            "Show close button",
            "With this style, a close button is available on the tab bar.",
        ),
        (
            "AUI_NB_CLOSE_ON_ACTIVE_TAB",
            "Show close button on active tab",
            "With this style, a close button is available on the active tab.",
        ),
        (
            "AUI_NB_CLOSE_ON_ALL_TABS",
            "Show close button on all tabs",
            "With this style, a close button is available on all tabs.",
        ),
        (
            "AUI_NB_MIDDLE_CLICK_CLOSE",
            "Close tab by mouse middle button click",
            "Allows to close notebook tabs by mouse middle button click.",
        ),
    )

    def __init__(self, parent):
        PreferencesPageBase.__init__(self, parent)
        panelManager = self.app.TopWindow.panelManager
        self.Append(pg.PropertyCategory("Main"))
        flags = [i[0] for i in self.draggingStyles]
        labels = [i[1] for i in self.draggingStyles]
        self.Append(
            pg.FlagsProperty(
                "Floating/Dragging Styles",
                "AUI_MGR_FLAGS",
                labels,
                flags,
                panelManager.Flags,
            )
        )
        notebook = panelManager.documentNotebook
        flags = [getattr(aui, i[0]) for i in self.notebookFlags]
        labels = [i[1] for i in self.notebookFlags]
        self.Append(
            pg.FlagsProperty(
                "Notebook Styles",
                "AUI_NB_FLAGS",
                labels,
                flags,
                notebook.WindowStyleFlag,
            )
        )
        self.Append(pg.PropertyCategory("Metric"))
        getMetric = lambda name: panelManager.ArtProvider.GetMetric(getattr(aui, name))
        for name, label, helptext in self.dockArtMetrics:
            if name == "AUI_DOCKART_GRADIENT_TYPE":
                labels = ["No gradient", "Vertical gradient", "Horizontal gradient"]
                values = [
                    aui.AUI_GRADIENT_NONE,
                    aui.AUI_GRADIENT_VERTICAL,
                    aui.AUI_GRADIENT_HORIZONTAL,
                ]
                self.Append(
                    pg.EnumProperty(label, name, labels, values, getMetric(name))
                )
            else:
                self.Append(pg.IntProperty(label, name, getMetric(name)))
                self.SetPropertyEditor(name, "SpinCtrl")
        self.Append(pg.PropertyCategory("Colour"))
        getColour = lambda name: panelManager.ArtProvider.GetColour(getattr(aui, name))
        for name, label, helptext in self.dockArtColours:
            self.Append(pg.ColourProperty(label, name, getColour(name)))
        self.SetPropertyAttributeAll("UseCheckbox", True)

    @property
    def config(self):
        result = self.app.TopWindow.config
        result.SetPath("/Window/Panels/")
        return result

    def applyValues(self):
        values = self.GetPropertyValues()
        panelManager = self.app.TopWindow.panelManager
        panelManager.SetFlags(values["AUI_MGR_FLAGS"])
        notebook = panelManager.documentNotebook
        notebook.SetWindowStyleFlag(values["AUI_NB_FLAGS"])
        notebook.SendSizeEvent()
        if notebook.PageCount > 0:
            notebook.CurrentPage.SendSizeEvent()
            notebook.CurrentPage.Refresh()
        # metric
        setMetric = lambda name: panelManager.ArtProvider.SetMetric(
            getattr(aui, name), values[name]
        )
        for dockArtMetric in self.dockArtMetrics:
            setMetric(dockArtMetric[0])
        # colour
        setColour = lambda name: panelManager.ArtProvider.SetColour(
            getattr(aui, name), values[name]
        )
        for dockArtColour in self.dockArtColours:
            setColour(dockArtColour[0])
        panelManager.Update()

    def saveValues(self):
        values = self.GetPropertyValues()
        cfg = self.config
        cfg.WriteInt("AUI_MGR_FLAGS", values["AUI_MGR_FLAGS"])
        cfg.WriteInt("AUI_NB_FLAGS", values["AUI_NB_FLAGS"])
        # metric
        for name, label, helptext in self.dockArtMetrics:
            cfg.WriteInt(name, values[name])
        # colour
        for name, label, helptext in self.dockArtColours:
            cfg.WriteInt(name, values[name].GetRGB())


class ExternalToolPreferences(PreferencesPageFacade, ExternalToolConfig):
    def __init__(self, parent):
        ExternalToolConfig.__init__(self, parent)

    @property
    def config(self):
        result = self.app.TopWindow.config
        result.SetPath("/Application/")
        return result

    def IsAnyModified(self) -> bool:
        return self._modified

    def applyValues(self):
        selection = self.listBox_tools.Selection
        tool = dict(
            name=self.textCtrl_label.Value,
            cmd=self.textCtrl_command.Value,
            folder=self.textCtrl_directory.Value,
        )
        if tool["name"] and tool["cmd"]:
            if selection == 0:
                self.externalTools.append(tool)
                self.listBox_tools.Append(tool["name"])
                self.listBox_tools.Selection = len(self.externalTools)
            else:
                items = self.listBox_tools.Items
                items[selection] = tool["name"]
                self.externalTools[selection - 1] = tool
                self.listBox_tools.SetItems(items)
                self.listBox_tools.Selection = selection
        self.app.TopWindow.buildExtraMenu()

    def saveValues(self):
        self.applyValues()
        cfg = self.config
        cfg.Write("ExternalTools", repr(self.externalTools))


class ShortcutPreferences(PreferencesPageFacade, ShortcutEditPanel):
    def __init__(self, parent):
        ShortcutEditPanel.__init__(self, parent)

    def IsAnyModified(self) -> bool:
        return self._modified

    def applyValues(self):
        shortcutsToMenuBar(self.manager)

    def saveValues(self):
        self.applyValues()
        shortcutsToConfig(self.manager)
