# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.9.0 Oct 29 2020)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class RevertFontDialogUI
###########################################################################

class RevertFontDialogUI ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Revert Font", pos = wx.DefaultPosition, size = wx.Size( 350,400 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        sizer_main = wx.BoxSizer( wx.VERTICAL )

        self.lbl_message = wx.StaticText( self, wx.ID_ANY, u"Select Font Components to Revert", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_message.Wrap( -1 )

        sizer_main.Add( self.lbl_message, 0, wx.ALL, 5 )

        self.checkBox_all = wx.CheckBox( self, wx.ID_ANY, u"Revert Everything", wx.DefaultPosition, wx.DefaultSize, 0 )
        sizer_main.Add( self.checkBox_all, 0, wx.ALL, 5 )

        self.m_staticline1 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        sizer_main.Add( self.m_staticline1, 0, wx.EXPAND, 5 )

        sizer_ctrl = wx.BoxSizer( wx.HORIZONTAL )

        sizer_check = wx.BoxSizer( wx.VERTICAL )

        self.checkBox_font_lib = wx.CheckBox( self, wx.ID_ANY, u"Font Lib", wx.DefaultPosition, wx.DefaultSize, 0 )
        sizer_check.Add( self.checkBox_font_lib, 0, wx.ALL|wx.EXPAND, 5 )

        self.checkBox_font_info = wx.CheckBox( self, wx.ID_ANY, u"Font Info", wx.DefaultPosition, wx.DefaultSize, 0 )
        sizer_check.Add( self.checkBox_font_info, 0, wx.ALL|wx.EXPAND, 5 )

        self.checkBox_groups = wx.CheckBox( self, wx.ID_ANY, u"Groups", wx.DefaultPosition, wx.DefaultSize, 0 )
        sizer_check.Add( self.checkBox_groups, 0, wx.ALL, 5 )

        self.checkBox_kerning = wx.CheckBox( self, wx.ID_ANY, u"Kerning", wx.DefaultPosition, wx.DefaultSize, 0 )
        sizer_check.Add( self.checkBox_kerning, 0, wx.ALL|wx.EXPAND, 5 )

        self.checkBox_features = wx.CheckBox( self, wx.ID_ANY, u"Features", wx.DefaultPosition, wx.DefaultSize, 0 )
        sizer_check.Add( self.checkBox_features, 0, wx.ALL|wx.EXPAND, 5 )

        self.checkBox_images = wx.CheckBox( self, wx.ID_ANY, u"Images", wx.DefaultPosition, wx.DefaultSize, 0 )
        sizer_check.Add( self.checkBox_images, 0, wx.ALL|wx.EXPAND, 5 )

        self.checkBox_data = wx.CheckBox( self, wx.ID_ANY, u"Data", wx.DefaultPosition, wx.DefaultSize, 0 )
        sizer_check.Add( self.checkBox_data, 0, wx.ALL|wx.EXPAND, 5 )


        sizer_ctrl.Add( sizer_check, 0, wx.EXPAND, 5 )

        sizer_layer = wx.BoxSizer( wx.VERTICAL )

        self.lbl_layer = wx.StaticText( self, wx.ID_ANY, u"Layers", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_layer.Wrap( -1 )

        sizer_layer.Add( self.lbl_layer, 0, wx.ALL|wx.EXPAND, 5 )

        self.checkBox_defaultLayer = wx.CheckBox( self, wx.ID_ANY, u"Default Layer", wx.DefaultPosition, wx.DefaultSize, 0 )
        sizer_layer.Add( self.checkBox_defaultLayer, 0, wx.ALL|wx.EXPAND, 5 )

        self.checkBox_layer_order = wx.CheckBox( self, wx.ID_ANY, u"Layer Order", wx.DefaultPosition, wx.DefaultSize, 0 )
        sizer_layer.Add( self.checkBox_layer_order, 0, wx.ALL|wx.EXPAND, 5 )

        self.scrolledWindow_layers = wx.ScrolledWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.ALWAYS_SHOW_SB|wx.VSCROLL )
        self.scrolledWindow_layers.SetScrollRate( 5, 5 )
        sizer_layer.Add( self.scrolledWindow_layers, 1, wx.EXPAND |wx.ALL, 5 )


        sizer_ctrl.Add( sizer_layer, 1, wx.EXPAND, 5 )


        sizer_main.Add( sizer_ctrl, 1, wx.EXPAND, 5 )

        sizer_buttons = wx.StdDialogButtonSizer()
        self.sizer_buttonsOK = wx.Button( self, wx.ID_OK )
        sizer_buttons.AddButton( self.sizer_buttonsOK )
        self.sizer_buttonsCancel = wx.Button( self, wx.ID_CANCEL )
        sizer_buttons.AddButton( self.sizer_buttonsCancel )
        sizer_buttons.Realize();

        sizer_main.Add( sizer_buttons, 0, wx.ALL|wx.EXPAND, 5 )


        self.SetSizer( sizer_main )
        self.Layout()

        self.Centre( wx.BOTH )

        # Connect Events
        self.checkBox_all.Bind( wx.EVT_CHECKBOX, self.on_checkBox_all )
        self.checkBox_font_lib.Bind( wx.EVT_CHECKBOX, self.on_checkBox_single )
        self.checkBox_font_info.Bind( wx.EVT_CHECKBOX, self.on_checkBox_single )
        self.checkBox_groups.Bind( wx.EVT_CHECKBOX, self.on_checkBox_single )
        self.checkBox_kerning.Bind( wx.EVT_CHECKBOX, self.on_checkBox_single )
        self.checkBox_features.Bind( wx.EVT_CHECKBOX, self.on_checkBox_single )
        self.checkBox_images.Bind( wx.EVT_CHECKBOX, self.on_checkBox_single )
        self.checkBox_data.Bind( wx.EVT_CHECKBOX, self.on_checkBox_single )
        self.checkBox_defaultLayer.Bind( wx.EVT_CHECKBOX, self.on_checkBox_single )
        self.checkBox_layer_order.Bind( wx.EVT_CHECKBOX, self.on_checkBox_single )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def on_checkBox_all( self, event ):
        event.Skip()

    def on_checkBox_single( self, event ):
        event.Skip()










###########################################################################
## Class LayerPanelUI
###########################################################################

class LayerPanelUI ( wx.Panel ):

    def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
        wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

        sizer_main = wx.BoxSizer( wx.VERTICAL )

        self.lbl_name = wx.StaticText( self, wx.ID_ANY, u"Layer:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_name.Wrap( -1 )

        sizer_main.Add( self.lbl_name, 0, wx.ALL|wx.EXPAND, 5 )

        self.checkBox_info = wx.CheckBox( self, wx.ID_ANY, u"Info", wx.DefaultPosition, wx.DefaultSize, 0 )
        sizer_main.Add( self.checkBox_info, 0, wx.ALL|wx.EXPAND, 5 )

        self.lbl_glyphs = wx.StaticText( self, wx.ID_ANY, u"Glyphs", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_glyphs.Wrap( -1 )

        sizer_main.Add( self.lbl_glyphs, 0, wx.ALL|wx.EXPAND, 5 )

        checkList_glyphNamesChoices = []
        self.checkList_glyphNames = wx.CheckListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, checkList_glyphNamesChoices, wx.LB_ALWAYS_SB|wx.LB_MULTIPLE )
        sizer_main.Add( self.checkList_glyphNames, 1, wx.ALL|wx.EXPAND, 5 )

        self.staticline = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        sizer_main.Add( self.staticline, 0, wx.BOTTOM|wx.EXPAND|wx.TOP, 5 )


        self.SetSizer( sizer_main )
        self.Layout()
        sizer_main.Fit( self )

    def __del__( self ):
        pass


