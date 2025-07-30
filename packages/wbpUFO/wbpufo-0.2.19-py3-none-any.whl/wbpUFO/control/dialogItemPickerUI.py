# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Oct 26 2018)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

from .panelItemPicker import PanelItemPicker
import wx
import wx.xrc

###########################################################################
## Class DialogItemPickerUI
###########################################################################

class DialogItemPickerUI ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"ItemPicker", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.CAPTION|wx.CLOSE_BOX|wx.RESIZE_BORDER )

		self.SetSizeHints( wx.Size( 300,280 ), wx.DefaultSize )

		sizer_main = wx.BoxSizer( wx.VERTICAL )

		self.label_message = wx.StaticText( self, wx.ID_ANY, u"Message", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.label_message.Wrap( -1 )

		sizer_main.Add( self.label_message, 0, wx.ALL|wx.EXPAND, 5 )

		self.itemPicker = PanelItemPicker( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		sizer_main.Add( self.itemPicker, 1, wx.EXPAND, 0 )

		sdbSizer = wx.StdDialogButtonSizer()
		self.sdbSizerOK = wx.Button( self, wx.ID_OK )
		sdbSizer.AddButton( self.sdbSizerOK )
		self.sdbSizerCancel = wx.Button( self, wx.ID_CANCEL )
		sdbSizer.AddButton( self.sdbSizerCancel )
		sdbSizer.Realize()

		sizer_main.Add( sdbSizer, 0, wx.ALL|wx.EXPAND, 5 )


		self.SetSizer( sizer_main )
		self.Layout()
		sizer_main.Fit( self )

		self.Centre( wx.BOTH )

	def __del__( self ):
		pass


