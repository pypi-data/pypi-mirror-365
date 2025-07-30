# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.1-0-g8feb16b3)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

from .hintPSpanel import StemPanel
from .hintPSpanel import ZonePanel
from .fontInfoBase import FontInfoBasePage
import wx
import wx.xrc

###########################################################################
## Class FontInfoHintingPSUI
###########################################################################

class FontInfoHintingPSUI ( FontInfoBasePage ):

    def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 416,486 ), style = 0, name = u"FontInfoHintingPS" ):
        FontInfoBasePage.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

        self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )

        sizer = wx.BoxSizer( wx.VERTICAL )

        boxMain = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Main" ), wx.VERTICAL )

        sizerMain = wx.GridBagSizer( 0, 0 )
        sizerMain.SetFlexibleDirection( wx.HORIZONTAL )
        sizerMain.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.lbl_postscriptBlueFuzz = wx.StaticText( self, wx.ID_ANY, u"Blue Fuzz", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_postscriptBlueFuzz.Wrap( -1 )

        self.lbl_postscriptBlueFuzz.SetMinSize( wx.Size( 170,-1 ) )

        sizerMain.Add( self.lbl_postscriptBlueFuzz, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_postscriptBlueFuzz = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"postscriptBlueFuzz" )
        sizerMain.Add( self.txtCtrl_postscriptBlueFuzz, wx.GBPosition( 0, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.lbl_postscriptBlueShift = wx.StaticText( self, wx.ID_ANY, u"Blue Shift", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_postscriptBlueShift.Wrap( -1 )

        sizerMain.Add( self.lbl_postscriptBlueShift, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_postscriptBlueShift = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"postscriptBlueShift" )
        sizerMain.Add( self.txtCtrl_postscriptBlueShift, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.lbl_postscriptBlueScale = wx.StaticText( self, wx.ID_ANY, u"Blue Scale", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_postscriptBlueScale.Wrap( -1 )

        sizerMain.Add( self.lbl_postscriptBlueScale, wx.GBPosition( 2, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_postscriptBlueScale = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"postscriptBlueScale" )
        sizerMain.Add( self.txtCtrl_postscriptBlueScale, wx.GBPosition( 2, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.lbl_postscriptForceBold = wx.StaticText( self, wx.ID_ANY, u"Force Bold", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_postscriptForceBold.Wrap( -1 )

        sizerMain.Add( self.lbl_postscriptForceBold, wx.GBPosition( 3, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.checkBox_postscriptForceBold = wx.CheckBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"postscriptForceBold" )
        sizerMain.Add( self.checkBox_postscriptForceBold, wx.GBPosition( 3, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        sizerMain.AddGrowableCol( 1 )

        boxMain.Add( sizerMain, 1, wx.EXPAND, 5 )


        sizer.Add( boxMain, 0, wx.ALL|wx.EXPAND, 5 )

        boxStems = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Stems" ), wx.VERTICAL )

        sizerStems = wx.GridBagSizer( 0, 0 )
        sizerStems.SetFlexibleDirection( wx.BOTH )
        sizerStems.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )


        sizerStems.Add( ( 170, 0 ), wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.lbl_postscriptStemSnapH = wx.StaticText( self, wx.ID_ANY, u"Horizontal Stems", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_postscriptStemSnapH.Wrap( -1 )

        self.lbl_postscriptStemSnapH.SetMinSize( wx.Size( 170,-1 ) )

        sizerStems.Add( self.lbl_postscriptStemSnapH, wx.GBPosition( 0, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.lbl_postscriptStemSnapV = wx.StaticText( self, wx.ID_ANY, u"Vertical Stems", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_postscriptStemSnapV.Wrap( -1 )

        sizerStems.Add( self.lbl_postscriptStemSnapV, wx.GBPosition( 0, 2 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.m_button3 = wx.Button( self, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_button3.SetMinSize( wx.Size( 160,40 ) )

        sizerStems.Add( self.m_button3, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.panel_postscriptStemSnapH = StemPanel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL, u"postscriptStemSnapH" )
        sizerStems.Add( self.panel_postscriptStemSnapH, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.panel_postscriptStemSnapV = StemPanel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL, u"postscriptStemSnapV" )
        sizerStems.Add( self.panel_postscriptStemSnapV, wx.GBPosition( 1, 2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )


        boxStems.Add( sizerStems, 1, wx.EXPAND, 5 )


        sizer.Add( boxStems, 0, wx.ALL|wx.EXPAND, 5 )

        boxZones = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Allignment Zones" ), wx.VERTICAL )

        gridZones = wx.GridBagSizer( 0, 0 )
        gridZones.SetFlexibleDirection( wx.BOTH )
        gridZones.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.lbl_localZones = wx.StaticText( self, wx.ID_ANY, u"Local Zones", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_localZones.Wrap( -1 )

        self.lbl_localZones.SetMinSize( wx.Size( 170,-1 ) )

        gridZones.Add( self.lbl_localZones, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.lbl_postscriptBlueValues = wx.StaticText( self, wx.ID_ANY, u"Blue Values", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_postscriptBlueValues.Wrap( -1 )

        self.lbl_postscriptBlueValues.SetMinSize( wx.Size( 170,-1 ) )

        gridZones.Add( self.lbl_postscriptBlueValues, wx.GBPosition( 0, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.lbl_postscriptOtherBlues = wx.StaticText( self, wx.ID_ANY, u"Other Blues", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_postscriptOtherBlues.Wrap( -1 )

        gridZones.Add( self.lbl_postscriptOtherBlues, wx.GBPosition( 0, 2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.button_copy_localZones = wx.Button( self, wx.ID_ANY, u"Copy local zones\nto family zones", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.button_copy_localZones.SetMinSize( wx.Size( 160,40 ) )

        gridZones.Add( self.button_copy_localZones, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.panel_postscriptBlueValues = ZonePanel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL, u"postscriptBlueValues" )
        gridZones.Add( self.panel_postscriptBlueValues, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.panel_postscriptOtherBlues = ZonePanel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL, u"postscriptOtherBlues" )
        gridZones.Add( self.panel_postscriptOtherBlues, wx.GBPosition( 1, 2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.lbl_FamilyZones = wx.StaticText( self, wx.ID_ANY, u"Family Zones", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_FamilyZones.Wrap( -1 )

        gridZones.Add( self.lbl_FamilyZones, wx.GBPosition( 2, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.lbl_postscriptFamilyBlues = wx.StaticText( self, wx.ID_ANY, u"Family Blues", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_postscriptFamilyBlues.Wrap( -1 )

        self.lbl_postscriptFamilyBlues.SetMinSize( wx.Size( 170,-1 ) )

        gridZones.Add( self.lbl_postscriptFamilyBlues, wx.GBPosition( 2, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.lbl_postscriptFamilyOtherBlues = wx.StaticText( self, wx.ID_ANY, u"Family Other Blues", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_postscriptFamilyOtherBlues.Wrap( -1 )

        gridZones.Add( self.lbl_postscriptFamilyOtherBlues, wx.GBPosition( 2, 2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.button_copy_familyZones = wx.Button( self, wx.ID_ANY, u"Copy family zones\nto other fonts", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.button_copy_familyZones.SetMinSize( wx.Size( 160,40 ) )

        gridZones.Add( self.button_copy_familyZones, wx.GBPosition( 3, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.panel_postscriptFamilyBlues = ZonePanel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL, u"postscriptFamilyBlues" )
        gridZones.Add( self.panel_postscriptFamilyBlues, wx.GBPosition( 3, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.panel_postscriptFamilyOtherBlues = ZonePanel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL, u"postscriptFamilyOtherBlues" )
        gridZones.Add( self.panel_postscriptFamilyOtherBlues, wx.GBPosition( 3, 2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )


        boxZones.Add( gridZones, 1, wx.EXPAND, 5 )


        sizer.Add( boxZones, 0, wx.ALL|wx.EXPAND, 5 )


        self.SetSizer( sizer )
        self.Layout()

        # Connect Events
        self.button_copy_localZones.Bind( wx.EVT_BUTTON, self.on_button_copy_localZones )
        self.button_copy_familyZones.Bind( wx.EVT_BUTTON, self.on_button_copy_familyZones )
        self.button_copy_familyZones.Bind( wx.EVT_UPDATE_UI, self.onUpdate_button_copy_familyZones )

    def __del__( self ):
        pass


    # Virtual event handlers, override them in your derived class
    def on_button_copy_localZones( self, event ):
        event.Skip()

    def on_button_copy_familyZones( self, event ):
        event.Skip()

    def onUpdate_button_copy_familyZones( self, event ):
        event.Skip()


