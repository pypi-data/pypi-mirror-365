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
## Class NewGlyphDialogUI
###########################################################################

class NewGlyphDialogUI ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New Glyph", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.CAPTION|wx.RESIZE_BORDER )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		sizer = wx.BoxSizer( wx.VERTICAL )

		sizerForm = wx.FlexGridSizer( 0, 2, 0, 0 )
		sizerForm.AddGrowableCol( 1 )
		sizerForm.SetFlexibleDirection( wx.BOTH )
		sizerForm.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.label_name = wx.StaticText( self, wx.ID_ANY, u"Name", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.label_name.Wrap( -1 )

		sizerForm.Add( self.label_name, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.textCtrl_name = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		sizerForm.Add( self.textCtrl_name, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )

		self.label_unicode = wx.StaticText( self, wx.ID_ANY, u"Unicode", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.label_unicode.Wrap( -1 )

		sizerForm.Add( self.label_unicode, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.textCtrl_unicode = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		sizerForm.Add( self.textCtrl_unicode, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )


		sizer.Add( sizerForm, 1, wx.EXPAND, 5 )

		sizerButtons = wx.StdDialogButtonSizer()
		self.sizerButtonsOK = wx.Button( self, wx.ID_OK )
		sizerButtons.AddButton( self.sizerButtonsOK )
		self.sizerButtonsCancel = wx.Button( self, wx.ID_CANCEL )
		sizerButtons.AddButton( self.sizerButtonsCancel )
		sizerButtons.Realize();

		sizer.Add( sizerButtons, 0, wx.ALL|wx.EXPAND, 5 )


		self.SetSizer( sizer )
		self.Layout()
		sizer.Fit( self )

		self.Centre( wx.BOTH )

	def __del__( self ):
		pass


