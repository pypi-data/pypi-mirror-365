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
## Class NewFontDialogUI
###########################################################################

class NewFontDialogUI ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New Font", pos = wx.DefaultPosition, size = wx.Size( 300,-1 ), style = wx.CAPTION|wx.RESIZE_BORDER )

		self.SetSizeHints( wx.Size( 200,-1 ), wx.DefaultSize )

		sizer_main = wx.BoxSizer( wx.VERTICAL )

		sizer_form = wx.FlexGridSizer( 0, 2, 0, 0 )
		sizer_form.AddGrowableCol( 1 )
		sizer_form.SetFlexibleDirection( wx.HORIZONTAL )
		sizer_form.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.label_family = wx.StaticText( self, wx.ID_ANY, u"Family Name", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.label_family.Wrap( -1 )

		sizer_form.Add( self.label_family, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.textCtrl_family = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer_form.Add( self.textCtrl_family, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )

		self.label_style = wx.StaticText( self, wx.ID_ANY, u"Style Name", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.label_style.Wrap( -1 )

		sizer_form.Add( self.label_style, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.textCtrl_style = wx.TextCtrl( self, wx.ID_ANY, u"Regular", wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer_form.Add( self.textCtrl_style, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )

		self.label_upm = wx.StaticText( self, wx.ID_ANY, u"UPM-Size", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.label_upm.Wrap( -1 )

		sizer_form.Add( self.label_upm, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.spinCtrl_upm = wx.SpinCtrl( self, wx.ID_ANY, u"1000", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 10000, 1000 )
		sizer_form.Add( self.spinCtrl_upm, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		sizer_main.Add( sizer_form, 1, wx.EXPAND, 5 )

		sizer_dialog = wx.StdDialogButtonSizer()
		self.sizer_dialogOK = wx.Button( self, wx.ID_OK )
		sizer_dialog.AddButton( self.sizer_dialogOK )
		self.sizer_dialogCancel = wx.Button( self, wx.ID_CANCEL )
		sizer_dialog.AddButton( self.sizer_dialogCancel )
		sizer_dialog.Realize();

		sizer_main.Add( sizer_dialog, 0, wx.ALL|wx.EXPAND, 5 )


		self.SetSizer( sizer_main )
		self.Layout()

		self.Centre( wx.BOTH )

	def __del__( self ):
		pass


