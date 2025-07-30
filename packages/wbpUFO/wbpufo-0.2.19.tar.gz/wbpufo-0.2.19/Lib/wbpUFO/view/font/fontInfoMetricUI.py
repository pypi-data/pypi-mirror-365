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
## Class FontInfoMetricUI
###########################################################################

class FontInfoMetricUI ( FontInfoBasePage ):

    def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = 0, name = u"FontInfoMetric" ):
        FontInfoBasePage.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

        self.SetBackgroundColour( wx.Colour( 255, 255, 255 ) )

        sizer = wx.BoxSizer( wx.VERTICAL )

        boxMain = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Main" ), wx.VERTICAL )

        gridMain = wx.FlexGridSizer( 0, 2, 0, 0 )
        gridMain.AddGrowableCol( 1 )
        gridMain.SetFlexibleDirection( wx.HORIZONTAL )
        gridMain.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.lbl_unitsPerEm = wx.StaticText( self, wx.ID_ANY, u"Units per Em", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_unitsPerEm.Wrap( -1 )

        self.lbl_unitsPerEm.SetMinSize( wx.Size( 170,-1 ) )

        gridMain.Add( self.lbl_unitsPerEm, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_unitsPerEm = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"unitsPerEm" )
        gridMain.Add( self.txtCtrl_unitsPerEm, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.lbl_ascender = wx.StaticText( self, wx.ID_ANY, u"Ascender", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_ascender.Wrap( -1 )

        gridMain.Add( self.lbl_ascender, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_ascender = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"ascender" )
        gridMain.Add( self.txtCtrl_ascender, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.lbl_capHeight = wx.StaticText( self, wx.ID_ANY, u"Cap-Height", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_capHeight.Wrap( -1 )

        gridMain.Add( self.lbl_capHeight, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_capHeight = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"capHeight" )
        gridMain.Add( self.txtCtrl_capHeight, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.lbl_xHeight = wx.StaticText( self, wx.ID_ANY, u"x-Height", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_xHeight.Wrap( -1 )

        gridMain.Add( self.lbl_xHeight, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_xHeight = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"xHeight" )
        gridMain.Add( self.txtCtrl_xHeight, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.lbl_descender = wx.StaticText( self, wx.ID_ANY, u"Descender", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_descender.Wrap( -1 )

        gridMain.Add( self.lbl_descender, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_descender = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"descender" )
        gridMain.Add( self.txtCtrl_descender, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.lbl_italicAngle = wx.StaticText( self, wx.ID_ANY, u"Italic Angle", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_italicAngle.Wrap( -1 )

        gridMain.Add( self.lbl_italicAngle, 0, wx.ALL, 5 )

        self.txtCtrl_italicAngle = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"italicAngle" )
        gridMain.Add( self.txtCtrl_italicAngle, 0, wx.ALL, 5 )


        boxMain.Add( gridMain, 0, wx.EXPAND, 5 )


        sizer.Add( boxMain, 0, wx.ALL|wx.EXPAND, 5 )

        boxHhea = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"hhea Metric" ), wx.VERTICAL )

        fgSizer2 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer2.AddGrowableCol( 1 )
        fgSizer2.SetFlexibleDirection( wx.HORIZONTAL )
        fgSizer2.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.lbl_openTypeHheaAscender = wx.StaticText( self, wx.ID_ANY, u"Ascender", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_openTypeHheaAscender.Wrap( -1 )

        self.lbl_openTypeHheaAscender.SetMinSize( wx.Size( 170,-1 ) )

        fgSizer2.Add( self.lbl_openTypeHheaAscender, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_openTypeHheaAscender = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeHheaAscender" )
        fgSizer2.Add( self.txtCtrl_openTypeHheaAscender, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.lbl_openTypeHheaDescender = wx.StaticText( self, wx.ID_ANY, u"Descender", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_openTypeHheaDescender.Wrap( -1 )

        fgSizer2.Add( self.lbl_openTypeHheaDescender, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_openTypeHheaDescender = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeHheaDescender" )
        fgSizer2.Add( self.txtCtrl_openTypeHheaDescender, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.lbl_openTypeHheaLineGap = wx.StaticText( self, wx.ID_ANY, u"Line Gap", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_openTypeHheaLineGap.Wrap( -1 )

        fgSizer2.Add( self.lbl_openTypeHheaLineGap, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_openTypeHheaLineGap = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeHheaLineGap" )
        fgSizer2.Add( self.txtCtrl_openTypeHheaLineGap, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        boxHhea.Add( fgSizer2, 1, wx.EXPAND, 5 )


        sizer.Add( boxHhea, 0, wx.ALL|wx.EXPAND, 5 )

        boxOS2typo = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"OS/2 Typo Metric" ), wx.VERTICAL )

        gridOS2typo = wx.FlexGridSizer( 0, 2, 0, 0 )
        gridOS2typo.SetFlexibleDirection( wx.HORIZONTAL )
        gridOS2typo.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.lbl_openTypeOS2TypoAscender = wx.StaticText( self, wx.ID_ANY, u"Ascender", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_openTypeOS2TypoAscender.Wrap( -1 )

        self.lbl_openTypeOS2TypoAscender.SetMinSize( wx.Size( 170,-1 ) )

        gridOS2typo.Add( self.lbl_openTypeOS2TypoAscender, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_openTypeOS2TypoAscender = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeOS2TypoAscender" )
        gridOS2typo.Add( self.txtCtrl_openTypeOS2TypoAscender, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.lbl_openTypeOS2TypoDescender = wx.StaticText( self, wx.ID_ANY, u"Descender", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_openTypeOS2TypoDescender.Wrap( -1 )

        gridOS2typo.Add( self.lbl_openTypeOS2TypoDescender, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_openTypeOS2TypoDescender = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeOS2TypoDescender" )
        gridOS2typo.Add( self.txtCtrl_openTypeOS2TypoDescender, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.lbl_openTypeOS2TypoLineGap = wx.StaticText( self, wx.ID_ANY, u"Line Gap", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_openTypeOS2TypoLineGap.Wrap( -1 )

        gridOS2typo.Add( self.lbl_openTypeOS2TypoLineGap, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_openTypeOS2TypoLineGap = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeOS2TypoLineGap" )
        gridOS2typo.Add( self.txtCtrl_openTypeOS2TypoLineGap, 0, wx.ALL, 5 )

        self.m_staticText16 = wx.StaticText( self, wx.ID_ANY, u"Selection Bit 7", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText16.Wrap( -1 )

        gridOS2typo.Add( self.m_staticText16, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.checkBox_openTypeOS2Selection_7 = wx.CheckBox( self, wx.ID_ANY, u"Use Typo Metric", wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeOS2Selection 7" )
        gridOS2typo.Add( self.checkBox_openTypeOS2Selection_7, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        boxOS2typo.Add( gridOS2typo, 1, wx.EXPAND, 5 )


        sizer.Add( boxOS2typo, 0, wx.ALL|wx.EXPAND, 5 )

        boxOS2win = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"OS/2 Win Metric" ), wx.VERTICAL )

        gridOS2win = wx.FlexGridSizer( 0, 2, 0, 0 )
        gridOS2win.SetFlexibleDirection( wx.HORIZONTAL )
        gridOS2win.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.lbl_openTypeOS2WinAscent = wx.StaticText( boxOS2win.GetStaticBox(), wx.ID_ANY, u"Ascender", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_openTypeOS2WinAscent.Wrap( -1 )

        self.lbl_openTypeOS2WinAscent.SetMinSize( wx.Size( 170,-1 ) )

        gridOS2win.Add( self.lbl_openTypeOS2WinAscent, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_openTypeOS2WinAscent = wx.TextCtrl( boxOS2win.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeOS2WinAscent" )
        gridOS2win.Add( self.txtCtrl_openTypeOS2WinAscent, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.lbl_openTypeOS2WinDescent = wx.StaticText( boxOS2win.GetStaticBox(), wx.ID_ANY, u"Descender", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_openTypeOS2WinDescent.Wrap( -1 )

        gridOS2win.Add( self.lbl_openTypeOS2WinDescent, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_openTypeOS2WinDescent = wx.TextCtrl( boxOS2win.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeOS2WinDescent" )
        gridOS2win.Add( self.txtCtrl_openTypeOS2WinDescent, 0, wx.ALL, 5 )


        boxOS2win.Add( gridOS2win, 1, wx.EXPAND, 5 )


        sizer.Add( boxOS2win, 0, wx.ALL|wx.EXPAND, 5 )

        boxVhea = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"vhea Typo Metric" ), wx.VERTICAL )

        gridVhea = wx.FlexGridSizer( 0, 2, 0, 0 )
        gridVhea.AddGrowableCol( 1 )
        gridVhea.SetFlexibleDirection( wx.HORIZONTAL )
        gridVhea.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.lbl_openTypeVheaVertTypoAscender = wx.StaticText( boxVhea.GetStaticBox(), wx.ID_ANY, u"Vertical Ascender", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_openTypeVheaVertTypoAscender.Wrap( -1 )

        self.lbl_openTypeVheaVertTypoAscender.SetMinSize( wx.Size( 170,-1 ) )

        gridVhea.Add( self.lbl_openTypeVheaVertTypoAscender, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_openTypeVheaVertTypoAscender = wx.TextCtrl( boxVhea.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeVheaVertTypoAscender" )
        gridVhea.Add( self.txtCtrl_openTypeVheaVertTypoAscender, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.lbl_openTypeVheaVertTypoDescender = wx.StaticText( boxVhea.GetStaticBox(), wx.ID_ANY, u"Vertical Descender", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_openTypeVheaVertTypoDescender.Wrap( -1 )

        gridVhea.Add( self.lbl_openTypeVheaVertTypoDescender, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_openTypeVheaVertTypoDescender = wx.TextCtrl( boxVhea.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeVheaVertTypoDescender" )
        gridVhea.Add( self.txtCtrl_openTypeVheaVertTypoDescender, 0, wx.ALL, 5 )

        self.lbl_openTypeVheaVertTypoLineGap = wx.StaticText( boxVhea.GetStaticBox(), wx.ID_ANY, u"Vertical LineGap", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_openTypeVheaVertTypoLineGap.Wrap( -1 )

        gridVhea.Add( self.lbl_openTypeVheaVertTypoLineGap, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtCtrl_openTypeVheaVertTypoLineGap = wx.TextCtrl( boxVhea.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeVheaVertTypoLineGap" )
        gridVhea.Add( self.txtCtrl_openTypeVheaVertTypoLineGap, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        boxVhea.Add( gridVhea, 1, wx.EXPAND, 5 )


        sizer.Add( boxVhea, 0, wx.ALL|wx.EXPAND, 5 )


        self.SetSizer( sizer )
        self.Layout()
        sizer.Fit( self )

    def __del__( self ):
        pass


