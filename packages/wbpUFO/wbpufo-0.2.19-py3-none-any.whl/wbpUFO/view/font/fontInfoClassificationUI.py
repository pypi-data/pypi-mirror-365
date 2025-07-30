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
## Class FontInfoClassificationUI
###########################################################################

class FontInfoClassificationUI ( FontInfoBasePage ):

    def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = 0, name = u"FontInfoClassification" ):
        FontInfoBasePage.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

        self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )

        sizerMain = wx.BoxSizer( wx.VERTICAL )

        boxPostScript = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"PostScript" ), wx.VERTICAL )

        sizerPostScript = wx.GridBagSizer( 0, 0 )
        sizerPostScript.SetFlexibleDirection( wx.HORIZONTAL )
        sizerPostScript.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.lbl_postscriptIsFixedPitch = wx.StaticText( self, wx.ID_ANY, u"Fixed Pitch", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_postscriptIsFixedPitch.Wrap( -1 )

        self.lbl_postscriptIsFixedPitch.SetMinSize( wx.Size( 170,-1 ) )

        sizerPostScript.Add( self.lbl_postscriptIsFixedPitch, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.checkBox_postscriptIsFixedPitch = wx.CheckBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"postscriptIsFixedPitch" )
        sizerPostScript.Add( self.checkBox_postscriptIsFixedPitch, wx.GBPosition( 0, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )


        sizerPostScript.AddGrowableCol( 1 )

        boxPostScript.Add( sizerPostScript, 1, wx.EXPAND, 5 )


        sizerMain.Add( boxPostScript, 0, wx.ALL|wx.EXPAND, 5 )

        boxOS2 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"OpenType OS/2 Table" ), wx.VERTICAL )

        sizerOS2 = wx.GridBagSizer( 0, 0 )
        sizerOS2.SetFlexibleDirection( wx.HORIZONTAL )
        sizerOS2.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.lbl_openTypeOS2WidthClass = wx.StaticText( self, wx.ID_ANY, u"Width Class", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_openTypeOS2WidthClass.Wrap( -1 )

        self.lbl_openTypeOS2WidthClass.SetMinSize( wx.Size( 170,-1 ) )

        sizerOS2.Add( self.lbl_openTypeOS2WidthClass, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_openTypeOS2WidthClass = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeOS2WidthClass" )
        sizerOS2.Add( self.txtCtrl_openTypeOS2WidthClass, wx.GBPosition( 0, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.lbl_openTypeOS2WeightClass = wx.StaticText( self, wx.ID_ANY, u"Weight Class", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_openTypeOS2WeightClass.Wrap( -1 )

        sizerOS2.Add( self.lbl_openTypeOS2WeightClass, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_openTypeOS2WeightClass = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeOS2WeightClass" )
        sizerOS2.Add( self.txtCtrl_openTypeOS2WeightClass, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )


        sizerOS2.AddGrowableCol( 1 )

        boxOS2.Add( sizerOS2, 1, wx.EXPAND, 5 )


        sizerMain.Add( boxOS2, 0, wx.ALL|wx.EXPAND, 5 )


        self.SetSizer( sizerMain )
        self.Layout()
        sizerMain.Fit( self )

    def __del__( self ):
        pass


