# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Oct 26 2018)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class GenerateOTCFFoptionsDialogUI
###########################################################################

class GenerateOTCFFoptionsDialogUI ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Generate OT-CFF", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.CAPTION|wx.RESIZE_BORDER )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        sizer = wx.BoxSizer( wx.VERTICAL )

        self.message = wx.StaticText( self, wx.ID_ANY, u"Options", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.message.Wrap( -1 )

        sizer.Add( self.message, 0, wx.ALL, 5 )

        gbSizer = wx.GridBagSizer( 0, 0 )
        gbSizer.SetFlexibleDirection( wx.BOTH )
        gbSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.checkBox_autohint = wx.CheckBox( self, wx.ID_ANY, u"PS-Autohint", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.checkBox_autohint.SetValue(True)
        gbSizer.Add( self.checkBox_autohint, wx.GBPosition( 0, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.checkBox_removeOverlap = wx.CheckBox( self, wx.ID_ANY, u"Remove Overlap", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.checkBox_removeOverlap.SetValue(True)
        gbSizer.Add( self.checkBox_removeOverlap, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.staticText_cffcompress = wx.StaticText( self, wx.ID_ANY, u"CFF Compress", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.staticText_cffcompress.Wrap( -1 )

        gbSizer.Add( self.staticText_cffcompress, wx.GBPosition( 2, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        choice_cffcompressChoices = [ u"NONE", u"SPECIALIZE", u"SUBROUTINIZE" ]
        self.choice_cffcompress = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choice_cffcompressChoices, 0 )
        self.choice_cffcompress.SetSelection( 2 )
        gbSizer.Add( self.choice_cffcompress, wx.GBPosition( 2, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.checkBox_useProductionNames = wx.CheckBox( self, wx.ID_ANY, u"Use Production Names", wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer.Add( self.checkBox_useProductionNames, wx.GBPosition( 3, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.checkBox_writeKernFeature = wx.CheckBox( self, wx.ID_ANY, u"Write kern Feature", wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer.Add( self.checkBox_writeKernFeature, wx.GBPosition( 4, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.checkBox_writeMarkFeature = wx.CheckBox( self, wx.ID_ANY, u"Write mark Feature", wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer.Add( self.checkBox_writeMarkFeature, wx.GBPosition( 5, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )


        sizer.Add( gbSizer, 1, wx.ALL|wx.EXPAND, 5 )

        self.staticline = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        sizer.Add( self.staticline, 0, wx.BOTTOM|wx.EXPAND|wx.TOP, 5 )

        sdbSizer = wx.StdDialogButtonSizer()
        self.sdbSizerOK = wx.Button( self, wx.ID_OK )
        sdbSizer.AddButton( self.sdbSizerOK )
        self.sdbSizerCancel = wx.Button( self, wx.ID_CANCEL )
        sdbSizer.AddButton( self.sdbSizerCancel )
        sdbSizer.Realize();

        sizer.Add( sdbSizer, 0, wx.ALL|wx.EXPAND, 5 )


        self.SetSizer( sizer )
        self.Layout()
        sizer.Fit( self )

        self.Centre( wx.BOTH )

    def __del__( self ):
        pass


