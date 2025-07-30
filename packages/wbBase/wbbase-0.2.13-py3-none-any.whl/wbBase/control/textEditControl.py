from __future__ import annotations

import sys
from collections import OrderedDict
from typing import TYPE_CHECKING, Protocol

import wx
import wx.propgrid as pg
import wx.stc as stc
from wx.lib.gizmos.dynamicsash import EVT_DYNAMIC_SASH_SPLIT, EVT_DYNAMIC_SASH_UNIFY

from .propgrid import (
    FontfacenameMonoProperty,
    OptColourEditor,
    StyleSpecEditor,
    StyleSpecProperty,
)

if TYPE_CHECKING:
    from ..application import App
    from ..dialog.preferences import PreferencesPageBase

MARGIN_NUMBERS = 0
MARGIN_SYMBOLS = 1
MARGIN_FOLDMARK = 2


class STCdropTarget(wx.DropTarget):
    """
    DropTarget for TextEditCtrl.
    Accept TextDataObject as well as FileDataObject
    """

    def __init__(self, styledTextCtrl: stc.StyledTextCtrl):
        wx.DropTarget.__init__(self)
        self.control: stc.StyledTextCtrl = styledTextCtrl
        self.data = {}
        self.initObjects()

    @property
    def app(self) -> App:
        return wx.GetApp()

    def initObjects(self):
        self.data = {
            "data": wx.DataObjectComposite(),
            "text_data": wx.TextDataObject(),
            "file_data": wx.FileDataObject(),
        }
        self.data["data"].Add(self.data["text_data"], True)
        self.data["data"].Add(self.data["file_data"], False)
        self.SetDataObject(self.data["data"])

    def OnDragOver(self, x_cord, y_cord, drag_result):
        control = self.control
        if hasattr(control, "DoDragOver"):
            val = control.DoDragOver(x_cord, y_cord, drag_result)
            self.ScrollBuffer(control, x_cord, y_cord)
        return drag_result

    def OnData(self, x_cord, y_cord, drag_result):
        try:
            data = self.GetData()
        except wx.PyAssertionError:
            wx.LogError("Unable to accept dropped file or text")
            data = False
            drag_result = wx.DragCancel
        if data:
            files = self.data["file_data"].GetFilenames()
            text = self.data["text_data"].GetText()
            if len(files) > 0:
                wx.CallAfter(self.app.TopWindow.documentManager.openDocuments, files)
            elif len(text) > 0:
                self.control.DoDropText(x_cord, y_cord, text)
        self.initObjects()
        return drag_result

    @staticmethod
    def ScrollBuffer(styledTextCtrl: stc.StyledTextCtrl, x_cord: int, y_cord: int):
        try:
            cline = styledTextCtrl.PositionFromPoint(wx.Point(x_cord, y_cord))
            if cline != stc.STC_INVALID_POSITION:
                cline = styledTextCtrl.LineFromPosition(cline)
                fline = styledTextCtrl.GetFirstVisibleLine()
                lline = styledTextCtrl.GetLastVisibleLine()
                if (cline - fline) < 2:
                    styledTextCtrl.ScrollLines(-1)
                elif lline - cline < 2:
                    styledTextCtrl.ScrollLines(1)
                else:
                    pass
        except wx.PyAssertionError as msg:
            wx.LogError("[droptargetft][err] ScrollBuffer: %s" % msg)


class STCprotocol(Protocol):
    def GetFoldExpanded(self, line: int) -> bool:
        ...

    def GetFoldLevel(self, line: int) -> int:
        ...

    def GetLastChild(self, line: int, level: int) -> int:
        ...

    def GetLineCount(self) -> int:
        ...

    def HideLines(self, lineStart: int, lineEnd: int) -> None:
        ...

    def MarkerDefine(
        self,
        markerNumber: int,
        markerSymbol: int,
        foreground: wx.Colour = wx.NullColour,
        background: wx.Colour = wx.NullColour,
    ):
        ...

    def SetFoldExpanded(self, line: int, expanded: bool) -> None:
        ...

    def SetMarginMask(self, margin: int, mask: int) -> None:
        ...

    def SetMarginType(self, margin: int, marginType: int) -> None:
        ...

    def ShowLines(self, lineStart: int, lineEnd: int) -> None:
        ...

class STCfoldMixin:
    def __init__(self:STCprotocol):
        self.SetMarginType(MARGIN_FOLDMARK, stc.STC_MARGIN_SYMBOL)
        self.SetMarginMask(MARGIN_FOLDMARK, stc.STC_MASK_FOLDERS)
        self.Bind(stc.EVT_STC_MARGINCLICK, self.on_MARGINCLICK)

    def defineFoldMarker(self: STCprotocol, style, line, fill, highlight):
        _line = line.GetAsString(wx.C2S_HTML_SYNTAX)
        _fill = fill.GetAsString(wx.C2S_HTML_SYNTAX)
        _highlight = highlight.GetAsString(wx.C2S_HTML_SYNTAX)
        box, circle, arrow, plusminus = range(4)
        md = self.MarkerDefine
        if style == box:
            md(stc.STC_MARKNUM_FOLDEROPEN, stc.STC_MARK_BOXMINUS, _fill, _line)
            md(stc.STC_MARKNUM_FOLDER, stc.STC_MARK_BOXPLUS, _highlight, _line)
            md(stc.STC_MARKNUM_FOLDERSUB, stc.STC_MARK_VLINE, _fill, _line)
            md(stc.STC_MARKNUM_FOLDERTAIL, stc.STC_MARK_LCORNER, _fill, _line)
            md(
                stc.STC_MARKNUM_FOLDEREND,
                stc.STC_MARK_BOXPLUSCONNECTED,
                _highlight,
                _line,
            )
            md(
                stc.STC_MARKNUM_FOLDEROPENMID,
                stc.STC_MARK_BOXMINUSCONNECTED,
                _fill,
                _line,
            )
            md(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_TCORNER, _fill, _line)
        elif style == circle:
            md(stc.STC_MARKNUM_FOLDEROPEN, stc.STC_MARK_CIRCLEMINUS, _fill, _line)
            md(stc.STC_MARKNUM_FOLDER, stc.STC_MARK_CIRCLEPLUS, _highlight, _line)
            md(stc.STC_MARKNUM_FOLDERSUB, stc.STC_MARK_VLINE, _fill, _line)
            md(stc.STC_MARKNUM_FOLDERTAIL, stc.STC_MARK_LCORNERCURVE, _fill, _line)
            md(
                stc.STC_MARKNUM_FOLDEREND,
                stc.STC_MARK_CIRCLEPLUSCONNECTED,
                _highlight,
                _line,
            )
            md(
                stc.STC_MARKNUM_FOLDEROPENMID,
                stc.STC_MARK_CIRCLEMINUSCONNECTED,
                _fill,
                _line,
            )
            md(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_TCORNERCURVE, _fill, _line)
        elif style == arrow:
            md(stc.STC_MARKNUM_FOLDEROPEN, stc.STC_MARK_ARROWDOWN, _line, _line)
            md(stc.STC_MARKNUM_FOLDER, stc.STC_MARK_ARROW, _highlight, _highlight)
            md(stc.STC_MARKNUM_FOLDERSUB, stc.STC_MARK_EMPTY, _line, _line)
            md(stc.STC_MARKNUM_FOLDERTAIL, stc.STC_MARK_EMPTY, _line, _line)
            md(stc.STC_MARKNUM_FOLDEREND, stc.STC_MARK_EMPTY, _line, _line)
            md(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_EMPTY, _line, _line)
            md(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_EMPTY, _line, _line)
        elif style == plusminus:
            md(stc.STC_MARKNUM_FOLDEROPEN, stc.STC_MARK_MINUS, _line, _line)
            md(stc.STC_MARKNUM_FOLDER, stc.STC_MARK_PLUS, _highlight, _highlight)
            md(stc.STC_MARKNUM_FOLDERSUB, stc.STC_MARK_EMPTY, _line, _line)
            md(stc.STC_MARKNUM_FOLDERTAIL, stc.STC_MARK_EMPTY, _line, _line)
            md(stc.STC_MARKNUM_FOLDEREND, stc.STC_MARK_EMPTY, _line, _line)
            md(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_EMPTY, _line, _line)
            md(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_EMPTY, _line, _line)

    def FoldAll(self: STCprotocol):
        lineCount = self.GetLineCount()
        expanding = True
        # find out if we are folding or unfolding
        for lineNum in range(lineCount):
            if self.GetFoldLevel(lineNum) & stc.STC_FOLDLEVELHEADERFLAG:
                expanding = not self.GetFoldExpanded(lineNum)
                break
        lineNum = 0
        while lineNum < lineCount:
            level = self.GetFoldLevel(lineNum)
            if (
                level & stc.STC_FOLDLEVELHEADERFLAG
                and (level & stc.STC_FOLDLEVELNUMBERMASK) == stc.STC_FOLDLEVELBASE
            ):
                if expanding:
                    self.SetFoldExpanded(lineNum, True)
                    lineNum = self.Expand(lineNum, True)
                    lineNum = lineNum - 1
                else:
                    lastChild = self.GetLastChild(lineNum, -1)
                    self.SetFoldExpanded(lineNum, False)

                    if lastChild > lineNum:
                        self.HideLines(lineNum + 1, lastChild)
            lineNum = lineNum + 1

    def Expand(
        self,
        line,
        doExpand,
        force: bool = False,
        visLevels: int = 0,
        level: int = -1,
    ) -> int: 
        
        lastChild = self.GetLastChild(line, level)
        line = line + 1
        while line <= lastChild:
            if force:
                if visLevels > 0:
                    self.ShowLines(line, line)
                else:
                    self.HideLines(line, line)
            else:
                if doExpand:
                    self.ShowLines(line, line)
            if level == -1:
                level = self.GetFoldLevel(line)
            if level & stc.STC_FOLDLEVELHEADERFLAG:
                if force:
                    if visLevels > 1:
                        self.SetFoldExpanded(line, True)
                    else:
                        self.SetFoldExpanded(line, False)
                    line = self.Expand(line, doExpand, force, visLevels - 1)
                else:
                    if doExpand and self.GetFoldExpanded(line):
                        line = self.Expand(line, True, force, visLevels - 1)
                    else:
                        line = self.Expand(line, False, force, visLevels - 1)
            else:
                line = line + 1
        return line

    # -----------------------------------------------------------------------------
    # Event handler
    # -----------------------------------------------------------------------------

    def on_MARGINCLICK(self: STCprotocol, evt):
        # fold and unfold as needed
        # if evt.GetMargin() == MARGIN_FOLDMARK:
        # 	if evt.GetShift() and evt.GetControl():
        if evt.Margin == MARGIN_FOLDMARK:
            if evt.Shift and evt.Control:
                self.FoldAll()
            else:
                lineClicked = self.LineFromPosition(evt.GetPosition())
                if self.GetFoldLevel(lineClicked) & stc.STC_FOLDLEVELHEADERFLAG:
                    if evt.GetShift():
                        self.SetFoldExpanded(lineClicked, True)
                        self.Expand(lineClicked, True, True, 1)
                    elif evt.GetControl():
                        if self.GetFoldExpanded(lineClicked):
                            self.SetFoldExpanded(lineClicked, False)
                            self.Expand(lineClicked, False, True, 0)
                        else:
                            self.SetFoldExpanded(lineClicked, True)
                            self.Expand(lineClicked, True, True, 100)
                    else:
                        self.ToggleFold(lineClicked)


class STCfindReplaceMixin:
    def __init__(self, titleFind="Find", titleReplace="Replace"):
        self.titleFind = titleFind
        self.titleReplace = titleReplace
        self.findFlagMask = wx.FR_MATCHCASE | wx.FR_WHOLEWORD
        self.finddlg = None
        self.finddata = wx.FindReplaceData()
        self.finddata.SetFlags(wx.FR_DOWN)
        self.Bind(wx.EVT_FIND, self.OnFind)
        self.Bind(wx.EVT_FIND_NEXT, self.OnFind)
        self.Bind(wx.EVT_FIND_REPLACE, self.OnReplace)
        self.Bind(wx.EVT_FIND_REPLACE_ALL, self.OnReplaceAll)
        self.Bind(wx.EVT_FIND_CLOSE, self.OnFindClose)

    def CanFind(self):
        return self.TextLength > 0

    def CanFindNext(self):
        return bool(self.CanFind() and self.finddata.FindString)

    def CanReplace(self):
        return not self.ReadOnly and self.TextLength > 0

    def doFind(self):
        self.finddlg = wx.FindReplaceDialog(
            self,
            data=self.finddata,
            title=self.titleFind,
        )
        self.finddlg.Show(True)

    def doFindNext(self):
        self.finddata.Flags |= wx.FR_DOWN
        self.OnFind(wx.FindDialogEvent())

    def doReplace(self):
        self.finddlg = wx.FindReplaceDialog(
            self,
            data=self.finddata,
            title=self.titleReplace,
            style=wx.FR_REPLACEDIALOG,
        )
        self.finddlg.Show(True)

    # -----------------------------------------------------------------------------
    # Event handler
    # -----------------------------------------------------------------------------
    def OnFind(self, event):
        findString = self.finddata.FindString
        flags = self.finddata.Flags & self.findFlagMask
        if self.finddata.Flags & wx.FR_DOWN:
            start = self.SelectionEnd
            end = self.LastPosition
        else:
            start = self.SelectionStart
            end = 0
        f_start, f_end = self.FindText(start, end, findString, flags)
        if (f_start, f_end) == (-1, -1):
            if self.finddata.Flags & wx.FR_DOWN and start != 0:
                f_start, f_end = self.FindText(0, end, findString, flags)
            elif not (self.finddata.Flags & wx.FR_DOWN) and start != self.LastPosition:
                f_start, f_end = self.FindText(
                    self.LastPosition, end, findString, flags
                )

        if (f_start, f_end) == (-1, -1):
            dlg = wx.MessageDialog(
                self,
                f'Find String "{findString}" Not Found',
                "Find String Not Found",
                wx.OK | wx.ICON_INFORMATION,
            )
            dlg.ShowModal()
            dlg.Destroy()
        else:
            self.ShowPosition(f_start)
            self.SetSelection(f_start, f_end)

    def OnReplace(self, event):
        findString = self.finddata.FindString
        flags = self.finddata.Flags & self.findFlagMask
        f_start, f_end = self.FindText(
            self.SelectionStart, self.LastPosition, findString, flags
        )
        if (f_start, f_end) == (self.SelectionStart, self.SelectionEnd):
            self.ReplaceSelection(self.finddata.ReplaceString)
        self.OnFind(event)

    def OnReplaceAll(self, event):
        findString = self.finddata.FindString
        flags = self.finddata.Flags & self.findFlagMask
        start = 0
        end = self.LastPosition
        counter = 0
        while True:
            f_start, f_end = self.FindText(start, end, findString, flags)
            if (f_start, f_end) == (-1, -1):
                break
            self.SelectionStart = f_start
            self.SelectionEnd = f_end
            self.ReplaceSelection(self.finddata.ReplaceString)
            counter += 1
            start = f_end
        dlg = wx.MessageDialog(
            self,
            f'Replaced "{findString}" with "{self.finddata.ReplaceString}" {counter} times',
            "Replace done",
            wx.OK | wx.ICON_INFORMATION,
        )
        dlg.ShowModal()
        dlg.Destroy()

    def OnFindClose(self, event):
        event.GetDialog().Destroy()
        self.finddlg = None


class TextEditCtrl(stc.StyledTextCtrl, STCfoldMixin, STCfindReplaceMixin):
    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.BORDER_NONE,
        name="TextEditCtrl",
    ):
        stc.StyledTextCtrl.__init__(self, parent, id, pos, size, style, name)
        STCfoldMixin.__init__(self)
        STCfindReplaceMixin.__init__(self)
        self.SetLayoutCache(stc.STC_CACHE_DOCUMENT)
        if sys.platform == "win32":
            self.SetTechnology(stc.STC_TECHNOLOGY_DIRECTWRITE)
        else:
            self.SetTechnology(stc.STC_TECHNOLOGY_DEFAULT)
        # Setup Margins
        self.SetMargins(2, 2)
        self.SetMarginType(MARGIN_NUMBERS, stc.STC_MARGIN_NUMBER)
        self.SetMarginWidth(MARGIN_SYMBOLS, 0)  # not used yet - turn off
        self.SetDropTarget(STCdropTarget(self))

    # -----------------------------------------------------------------------------
    # Properties
    # -----------------------------------------------------------------------------

    @property
    def app(self) -> App:
        return wx.GetApp()

    @property
    def indentChar(self) -> str:
        if self.UseTabs:
            return "\t"
        else:
            return " " * self.GetIndent()

    @property
    def EOLChar(self) -> str:
        mode = self.EOLMode
        if mode == stc.STC_EOL_CR:
            return "\r"
        elif mode == stc.STC_EOL_CRLF:
            return "\r\n"
        else:
            return "\n"

    def GetLastVisibleLine(self) -> int:
        """Return what the last visible line is"""
        return self.GetFirstVisibleLine() + self.LinesOnScreen() - 1


class TextEditDynSashMixin:
    def __init__(self, dyn_sash):
        self.dyn_sash = dyn_sash
        self.Bind(EVT_DYNAMIC_SASH_SPLIT, self.on_DYNAMIC_SASH_SPLIT)
        self.Bind(EVT_DYNAMIC_SASH_UNIFY, self.on_DYNAMIC_SASH_UNIFY)
        self.setupScrollBars()

    def clone(self):
        obj = self.__class__(
            self.dyn_sash, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.BORDER_NONE
        )
        obj.DocPointer = self.DocPointer  # use the same document
        obj.ScrollToLine(self.GetFirstVisibleLine())
        return obj

    def setupScrollBars(self):
        # hook the scrollbars provided by the wxDynamicSashWindow to this view
        v_bar = self.dyn_sash.GetVScrollBar(self)
        v_bar.Bind(wx.EVT_SCROLL, self.on_SCROLL)
        v_bar.Bind(wx.EVT_SET_FOCUS, self.on_SCROLLBAR_FOCUS)
        self.SetVScrollBar(v_bar)

        h_bar = self.dyn_sash.GetHScrollBar(self)
        h_bar.Bind(wx.EVT_SCROLL, self.on_SCROLL)
        h_bar.Bind(wx.EVT_SET_FOCUS, self.on_SCROLLBAR_FOCUS)
        self.SetHScrollBar(h_bar)

    # -----------------------------------------------------------------------------
    # Event handler
    # -----------------------------------------------------------------------------

    def on_SCROLL(self, event):
        # redirect the scroll events from the dyn_sash's scrollbars to the STC
        self.GetEventHandler().ProcessEvent(event)

    def on_SCROLLBAR_FOCUS(self, event):
        # when the scrollbar gets the focus move it back to the STC
        self.SetFocus()
        event.Skip()

    def on_DYNAMIC_SASH_SPLIT(self, event):
        newEditor = self.clone()
        self.setupScrollBars()

    def on_DYNAMIC_SASH_UNIFY(self, event):
        self.setupScrollBars()


class TextEditSashChild(TextEditCtrl, TextEditDynSashMixin):
    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.BORDER_NONE,
        name="TextEditSashChild",
    ):
        TextEditCtrl.__init__(self, parent, id, pos, size, style, name)
        TextEditDynSashMixin.__init__(self, parent)


class TextEditConfig:
    def __init__(self, parent):
        self.parent = parent
        # self.configPath: str = ""
        """Set default values"""
        # default style spec
        self.STC_STYLE_DEFAULT = "fore:black,back:white,face:Consolas,size:10"
        self.STC_STYLE_CONTROLCHAR = ""
        self.STC_STYLE_BRACELIGHT = ""
        self.STC_STYLE_BRACEBAD = ""
        # Caret
        self.CaretWidth = 2
        self.CaretForeground = wx.Colour("#0000FF")
        self.CaretLineVisible = True
        self.CaretLineBackground = wx.Colour("#090909")
        self.CaretLineBackAlpha = 32
        # Selection
        self.UseSelForeground = False
        self.SelForeground = wx.Colour("#090909")
        self.UseSelBackground = True
        self.SelBackground = wx.Colour("#090909")
        self.SelectionAlpha = 32
        self.SelEOLFilled = False
        # Indentation and White Space
        self.Indent = 2
        self.TabWidth = 2
        self.UseTabs = False
        self.TabIndents = True
        self.BackSpaceUnIndents = True
        self.IndentationGuides = False
        self.STC_STYLE_INDENTGUIDE = ""
        self.ShowWhiteSpace = stc.STC_WS_INVISIBLE
        # Line Endings
        self.EOLMode = stc.STC_EOL_CRLF
        self.ViewEOL = False
        self.WrapMode = stc.STC_WRAP_NONE
        self.WrapIndentMode = stc.STC_WRAPINDENT_FIXED
        self.WrapVisualFlags = stc.STC_WRAPVISUALFLAG_NONE
        self.WrapVisualFlagsLocation = stc.STC_WRAPVISUALFLAG_NONE
        # Line Numbers
        self.ShowLineNumbers = True
        self.LineNumColWidth = 40
        self.STC_STYLE_LINENUMBER = ""
        # Code Folding
        self.ShowFoldMarks = True
        self.FoldMarkColWidth = 12
        self.FoldMarkStyle = 0
        self.FoldFlags = 0
        self.FoldMarkBackground = wx.Colour("#808080")
        self.FoldMarkLine = wx.Colour("#000000")
        self.FoldMarkFill = wx.Colour("#FFFFFF")
        self.FoldMarkHighlight = wx.Colour("#FF0000")
        # Syntax
        self.syntax = OrderedDict()
        self.load()


    @property
    def config(self) -> wx.ConfigBase:
        return self.parent.config

    @property
    def backgroundColour(self):
        back = "#FFFFFF"
        for stylePart in self.STC_STYLE_DEFAULT.split(","):
            key, value = stylePart.split(":")
            if key == "back":
                back = value
                break
        return wx.Colour(back)

    @property
    def foregroundColour(self):
        fore = "#000000"
        for stylePart in self.STC_STYLE_DEFAULT.split(","):
            key, value = stylePart.split(":")
            if key == "fore":
                fore = value
                break
        return wx.Colour(fore)

    @property
    def fontFacename(self):
        face = "Consolas"
        for stylePart in self.STC_STYLE_DEFAULT.split(","):
            key, value = stylePart.split(":")
            if key == "face":
                face = value
                break
        return face

    @property
    def fontSize(self) -> int:
        size = 10
        for stylePart in self.STC_STYLE_DEFAULT.split(","):
            key, value = stylePart.split(":")
            if key == "size":
                size = int(value)
                break
        return size

    def load(self):
        """Load values from the application config"""
        cfg = self.config
        if cfg:
            # default style spec
            self.STC_STYLE_DEFAULT = cfg.Read(
                "STC_STYLE_DEFAULT", self.STC_STYLE_DEFAULT
            )
            self.STC_STYLE_CONTROLCHAR = cfg.Read(
                "STC_STYLE_CONTROLCHAR", self.STC_STYLE_CONTROLCHAR
            )
            self.STC_STYLE_BRACELIGHT = cfg.Read(
                "STC_STYLE_BRACELIGHT", self.STC_STYLE_BRACELIGHT
            )
            self.STC_STYLE_BRACEBAD = cfg.Read(
                "STC_STYLE_BRACEBAD", self.STC_STYLE_BRACEBAD
            )
            self.STC_STYLE_INDENTGUIDE = cfg.Read(
                "STC_STYLE_INDENTGUIDE", self.STC_STYLE_INDENTGUIDE
            )
            self.STC_STYLE_LINENUMBER = cfg.Read(
                "STC_STYLE_LINENUMBER", self.STC_STYLE_LINENUMBER
            )
            # Caret
            self.CaretWidth = cfg.ReadInt("CaretWidth", self.CaretWidth)
            self.CaretForeground = wx.Colour(
                cfg.Read(
                    "CaretForeground",
                    self.CaretForeground.GetAsString(wx.C2S_HTML_SYNTAX),
                )
            )
            self.CaretLineVisible = cfg.ReadBool(
                "CaretLineVisible", self.CaretLineVisible
            )
            self.CaretLineBackground = wx.Colour(
                cfg.Read(
                    "CaretLineBackground",
                    self.CaretLineBackground.GetAsString(wx.C2S_HTML_SYNTAX),
                )
            )
            self.CaretLineBackAlpha = cfg.ReadInt(
                "CaretLineBackAlpha", self.CaretLineBackAlpha
            )
            # Selection
            self.UseSelForeground = cfg.ReadBool(
                "UseSelForeground", self.UseSelForeground
            )
            self.SelForeground = wx.Colour(
                cfg.Read(
                    "SelForeground", self.SelForeground.GetAsString(wx.C2S_HTML_SYNTAX)
                )
            )
            self.UseSelBackground = cfg.ReadBool(
                "UseSelBackground", self.UseSelBackground
            )
            self.SelBackground = wx.Colour(
                cfg.Read(
                    "SelBackground", self.SelBackground.GetAsString(wx.C2S_HTML_SYNTAX)
                )
            )
            self.SelectionAlpha = cfg.ReadInt("SelectionAlpha", self.SelectionAlpha)
            self.SelEOLFilled = cfg.ReadBool("SelEOLFilled", self.SelEOLFilled)
            # Indentation and White Space
            self.Indent = cfg.ReadInt("Indent", self.Indent)
            self.TabWidth = cfg.ReadInt("TabWidth", self.TabWidth)
            self.UseTabs = cfg.ReadBool("UseTabs", self.UseTabs)
            self.TabIndents = cfg.ReadBool("TabIndents", self.TabIndents)
            self.BackSpaceUnIndents = cfg.ReadBool(
                "BackSpaceUnIndents", self.BackSpaceUnIndents
            )
            self.IndentationGuides = cfg.ReadBool(
                "IndentationGuides", self.IndentationGuides
            )
            self.ShowWhiteSpace = cfg.ReadInt("ShowWhiteSpace", self.ShowWhiteSpace)
            # Line Endings
            self.EOLMode = cfg.ReadInt("EOLMode", self.EOLMode)
            self.ViewEOL = cfg.ReadBool("ViewEOL", self.ViewEOL)
            self.WrapMode = cfg.ReadInt("WrapMode", self.WrapMode)
            self.WrapIndentMode = cfg.ReadInt("WrapIndentMode", self.WrapIndentMode)
            self.WrapVisualFlags = cfg.ReadInt("WrapVisualFlags", self.WrapVisualFlags)
            self.WrapVisualFlagsLocation = cfg.ReadInt(
                "WrapVisualFlagsLocation", self.WrapVisualFlagsLocation
            )
            # Line Numbers
            self.ShowLineNumbers = cfg.ReadBool("ShowLineNumbers", self.ShowLineNumbers)
            self.LineNumColWidth = cfg.ReadInt("LineNumColWidth", self.LineNumColWidth)
            # Code Folding
            self.ShowFoldMarks = cfg.ReadBool("ShowFoldMarks", self.ShowFoldMarks)
            self.FoldMarkColWidth = cfg.ReadInt(
                "FoldMarkColWidth", self.FoldMarkColWidth
            )
            self.FoldMarkStyle = cfg.ReadInt("FoldMarkStyle", self.FoldMarkStyle)
            self.FoldFlags = cfg.ReadInt("FoldFlags", self.FoldFlags)
            self.FoldMarkBackground = wx.Colour(
                cfg.Read(
                    "FoldMarkBackground",
                    self.FoldMarkBackground.GetAsString(wx.C2S_HTML_SYNTAX),
                )
            )
            self.FoldMarkLine = wx.Colour(
                cfg.Read(
                    "FoldMarkLine", self.FoldMarkLine.GetAsString(wx.C2S_HTML_SYNTAX)
                )
            )
            self.FoldMarkFill = wx.Colour(
                cfg.Read(
                    "FoldMarkFill", self.FoldMarkFill.GetAsString(wx.C2S_HTML_SYNTAX)
                )
            )
            self.FoldMarkHighlight = wx.Colour(
                cfg.Read(
                    "FoldMarkHighlight",
                    self.FoldMarkHighlight.GetAsString(wx.C2S_HTML_SYNTAX),
                )
            )
            # Syntax colouring
            for name in self.syntax:
                self.syntax[name] = cfg.Read(name, self.syntax[name])

    def save(self):
        """Save values to the application config"""
        cfg = self.config
        if cfg:
            # default style spec
            cfg.Write("STC_STYLE_DEFAULT", self.STC_STYLE_DEFAULT)
            cfg.Write("STC_STYLE_CONTROLCHAR", self.STC_STYLE_CONTROLCHAR)
            cfg.Write("STC_STYLE_BRACELIGHT", self.STC_STYLE_BRACELIGHT)
            cfg.Write("STC_STYLE_BRACEBAD", self.STC_STYLE_BRACEBAD)
            cfg.Write("STC_STYLE_INDENTGUIDE", self.STC_STYLE_INDENTGUIDE)
            cfg.Write("STC_STYLE_LINENUMBER", self.STC_STYLE_LINENUMBER)
            # Caret
            cfg.WriteInt("CaretWidth", self.CaretWidth)
            cfg.Write(
                "CaretForeground", self.CaretForeground.GetAsString(wx.C2S_HTML_SYNTAX)
            )
            cfg.WriteBool("CaretLineVisible", self.CaretLineVisible)
            cfg.Write(
                "CaretLineBackground",
                self.CaretLineBackground.GetAsString(wx.C2S_HTML_SYNTAX),
            )
            cfg.WriteInt("CaretLineBackAlpha", self.CaretLineBackAlpha)
            # Selection
            cfg.WriteBool("UseSelForeground", self.UseSelForeground)
            cfg.Write(
                "SelForeground", self.SelForeground.GetAsString(wx.C2S_HTML_SYNTAX)
            )
            cfg.WriteBool("UseSelBackground", self.UseSelBackground)
            cfg.Write(
                "SelBackground", self.SelBackground.GetAsString(wx.C2S_HTML_SYNTAX)
            )
            cfg.WriteInt("SelectionAlpha", self.SelectionAlpha)
            cfg.WriteBool("SelEOLFilled", self.SelEOLFilled)
            # Indentation and White Space
            cfg.WriteInt("Indent", self.Indent)
            cfg.WriteInt("TabWidth", self.TabWidth)
            cfg.WriteBool("UseTabs", self.UseTabs)
            cfg.WriteBool("TabIndents", self.TabIndents)
            cfg.WriteBool("BackSpaceUnIndents", self.BackSpaceUnIndents)
            cfg.WriteBool("IndentationGuides", self.IndentationGuides)
            cfg.WriteInt("ShowWhiteSpace", self.ShowWhiteSpace)
            # Line Endings
            cfg.WriteInt("EOLMode", self.EOLMode)
            cfg.WriteBool("ViewEOL", self.ViewEOL)
            cfg.WriteInt("WrapMode", self.WrapMode)
            cfg.WriteInt("WrapIndentMode", self.WrapIndentMode)
            cfg.WriteInt("WrapVisualFlags", self.WrapVisualFlags)
            cfg.WriteInt("WrapVisualFlagsLocation", self.WrapVisualFlagsLocation)
            # Line Numbers
            cfg.WriteBool("ShowLineNumbers", self.ShowLineNumbers)
            cfg.WriteInt("LineNumColWidth", self.LineNumColWidth)
            # Code Folding
            cfg.WriteBool("ShowFoldMarks", self.ShowFoldMarks)
            cfg.WriteInt("FoldMarkColWidth", self.FoldMarkColWidth)
            cfg.WriteInt("FoldMarkStyle", self.FoldMarkStyle)
            cfg.WriteInt("FoldFlags", self.FoldFlags)
            cfg.Write(
                "FoldMarkBackground",
                self.FoldMarkBackground.GetAsString(wx.C2S_HTML_SYNTAX),
            )
            cfg.Write("FoldMarkLine", self.FoldMarkLine.GetAsString(wx.C2S_HTML_SYNTAX))
            cfg.Write("FoldMarkFill", self.FoldMarkFill.GetAsString(wx.C2S_HTML_SYNTAX))
            cfg.Write(
                "FoldMarkHighlight",
                self.FoldMarkHighlight.GetAsString(wx.C2S_HTML_SYNTAX),
            )
            # Syntax colouring
            for name in self.syntax:
                cfg.Write(name, self.syntax[name])
        else:
            wx.LogDebug(f"no config for {self}")

    def apply(self, textEditCtrl):
        """Apply values to TextEditCtrl"""
        ctrl: TextEditCtrl = textEditCtrl
        # default style spec
        ctrl.StyleSetSpec(stc.STC_STYLE_DEFAULT, self.STC_STYLE_DEFAULT)
        ctrl.StyleClearAll()
        ctrl.StyleSetSpec(stc.STC_STYLE_CONTROLCHAR, self.STC_STYLE_CONTROLCHAR)
        ctrl.StyleSetSpec(stc.STC_STYLE_BRACELIGHT, self.STC_STYLE_BRACELIGHT)
        ctrl.StyleSetSpec(stc.STC_STYLE_BRACEBAD, self.STC_STYLE_BRACEBAD)
        ctrl.StyleSetSpec(stc.STC_STYLE_INDENTGUIDE, self.STC_STYLE_INDENTGUIDE)
        ctrl.StyleSetSpec(stc.STC_STYLE_LINENUMBER, self.STC_STYLE_LINENUMBER)
        # Setup Caret
        ctrl.SetCaretWidth(self.CaretWidth)
        ctrl.SetCaretForeground(self.CaretForeground)
        ctrl.SetCaretLineVisible(self.CaretLineVisible)
        ctrl.SetCaretLineBackground(self.CaretLineBackground)
        ctrl.SetCaretLineBackAlpha(self.CaretLineBackAlpha)
        # Setup Selection
        ctrl.SetSelForeground(self.UseSelForeground, self.SelForeground)
        ctrl.SetSelBackground(self.UseSelBackground, self.SelBackground)
        ctrl.SetSelAlpha(self.SelectionAlpha)
        ctrl.SetSelEOLFilled(self.SelEOLFilled)
        # Setup Indentation and White Space
        ctrl.SetIndent(self.Indent)
        ctrl.SetTabWidth(self.TabWidth)
        ctrl.SetIndentationGuides(self.IndentationGuides)
        ctrl.SetBackSpaceUnIndents(self.BackSpaceUnIndents)
        ctrl.SetTabIndents(self.TabIndents)
        ctrl.SetUseTabs(self.UseTabs)
        ctrl.SetViewWhiteSpace(self.ShowWhiteSpace)
        # Setup Line Endings
        ctrl.SetEOLMode(self.EOLMode)
        ctrl.SetViewEOL(self.ViewEOL)
        ctrl.SetWrapMode(self.WrapMode)
        ctrl.SetWrapIndentMode(self.WrapIndentMode)
        ctrl.SetWrapVisualFlags(self.WrapVisualFlags)
        ctrl.SetWrapVisualFlagsLocation(self.WrapVisualFlagsLocation)
        # Setup Line Numbers
        if self.ShowLineNumbers:
            ctrl.SetMarginWidth(MARGIN_NUMBERS, self.LineNumColWidth)
        else:
            ctrl.SetMarginWidth(MARGIN_NUMBERS, 0)
        # Setup Code Folding
        if isinstance(ctrl, STCfoldMixin) and self.ShowFoldMarks:
            ctrl.SetMarginWidth(MARGIN_FOLDMARK, self.FoldMarkColWidth)
            ctrl.SetMarginSensitive(MARGIN_FOLDMARK, True)
            ctrl.SetFoldMarginColour(True, self.FoldMarkBackground)
            ctrl.SetFoldMarginHiColour(True, self.FoldMarkBackground)
            ctrl.SetFoldFlags(self.FoldFlags)
            ctrl.defineFoldMarker(
                self.FoldMarkStyle,
                self.FoldMarkLine,
                self.FoldMarkFill,
                self.FoldMarkHighlight,
            )
        else:
            ctrl.SetMarginWidth(MARGIN_FOLDMARK, 0)
            ctrl.SetMarginSensitive(MARGIN_FOLDMARK, False)
        # Syntax colouring
        # print('Syntax colouring')
        for name in self.syntax:
            # print(' ', name, self.syntax[name])
            ctrl.StyleSetSpec(getattr(stc, name), self.syntax[name])

    def registerPropertyEditors(self, page: PreferencesPageBase):
        if not page.GetEditorByName("OptColourEditor"):
            page.RegisterEditor(OptColourEditor, "OptColourEditor")
        if not page.GetEditorByName("StyleSpecEditor"):
            page.RegisterEditor(StyleSpecEditor, "StyleSpecEditor")

    def appendProperties_main(self, page: PreferencesPageBase):
        page.Append(pg.PropertyCategory("Main"))
        page.Append(FontfacenameMonoProperty("Font", "font", self.fontFacename))
        page.Append(pg.IntProperty("Font Size", "size", self.fontSize))
        page.Append(
            pg.ColourProperty("Foreground Colour", "foreground", self.foregroundColour)
        )
        page.Append(
            pg.ColourProperty("Background Colour", "background", self.backgroundColour)
        )
        page.Append(
            StyleSpecProperty(
                "Controlchar", "STC_STYLE_CONTROLCHAR", self.STC_STYLE_CONTROLCHAR
            )
        )
        page.Append(
            StyleSpecProperty(
                "Brace highlight", "STC_STYLE_BRACELIGHT", self.STC_STYLE_BRACELIGHT
            )
        )
        page.Append(
            StyleSpecProperty(
                "Brace mismatch", "STC_STYLE_BRACEBAD", self.STC_STYLE_BRACEBAD
            )
        )

    def appendProperties_caret(self, page: PreferencesPageBase):
        page.Append(pg.PropertyCategory("Caret"))
        page.Append(pg.IntProperty("Caret Width", "CaretWidth", self.CaretWidth))
        page.Append(
            pg.ColourProperty("Caret Colour", "CaretForeground", self.CaretForeground)
        )
        page.Append(
            pg.BoolProperty(
                "Show Caret Line", "CaretLineVisible", self.CaretLineVisible
            )
        )
        page.Append(
            pg.ColourProperty(
                "Caret Line Colour", "CaretLineBackground", self.CaretLineBackground
            )
        )
        page.Append(
            pg.IntProperty(
                "Caret Line Alpha", "CaretLineBackAlpha", self.CaretLineBackAlpha
            )
        )

    def appendProperties_selection(self, page: PreferencesPageBase):
        page.Append(pg.PropertyCategory("Selection"))
        page.Append(
            pg.BoolProperty(
                "Use Selection Foreground", "UseSelForeground", self.UseSelForeground
            )
        )
        page.Append(
            pg.ColourProperty(
                "Selection Foreground Colour", "SelForeground", self.SelForeground
            )
        )
        page.Append(
            pg.BoolProperty(
                "Use Selection Background", "UseSelBackground", self.UseSelBackground
            )
        )
        page.Append(
            pg.ColourProperty(
                "Selection Background Colour", "SelBackground", self.SelBackground
            )
        )
        page.Append(
            pg.IntProperty("Selection Alpha", "SelectionAlpha", self.SelectionAlpha)
        )
        page.Append(
            pg.BoolProperty("Selection EOL Filled", "SelEOLFilled", self.SelEOLFilled)
        )

    def appendProperties_indentation(self, page: PreferencesPageBase):
        page.Append(pg.PropertyCategory("Indentation and White Space"))
        page.Append(pg.IntProperty("Indetation Size", "Indent", self.Indent))
        page.Append(pg.IntProperty("Tab Size", "TabWidth", self.TabWidth))
        page.Append(pg.BoolProperty("Use Tabs for Indetation", "UseTabs", self.UseTabs))
        page.Append(pg.BoolProperty("Tab Indents", "TabIndents", self.TabIndents))
        page.Append(
            pg.BoolProperty(
                "BackSpace UnIndents", "BackSpaceUnIndents", self.BackSpaceUnIndents
            )
        )
        page.Append(
            pg.BoolProperty(
                "Show Indetation Guides", "IndentationGuides", self.IndentationGuides
            )
        )
        page.Append(
            StyleSpecProperty(
                "Indetation Guides", "STC_STYLE_INDENTGUIDE", self.STC_STYLE_INDENTGUIDE
            )
        )
        page.Append(
            pg.EnumProperty(
                "Show White Space",
                "ShowWhiteSpace",
                ("Never", "Alwasy", "Only after Indentation"),
                (
                    stc.STC_WS_INVISIBLE,
                    stc.STC_WS_VISIBLEALWAYS,
                    stc.STC_WS_VISIBLEAFTERINDENT,
                ),
                self.ShowWhiteSpace,
            )
        )

    def appendProperties_line_ending(self, page: PreferencesPageBase):
        page.Append(pg.PropertyCategory("Line Endings"))
        page.Append(
            pg.EnumProperty(
                "End of Line Mode",
                "EOLMode",
                ("DOS/Windows [CR+LF]", "Unix/Linux [LF]", "Mac Classic [CR]"),
                (stc.STC_EOL_CRLF, stc.STC_EOL_LF, stc.STC_EOL_CR),
                self.EOLMode,
            )
        )
        page.Append(pg.BoolProperty("Show EOL Symbols", "ViewEOL", self.ViewEOL))

    def appendProperties_line_warp(self, page: PreferencesPageBase):
        page.Append(pg.PropertyCategory("Line Wrap"))
        page.Append(
            pg.EnumProperty(
                "Wrap Mode",
                "WrapMode",
                ("Disabled", "Word Boundaries", "Characters"),
                (stc.STC_WRAP_NONE, stc.STC_WRAP_WORD, stc.STC_WRAP_CHAR),
                self.WrapMode,
            )
        )
        page.Append(
            pg.EnumProperty(
                "Wrap Indentation",
                "WrapIndentMode",
                ("Fixed", "Same", "Indent"),
                (
                    stc.STC_WRAPINDENT_FIXED,
                    stc.STC_WRAPINDENT_SAME,
                    stc.STC_WRAPINDENT_INDENT,
                ),
                self.WrapIndentMode,
            )
        )
        page.Append(
            pg.FlagsProperty(
                "Visual Wrap Flags",
                "WrapVisualFlags",
                (
                    "End of wrapped line",
                    "Begin of wrapped line",
                    "In line number margin",
                ),
                # (stc.STC_WRAPVISUALFLAG_NONE,
                (
                    stc.STC_WRAPVISUALFLAG_END,
                    stc.STC_WRAPVISUALFLAG_START,
                    stc.STC_WRAPVISUALFLAG_MARGIN,
                ),
                self.WrapVisualFlags,
            )
        )
        page.Append(
            pg.FlagsProperty(
                "Visual Wrap Flag Location",
                "WrapVisualFlagsLocation",
                ("At end near text", "At beginning near text"),
                (
                    stc.STC_WRAPVISUALFLAGLOC_END_BY_TEXT,
                    stc.STC_WRAPVISUALFLAGLOC_START_BY_TEXT,
                ),
                self.WrapVisualFlagsLocation,
            )
        )

    def appendProperties_line_numbers(self, page: PreferencesPageBase):
        page.Append(pg.PropertyCategory("Line Numbers"))
        page.Append(
            pg.BoolProperty(
                "Show Line Numbers", "ShowLineNumbers", self.ShowLineNumbers
            )
        )
        page.Append(
            pg.IntProperty("Column Width", "LineNumColWidth", self.LineNumColWidth)
        )
        page.Append(
            StyleSpecProperty(
                "Line Numbers", "STC_STYLE_LINENUMBER", self.STC_STYLE_LINENUMBER
            )
        )

    def appendProperties_code_folding(self, page: PreferencesPageBase):
        page.Append(pg.PropertyCategory("Code Folding"))
        page.Append(
            pg.BoolProperty("Show Fold Marks", "ShowFoldMarks", self.ShowFoldMarks)
        )
        page.Append(
            pg.IntProperty("Column Width", "FoldMarkColWidth", self.FoldMarkColWidth)
        )
        page.Append(
            pg.EnumProperty(
                "Mark Style",
                "FoldMarkStyle",
                ("Box", "Circle", "Arrow", "Plus-Minus"),
                (0, 1, 2, 3, 4),
                self.FoldMarkStyle,
            )
        )
        page.Append(
            pg.FlagsProperty(
                "Fold Flags",
                "FoldFlags",
                (
                    "Draw above if expanded",
                    "Draw above if not expanded",
                    "Draw below if expanded",
                    "Draw below if not expanded",
                ),
                (
                    stc.STC_FOLDFLAG_LINEBEFORE_EXPANDED,
                    stc.STC_FOLDFLAG_LINEBEFORE_CONTRACTED,
                    stc.STC_FOLDFLAG_LINEAFTER_EXPANDED,
                    stc.STC_FOLDFLAG_LINEAFTER_CONTRACTED,
                ),
                self.FoldFlags,
            )
        )
        page.Append(
            pg.ColourProperty(
                "Background Colour", "FoldMarkBackground", self.FoldMarkBackground
            )
        )
        page.Append(pg.ColourProperty("Line Colour", "FoldMarkLine", self.FoldMarkLine))
        page.Append(pg.ColourProperty("Fill Colour", "FoldMarkFill", self.FoldMarkFill))
        page.Append(
            pg.ColourProperty(
                "Highlight Colour", "FoldMarkHighlight", self.FoldMarkHighlight
            )
        )

    def appendProperties_syntax_colour(self, page: PreferencesPageBase):
        if self.syntax:
            page.Append(pg.PropertyCategory("Syntax Colour"))
            for name in self.syntax:
                label = name.split("_", 2)[2].title()
                page.Append(StyleSpecProperty(label, name, self.syntax[name]))

    def appendProperties(self, page: PreferencesPageBase):
        """Append properties to PreferencesPage"""
        self.registerPropertyEditors(page)
        self.appendProperties_main(page)
        self.appendProperties_caret(page)
        self.appendProperties_selection(page)
        self.appendProperties_indentation(page)
        self.appendProperties_line_ending(page)
        self.appendProperties_line_warp(page)
        self.appendProperties_line_numbers(page)
        self.appendProperties_code_folding(page)
        self.appendProperties_syntax_colour(page)

    def getPropertyValues(self, page: PreferencesPageBase):
        values = page.GetPropertyValues()
        fg = values.pop("foreground", wx.BLACK).GetAsString(wx.C2S_HTML_SYNTAX)
        bg = values.pop("background", wx.WHITE).GetAsString(wx.C2S_HTML_SYNTAX)
        font = values.pop("font", "Consolas")
        size = values.pop("size", 10)
        self.STC_STYLE_DEFAULT = f"fore:{fg},back:{bg},face:{font},size:{size}"
        for name in values:
            val = values[name]
            if hasattr(self, name):
                if isinstance(val, type(getattr(self, name))):
                    setattr(self, name, val)
                elif isinstance(val, type(None)) and isinstance(
                    getattr(self, name), str
                ):
                    setattr(self, name, "")
            elif name in self.syntax:
                if isinstance(val, type(None)):
                    self.syntax[name] = ""
                elif isinstance(val, str):
                    self.syntax[name] = val


class PyTextEditConfig(TextEditConfig):
    def __init__(self, parent):
        super().__init__(parent)
        self.syntax["STC_P_DEFAULT"] = "fore:black,back:white"
        self.syntax["STC_P_IDENTIFIER"] = "fore:#000000"
        self.syntax["STC_P_WORD"] = "fore:#000080,italic"
        self.syntax["STC_P_WORD2"] = "fore:#B00000,italic"
        self.syntax["STC_P_COMMENTLINE"] = "fore:#008000,back:#F0FFF0"
        self.syntax["STC_P_COMMENTBLOCK"] = "fore:#008000,back:#F0FFF0"
        self.syntax["STC_P_NUMBER"] = "fore:#008080"
        self.syntax["STC_P_STRING"] = "fore:#800080"
        self.syntax["STC_P_CHARACTER"] = "fore:#800080"
        self.syntax["STC_P_TRIPLE"] = "fore:#800080"
        self.syntax["STC_P_TRIPLEDOUBLE"] = "fore:#800080"
        self.syntax["STC_P_CLASSNAME"] = "fore:#0000FF,bold"
        self.syntax["STC_P_DEFNAME"] = "fore:#008080,bold"
        self.syntax["STC_P_DECORATOR"] = "fore:#006060"
        self.syntax["STC_P_OPERATOR"] = "fore:#900000,bold"
        self.syntax["STC_P_STRINGEOL"] = "fore:#800080"


class XmlTextEditConfig(TextEditConfig):
    def __init__(self, parent):
        super().__init__(parent)
        self.syntax["STC_H_DEFAULT"] = "fore:black,back:white"
        self.syntax["STC_H_XMLSTART"] = "fore:#CA0000,bold"
        self.syntax["STC_H_XMLEND"] = "fore:#CA0000,bold"
        self.syntax["STC_H_TAG"] = "fore:#800040,bold"
        self.syntax["STC_H_TAGEND"] = "#fore:800040,bold"
        self.syntax["STC_H_TAGUNKNOWN"] = "#fore:800040,bold"
        self.syntax["STC_H_ATTRIBUTE"] = "fore:#804000,italic"
        self.syntax["STC_H_ATTRIBUTEUNKNOWN"] = "fore:#804000,italic"
        self.syntax["STC_H_NUMBER"] = "fore:black"
        self.syntax["STC_H_SINGLESTRING"] = "fore:#004080"
        self.syntax["STC_H_DOUBLESTRING"] = "fore:#004080"
        self.syntax["STC_H_OTHER"] = "fore:black"
        self.syntax["STC_H_COMMENT"] = "fore:#8B8B8B"
        self.syntax["STC_H_ENTITY"] = "fore:#008000"
        self.syntax["STC_H_VALUE"] = "fore:black"
        self.syntax["STC_H_QUESTION"] = "fore:black"
        self.syntax["STC_H_CDATA"] = "fore:#8000FF"
