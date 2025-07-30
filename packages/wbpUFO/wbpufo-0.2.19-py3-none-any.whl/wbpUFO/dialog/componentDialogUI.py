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
## Class ComponentDialogUI
###########################################################################

class ComponentDialogUI ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Component", pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.CAPTION|wx.CLOSE_BOX|wx.RESIZE_BORDER|wx.STAY_ON_TOP )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		sizerMain = wx.BoxSizer( wx.VERTICAL )

		sizer_name = wx.BoxSizer( wx.HORIZONTAL )

		self.label_name = wx.StaticText( self, wx.ID_ANY, u"Name", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.label_name.Wrap( -1 )

		sizer_name.Add( self.label_name, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.textCtrl_name = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer_name.Add( self.textCtrl_name, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.button_name = wx.Button( self, wx.ID_ANY, u"...", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
		sizer_name.Add( self.button_name, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		sizerMain.Add( sizer_name, 0, wx.ALL|wx.EXPAND, 5 )

		sizerPos = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Position [Unit]" ), wx.HORIZONTAL )

		self.label_pos_x = wx.StaticText( sizerPos.GetStaticBox(), wx.ID_ANY, u"x", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.label_pos_x.Wrap( -1 )

		sizerPos.Add( self.label_pos_x, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.spinCtrl_pos_x = wx.SpinCtrl( sizerPos.GetStaticBox(), wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, -65535, 65535, 0 )
		sizerPos.Add( self.spinCtrl_pos_x, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.label_pos_y = wx.StaticText( sizerPos.GetStaticBox(), wx.ID_ANY, u"y", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.label_pos_y.Wrap( -1 )

		sizerPos.Add( self.label_pos_y, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.spinCtrl_pos_y = wx.SpinCtrl( sizerPos.GetStaticBox(), wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, -65535, 65535, 0 )
		sizerPos.Add( self.spinCtrl_pos_y, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		sizerMain.Add( sizerPos, 0, wx.ALL|wx.EXPAND, 5 )

		sizerScale = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Scale [%]" ), wx.HORIZONTAL )

		self.label_scale_x = wx.StaticText( sizerScale.GetStaticBox(), wx.ID_ANY, u"x", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.label_scale_x.Wrap( -1 )

		sizerScale.Add( self.label_scale_x, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.spinCtrl_scale_x = wx.SpinCtrl( sizerScale.GetStaticBox(), wx.ID_ANY, u"100", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, -1000, 1000, 100 )
		sizerScale.Add( self.spinCtrl_scale_x, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.label_scale_y = wx.StaticText( sizerScale.GetStaticBox(), wx.ID_ANY, u"y", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.label_scale_y.Wrap( -1 )

		sizerScale.Add( self.label_scale_y, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.spinCtrl_scale_y = wx.SpinCtrl( sizerScale.GetStaticBox(), wx.ID_ANY, u"100", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, -1000, 1000, 100 )
		sizerScale.Add( self.spinCtrl_scale_y, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		sizerMain.Add( sizerScale, 0, wx.ALL|wx.EXPAND, 5 )

		sizerDlgButtons = wx.StdDialogButtonSizer()
		self.sizerDlgButtonsOK = wx.Button( self, wx.ID_OK )
		sizerDlgButtons.AddButton( self.sizerDlgButtonsOK )
		self.sizerDlgButtonsCancel = wx.Button( self, wx.ID_CANCEL )
		sizerDlgButtons.AddButton( self.sizerDlgButtonsCancel )
		sizerDlgButtons.Realize();

		sizerMain.Add( sizerDlgButtons, 0, wx.ALL|wx.EXPAND, 5 )


		self.SetSizer( sizerMain )
		self.Layout()
		sizerMain.Fit( self )

		self.Centre( wx.BOTH )

		# Connect Events
		self.button_name.Bind( wx.EVT_BUTTON, self.on_button_name )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def on_button_name( self, event ):
		event.Skip()


