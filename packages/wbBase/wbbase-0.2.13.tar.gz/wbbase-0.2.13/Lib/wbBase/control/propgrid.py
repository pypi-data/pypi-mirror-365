"""
Custom Properties for WX-Property-Grid control
"""

import wx
import wx.propgrid as pg


class FontfacenameMonoProperty(pg.EnumProperty):
    """Select the facename of a monospaced font"""

    def __init__(self, label=pg.PG_LABEL, name=pg.PG_LABEL, value=None):
        labels = sorted(
            [
                n
                for n in wx.FontEnumerator().GetFacenames(fixedWidthOnly=True)
                if not n.startswith("@")
            ]
        )
        values = list(range(len(labels)))
        if value is not None and value in labels:
            default = labels.index(value)
        else:
            default = 0
        pg.EnumProperty.__init__(
            self, label=label, name=name, labels=labels, values=values, value=default
        )

    def DoGetValue(self):
        choices = self.GetChoices()
        return choices.Labels[self.ChoiceSelection]


class OptColourEditor(pg.PGEditor):
    """Property Editor for OptColourProperty"""

    def CreateControls(self, propgrid, property, pos, sz):
        # wnd = super().CreateControls(propgrid, property, pos, sz).GetPrimary()
        return pg.PGWindowList(None)
        # pass

    def DrawValue(self, dc, rect, property, text):
        if not property.IsValueUnspecified():
            if not property.m_default:
                brush = wx.TheBrushList.FindOrCreateBrush(
                    property.m_colour, wx.BRUSHSTYLE_SOLID
                )
                dc.SetBrush(brush)
                dc.DrawRoundedRectangle(rect, 4)


class OptColourProperty(pg.PGProperty):
    """Optional Colour Property"""

    def __init__(self, label, name="", value=None):
        pg.PGProperty.__init__(self, label, name)
        if value is None:
            self.m_default = True
            self.m_colour = wx.BLACK
        else:
            self.m_colour = wx.Colour(value)
            if self.m_colour.IsOk():
                self.m_default = False
            else:
                self.m_default = True
                self.m_colour = wx.BLACK

        self.AddPrivateChild(pg.BoolProperty("Use default", "default", self.m_default))
        self.AddPrivateChild(pg.ColourProperty("Colour", "colour", self.m_colour))
        self.SetEditor("OptColourEditor")
        self._calcValue()
        self.Item(0).SetAttribute("UseCheckbox", True)

    def _calcValue(self):
        if self.m_default:
            self.Item(1).Enable(False)
            self.m_value = ""
        elif self.m_colour.IsOk():
            self.Item(1).Enable(True)
            self.m_value = self.m_colour.GetAsString(wx.C2S_HTML_SYNTAX)
        else:
            self.Item(1).Enable(False)
            self.m_value = ""

    def ValueToString(self, value, argFlags=0):
        result = ""
        try:
            c = wx.Colour(value)
            if c.IsOk():
                result = c.GetAsString(wx.C2S_HTML_SYNTAX)
        except:
            pass
        return result

    def StringToValue(self, text, argFlags=0):
        if not text:
            self.m_default = True
            self._calcValue()
            return (True, "")
        else:
            c = wx.Colour(text)
            if c.IsOk():
                self.m_default = False
                self.m_colour = c
                self._calcValue()
                return (True, c.GetAsString(wx.C2S_HTML_SYNTAX))
            else:
                self.m_default = True
                self._calcValue()
                return (False, None)

    def ChildChanged(self, thisValue, childIndex, childValue):
        if childIndex == 0:
            self.m_default = childValue
            self.Item(1).Enable(not childValue)
        elif childIndex == 1:
            self.m_colour = childValue
        self._calcValue()
        return self.m_value

    def RefreshChildren(self):
        self.Item(0).SetValue(self.m_default)
        self.Item(1).SetValue(self.m_colour)


class StyleSpecEditor(pg.PGEditor):
    """Property Editor for StyleSpecProperty"""

    def CreateControls(self, propgrid, property, pos, sz):
        # wnd = super().CreateControls(propgrid, property, pos, sz).GetPrimary()
        return pg.PGWindowList(None)
        # pass

    def DrawValue(self, dc, rect, property, text):
        if not property.IsValueUnspecified():
            # save current dc settings
            backgroundMode = dc.GetBackgroundMode()
            font = dc.GetFont()
            # get global settings
            grid = property.GetGrid()
            bgProp = grid.GetPropertyByName("background")
            if bgProp is not None:
                bgColour = bgProp.GetValue()
            else:
                bgColour = wx.WHITE
            dc.SetBackground(
                wx.TheBrushList.FindOrCreateBrush(bgColour, wx.BRUSHSTYLE_SOLID)
            )
            dc.Clear()
            fontInfo = wx.FontInfo(10).Bold(property.m_bold).Italic(property.m_italic)
            fontProp = grid.GetPropertyByName("font")
            if fontProp is not None:
                fontInfo = fontInfo.FaceName(fontProp.GetValue())
            else:
                fontInfo = fontInfo.Family(wx.FONTFAMILY_MODERN)
            if property.m_fore:
                dc.SetTextForeground(wx.Colour(property.m_fore))
            else:
                fgProp = grid.GetPropertyByName("foreground")
                if fgProp is not None:
                    fgColour = fgProp.GetValue()
                else:
                    fgColour = wx.BLACK
                dc.SetTextForeground(fgColour)
            if property.m_back:
                dc.SetBackgroundMode(wx.SOLID)
                dc.SetTextBackground(wx.Colour(property.m_back))
            dc.SetFont(wx.Font(fontInfo))
            dc.DrawText("Sample", rect.x + 5, rect.y)
            dc.SetFont(font)
            dc.SetBackgroundMode(backgroundMode)


class StyleSpecProperty(pg.PGProperty):
    def __init__(self, label, name=pg.PG_LABEL, value=""):
        pg.PGProperty.__init__(self, label, name)
        parts = [p.strip() for p in value.split(",")]
        self.m_fore = ""
        self.m_back = ""
        self.m_bold = ""
        self.m_italic = ""
        self.StringToValue(value)
        self.AddPrivateChild(OptColourProperty("Text colour", "fore", self.m_fore))
        self.AddPrivateChild(
            OptColourProperty("Background colour", "back", self.m_back)
        )
        self.AddPrivateChild(pg.BoolProperty("Bold", "bold", self.m_bold))
        self.AddPrivateChild(pg.BoolProperty("Italic", "italic", self.m_italic))
        self.SetEditor("StyleSpecEditor")
        self._calcValue()
        self.Item(2).SetAttribute("UseCheckbox", True)
        self.Item(3).SetAttribute("UseCheckbox", True)

    def _calcValue(self):
        parts = []
        if self.m_fore:
            parts.append(f"fore:{self.m_fore}")
        if self.m_back:
            parts.append(f"back:{self.m_back}")
        if self.m_bold:
            parts.append("bold")
        if self.m_italic:
            parts.append("italic")
        self.m_value = ",".join(parts)

    def ValueToString(self, value, argFlags=0):
        if not value:
            return ""
        if isinstance(value, str):
            return value
        else:
            print("ERROR")
            return ""

    def StringToValue(self, text, argFlags=0):
        parts = [p.strip() for p in text.split(",")]
        self.m_fore = ""
        self.m_back = ""
        self.m_bold = "bold" in parts
        self.m_italic = "italic" in parts
        for part in parts:
            if part.startswith("fore:"):
                colour = wx.Colour(part.split(":")[1])
                if colour.IsOk():
                    self.m_fore = colour.GetAsString(wx.C2S_HTML_SYNTAX)
            elif part.startswith("back:"):
                colour = wx.Colour(part.split(":")[1])
                if colour.IsOk():
                    self.m_back = colour.GetAsString(wx.C2S_HTML_SYNTAX)
        self._calcValue()
        return (True, self.m_value)

    def ChildChanged(self, thisValue, childIndex, childValue):
        if childIndex == 0:
            self.m_fore = childValue
        if childIndex == 1:
            self.m_back = childValue
        if childIndex == 2:
            self.m_bold = childValue
        if childIndex == 3:
            self.m_italic = childValue
        self._calcValue()
        return self.m_value

    def RefreshChildren(self):
        self.Item(0).SetValue(self.m_fore)
        self.Item(1).SetValue(self.m_back)
        self.Item(2).SetValue(self.m_bold)
        self.Item(3).SetValue(self.m_italic)
