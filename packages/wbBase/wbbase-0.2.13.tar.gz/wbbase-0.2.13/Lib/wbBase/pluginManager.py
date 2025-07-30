"""
pluginManager
========================================================

Test new PluginManager class.
"""

from __future__ import annotations
from logging import getLogger
import sys

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points

from typing import TYPE_CHECKING

import wx

if TYPE_CHECKING:
    from wbBase.application import App

log = getLogger(__name__)


class PluginManager(dict):
    def __init__(self):
        super().__init__()
        self.loadPlugins()

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} of "{self.app.AppName}">'

    @property
    def app(self) -> App:
        """
        The running Workbench application.
        """
        return wx.GetApp()

    def loadPlugins(self):
        app = self.app
        app.splashMessage("loading plugins")
        available_plugins = {}
        entryPoints = entry_points(group="wbbase.plugin")
        if entryPoints:
            available_plugins = {e.name: e for e in entryPoints}
        appInfo_plugins = app.info.Plugins
        disabled_plugins = app.cmdLineArguments.disabledPlugins or []
        main = sys.modules.get("__main__")
        main.__dict__["app"] = app
        for plugin in appInfo_plugins:
            if plugin.Installation == "exclude":
                continue
            name = plugin.Name
            if name in disabled_plugins:
                continue
            app.splashMessage(f"loading plugin {name}")
            if name in available_plugins:
                try:
                    module = available_plugins[name].load()
                    if hasattr(module, "globalObjects"):
                        for globalObject in module.globalObjects:
                            if (
                                globalObject not in main.__dict__
                                and globalObject not in self.app.globalObjects
                                and hasattr(module, globalObject)
                            ):
                                main.__dict__[globalObject] = getattr(
                                    module, globalObject
                                )
                                self.app.globalObjects.append(globalObject)
                    self[name] = module
                except ImportError:
                    log.exception(
                        "=============== Can't load plugin %s ===============", name
                    )
                    if plugin.Installation == "required":
                        if app._splashScreen:
                            app._splashScreen.Hide()
                        wx.LogError(
                            "Required plugin error\n\n"
                            f"Can't load plugin '{name}'\n"
                            "See terminal output for traceback.\n"
                            "Application will terminate."
                        )
                        sys.exit(1)
            elif plugin.Installation == "required":
                if app._splashScreen:
                    app._splashScreen.Hide()
                wx.LogError(
                    "Missing required plugin\n\n"
                    f"Can't load plugin '{name}'\n"
                    "Application will terminate."
                )
                sys.exit(1)
