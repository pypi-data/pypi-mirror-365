# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.1-0-g8feb16b3)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class GlyphGridStatusPanelUI
###########################################################################

class GlyphGridStatusPanelUI ( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = 0, name = u"GlyphGridStatusPanel" ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		self.SetFont( wx.Font( 8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )
		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_3DLIGHT ) )

		sizer = wx.BoxSizer( wx.HORIZONTAL )

		self.button_fontinfo = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )

		self.button_fontinfo.SetBitmap( wx.ArtProvider.GetBitmap( "VIEW_INFO", wx.ART_BUTTON ) )
		self.button_fontinfo.SetToolTip( u"Open Font Info" )

		sizer.Add( self.button_fontinfo, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		sizer.Add( ( 0, 0), 1, wx.EXPAND, 0 )

		self.searchCtrl = wx.SearchCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_NOHIDESEL )
		self.searchCtrl.ShowSearchButton( True )
		self.searchCtrl.ShowCancelButton( True )
		self.searchCtrl.SetMinSize( wx.Size( 100,-1 ) )
		self.searchCtrl.SetMaxSize( wx.Size( 250,-1 ) )

		sizer.Add( self.searchCtrl, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.text_glyph = wx.StaticText( self, wx.ID_ANY, u"Glyph", wx.DefaultPosition, wx.Size( -1,-1 ), 0 )
		self.text_glyph.Wrap( -1 )

		sizer.Add( self.text_glyph, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2 )

		self.text_current = wx.StaticText( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 150,-1 ), wx.ST_ELLIPSIZE_MIDDLE|wx.BORDER_THEME )
		self.text_current.Wrap( -1 )

		sizer.Add( self.text_current, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2 )

		self.text_uni = wx.StaticText( self, wx.ID_ANY, u"Unicode", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.text_uni.Wrap( -1 )

		sizer.Add( self.text_uni, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2 )

		self.text_unicodes = wx.StaticText( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 100,-1 ), wx.ST_ELLIPSIZE_MIDDLE|wx.BORDER_THEME )
		self.text_unicodes.Wrap( -1 )

		sizer.Add( self.text_unicodes, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2 )

		self.text_selected = wx.StaticText( self, wx.ID_ANY, u"Selected", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.text_selected.Wrap( -1 )

		sizer.Add( self.text_selected, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2 )

		self.text_selected_count = wx.StaticText( self, wx.ID_ANY, u"0", wx.DefaultPosition, wx.Size( 35,-1 ), wx.ALIGN_RIGHT|wx.BORDER_THEME )
		self.text_selected_count.Wrap( -1 )

		sizer.Add( self.text_selected_count, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2 )

		self.text_of = wx.StaticText( self, wx.ID_ANY, u"/", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.text_of.Wrap( -1 )

		sizer.Add( self.text_of, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2 )

		self.text_total_count = wx.StaticText( self, wx.ID_ANY, u"0", wx.DefaultPosition, wx.Size( 35,-1 ), wx.ALIGN_RIGHT|wx.BORDER_THEME )
		self.text_total_count.Wrap( -1 )

		sizer.Add( self.text_total_count, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2 )


		self.SetSizer( sizer )
		self.Layout()
		sizer.Fit( self )

		# Connect Events
		self.button_fontinfo.Bind( wx.EVT_BUTTON, self.on_button_fontinfo )
		self.searchCtrl.Bind( wx.EVT_SEARCHCTRL_CANCEL_BTN, self.onSearchCancel )
		self.searchCtrl.Bind( wx.EVT_TEXT, self.onSearchText )
		self.text_current.Bind( wx.EVT_UPDATE_UI, self.update_current )
		self.text_unicodes.Bind( wx.EVT_UPDATE_UI, self.update_unicodes )
		self.text_selected_count.Bind( wx.EVT_UPDATE_UI, self.update_selected_count )
		self.text_total_count.Bind( wx.EVT_UPDATE_UI, self.update_total_count )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def on_button_fontinfo( self, event ):
		event.Skip()

	def onSearchCancel( self, event ):
		event.Skip()

	def onSearchText( self, event ):
		event.Skip()

	def update_current( self, event ):
		event.Skip()

	def update_unicodes( self, event ):
		event.Skip()

	def update_selected_count( self, event ):
		event.Skip()

	def update_total_count( self, event ):
		event.Skip()


