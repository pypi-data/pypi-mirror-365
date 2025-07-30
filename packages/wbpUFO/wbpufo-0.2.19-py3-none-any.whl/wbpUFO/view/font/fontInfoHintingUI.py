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
import wx.grid

###########################################################################
## Class FontInfoHintingUI
###########################################################################

class FontInfoHintingUI ( FontInfoBasePage ):

    def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = 0, name = u"FontInfoHinting" ):
        FontInfoBasePage.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

        self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )

        sizerMain = wx.BoxSizer( wx.VERTICAL )

        boxHead = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"OpenType head Table" ), wx.VERTICAL )

        sizerHead = wx.GridBagSizer( 0, 0 )
        sizerHead.SetFlexibleDirection( wx.HORIZONTAL )
        sizerHead.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.lbl_openTypeHeadLowestRecPPEM = wx.StaticText( self, wx.ID_ANY, u"Lowest Rec PPEM", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_openTypeHeadLowestRecPPEM.Wrap( -1 )

        self.lbl_openTypeHeadLowestRecPPEM.SetMinSize( wx.Size( 170,-1 ) )

        sizerHead.Add( self.lbl_openTypeHeadLowestRecPPEM, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_openTypeHeadLowestRecPPEM = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeHeadLowestRecPPEM" )
        sizerHead.Add( self.txtCtrl_openTypeHeadLowestRecPPEM, wx.GBPosition( 0, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.lbl_openTypeHeadFlags = wx.StaticText( self, wx.ID_ANY, u"Head Flags", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_openTypeHeadFlags.Wrap( -1 )

        sizerHead.Add( self.lbl_openTypeHeadFlags, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.checkBox_openTypeHeadFlags_0 = wx.CheckBox( self, wx.ID_ANY, u"Baseline for font at y=0", wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeHeadFlags 0" )
        sizerHead.Add( self.checkBox_openTypeHeadFlags_0, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.checkBox_openTypeHeadFlags_1 = wx.CheckBox( self, wx.ID_ANY, u"Left sidebearing point at x=0", wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeHeadFlags 1" )
        sizerHead.Add( self.checkBox_openTypeHeadFlags_1, wx.GBPosition( 2, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.checkBox_openTypeHeadFlags_2 = wx.CheckBox( self, wx.ID_ANY, u"Instructions may depend on point size", wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeHeadFlags 2" )
        sizerHead.Add( self.checkBox_openTypeHeadFlags_2, wx.GBPosition( 3, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.checkBox_openTypeHeadFlags_3 = wx.CheckBox( self, wx.ID_ANY, u"Force ppem to integer values for all internal scaler math", wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeHeadFlags 3" )
        sizerHead.Add( self.checkBox_openTypeHeadFlags_3, wx.GBPosition( 4, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.checkBox_openTypeHeadFlags_4 = wx.CheckBox( self, wx.ID_ANY, u"Instructions may alter advance width", wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeHeadFlags 4" )
        sizerHead.Add( self.checkBox_openTypeHeadFlags_4, wx.GBPosition( 5, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.checkBox_openTypeHeadFlags_11 = wx.CheckBox( self, wx.ID_ANY, u"Font data is “lossless”", wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeHeadFlags 11" )
        sizerHead.Add( self.checkBox_openTypeHeadFlags_11, wx.GBPosition( 6, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.checkBox_openTypeHeadFlags_12 = wx.CheckBox( self, wx.ID_ANY, u"Font converted (produce compatible metrics)", wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeHeadFlags 12" )
        sizerHead.Add( self.checkBox_openTypeHeadFlags_12, wx.GBPosition( 7, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.checkBox_openTypeHeadFlags_13 = wx.CheckBox( self, wx.ID_ANY, u"Font optimized for ClearType", wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeHeadFlags 13" )
        sizerHead.Add( self.checkBox_openTypeHeadFlags_13, wx.GBPosition( 8, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )


        sizerHead.AddGrowableCol( 1 )

        boxHead.Add( sizerHead, 1, wx.EXPAND, 5 )


        sizerMain.Add( boxHead, 0, wx.ALL|wx.EXPAND, 5 )

        boxGasp = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"OpenType gasp Table" ), wx.VERTICAL )

        self.grid_gasp = wx.grid.Grid( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0, u"openTypeGaspRangeRecords" )

        # Grid
        self.grid_gasp.CreateGrid( 0, 5 )
        self.grid_gasp.EnableEditing( True )
        self.grid_gasp.EnableGridLines( True )
        self.grid_gasp.EnableDragGridSize( False )
        self.grid_gasp.SetMargins( 0, 0 )

        # Columns
        self.grid_gasp.SetColSize( 0, 100 )
        self.grid_gasp.SetColSize( 1, 100 )
        self.grid_gasp.SetColSize( 2, 100 )
        self.grid_gasp.SetColSize( 3, 100 )
        self.grid_gasp.SetColSize( 4, 100 )
        self.grid_gasp.EnableDragColMove( False )
        self.grid_gasp.EnableDragColSize( True )
        self.grid_gasp.SetColLabelValue( 0, u"Range" )
        self.grid_gasp.SetColLabelValue( 1, u"Gritfit" )
        self.grid_gasp.SetColLabelValue( 2, u"Grayscale" )
        self.grid_gasp.SetColLabelValue( 3, u"Sym. Smoothing" )
        self.grid_gasp.SetColLabelValue( 4, u"Sym. Gritfit" )
        self.grid_gasp.SetColLabelSize( 20 )
        self.grid_gasp.SetColLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )

        # Rows
        self.grid_gasp.EnableDragRowSize( False )
        self.grid_gasp.SetRowLabelSize( 1 )
        self.grid_gasp.SetRowLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )

        # Label Appearance

        # Cell Defaults
        self.grid_gasp.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
        boxGasp.Add( self.grid_gasp, 1, wx.ALL|wx.EXPAND, 5 )


        sizerMain.Add( boxGasp, 1, wx.ALL|wx.EXPAND, 5 )


        self.SetSizer( sizerMain )
        self.Layout()
        sizerMain.Fit( self )

    def __del__( self ):
        pass


