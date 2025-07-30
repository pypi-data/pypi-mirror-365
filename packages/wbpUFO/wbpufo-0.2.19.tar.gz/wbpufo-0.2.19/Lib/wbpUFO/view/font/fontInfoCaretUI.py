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
## Class FontInfoCaretUI
###########################################################################

class FontInfoCaretUI ( FontInfoBasePage ):

    def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = 0, name = u"FontInfoCaret" ):
        FontInfoBasePage.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

        self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )

        sizerMain = wx.BoxSizer( wx.VERTICAL )

        boxHhea = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"hhea" ), wx.VERTICAL )

        sizerHhea = wx.GridBagSizer( 0, 0 )
        sizerHhea.SetFlexibleDirection( wx.HORIZONTAL )
        sizerHhea.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.lbl_openTypeHheaCaretSlopeRise = wx.StaticText( self, wx.ID_ANY, u"Caret Slope Rise", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_openTypeHheaCaretSlopeRise.Wrap( -1 )

        self.lbl_openTypeHheaCaretSlopeRise.SetMinSize( wx.Size( 170,-1 ) )

        sizerHhea.Add( self.lbl_openTypeHheaCaretSlopeRise, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_openTypeHheaCaretSlopeRise = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeHheaCaretSlopeRise" )
        sizerHhea.Add( self.txtCtrl_openTypeHheaCaretSlopeRise, wx.GBPosition( 0, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.lbl_openTypeHheaCaretSlopeRun = wx.StaticText( self, wx.ID_ANY, u"Caret Slope Run", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_openTypeHheaCaretSlopeRun.Wrap( -1 )

        sizerHhea.Add( self.lbl_openTypeHheaCaretSlopeRun, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_openTypeHheaCaretSlopeRun = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeHheaCaretSlopeRun" )
        sizerHhea.Add( self.txtCtrl_openTypeHheaCaretSlopeRun, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.lbl_openTypeHheaCaretOffset = wx.StaticText( self, wx.ID_ANY, u"Caret Offset", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_openTypeHheaCaretOffset.Wrap( -1 )

        sizerHhea.Add( self.lbl_openTypeHheaCaretOffset, wx.GBPosition( 2, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_openTypeHheaCaretOffset = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeHheaCaretOffset" )
        sizerHhea.Add( self.txtCtrl_openTypeHheaCaretOffset, wx.GBPosition( 2, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        sizerHhea.AddGrowableCol( 1 )

        boxHhea.Add( sizerHhea, 1, wx.EXPAND, 5 )


        sizerMain.Add( boxHhea, 0, wx.ALL|wx.EXPAND, 5 )

        boxVhea = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"vhea" ), wx.VERTICAL )

        sizerVhea = wx.GridBagSizer( 0, 0 )
        sizerVhea.SetFlexibleDirection( wx.HORIZONTAL )
        sizerVhea.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.lbl_openTypeVheaCaretSlopeRise = wx.StaticText( self, wx.ID_ANY, u"Caret Slope Rise", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_openTypeVheaCaretSlopeRise.Wrap( -1 )

        self.lbl_openTypeVheaCaretSlopeRise.SetMinSize( wx.Size( 170,-1 ) )

        sizerVhea.Add( self.lbl_openTypeVheaCaretSlopeRise, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_openTypeVheaCaretSlopeRise = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeVheaCaretSlopeRise" )
        sizerVhea.Add( self.txtCtrl_openTypeVheaCaretSlopeRise, wx.GBPosition( 0, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.lbl_openTypeVheaCaretSlopeRun = wx.StaticText( self, wx.ID_ANY, u"Caret Slope Run", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_openTypeVheaCaretSlopeRun.Wrap( -1 )

        sizerVhea.Add( self.lbl_openTypeVheaCaretSlopeRun, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_openTypeVheaCaretSlopeRun = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeVheaCaretSlopeRun" )
        sizerVhea.Add( self.txtCtrl_openTypeVheaCaretSlopeRun, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.lbl_openTypeVheaCaretOffset = wx.StaticText( self, wx.ID_ANY, u"Caret Offset", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_openTypeVheaCaretOffset.Wrap( -1 )

        sizerVhea.Add( self.lbl_openTypeVheaCaretOffset, wx.GBPosition( 2, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_openTypeVheaCaretOffset = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeVheaCaretOffset" )
        sizerVhea.Add( self.txtCtrl_openTypeVheaCaretOffset, wx.GBPosition( 2, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        sizerVhea.AddGrowableCol( 1 )

        boxVhea.Add( sizerVhea, 1, wx.EXPAND, 5 )


        sizerMain.Add( boxVhea, 0, wx.ALL|wx.EXPAND, 5 )


        self.SetSizer( sizerMain )
        self.Layout()
        sizerMain.Fit( self )

    def __del__( self ):
        pass


