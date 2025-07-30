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
## Class KerningStatusPanelUI
###########################################################################

class KerningStatusPanelUI ( wx.Panel ):

    def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.BORDER_NONE|wx.TAB_TRAVERSAL, name = wx.EmptyString ):
        wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

        sizer_outer = wx.BoxSizer( wx.VERTICAL )

        self.staticline = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        sizer_outer.Add( self.staticline, 0, wx.EXPAND, 0 )

        sizer = wx.BoxSizer( wx.HORIZONTAL )

        self.button_New = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )

        self.button_New.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_NEW, wx.ART_BUTTON ) )
        self.button_New.SetToolTip( u"Add new Group" )

        sizer.Add( self.button_New, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5 )

        self.button_Delete = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )

        self.button_Delete.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_DELETE, wx.ART_BUTTON ) )
        self.button_Delete.SetToolTip( u"Delete current Group" )

        sizer.Add( self.button_Delete, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5 )


        sizer.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.button_macro = wx.Button( self, wx.ID_ANY, u"▼", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )

        self.button_macro.SetBitmap( wx.ArtProvider.GetBitmap( "PYTHON", wx.ART_BUTTON ) )
        sizer.Add( self.button_macro, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        sizer_outer.Add( sizer, 1, wx.EXPAND, 5 )


        self.SetSizer( sizer_outer )
        self.Layout()
        sizer_outer.Fit( self )

        # Connect Events
        self.button_New.Bind( wx.EVT_BUTTON, self.on_button_New )
        self.button_Delete.Bind( wx.EVT_BUTTON, self.on_button_Delete )
        self.button_Delete.Bind( wx.EVT_UPDATE_UI, self.update_button_Delete )

    def __del__( self ):
        pass


    # Virtual event handlers, override them in your derived class
    def on_button_New( self, event ):
        event.Skip()

    def on_button_Delete( self, event ):
        event.Skip()

    def update_button_Delete( self, event ):
        event.Skip()


