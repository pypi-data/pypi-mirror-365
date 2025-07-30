# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Oct 26 2018)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class ExternalToolConfigUI
###########################################################################

class ExternalToolConfigUI ( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		self.SetMinSize( wx.Size( 300,200 ) )

		sizerMain = wx.BoxSizer( wx.HORIZONTAL )

		sizerLeft = wx.BoxSizer( wx.VERTICAL )

		listBox_toolsChoices = [ u"<new>" ]
		self.listBox_tools = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, listBox_toolsChoices, wx.LB_SINGLE )
		self.listBox_tools.SetMinSize( wx.Size( 100,-1 ) )

		sizerLeft.Add( self.listBox_tools, 1, wx.EXPAND, 0 )

		sizerButtons = wx.BoxSizer( wx.HORIZONTAL )

		self.button_up = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )

		self.button_up.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_GO_UP, wx.ART_BUTTON ) )
		self.button_up.Enable( False )
		self.button_up.SetToolTip( u"Move tool up" )

		sizerButtons.Add( self.button_up, 0, wx.ALL, 5 )

		self.button_down = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )

		self.button_down.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_GO_DOWN, wx.ART_BUTTON ) )
		self.button_down.Enable( False )
		self.button_down.SetToolTip( u"Moce tool down" )

		sizerButtons.Add( self.button_down, 0, wx.ALL, 5 )

		self.button_delete = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )

		self.button_delete.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_MINUS, wx.ART_BUTTON ) )
		self.button_delete.Enable( False )
		self.button_delete.SetToolTip( u"Delete tool" )

		sizerButtons.Add( self.button_delete, 0, wx.ALL, 5 )


		sizerLeft.Add( sizerButtons, 0, wx.ALIGN_CENTER_HORIZONTAL, 5 )


		sizerMain.Add( sizerLeft, 1, wx.EXPAND, 5 )

		sizerRight = wx.BoxSizer( wx.VERTICAL )

		self.label_menu = wx.StaticText( self, wx.ID_ANY, u"Menu label", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.label_menu.Wrap( -1 )

		sizerRight.Add( self.label_menu, 0, wx.ALL, 5 )

		self.textCtrl_label = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		sizerRight.Add( self.textCtrl_label, 0, wx.ALL|wx.EXPAND, 5 )

		self.label_command = wx.StaticText( self, wx.ID_ANY, u"Command", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.label_command.Wrap( -1 )

		sizerRight.Add( self.label_command, 0, wx.ALL, 5 )

		sizerCommand = wx.BoxSizer( wx.HORIZONTAL )

		self.textCtrl_command = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		sizerCommand.Add( self.textCtrl_command, 1, wx.ALL|wx.EXPAND, 5 )

		self.button_command = wx.Button( self, wx.ID_ANY, u"...", wx.DefaultPosition, wx.DefaultSize, 0 )
		sizerCommand.Add( self.button_command, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		sizerRight.Add( sizerCommand, 0, wx.EXPAND, 5 )

		self.label_directory = wx.StaticText( self, wx.ID_ANY, u"Working directory", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.label_directory.Wrap( -1 )

		sizerRight.Add( self.label_directory, 0, wx.ALL, 5 )

		sizerDirectory = wx.BoxSizer( wx.HORIZONTAL )

		self.textCtrl_directory = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		sizerDirectory.Add( self.textCtrl_directory, 1, wx.ALL|wx.EXPAND, 5 )

		self.button_directory = wx.Button( self, wx.ID_ANY, u"...", wx.DefaultPosition, wx.DefaultSize, 0 )
		sizerDirectory.Add( self.button_directory, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		sizerRight.Add( sizerDirectory, 0, wx.EXPAND, 5 )


		sizerMain.Add( sizerRight, 2, wx.EXPAND, 5 )


		self.SetSizer( sizerMain )
		self.Layout()
		sizerMain.Fit( self )

		# Connect Events
		self.listBox_tools.Bind( wx.EVT_LISTBOX, self.on_listBox_tools )
		self.button_up.Bind( wx.EVT_BUTTON, self.on_button_up )
		self.button_up.Bind( wx.EVT_UPDATE_UI, self.update_button_up )
		self.button_down.Bind( wx.EVT_BUTTON, self.on_button_down )
		self.button_down.Bind( wx.EVT_UPDATE_UI, self.update_button_down )
		self.button_delete.Bind( wx.EVT_BUTTON, self.on_button_delete )
		self.button_delete.Bind( wx.EVT_UPDATE_UI, self.update_button_delete )
		self.textCtrl_label.Bind( wx.EVT_TEXT, self.on_textCtrl_label )
		self.textCtrl_command.Bind( wx.EVT_TEXT, self.on_textCtrl_command )
		self.button_command.Bind( wx.EVT_BUTTON, self.on_button_command )
		self.textCtrl_directory.Bind( wx.EVT_TEXT, self.on_textCtrl_directory )
		self.button_directory.Bind( wx.EVT_BUTTON, self.on_button_directory )

	def __del__( self ):
		pass


	# Virtual event handlers, overide them in your derived class
	def on_listBox_tools( self, event ):
		event.Skip()

	def on_button_up( self, event ):
		event.Skip()

	def update_button_up( self, event ):
		event.Skip()

	def on_button_down( self, event ):
		event.Skip()

	def update_button_down( self, event ):
		event.Skip()

	def on_button_delete( self, event ):
		event.Skip()

	def update_button_delete( self, event ):
		event.Skip()

	def on_textCtrl_label( self, event ):
		event.Skip()

	def on_textCtrl_command( self, event ):
		event.Skip()

	def on_button_command( self, event ):
		event.Skip()

	def on_textCtrl_directory( self, event ):
		event.Skip()

	def on_button_directory( self, event ):
		event.Skip()


