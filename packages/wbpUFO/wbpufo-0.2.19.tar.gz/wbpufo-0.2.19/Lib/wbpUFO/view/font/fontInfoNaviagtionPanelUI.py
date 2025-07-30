# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.1-0-g8feb16b3)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class FontInfoNaviagtionPanelUI
###########################################################################

class FontInfoNaviagtionPanelUI ( wx.Panel ):

    def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
        wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

        bSizer3 = wx.BoxSizer( wx.VERTICAL )

        self.staticline = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer3.Add( self.staticline, 0, wx.EXPAND, 0 )

        sizer = wx.BoxSizer( wx.HORIZONTAL )

        self.button_back = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )

        self.button_back.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_GO_BACK, wx.ART_BUTTON ) )
        sizer.Add( self.button_back, 0, wx.ALL, 5 )

        self.button_forward = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )

        self.button_forward.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_GO_FORWARD, wx.ART_BUTTON ) )
        sizer.Add( self.button_forward, 0, wx.ALL, 5 )


        sizer.Add( ( 100, 0), 0, 0, 0 )

        self.button_copy = wx.Button( self, wx.ID_ANY, u"Copy ...", wx.DefaultPosition, wx.DefaultSize, 0 )
        sizer.Add( self.button_copy, 0, wx.ALL, 5 )


        sizer.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.button_macro = wx.Button( self, wx.ID_ANY, u"▼", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )

        self.button_macro.SetBitmap( wx.ArtProvider.GetBitmap( "PYTHON", wx.ART_BUTTON ) )
        sizer.Add( self.button_macro, 0, wx.ALL, 5 )


        bSizer3.Add( sizer, 1, wx.EXPAND, 5 )


        self.SetSizer( bSizer3 )
        self.Layout()
        bSizer3.Fit( self )

        # Connect Events
        self.button_copy.Bind( wx.EVT_BUTTON, self.on_button_copy )
        self.button_copy.Bind( wx.EVT_UPDATE_UI, self.onUpdate_button_copy )

    def __del__( self ):
        pass


    # Virtual event handlers, override them in your derived class
    def on_button_copy( self, event ):
        event.Skip()

    def onUpdate_button_copy( self, event ):
        event.Skip()


