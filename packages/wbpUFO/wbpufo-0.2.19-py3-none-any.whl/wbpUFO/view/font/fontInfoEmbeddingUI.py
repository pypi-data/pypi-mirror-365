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
## Class FontInfoEmbeddingUI
###########################################################################

class FontInfoEmbeddingUI ( FontInfoBasePage ):

    def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = 0, name = u"FontInfoEmbedding" ):
        FontInfoBasePage.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

        self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )

        sizerMain = wx.BoxSizer( wx.VERTICAL )

        boxEmbedding = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Embedding" ), wx.VERTICAL )

        sizerEmbedding = wx.GridBagSizer( 0, 0 )
        sizerEmbedding.SetFlexibleDirection( wx.HORIZONTAL )
        sizerEmbedding.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.lbl_openTypeOS2Type = wx.StaticText( self, wx.ID_ANY, u"Main", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_openTypeOS2Type.Wrap( -1 )

        self.lbl_openTypeOS2Type.SetMinSize( wx.Size( 170,-1 ) )

        sizerEmbedding.Add( self.lbl_openTypeOS2Type, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_radioBtn2 = wx.RadioButton( self, wx.ID_ANY, u"No Embedding", wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeOS2Type 2" )
        sizerEmbedding.Add( self.m_radioBtn2, wx.GBPosition( 0, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.radioBtn_openTypeOS2Type3 = wx.RadioButton( self, wx.ID_ANY, u"Print and Preview Embedding", wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeOS2Type 4" )
        sizerEmbedding.Add( self.radioBtn_openTypeOS2Type3, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_radioBtn4 = wx.RadioButton( self, wx.ID_ANY, u"Editable Embedding", wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeOS2Type 8" )
        sizerEmbedding.Add( self.m_radioBtn4, wx.GBPosition( 2, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_radioBtn5 = wx.RadioButton( self, wx.ID_ANY, u"Installable Embedding", wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeOS2Type 0" )
        sizerEmbedding.Add( self.m_radioBtn5, wx.GBPosition( 3, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.lbl_postscriptUnderlineThickness = wx.StaticText( self, wx.ID_ANY, u"Options", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_postscriptUnderlineThickness.Wrap( -1 )

        sizerEmbedding.Add( self.lbl_postscriptUnderlineThickness, wx.GBPosition( 4, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.checkBox_openTypeOS2Type_8 = wx.CheckBox( self, wx.ID_ANY, u"No Subsetting", wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeOS2Type 8" )
        sizerEmbedding.Add( self.checkBox_openTypeOS2Type_8, wx.GBPosition( 4, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.checkBox_openTypeOS2Type_9 = wx.CheckBox( self, wx.ID_ANY, u"Bitmap Embedding Only", wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeOS2Type 9" )
        sizerEmbedding.Add( self.checkBox_openTypeOS2Type_9, wx.GBPosition( 5, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )


        sizerEmbedding.AddGrowableCol( 1 )

        boxEmbedding.Add( sizerEmbedding, 1, wx.EXPAND, 5 )


        sizerMain.Add( boxEmbedding, 0, wx.ALL|wx.EXPAND, 5 )


        self.SetSizer( sizerMain )
        self.Layout()
        sizerMain.Fit( self )

    def __del__( self ):
        pass


