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
## Class PanelItemPickerUI
###########################################################################

class PanelItemPickerUI ( wx.Panel ):

    def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
        wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

        self.SetMinSize( wx.Size( 300,220 ) )

        sizer_main = wx.BoxSizer( wx.HORIZONTAL )

        sizer_options = wx.BoxSizer( wx.VERTICAL )

        self.label_options = wx.StaticText( self, wx.ID_ANY, u"Options", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.label_options.Wrap( -1 )

        sizer_options.Add( self.label_options, 0, wx.ALL|wx.EXPAND, 5 )

        listBox_optionsChoices = []
        self.listBox_options = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, listBox_optionsChoices, wx.LB_EXTENDED )
        sizer_options.Add( self.listBox_options, 1, wx.ALL|wx.EXPAND, 5 )


        sizer_main.Add( sizer_options, 1, wx.EXPAND, 5 )

        sizer_buttons = wx.BoxSizer( wx.VERTICAL )


        sizer_buttons.Add( ( 0, 10), 1, wx.EXPAND, 5 )

        self.button_select = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )

        self.button_select.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_GO_FORWARD, wx.ART_BUTTON ) )
        sizer_buttons.Add( self.button_select, 0, wx.ALL, 5 )

        self.button_unselect = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )

        self.button_unselect.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_GO_BACK, wx.ART_BUTTON ) )
        sizer_buttons.Add( self.button_unselect, 0, wx.ALL, 5 )

        self.button_move_up = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )

        self.button_move_up.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_GO_UP, wx.ART_BUTTON ) )
        sizer_buttons.Add( self.button_move_up, 0, wx.ALL, 5 )

        self.button_move_down = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )

        self.button_move_down.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_GO_DOWN, wx.ART_BUTTON ) )
        sizer_buttons.Add( self.button_move_down, 0, wx.ALL, 5 )

        self.button_clear = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )

        self.button_clear.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_CLOSE, wx.ART_BUTTON ) )
        sizer_buttons.Add( self.button_clear, 0, wx.ALL, 5 )


        sizer_buttons.Add( ( 0, 0), 1, wx.EXPAND, 5 )


        sizer_main.Add( sizer_buttons, 0, wx.EXPAND, 5 )

        sizer_selection = wx.BoxSizer( wx.VERTICAL )

        self.label_selection = wx.StaticText( self, wx.ID_ANY, u"Selection", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.label_selection.Wrap( -1 )

        sizer_selection.Add( self.label_selection, 0, wx.ALL|wx.EXPAND, 5 )

        listBox_selectionChoices = []
        self.listBox_selection = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, listBox_selectionChoices, wx.LB_EXTENDED )
        sizer_selection.Add( self.listBox_selection, 1, wx.ALL|wx.EXPAND, 5 )


        sizer_main.Add( sizer_selection, 1, wx.EXPAND, 5 )


        self.SetSizer( sizer_main )
        self.Layout()
        sizer_main.Fit( self )

        # Connect Events
        self.listBox_options.Bind( wx.EVT_LISTBOX_DCLICK, self.on_listBox_dblclick )
        self.button_select.Bind( wx.EVT_BUTTON, self.on_select )
        self.button_select.Bind( wx.EVT_UPDATE_UI, self.update_button_select )
        self.button_unselect.Bind( wx.EVT_BUTTON, self.on_unselect )
        self.button_unselect.Bind( wx.EVT_UPDATE_UI, self.update_button_unselect )
        self.button_move_up.Bind( wx.EVT_BUTTON, self.on_button_move_up )
        self.button_move_up.Bind( wx.EVT_UPDATE_UI, self.update_button_move_up )
        self.button_move_down.Bind( wx.EVT_BUTTON, self.on_button_move_down )
        self.button_move_down.Bind( wx.EVT_UPDATE_UI, self.update_button_move_down )
        self.button_clear.Bind( wx.EVT_BUTTON, self.on_button_clear )
        self.button_clear.Bind( wx.EVT_UPDATE_UI, self.update_button_clear )
        self.listBox_selection.Bind( wx.EVT_LISTBOX_DCLICK, self.on_listBox_dblclick )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def on_listBox_dblclick( self, event ):
        event.Skip()

    def on_select( self, event ):
        event.Skip()

    def update_button_select( self, event ):
        event.Skip()

    def on_unselect( self, event ):
        event.Skip()

    def update_button_unselect( self, event ):
        event.Skip()

    def on_button_move_up( self, event ):
        event.Skip()

    def update_button_move_up( self, event ):
        event.Skip()

    def on_button_move_down( self, event ):
        event.Skip()

    def update_button_move_down( self, event ):
        event.Skip()

    def on_button_clear( self, event ):
        event.Skip()

    def update_button_clear( self, event ):
        event.Skip()



