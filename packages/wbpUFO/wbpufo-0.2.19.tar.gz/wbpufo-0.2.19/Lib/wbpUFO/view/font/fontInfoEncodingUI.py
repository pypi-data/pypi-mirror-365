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
## Class FontInfoEncodingUI
###########################################################################

class FontInfoEncodingUI ( FontInfoBasePage ):

    def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = 0, name = u"FontInfoEncoding" ):
        FontInfoBasePage.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

        self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )

        sizerMain = wx.BoxSizer( wx.VERTICAL )

        boxPostScript = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"PostScript" ), wx.VERTICAL )

        sizerPostScript = wx.GridBagSizer( 0, 0 )
        sizerPostScript.SetFlexibleDirection( wx.HORIZONTAL )
        sizerPostScript.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.lbl_postscriptWindowsCharacterSet = wx.StaticText( self, wx.ID_ANY, u"Windows Character Set", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_postscriptWindowsCharacterSet.Wrap( -1 )

        self.lbl_postscriptWindowsCharacterSet.SetMinSize( wx.Size( 170,-1 ) )

        sizerPostScript.Add( self.lbl_postscriptWindowsCharacterSet, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_postscriptWindowsCharacterSet = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"postscriptWindowsCharacterSet" )
        sizerPostScript.Add( self.txtCtrl_postscriptWindowsCharacterSet, wx.GBPosition( 0, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.lbl_postscriptDefaultCharacter = wx.StaticText( self, wx.ID_ANY, u"Default Character", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_postscriptDefaultCharacter.Wrap( -1 )

        sizerPostScript.Add( self.lbl_postscriptDefaultCharacter, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_postscriptDefaultCharacter = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"postscriptDefaultCharacter" )
        sizerPostScript.Add( self.txtCtrl_postscriptDefaultCharacter, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        sizerPostScript.AddGrowableCol( 1 )

        boxPostScript.Add( sizerPostScript, 1, wx.EXPAND, 5 )


        sizerMain.Add( boxPostScript, 0, wx.ALL|wx.EXPAND, 5 )

        boxMac = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Macintosh" ), wx.VERTICAL )

        sizerMac = wx.GridBagSizer( 0, 0 )
        sizerMac.SetFlexibleDirection( wx.HORIZONTAL )
        sizerMac.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.lbl_macintoshFONDFamilyID = wx.StaticText( self, wx.ID_ANY, u"FOND Family ID", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_macintoshFONDFamilyID.Wrap( -1 )

        self.lbl_macintoshFONDFamilyID.SetMinSize( wx.Size( 170,-1 ) )

        sizerMac.Add( self.lbl_macintoshFONDFamilyID, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_macintoshFONDFamilyID = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"macintoshFONDFamilyID" )
        sizerMac.Add( self.txtCtrl_macintoshFONDFamilyID, wx.GBPosition( 0, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        sizerMac.AddGrowableCol( 1 )

        boxMac.Add( sizerMac, 1, wx.EXPAND, 5 )


        sizerMain.Add( boxMac, 0, wx.ALL|wx.EXPAND, 5 )


        self.SetSizer( sizerMain )
        self.Layout()
        sizerMain.Fit( self )

    def __del__( self ):
        pass


