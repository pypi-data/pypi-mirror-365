# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.9.0 Oct 29 2020)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class MultiSaveModifiedDialogUI
###########################################################################

class MultiSaveModifiedDialogUI ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"WorkBench", pos = wx.DefaultPosition, size = wx.Size( 505,148 ), style = wx.CAPTION|wx.RESIZE_BORDER )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        sizer = wx.BoxSizer( wx.VERTICAL )

        self.lbl_message = wx.StaticText( self, wx.ID_ANY, u"Save changes to ...", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_message.Wrap( -1 )

        sizer.Add( self.lbl_message, 0, wx.ALL, 5 )

        self.lbl_path = wx.StaticText( self, wx.ID_ANY, u"path", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_path.Wrap( 300 )

        sizer.Add( self.lbl_path, 1, wx.ALL|wx.EXPAND, 5 )

        button_sizer = wx.BoxSizer( wx.HORIZONTAL )

        self.btn_yes_to_all = wx.Button( self, wx.ID_ANY, u"Yes to All", wx.DefaultPosition, wx.DefaultSize, 0 )
        button_sizer.Add( self.btn_yes_to_all, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.btn_no_to_all = wx.Button( self, wx.ID_ANY, u"No to All", wx.DefaultPosition, wx.DefaultSize, 0 )
        button_sizer.Add( self.btn_no_to_all, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        button_sizer.Add( ( 10, 0), 1, wx.EXPAND, 5 )

        std_button_sizer = wx.StdDialogButtonSizer()
        self.std_button_sizerYes = wx.Button( self, wx.ID_YES )
        std_button_sizer.AddButton( self.std_button_sizerYes )
        self.std_button_sizerNo = wx.Button( self, wx.ID_NO )
        std_button_sizer.AddButton( self.std_button_sizerNo )
        self.std_button_sizerCancel = wx.Button( self, wx.ID_CANCEL )
        std_button_sizer.AddButton( self.std_button_sizerCancel )
        std_button_sizer.Realize();

        button_sizer.Add( std_button_sizer, 0, wx.EXPAND, 5 )


        sizer.Add( button_sizer, 0, wx.EXPAND, 5 )


        self.SetSizer( sizer )
        self.Layout()

        self.Centre( wx.BOTH )

        # Connect Events
        self.btn_yes_to_all.Bind( wx.EVT_BUTTON, self.on_btn_yes_to_all )
        self.btn_no_to_all.Bind( wx.EVT_BUTTON, self.on_btn_no_to_all )
        self.std_button_sizerCancel.Bind( wx.EVT_BUTTON, self.on_btn_cancel )
        self.std_button_sizerNo.Bind( wx.EVT_BUTTON, self.on_btn_no )
        self.std_button_sizerYes.Bind( wx.EVT_BUTTON, self.on_btn_yes )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def on_btn_yes_to_all( self, event ):
        event.Skip()

    def on_btn_no_to_all( self, event ):
        event.Skip()

    def on_btn_cancel( self, event ):
        event.Skip()

    def on_btn_no( self, event ):
        event.Skip()

    def on_btn_yes( self, event ):
        event.Skip()


