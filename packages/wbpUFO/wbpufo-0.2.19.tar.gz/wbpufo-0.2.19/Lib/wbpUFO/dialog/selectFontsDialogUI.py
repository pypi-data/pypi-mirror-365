# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.0-4761b0c)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

from ..control import FontSelectListCtrl
import wx
import wx.xrc

###########################################################################
## Class SelectFontsDialogUI
###########################################################################

class SelectFontsDialogUI ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Select Fonts", pos = wx.DefaultPosition, size = wx.Size( 700,300 ), style = wx.CAPTION|wx.RESIZE_BORDER )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		sizer = wx.BoxSizer( wx.VERTICAL )

		self.label_message = wx.StaticText( self, wx.ID_ANY, u"Select Fonts", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_LEFT|wx.ST_ELLIPSIZE_MIDDLE )
		self.label_message.Wrap( -1 )

		sizer.Add( self.label_message, 0, wx.ALL|wx.EXPAND, 10 )

		self.listCtrl_fonts = FontSelectListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT|wx.LC_VIRTUAL )
		sizer.Add( self.listCtrl_fonts, 1, wx.EXPAND, 0 )

		sdbSizer = wx.StdDialogButtonSizer()
		self.sdbSizerOK = wx.Button( self, wx.ID_OK )
		sdbSizer.AddButton( self.sdbSizerOK )
		self.sdbSizerCancel = wx.Button( self, wx.ID_CANCEL )
		sdbSizer.AddButton( self.sdbSizerCancel )
		sdbSizer.Realize();

		sizer.Add( sdbSizer, 0, wx.ALL|wx.EXPAND, 5 )


		self.SetSizer( sizer )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.Bind( wx.EVT_KEY_DOWN, self.on_KEY_DOWN )
		self.listCtrl_fonts.Bind( wx.EVT_KEY_DOWN, self.on_KEY_DOWN )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def on_KEY_DOWN( self, event ):
		event.Skip()



