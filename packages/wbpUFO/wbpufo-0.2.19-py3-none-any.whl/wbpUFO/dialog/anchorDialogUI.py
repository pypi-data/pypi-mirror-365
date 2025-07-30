# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.0-4761b0c)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class AnchorDialogUI
###########################################################################

class AnchorDialogUI ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Anchor", pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.CAPTION|wx.RESIZE_BORDER )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		sizerMain = wx.GridBagSizer( 0, 0 )
		sizerMain.SetFlexibleDirection( wx.VERTICAL )
		sizerMain.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.message = wx.StaticText( self, wx.ID_ANY, u"Edit Anchor", wx.DefaultPosition, wx.DefaultSize, wx.ST_NO_AUTORESIZE|wx.ALIGN_CENTER_HORIZONTAL )
		self.message.Wrap( -1 )

		sizerMain.Add( self.message, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 2 ), wx.ALL|wx.EXPAND, 5 )

		self.label_name = wx.StaticText( self, wx.ID_ANY, u"Name", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.label_name.Wrap( -1 )

		sizerMain.Add( self.label_name, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.textCtrl_name = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		sizerMain.Add( self.textCtrl_name, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.label_position = wx.StaticText( self, wx.ID_ANY, u"Position", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.label_position.Wrap( -1 )

		sizerMain.Add( self.label_position, wx.GBPosition( 2, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

		sizerPos = wx.FlexGridSizer( 0, 2, 0, 0 )
		sizerPos.SetFlexibleDirection( wx.BOTH )
		sizerPos.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.label_x = wx.StaticText( self, wx.ID_ANY, u"x", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.label_x.Wrap( -1 )

		sizerPos.Add( self.label_x, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.spinCtrl_x = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT|wx.SP_ARROW_KEYS, -10000, 10000, 0 )
		sizerPos.Add( self.spinCtrl_x, 0, wx.ALL, 5 )

		self.label_y = wx.StaticText( self, wx.ID_ANY, u"y", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.label_y.Wrap( -1 )

		sizerPos.Add( self.label_y, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.spinCtrl_y = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT|wx.SP_ARROW_KEYS, -10000, 10000, 0 )
		sizerPos.Add( self.spinCtrl_y, 0, wx.ALL, 5 )


		sizerMain.Add( sizerPos, wx.GBPosition( 2, 1 ), wx.GBSpan( 1, 1 ), wx.EXPAND, 5 )

		self.label_colour = wx.StaticText( self, wx.ID_ANY, u"Colour", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.label_colour.Wrap( -1 )

		sizerMain.Add( self.label_colour, wx.GBPosition( 3, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )

		sizerColour = wx.BoxSizer( wx.HORIZONTAL )

		self.checkBox_color = wx.CheckBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		sizerColour.Add( self.checkBox_color, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.colourPicker = wx.ColourPickerCtrl( self, wx.ID_ANY, wx.Colour( 255, 0, 0 ), wx.DefaultPosition, wx.DefaultSize, wx.CLRP_DEFAULT_STYLE )
		self.colourPicker.Enable( False )

		sizerColour.Add( self.colourPicker, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		sizerMain.Add( sizerColour, wx.GBPosition( 3, 1 ), wx.GBSpan( 1, 1 ), wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0 )

		self.m_staticline1 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		sizerMain.Add( self.m_staticline1, wx.GBPosition( 4, 0 ), wx.GBSpan( 1, 2 ), wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 0 )

		dialogButtons = wx.StdDialogButtonSizer()
		self.dialogButtonsOK = wx.Button( self, wx.ID_OK )
		dialogButtons.AddButton( self.dialogButtonsOK )
		self.dialogButtonsCancel = wx.Button( self, wx.ID_CANCEL )
		dialogButtons.AddButton( self.dialogButtonsCancel )
		dialogButtons.Realize();

		sizerMain.Add( dialogButtons, wx.GBPosition( 5, 0 ), wx.GBSpan( 1, 2 ), wx.ALL|wx.EXPAND, 5 )


		sizerMain.AddGrowableCol( 1 )

		self.SetSizer( sizerMain )
		self.Layout()
		sizerMain.Fit( self )

		self.Centre( wx.BOTH )

		# Connect Events
		self.colourPicker.Bind( wx.EVT_UPDATE_UI, self.on_update_colourPicker )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def on_update_colourPicker( self, event ):
		event.Skip()


