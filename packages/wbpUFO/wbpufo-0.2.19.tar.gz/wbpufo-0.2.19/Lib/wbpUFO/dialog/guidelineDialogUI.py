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
## Class GuidelineDialogUI
###########################################################################

class GuidelineDialogUI ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Guideline", pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.CAPTION|wx.RESIZE_BORDER )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		sizerMain = wx.GridBagSizer( 0, 0 )
		sizerMain.SetFlexibleDirection( wx.VERTICAL )
		sizerMain.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.message = wx.StaticText( self, wx.ID_ANY, u"Edit Guideline", wx.DefaultPosition, wx.DefaultSize, wx.ST_NO_AUTORESIZE|wx.ALIGN_CENTER_HORIZONTAL )
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

		sizerPos = wx.FlexGridSizer( 2, 2, 0, 0 )
		sizerPos.AddGrowableCol( 1 )
		sizerPos.SetFlexibleDirection( wx.BOTH )
		sizerPos.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.label_x = wx.StaticText( self, wx.ID_ANY, u"x", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.label_x.Wrap( -1 )

		sizerPos.Add( self.label_x, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.spinCtrl_x = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT|wx.SP_ARROW_KEYS, -10000, 10000, 0 )
		self.spinCtrl_x.SetMinSize( wx.Size( 100,-1 ) )

		sizerPos.Add( self.spinCtrl_x, 0, wx.ALL|wx.ALIGN_RIGHT|wx.EXPAND, 5 )

		self.label_y = wx.StaticText( self, wx.ID_ANY, u"y", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.label_y.Wrap( -1 )

		sizerPos.Add( self.label_y, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.spinCtrl_y = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT|wx.SP_ARROW_KEYS, -10000, 10000, 0 )
		self.spinCtrl_y.SetMinSize( wx.Size( 100,-1 ) )

		sizerPos.Add( self.spinCtrl_y, 0, wx.ALL|wx.ALIGN_RIGHT|wx.EXPAND, 5 )


		sizerMain.Add( sizerPos, wx.GBPosition( 2, 1 ), wx.GBSpan( 1, 1 ), wx.EXPAND, 5 )

		self.label_angle = wx.StaticText( self, wx.ID_ANY, u"Angle", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.label_angle.Wrap( -1 )

		sizerMain.Add( self.label_angle, wx.GBPosition( 3, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.spinCtrlDouble_angle = wx.SpinCtrlDouble( self, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT|wx.SP_ARROW_KEYS, -360, 360, 0, 1 )
		self.spinCtrlDouble_angle.SetDigits( 1 )
		self.spinCtrlDouble_angle.SetMinSize( wx.Size( 100,-1 ) )

		sizerMain.Add( self.spinCtrlDouble_angle, wx.GBPosition( 3, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )

		self.label_colour = wx.StaticText( self, wx.ID_ANY, u"Colour", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.label_colour.Wrap( -1 )

		sizerMain.Add( self.label_colour, wx.GBPosition( 4, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )

		sizerColour = wx.BoxSizer( wx.HORIZONTAL )

		self.checkBox_color = wx.CheckBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		sizerColour.Add( self.checkBox_color, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.colourPicker = wx.ColourPickerCtrl( self, wx.ID_ANY, wx.Colour( 255, 0, 0 ), wx.DefaultPosition, wx.DefaultSize, wx.CLRP_DEFAULT_STYLE )
		self.colourPicker.Enable( False )
		self.colourPicker.SetMinSize( wx.Size( 100,-1 ) )

		sizerColour.Add( self.colourPicker, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		sizerMain.Add( sizerColour, wx.GBPosition( 4, 1 ), wx.GBSpan( 1, 1 ), wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 0 )

		self.m_staticline1 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		sizerMain.Add( self.m_staticline1, wx.GBPosition( 5, 0 ), wx.GBSpan( 1, 2 ), wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 0 )

		dialogButtons = wx.StdDialogButtonSizer()
		self.dialogButtonsOK = wx.Button( self, wx.ID_OK )
		dialogButtons.AddButton( self.dialogButtonsOK )
		self.dialogButtonsCancel = wx.Button( self, wx.ID_CANCEL )
		dialogButtons.AddButton( self.dialogButtonsCancel )
		dialogButtons.Realize();

		sizerMain.Add( dialogButtons, wx.GBPosition( 6, 0 ), wx.GBSpan( 1, 2 ), wx.ALL|wx.EXPAND, 5 )


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


