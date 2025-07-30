import wx
from wx.py.filling import FillingTree, FillingText


class Filling(wx.SplitterWindow):
    """This is a re-implementation of wx.py.filling.Filling
    to allow more styling
    """

    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.SP_LIVE_UPDATE | wx.SP_NOBORDER | wx.SP_NO_XP_THEME | wx.NO_BORDER,
        name="Filling",
        rootObject=None,
        rootLabel=None,
        rootIsNamespace=True,
        static=False,
    ):
        wx.SplitterWindow.__init__(self, parent, id, pos, size, style, name)
        self.tree = FillingTree(
            parent=self,
            style=wx.TR_FULL_ROW_HIGHLIGHT
            | wx.TR_HAS_BUTTONS
            | wx.TR_LINES_AT_ROOT
            | wx.TR_NO_LINES
            | wx.TR_SINGLE
            | wx.TR_TWIST_BUTTONS
            | wx.NO_BORDER,
            rootObject=rootObject,
            rootLabel=rootLabel,
            rootIsNamespace=rootIsNamespace,
            static=static,
        )
        self.text = FillingText(
            parent=self, style=wx.CLIP_CHILDREN | wx.NO_BORDER, static=static
        )
        self.text.SetMargins(2, 2)
        # self.applyConfig()
        wx.CallLater(25, self.SplitVertically, self.tree, self.text, 200)
        self.SetMinimumPaneSize(50)

        # Override the filling so that descriptions go to FillingText.
        self.tree.setText = self.text.SetText

        # Display the root item.
        self.tree.SelectItem(self.tree.root)
        self.tree.display()

        self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.OnChanged)

    def __repr__(self):
        return '<%s of "%s">' % (self.__class__.__name__, self.app.AppName)

    # -----------------------------------------------------------------------------
    # properties
    # -----------------------------------------------------------------------------

    @property
    def app(self):
        return wx.GetApp()

    # @property
    # def config(self):
    #     return None

    # -----------------------------------------------------------------------------
    # public methods
    # -----------------------------------------------------------------------------

    # def applyConfig(self):
    #     cfg = self.config
    #     if cfg:
    #         self.tree.SetBackgroundColour(cfg.backgroundColour.ChangeLightness(130))
    #         # self.tree.SetForegroundColour(cfg.foregroundColour)
    #         cfg.apply(self.text)

    def OnChanged(self, event):
        # this is important: do not evaluate this event=> otherwise,
        # splitterwindow behaves strangely
        pass
