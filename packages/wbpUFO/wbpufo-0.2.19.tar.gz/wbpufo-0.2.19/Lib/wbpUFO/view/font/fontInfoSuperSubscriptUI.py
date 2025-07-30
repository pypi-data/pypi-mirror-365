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
## Class FontInfoSuperSubscriptUI
###########################################################################

class FontInfoSuperSubscriptUI ( FontInfoBasePage ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = 0, name = u"FontInfoSuperSubscript" ):
		FontInfoBasePage.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )

		sizerMain = wx.BoxSizer( wx.VERTICAL )

		sizerTop = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Superscript" ), wx.VERTICAL )

		sizerSuperscript = wx.GridBagSizer( 0, 0 )
		sizerSuperscript.SetFlexibleDirection( wx.HORIZONTAL )
		sizerSuperscript.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.lbl_openTypeOS2SuperscriptXOffset = wx.StaticText( self, wx.ID_ANY, u"x-Offset", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_openTypeOS2SuperscriptXOffset.Wrap( -1 )

		self.lbl_openTypeOS2SuperscriptXOffset.SetMinSize( wx.Size( 170,-1 ) )

		sizerSuperscript.Add( self.lbl_openTypeOS2SuperscriptXOffset, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.txtCtrl_openTypeOS2SuperscriptXOffset = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeOS2SuperscriptXOffset" )
		sizerSuperscript.Add( self.txtCtrl_openTypeOS2SuperscriptXOffset, wx.GBPosition( 0, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.lbl_openTypeOS2SuperscriptXSize = wx.StaticText( self, wx.ID_ANY, u"x-Size", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_openTypeOS2SuperscriptXSize.Wrap( -1 )

		sizerSuperscript.Add( self.lbl_openTypeOS2SuperscriptXSize, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.txtCtrl_openTypeOS2SuperscriptXSize = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeOS2SuperscriptXSize" )
		sizerSuperscript.Add( self.txtCtrl_openTypeOS2SuperscriptXSize, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.lbl_openTypeOS2SuperscriptYOffset = wx.StaticText( self, wx.ID_ANY, u"y-Offset", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_openTypeOS2SuperscriptYOffset.Wrap( -1 )

		sizerSuperscript.Add( self.lbl_openTypeOS2SuperscriptYOffset, wx.GBPosition( 2, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.txtCtrl_openTypeOS2SuperscriptYOffset = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeOS2SuperscriptYOffset" )
		sizerSuperscript.Add( self.txtCtrl_openTypeOS2SuperscriptYOffset, wx.GBPosition( 2, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.lbl_openTypeOS2SuperscriptYSize = wx.StaticText( self, wx.ID_ANY, u"y-Size", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_openTypeOS2SuperscriptYSize.Wrap( -1 )

		sizerSuperscript.Add( self.lbl_openTypeOS2SuperscriptYSize, wx.GBPosition( 3, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.txtCtrl_openTypeOS2SuperscriptYSize = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeOS2SuperscriptYSize" )
		sizerSuperscript.Add( self.txtCtrl_openTypeOS2SuperscriptYSize, wx.GBPosition( 3, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		sizerSuperscript.AddGrowableCol( 1 )

		sizerTop.Add( sizerSuperscript, 1, wx.EXPAND, 5 )


		sizerMain.Add( sizerTop, 0, wx.ALL|wx.EXPAND, 5 )

		sizerBottom = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Subscript" ), wx.VERTICAL )

		sizerSubscript = wx.GridBagSizer( 0, 0 )
		sizerSubscript.SetFlexibleDirection( wx.HORIZONTAL )
		sizerSubscript.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.lbl_openTypeOS2SubscriptXOffset = wx.StaticText( self, wx.ID_ANY, u"x-Offset", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_openTypeOS2SubscriptXOffset.Wrap( -1 )

		self.lbl_openTypeOS2SubscriptXOffset.SetMinSize( wx.Size( 170,-1 ) )

		sizerSubscript.Add( self.lbl_openTypeOS2SubscriptXOffset, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.txtCtrl_openTypeOS2SubscriptXOffset = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeOS2SubscriptXOffset" )
		sizerSubscript.Add( self.txtCtrl_openTypeOS2SubscriptXOffset, wx.GBPosition( 0, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.lbl_openTypeOS2SubscriptXSize = wx.StaticText( self, wx.ID_ANY, u"x-Size", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_openTypeOS2SubscriptXSize.Wrap( -1 )

		sizerSubscript.Add( self.lbl_openTypeOS2SubscriptXSize, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.txtCtrl_openTypeOS2SubscriptXSize = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeOS2SubscriptXSize" )
		sizerSubscript.Add( self.txtCtrl_openTypeOS2SubscriptXSize, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

		self.lbl_openTypeOS2SubscriptYOffset = wx.StaticText( self, wx.ID_ANY, u"y-Offset", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_openTypeOS2SubscriptYOffset.Wrap( -1 )

		sizerSubscript.Add( self.lbl_openTypeOS2SubscriptYOffset, wx.GBPosition( 2, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.txtCtrl_openTypeOS2SubscriptYOffset = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeOS2SubscriptYOffset" )
		sizerSubscript.Add( self.txtCtrl_openTypeOS2SubscriptYOffset, wx.GBPosition( 2, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.lbl_openTypeOS2SubscriptYSize = wx.StaticText( self, wx.ID_ANY, u"y-Size", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_openTypeOS2SubscriptYSize.Wrap( -1 )

		sizerSubscript.Add( self.lbl_openTypeOS2SubscriptYSize, wx.GBPosition( 3, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.txtCtrl_openTypeOS2SubscriptYSize = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeOS2SubscriptYSize" )
		sizerSubscript.Add( self.txtCtrl_openTypeOS2SubscriptYSize, wx.GBPosition( 3, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )


		sizerSubscript.AddGrowableCol( 1 )

		sizerBottom.Add( sizerSubscript, 1, wx.EXPAND, 5 )


		sizerMain.Add( sizerBottom, 0, wx.ALL|wx.EXPAND, 5 )


		self.SetSizer( sizerMain )
		self.Layout()
		sizerMain.Fit( self )

	def __del__( self ):
		pass


