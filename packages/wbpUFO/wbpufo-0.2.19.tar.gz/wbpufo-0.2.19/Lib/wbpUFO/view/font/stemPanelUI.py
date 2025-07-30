# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.1-0-g8feb16b3)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

from .hintPSlistCtrl import StemListCtrl
import wx
import wx.xrc

###########################################################################
## Class StemPanelUI
###########################################################################

class StemPanelUI ( wx.Panel ):

    def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.BORDER_NONE|wx.TAB_TRAVERSAL, name = wx.EmptyString ):
        wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

        sizer = wx.BoxSizer( wx.VERTICAL )

        self.listCtrl_stem = StemListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 280,160 ), wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_VIRTUAL )
        self.listCtrl_stem.SetMinSize( wx.Size( 280,160 ) )

        sizer.Add( self.listCtrl_stem, 1, wx.EXPAND, 0 )

        sizer_edit = wx.BoxSizer( wx.HORIZONTAL )

        self.lbl_width = wx.StaticText( self, wx.ID_ANY, u"Width", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_width.Wrap( -1 )

        sizer_edit.Add( self.lbl_width, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.textCtrl_width = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_RIGHT )
        self.textCtrl_width.Enable( False )
        self.textCtrl_width.SetMinSize( wx.Size( 60,-1 ) )

        sizer_edit.Add( self.textCtrl_width, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.button_apply = wx.Button( self, wx.ID_ANY, u"Apply", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
        self.button_apply.Enable( False )
        self.button_apply.SetToolTip( u"Apply zone values" )

        sizer_edit.Add( self.button_apply, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        sizer.Add( sizer_edit, 0, wx.EXPAND, 0 )

        sizer_buttons = wx.BoxSizer( wx.HORIZONTAL )

        self.button_add = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )

        self.button_add.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_PLUS, wx.ART_BUTTON ) )
        self.button_add.Enable( False )
        self.button_add.SetToolTip( u"Add new zone" )

        sizer_buttons.Add( self.button_add, 0, wx.BOTTOM|wx.LEFT|wx.RIGHT, 5 )

        self.button_remove = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )

        self.button_remove.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_MINUS, wx.ART_BUTTON ) )
        self.button_remove.Enable( False )
        self.button_remove.SetToolTip( u"Delete selected zone" )

        sizer_buttons.Add( self.button_remove, 0, wx.BOTTOM|wx.LEFT|wx.RIGHT, 5 )


        sizer.Add( sizer_buttons, 0, wx.EXPAND, 0 )


        self.SetSizer( sizer )
        self.Layout()
        sizer.Fit( self )

        # Connect Events
        self.listCtrl_stem.Bind( wx.EVT_LIST_ITEM_SELECTED, self.on_listCtrl_stem_selected )
        self.textCtrl_width.Bind( wx.EVT_UPDATE_UI, self.onUpdate_editControls )
        self.button_apply.Bind( wx.EVT_BUTTON, self.on_button_apply )
        self.button_apply.Bind( wx.EVT_UPDATE_UI, self.onUpdate_editControls )
        self.button_add.Bind( wx.EVT_BUTTON, self.on_button_add )
        self.button_add.Bind( wx.EVT_UPDATE_UI, self.onUpdate_button_add )
        self.button_remove.Bind( wx.EVT_BUTTON, self.on_button_remove )
        self.button_remove.Bind( wx.EVT_UPDATE_UI, self.onUpdate_button_remove )

    def __del__( self ):
        pass


    # Virtual event handlers, override them in your derived class
    def on_listCtrl_stem_selected( self, event ):
        event.Skip()

    def onUpdate_editControls( self, event ):
        event.Skip()

    def on_button_apply( self, event ):
        event.Skip()


    def on_button_add( self, event ):
        event.Skip()

    def onUpdate_button_add( self, event ):
        event.Skip()

    def on_button_remove( self, event ):
        event.Skip()

    def onUpdate_button_remove( self, event ):
        event.Skip()


