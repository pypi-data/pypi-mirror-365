from __future__ import annotations
import logging
import wx
from wx.html2 import (
    WEBVIEWIE_EMU_IE11,
    WebView,
    WebViewBackendDefault,
    WebViewBackendEdge,
    WebViewBackendIE,
)

log = logging.getLogger(__name__)

class IEPanel(wx.Panel):
    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.TAB_TRAVERSAL,
        name=wx.EmptyString,
    ):
        wx.Panel.__init__(self, parent, id, pos, size, style, name)
        sizer = wx.BoxSizer(wx.VERTICAL)
        WebView.MSWSetEmulationLevel(WEBVIEWIE_EMU_IE11)
        self.backend = WebViewBackendDefault
        # if WebView.IsBackendAvailable(WebViewBackendEdge):
        #     self.backend = WebViewBackendEdge
        # elif WebView.IsBackendAvailable(WebViewBackendIE):
        #     self.backend = WebViewBackendIE
        self.webView = WebView.New(self, backend=self.backend)
        sizer.Add(self.webView, 1, wx.EXPAND)
        self.SetSizer(sizer)

    @property
    def html(self) -> str:
        return self.webView.GetPageSource()

    @html.setter
    def html(self, htmlText:str) -> None:
        if isinstance(htmlText, str):
            log.debug("calling IEPanel html.setter with %d chars of text", len(htmlText))
            self.webView.SetPage(htmlText, "")
            log.debug("call done")
            if self.backend == WebViewBackendIE:
                # force font to be shown
                while self.webView.IsBusy():
                    pass
                self.webView.Reload()
                log.debug("Reload done")
        else:
            self.webView.SetPage("", "")
