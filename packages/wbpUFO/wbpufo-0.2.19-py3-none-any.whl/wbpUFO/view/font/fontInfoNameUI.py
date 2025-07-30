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
## Class FontInfoNameUI
###########################################################################

class FontInfoNameUI ( FontInfoBasePage ):

    def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 437,924 ), style = 0, name = u"FontInfoName" ):
        FontInfoBasePage.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

        self.SetBackgroundColour( wx.Colour( 255, 255, 255 ) )

        sizer = wx.BoxSizer( wx.VERTICAL )

        boxMain = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Main" ), wx.VERTICAL )

        gridMain = wx.FlexGridSizer( 0, 2, 0, 0 )
        gridMain.AddGrowableCol( 1 )
        gridMain.SetFlexibleDirection( wx.HORIZONTAL )
        gridMain.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.lbl_familyName = wx.StaticText( self, wx.ID_ANY, u"Family Name", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_familyName.Wrap( -1 )

        self.lbl_familyName.SetMinSize( wx.Size( 170,-1 ) )

        gridMain.Add( self.lbl_familyName, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_familyName = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"familyName" )
        gridMain.Add( self.txtCtrl_familyName, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )

        self.lbl_styleName = wx.StaticText( self, wx.ID_ANY, u"Style Name", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_styleName.Wrap( -1 )

        gridMain.Add( self.lbl_styleName, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_styleName = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"styleName" )
        gridMain.Add( self.txtCtrl_styleName, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )


        boxMain.Add( gridMain, 0, wx.EXPAND, 5 )


        sizer.Add( boxMain, 0, wx.ALL|wx.EXPAND, 5 )

        boxStylemap = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"StyleMap" ), wx.VERTICAL )

        gridStylemap = wx.FlexGridSizer( 0, 2, 0, 0 )
        gridStylemap.AddGrowableCol( 1 )
        gridStylemap.SetFlexibleDirection( wx.HORIZONTAL )
        gridStylemap.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.lbl_styleMapFamilyName = wx.StaticText( self, wx.ID_ANY, u"Family Name", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_styleMapFamilyName.Wrap( -1 )

        self.lbl_styleMapFamilyName.SetMinSize( wx.Size( 170,-1 ) )

        gridStylemap.Add( self.lbl_styleMapFamilyName, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_styleMapFamilyName = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"styleMapFamilyName" )
        gridStylemap.Add( self.txtCtrl_styleMapFamilyName, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )

        self.lbl_styleMapStyleName = wx.StaticText( self, wx.ID_ANY, u"Style Name", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_styleMapStyleName.Wrap( -1 )

        gridStylemap.Add( self.lbl_styleMapStyleName, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        choice_styleMapStyleNameChoices = [ wx.EmptyString, u"regular", u"italic", u"bold", u"bold italic" ]
        self.choice_styleMapStyleName = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choice_styleMapStyleNameChoices, 0, wx.DefaultValidator, u"styleMapStyleName" )
        self.choice_styleMapStyleName.SetSelection( 0 )
        gridStylemap.Add( self.choice_styleMapStyleName, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        boxStylemap.Add( gridStylemap, 0, wx.EXPAND, 5 )


        sizer.Add( boxStylemap, 0, wx.ALL|wx.EXPAND, 5 )

        boxOpenType = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"OpenType" ), wx.VERTICAL )

        gridOpenType = wx.FlexGridSizer( 0, 2, 0, 0 )
        gridOpenType.AddGrowableCol( 1 )
        gridOpenType.SetFlexibleDirection( wx.HORIZONTAL )
        gridOpenType.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.lbl_openTypeNamePreferredFamilyName = wx.StaticText( self, wx.ID_ANY, u"Typographic Family Name", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_openTypeNamePreferredFamilyName.Wrap( -1 )

        self.lbl_openTypeNamePreferredFamilyName.SetMinSize( wx.Size( 170,-1 ) )

        gridOpenType.Add( self.lbl_openTypeNamePreferredFamilyName, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_openTypeNamePreferredFamilyName = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeNamePreferredFamilyName" )
        gridOpenType.Add( self.txtCtrl_openTypeNamePreferredFamilyName, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )

        self.lbl_openTypeNamePreferredSubfamilyName = wx.StaticText( self, wx.ID_ANY, u"Typographic Subfamily Name", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_openTypeNamePreferredSubfamilyName.Wrap( -1 )

        gridOpenType.Add( self.lbl_openTypeNamePreferredSubfamilyName, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_openTypeNamePreferredSubfamilyName = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeNamePreferredSubfamilyName" )
        gridOpenType.Add( self.txtCtrl_openTypeNamePreferredSubfamilyName, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )

        self.lbl_openTypeNameCompatibleFullName = wx.StaticText( self, wx.ID_ANY, u"Compatible Full Name", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_openTypeNameCompatibleFullName.Wrap( -1 )

        gridOpenType.Add( self.lbl_openTypeNameCompatibleFullName, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_openTypeNameCompatibleFullName = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeNameCompatibleFullName" )
        gridOpenType.Add( self.txtCtrl_openTypeNameCompatibleFullName, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )

        self.lbl_openTypeOS2Selection_8 = wx.StaticText( self, wx.ID_ANY, u"OS/2 Selection Bit 8", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_openTypeOS2Selection_8.Wrap( -1 )

        gridOpenType.Add( self.lbl_openTypeOS2Selection_8, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.checkBox_openTypeOS2Selection_8 = wx.CheckBox( self, wx.ID_ANY, u"Names are WWS compatible", wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeOS2Selection 8" )
        gridOpenType.Add( self.checkBox_openTypeOS2Selection_8, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )

        self.lbl_openTypeNameWWSFamilyName = wx.StaticText( self, wx.ID_ANY, u"WWS Family Name", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_openTypeNameWWSFamilyName.Wrap( -1 )

        gridOpenType.Add( self.lbl_openTypeNameWWSFamilyName, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_openTypeNameWWSFamilyName = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeNameWWSFamilyName" )
        gridOpenType.Add( self.txtCtrl_openTypeNameWWSFamilyName, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )

        self.lbl_openTypeNameWWSSubfamilyName = wx.StaticText( self, wx.ID_ANY, u"WWS Subfamily Name", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_openTypeNameWWSSubfamilyName.Wrap( -1 )

        gridOpenType.Add( self.lbl_openTypeNameWWSSubfamilyName, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_openTypeNameWWSSubfamilyName = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeNameWWSSubfamilyName" )
        gridOpenType.Add( self.txtCtrl_openTypeNameWWSSubfamilyName, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )

        self.m_staticText16 = wx.StaticText( self, wx.ID_ANY, u"OS/2 Selection Style Bits", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText16.Wrap( -1 )

        gridOpenType.Add( self.m_staticText16, 0, wx.LEFT|wx.TOP, 5 )

        self.checkBox_openTypeOS2Selection_1 = wx.CheckBox( self, wx.ID_ANY, u"Underscored (Bit 1)", wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeOS2Selection 1" )
        gridOpenType.Add( self.checkBox_openTypeOS2Selection_1, 0, wx.LEFT|wx.TOP, 5 )


        gridOpenType.Add( ( 0, 0), 0, 0, 0 )

        self.checkBox_openTypeOS2Selection_2 = wx.CheckBox( self, wx.ID_ANY, u"Negative (Bit 2)", wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeOS2Selection 2" )
        gridOpenType.Add( self.checkBox_openTypeOS2Selection_2, 0, wx.LEFT|wx.TOP, 5 )


        gridOpenType.Add( ( 0, 0), 0, 0, 0 )

        self.checkBox_openTypeOS2Selection_3 = wx.CheckBox( self, wx.ID_ANY, u"Outlined (Bit 3)", wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeOS2Selection 3" )
        gridOpenType.Add( self.checkBox_openTypeOS2Selection_3, 0, wx.LEFT|wx.TOP, 5 )


        gridOpenType.Add( ( 0, 0), 0, 0, 0 )

        self.checkBox_openTypeOS2Selection_4 = wx.CheckBox( self, wx.ID_ANY, u"Strikeout (Bit 4)", wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeOS2Selection 4" )
        gridOpenType.Add( self.checkBox_openTypeOS2Selection_4, 0, wx.LEFT|wx.TOP, 5 )


        gridOpenType.Add( ( 0, 0), 0, 0, 0 )

        self.checkBox_openTypeOS2Selection_9 = wx.CheckBox( self, wx.ID_ANY, u"Oblique (Bit 9)", wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeOS2Selection 9" )
        gridOpenType.Add( self.checkBox_openTypeOS2Selection_9, 0, wx.LEFT|wx.TOP, 5 )


        boxOpenType.Add( gridOpenType, 0, wx.ALL|wx.EXPAND, 5 )


        sizer.Add( boxOpenType, 0, wx.ALL|wx.EXPAND, 5 )

        boxPostScript = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"PostScript" ), wx.VERTICAL )

        gridPostScript = wx.FlexGridSizer( 0, 2, 0, 0 )
        gridPostScript.AddGrowableCol( 1 )
        gridPostScript.SetFlexibleDirection( wx.HORIZONTAL )
        gridPostScript.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.lbl_postscriptFontName = wx.StaticText( self, wx.ID_ANY, u"Font Name", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_postscriptFontName.Wrap( -1 )

        self.lbl_postscriptFontName.SetMinSize( wx.Size( 170,-1 ) )

        gridPostScript.Add( self.lbl_postscriptFontName, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_postscriptFontName = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"postscriptFontName" )
        gridPostScript.Add( self.txtCtrl_postscriptFontName, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )

        self.lbl_postscriptFullName = wx.StaticText( self, wx.ID_ANY, u"Full Name", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_postscriptFullName.Wrap( -1 )

        gridPostScript.Add( self.lbl_postscriptFullName, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_postscriptFullName = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"postscriptFullName" )
        gridPostScript.Add( self.txtCtrl_postscriptFullName, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )

        self.lbl_postscriptWeightName = wx.StaticText( self, wx.ID_ANY, u"Weight Name", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_postscriptWeightName.Wrap( -1 )

        gridPostScript.Add( self.lbl_postscriptWeightName, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.textCtrl_postscriptWeightName = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"postscriptWeightName" )
        gridPostScript.Add( self.textCtrl_postscriptWeightName, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )


        boxPostScript.Add( gridPostScript, 0, wx.EXPAND, 5 )


        sizer.Add( boxPostScript, 0, wx.ALL|wx.EXPAND, 5 )

        boxMacintosh = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Macintosh" ), wx.VERTICAL )

        gridMacintosh = wx.FlexGridSizer( 0, 2, 0, 0 )
        gridMacintosh.AddGrowableCol( 1 )
        gridMacintosh.SetFlexibleDirection( wx.BOTH )
        gridMacintosh.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.lbl_macintoshFONDName = wx.StaticText( boxMacintosh.GetStaticBox(), wx.ID_ANY, u"FOND Name", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_macintoshFONDName.Wrap( -1 )

        self.lbl_macintoshFONDName.SetMinSize( wx.Size( 170,-1 ) )

        gridMacintosh.Add( self.lbl_macintoshFONDName, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_macintoshFONDName = wx.TextCtrl( boxMacintosh.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"macintoshFONDName" )
        gridMacintosh.Add( self.txtCtrl_macintoshFONDName, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )


        boxMacintosh.Add( gridMacintosh, 1, wx.EXPAND, 5 )


        sizer.Add( boxMacintosh, 0, wx.ALL|wx.EXPAND, 5 )


        self.SetSizer( sizer )
        self.Layout()

    def __del__( self ):
        pass


