from __future__ import annotations
import os

import subprocess
import sys

import wx


def startfile(filePath) -> None:
    if sys.platform == "win32":
        os.startfile(filePath)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filePath])


def get_wxBrush(color=wx.BLACK, style=wx.BRUSHSTYLE_SOLID) -> wx.Brush:
    return wx.TheBrushList.FindOrCreateBrush(color, style)


def get_wxPen(color=wx.BLACK, width=1, style=wx.PENSTYLE_SOLID) -> wx.Pen:
    return wx.ThePenList.FindOrCreatePen(color, width, style)


def get_wxFont(
    pointSize=10,
    family=wx.FONTFAMILY_SWISS,
    style=wx.FONTSTYLE_NORMAL,
    weight=wx.FONTWEIGHT_NORMAL,
    underline=False,
    faceName="",
    encoding=wx.FONTENCODING_DEFAULT,
) -> wx.Font:
    return wx.TheFontList.FindOrCreateFont(
        round(pointSize), family, style, weight, underline, faceName, encoding
    )
