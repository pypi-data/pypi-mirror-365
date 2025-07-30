# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.1-0-g8feb16b3)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

from .fontInfoBase import FontInfoBasePage
import wx
import wx.xrc

###########################################################################
## Class FontInfoNoteUI
###########################################################################

class FontInfoNoteUI ( FontInfoBasePage ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = 0, name = u"FontInfoNote" ):
		FontInfoBasePage.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		self.SetBackgroundColour( wx.Colour( 255, 255, 255 ) )

		sizerMain = wx.GridBagSizer( 0, 0 )
		sizerMain.SetFlexibleDirection( wx.BOTH )
		sizerMain.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.lbl_note = wx.StaticText( self, wx.ID_ANY, u"Note", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_note.Wrap( -1 )

		self.lbl_note.SetMinSize( wx.Size( 170,-1 ) )

		sizerMain.Add( self.lbl_note, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

		self.txtCtrl_note = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE, wx.DefaultValidator, u"note" )
		sizerMain.Add( self.txtCtrl_note, wx.GBPosition( 0, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )


		sizerMain.AddGrowableCol( 1 )
		sizerMain.AddGrowableRow( 0 )

		self.SetSizer( sizerMain )
		self.Layout()
		sizerMain.Fit( self )

	def __del__( self ):
		pass


