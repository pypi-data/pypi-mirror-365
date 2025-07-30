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
## Class DeleteGlyphsDialogUI
###########################################################################

class DeleteGlyphsDialogUI ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Delete Glyphs", pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		sizer = wx.BoxSizer( wx.VERTICAL )

		sizer_message = wx.BoxSizer( wx.HORIZONTAL )

		self.bitmap_warn = wx.StaticBitmap( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_WARNING, wx.ART_MESSAGE_BOX ), wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer_message.Add( self.bitmap_warn, 0, wx.ALL, 5 )

		self.lbl_message = wx.StaticText( self, wx.ID_ANY, u"Delete selected glyphs - No Undo!", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_message.SetLabelMarkup( u"Delete selected glyphs - No Undo!" )
		self.lbl_message.Wrap( -1 )

		self.lbl_message.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )

		sizer_message.Add( self.lbl_message, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


		sizer.Add( sizer_message, 1, wx.EXPAND, 5 )


		sizer.Add( ( 0, 5), 0, 0, 0 )

		self.lbl_question = wx.StaticText( self, wx.ID_ANY, u"If deleted Glyphs are used as Component in other Glyphs", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_question.Wrap( -1 )

		sizer.Add( self.lbl_question, 0, wx.ALL, 5 )

		self.radioBtn_decompose = wx.RadioButton( self, wx.ID_ANY, u"Decompose Component", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.radioBtn_decompose.SetValue( True )
		sizer.Add( self.radioBtn_decompose, 0, wx.ALL|wx.EXPAND, 10 )

		self.radioBtn_remove = wx.RadioButton( self, wx.ID_ANY, u"Remove Component from Composite", wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer.Add( self.radioBtn_remove, 0, wx.ALL|wx.EXPAND, 10 )


		sizer.Add( ( 0, 5), 0, 0, 0 )

		buttonSizer = wx.StdDialogButtonSizer()
		self.buttonSizerOK = wx.Button( self, wx.ID_OK )
		buttonSizer.AddButton( self.buttonSizerOK )
		self.buttonSizerCancel = wx.Button( self, wx.ID_CANCEL )
		buttonSizer.AddButton( self.buttonSizerCancel )
		buttonSizer.Realize();

		sizer.Add( buttonSizer, 1, wx.ALL|wx.EXPAND, 5 )


		self.SetSizer( sizer )
		self.Layout()
		sizer.Fit( self )

		self.Centre( wx.BOTH )

	def __del__( self ):
		pass


