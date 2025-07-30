# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.1-0-g8feb16b3)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

from .fontInfoControl import UnicodeRangeBitList
from .fontInfoBase import FontInfoBasePage
import wx
import wx.xrc

###########################################################################
## Class FontInfoUnicodeUI
###########################################################################

class FontInfoUnicodeUI ( FontInfoBasePage ):

    def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = 0, name = u"FontInfoUnicode" ):
        FontInfoBasePage.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

        self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )

        sizerMain = wx.BoxSizer( wx.VERTICAL )

        boxOS2 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"OpenType OS/2 Table" ), wx.VERTICAL )

        sizerOS2 = wx.GridBagSizer( 0, 0 )
        sizerOS2.SetFlexibleDirection( wx.HORIZONTAL )
        sizerOS2.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.lbl_openTypeOS2UnicodeRanges = wx.StaticText( self, wx.ID_ANY, u"Unicode Ranges", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_openTypeOS2UnicodeRanges.Wrap( -1 )

        self.lbl_openTypeOS2UnicodeRanges.SetMinSize( wx.Size( 170,-1 ) )

        sizerOS2.Add( self.lbl_openTypeOS2UnicodeRanges, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        checkList_openTypeOS2UnicodeRangesChoices = []
        self.checkList_openTypeOS2UnicodeRanges = UnicodeRangeBitList( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, checkList_openTypeOS2UnicodeRangesChoices, wx.LB_EXTENDED|wx.LB_NEEDED_SB, wx.DefaultValidator, u"openTypeOS2UnicodeRanges" )
        sizerOS2.Add( self.checkList_openTypeOS2UnicodeRanges, wx.GBPosition( 0, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )


        sizerOS2.AddGrowableCol( 1 )
        sizerOS2.AddGrowableRow( 0 )

        boxOS2.Add( sizerOS2, 1, wx.EXPAND, 5 )


        sizerMain.Add( boxOS2, 1, wx.ALL|wx.EXPAND, 5 )


        self.SetSizer( sizerMain )
        self.Layout()
        sizerMain.Fit( self )

    def __del__( self ):
        pass


