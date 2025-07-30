"""Collection of various controls used by workbench applications"""
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import wx

if TYPE_CHECKING:
    from types import ModuleType
    from ..application import App


class PanelMixin:
    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} of "{self.app.AppName}">'

    @property
    def app(self) -> App:
        """
        The running Workbench application.
        """
        return wx.GetApp()

    @property
    def plugin(self) -> str:
        """
        :return: Name of the plugin from which this panel was loaded
        """
        for name, module in self.app.pluginManager.items():
            if hasattr(module, "panels"):
                for cls, __ in module.panels:
                    if cls == self.__class__:
                        return name
        return ""

    @property
    def config(self) -> Optional[wx.ConfigBase]:
        plugin = self.plugin
        if plugin:
            cfg = self.app.config
            cfg.SetPath(f"/Plugin/{plugin}/")
            return cfg
        return None
