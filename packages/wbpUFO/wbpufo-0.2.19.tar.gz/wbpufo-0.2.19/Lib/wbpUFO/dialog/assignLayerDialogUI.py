# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.0-4761b0c)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class AssignLayerDialogUI
###########################################################################

class AssignLayerDialogUI ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Assign Layer from Font", pos = wx.DefaultPosition, size = wx.Size( 450,-1 ), style = wx.CAPTION|wx.RESIZE_BORDER )

        self.SetSizeHints( wx.Size( 400,300 ), wx.DefaultSize )

        sizer_main = wx.BoxSizer( wx.VERTICAL )

        sizer_source = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Source" ), wx.VERTICAL )

        sizer_source_grid = wx.FlexGridSizer( 0, 2, 0, 0 )
        sizer_source_grid.AddGrowableCol( 1 )
        sizer_source_grid.SetFlexibleDirection( wx.BOTH )
        sizer_source_grid.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.lbl_soure_font = wx.StaticText( sizer_source.GetStaticBox(), wx.ID_ANY, u"Font", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_soure_font.Wrap( -1 )

        sizer_source_grid.Add( self.lbl_soure_font, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        choice_source_fontChoices = []
        self.choice_source_font = wx.Choice( sizer_source.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choice_source_fontChoices, 0 )
        self.choice_source_font.SetSelection( 0 )
        sizer_source_grid.Add( self.choice_source_font, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.lbl_soure_layer = wx.StaticText( sizer_source.GetStaticBox(), wx.ID_ANY, u"Layer", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_soure_layer.Wrap( -1 )

        sizer_source_grid.Add( self.lbl_soure_layer, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        choice_source_layerChoices = []
        self.choice_source_layer = wx.Choice( sizer_source.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choice_source_layerChoices, 0 )
        self.choice_source_layer.SetSelection( 0 )
        sizer_source_grid.Add( self.choice_source_layer, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )


        sizer_source.Add( sizer_source_grid, 1, wx.EXPAND, 5 )


        sizer_main.Add( sizer_source, 0, wx.ALL|wx.EXPAND, 5 )

        sizer_target = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Target" ), wx.VERTICAL )

        sizer_target_grid = wx.FlexGridSizer( 0, 2, 0, 0 )
        sizer_target_grid.AddGrowableCol( 1 )
        sizer_target_grid.SetFlexibleDirection( wx.BOTH )
        sizer_target_grid.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.lbl_target_font = wx.StaticText( sizer_target.GetStaticBox(), wx.ID_ANY, u"Font", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_target_font.Wrap( -1 )

        sizer_target_grid.Add( self.lbl_target_font, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        choice_target_fontChoices = []
        self.choice_target_font = wx.Choice( sizer_target.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choice_target_fontChoices, 0 )
        self.choice_target_font.SetSelection( 0 )
        sizer_target_grid.Add( self.choice_target_font, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.lbl_target_layer = wx.StaticText( sizer_target.GetStaticBox(), wx.ID_ANY, u"Layer", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_target_layer.Wrap( -1 )

        sizer_target_grid.Add( self.lbl_target_layer, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        choice_target_layerChoices = []
        self.choice_target_layer = wx.Choice( sizer_target.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choice_target_layerChoices, 0 )
        self.choice_target_layer.SetSelection( 0 )
        sizer_target_grid.Add( self.choice_target_layer, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )


        sizer_target_grid.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.checkBox_new_glyphs = wx.CheckBox( sizer_target.GetStaticBox(), wx.ID_ANY, u"Create new Glyphs", wx.DefaultPosition, wx.DefaultSize, 0 )
        sizer_target_grid.Add( self.checkBox_new_glyphs, 0, wx.ALL, 5 )


        sizer_target.Add( sizer_target_grid, 1, wx.EXPAND, 5 )


        sizer_main.Add( sizer_target, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_staticline1 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        sizer_main.Add( self.m_staticline1, 0, wx.EXPAND, 0 )

        button_sizer = wx.StdDialogButtonSizer()
        self.button_sizerOK = wx.Button( self, wx.ID_OK )
        button_sizer.AddButton( self.button_sizerOK )
        self.button_sizerCancel = wx.Button( self, wx.ID_CANCEL )
        button_sizer.AddButton( self.button_sizerCancel )
        button_sizer.Realize();

        sizer_main.Add( button_sizer, 1, wx.ALIGN_RIGHT|wx.ALL, 5 )


        self.SetSizer( sizer_main )
        self.Layout()

        self.Centre( wx.BOTH )

        # Connect Events
        self.choice_source_font.Bind( wx.EVT_CHOICE, self.on_choice_source_font )
        self.choice_source_layer.Bind( wx.EVT_CHOICE, self.on_choice_source_layer )
        self.choice_target_font.Bind( wx.EVT_CHOICE, self.on_choice_target_font )
        self.choice_target_layer.Bind( wx.EVT_CHOICE, self.on_choice_target_layer )

    def __del__( self ):
        pass


    # Virtual event handlers, override them in your derived class
    def on_choice_source_font( self, event ):
        event.Skip()

    def on_choice_source_layer( self, event ):
        event.Skip()

    def on_choice_target_font( self, event ):
        event.Skip()

    def on_choice_target_layer( self, event ):
        event.Skip()


