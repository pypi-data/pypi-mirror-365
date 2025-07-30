# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.0-4761b0c)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

from .commandListCtrl import CommandListCtrl
import wx
import wx.xrc
import wx.propgrid as pg

###########################################################################
## Class CommandListDialogUI
###########################################################################

class CommandListDialogUI ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Command List", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        sizer_main = wx.BoxSizer( wx.VERTICAL )

        sizer_head = wx.GridBagSizer( 0, 0 )
        sizer_head.SetFlexibleDirection( wx.BOTH )
        sizer_head.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.label_target = wx.StaticText( self, wx.ID_ANY, u"Apply command list to", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.label_target.Wrap( -1 )

        sizer_head.Add( self.label_target, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        choice_targetChoices = [ u"Current Glyph", u"Selected Glyphs in Current Font", u"All Glyphs in Current Font", u"All Glyphs in all open Fonts", u"Glyphs from List in Current Font", u"Glyphs from List in all open Fonts" ]
        self.choice_target = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choice_targetChoices, 0 )
        self.choice_target.SetSelection( 0 )
        sizer_head.Add( self.choice_target, wx.GBPosition( 0, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )

        self.message_target = wx.StaticText( self, wx.ID_ANY, u"Action set will affect some glyphs in some fonts", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.message_target.Wrap( -1 )

        sizer_head.Add( self.message_target, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 2 ), wx.ALL, 5 )

        self.labet_saved_lists = wx.StaticText( self, wx.ID_ANY, u"Saved command lists", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.labet_saved_lists.Wrap( -1 )

        sizer_head.Add( self.labet_saved_lists, wx.GBPosition( 2, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        choice_saved_listsChoices = []
        self.choice_saved_lists = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choice_saved_listsChoices, 0 )
        self.choice_saved_lists.SetSelection( 0 )
        sizer_head.Add( self.choice_saved_lists, wx.GBPosition( 2, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )


        sizer_head.AddGrowableCol( 1 )

        sizer_main.Add( sizer_head, 0, wx.EXPAND, 5 )

        self.staticline_head = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        sizer_main.Add( self.staticline_head, 0, wx.BOTTOM|wx.EXPAND|wx.TOP, 5 )

        sizer_command = wx.BoxSizer( wx.HORIZONTAL )

        sizer_commands_available = wx.BoxSizer( wx.VERTICAL )

        self.label_commands_available = wx.StaticText( self, wx.ID_ANY, u"Available commands", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.label_commands_available.Wrap( -1 )

        sizer_commands_available.Add( self.label_commands_available, 0, wx.ALL, 5 )

        self.treeCtrl_commands_available = wx.TreeCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TR_DEFAULT_STYLE|wx.TR_HIDE_ROOT|wx.TR_TWIST_BUTTONS )
        sizer_commands_available.Add( self.treeCtrl_commands_available, 1, wx.ALL|wx.EXPAND, 5 )


        sizer_command.Add( sizer_commands_available, 1, wx.EXPAND, 5 )

        sizer_command_select = wx.BoxSizer( wx.VERTICAL )


        sizer_command_select.Add( ( 0, 20), 1, wx.EXPAND, 5 )

        self.button_add = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )

        self.button_add.SetBitmap( wx.ArtProvider.GetBitmap( 'GO_FORWARD', wx.ART_BUTTON ) )
        self.button_add.SetBitmapDisabled( wx.ArtProvider.GetBitmap( 'GO_FORWARD_DISABLED', wx.ART_BUTTON ) )
        self.button_add.Enable( False )
        self.button_add.SetToolTip( u"Add command to list" )

        sizer_command_select.Add( self.button_add, 0, wx.ALL, 5 )

        self.button_remove = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )

        self.button_remove.SetBitmap( wx.ArtProvider.GetBitmap( 'GO_BACK', wx.ART_BUTTON ) )
        self.button_remove.SetBitmapDisabled( wx.ArtProvider.GetBitmap( 'GO_BACK_DISABLED', wx.ART_BUTTON ) )
        self.button_remove.Enable( False )
        self.button_remove.SetToolTip( u"Remove command from list" )

        sizer_command_select.Add( self.button_remove, 0, wx.ALL, 5 )

        self.button_open = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )

        self.button_open.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_FILE_OPEN, wx.ART_BUTTON ) )
        self.button_open.SetToolTip( u"Open command list from file" )

        sizer_command_select.Add( self.button_open, 0, wx.ALL, 5 )

        self.button_save = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )

        self.button_save.SetBitmap( wx.ArtProvider.GetBitmap( 'FILE_SAVE', wx.ART_BUTTON ) )
        self.button_save.SetBitmapDisabled( wx.ArtProvider.GetBitmap( 'FILE_SAVE_DISABLED', wx.ART_BUTTON ) )
        self.button_save.Enable( False )
        self.button_save.SetToolTip( u"Save command list to file" )

        sizer_command_select.Add( self.button_save, 0, wx.ALL, 5 )


        sizer_command.Add( sizer_command_select, 0, wx.EXPAND, 5 )

        sizer_command_list = wx.BoxSizer( wx.VERTICAL )

        self.label_command_list = wx.StaticText( self, wx.ID_ANY, u"Command list", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.label_command_list.Wrap( -1 )

        sizer_command_list.Add( self.label_command_list, 0, wx.ALL, 5 )

        self.listCtrl_commands = CommandListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_NO_HEADER|wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_VIRTUAL )
        sizer_command_list.Add( self.listCtrl_commands, 1, wx.ALL|wx.EXPAND, 5 )


        sizer_command.Add( sizer_command_list, 1, wx.EXPAND, 5 )

        sizer_command_sort = wx.BoxSizer( wx.VERTICAL )


        sizer_command_sort.Add( ( 0, 20), 1, wx.EXPAND, 5 )

        self.button_up = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )

        self.button_up.SetBitmap( wx.ArtProvider.GetBitmap( 'GO_UP', wx.ART_BUTTON ) )
        self.button_up.SetBitmapDisabled( wx.ArtProvider.GetBitmap( 'GO_UP_DISABLED', wx.ART_BUTTON ) )
        self.button_up.Enable( False )
        self.button_up.SetToolTip( u"Move selected command up" )

        sizer_command_sort.Add( self.button_up, 0, wx.ALL, 5 )

        self.button_down = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )

        self.button_down.SetBitmap( wx.ArtProvider.GetBitmap( 'GO_DOWN', wx.ART_BUTTON ) )
        self.button_down.SetBitmapDisabled( wx.ArtProvider.GetBitmap( 'GO_DOWN_DISABLED', wx.ART_BUTTON ) )
        self.button_down.Enable( False )
        self.button_down.SetToolTip( u"Move selected command down" )

        sizer_command_sort.Add( self.button_down, 0, wx.ALL, 5 )

        self.button_clear = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )

        self.button_clear.SetBitmap( wx.ArtProvider.GetBitmap( 'DELETE', wx.ART_BUTTON ) )
        self.button_clear.SetBitmapDisabled( wx.ArtProvider.GetBitmap( 'DELETE_DISABLED', wx.ART_BUTTON ) )
        self.button_clear.Enable( False )
        self.button_clear.SetToolTip( u"Clear command list" )

        sizer_command_sort.Add( self.button_clear, 0, wx.ALL, 5 )


        sizer_command.Add( sizer_command_sort, 0, wx.EXPAND, 5 )


        sizer_main.Add( sizer_command, 1, wx.EXPAND, 5 )

        self.staticline_action = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        sizer_main.Add( self.staticline_action, 0, wx.BOTTOM|wx.EXPAND|wx.TOP, 5 )

        self.label_current_command = wx.StaticText( self, wx.ID_ANY, u"Current command is:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.label_current_command.Wrap( -1 )

        sizer_main.Add( self.label_current_command, 0, wx.ALL, 5 )

        self.parameterGrid = pg.PropertyGrid(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.propgrid.PG_DEFAULT_STYLE|wx.propgrid.PG_SPLITTER_AUTO_CENTER)
        sizer_main.Add( self.parameterGrid, 1, wx.ALL|wx.EXPAND, 5 )

        sizer_dialog_buttons = wx.StdDialogButtonSizer()
        self.sizer_dialog_buttonsOK = wx.Button( self, wx.ID_OK )
        sizer_dialog_buttons.AddButton( self.sizer_dialog_buttonsOK )
        self.sizer_dialog_buttonsCancel = wx.Button( self, wx.ID_CANCEL )
        sizer_dialog_buttons.AddButton( self.sizer_dialog_buttonsCancel )
        sizer_dialog_buttons.Realize();

        sizer_main.Add( sizer_dialog_buttons, 0, wx.ALL|wx.EXPAND, 5 )


        self.SetSizer( sizer_main )
        self.Layout()
        sizer_main.Fit( self )

        self.Centre( wx.BOTH )

        # Connect Events
        self.Bind( wx.EVT_INIT_DIALOG, self.on_InitDialog )
        self.choice_target.Bind( wx.EVT_CHOICE, self.on_choice_target )
        self.choice_saved_lists.Bind( wx.EVT_CHOICE, self.on_choice_saved_lists )
        self.treeCtrl_commands_available.Bind( wx.EVT_TREE_ITEM_ACTIVATED, self.on_TreeCommandActivated )
        self.treeCtrl_commands_available.Bind( wx.EVT_TREE_SEL_CHANGED, self.on_TreeCommandSelChanged )
        self.button_add.Bind( wx.EVT_BUTTON, self.on_button_add )
        self.button_add.Bind( wx.EVT_UPDATE_UI, self.onUpdate_button_add )
        self.button_remove.Bind( wx.EVT_BUTTON, self.on_button_remove )
        self.button_remove.Bind( wx.EVT_UPDATE_UI, self.onUpdate_button_remove )
        self.button_open.Bind( wx.EVT_BUTTON, self.on_button_open )
        self.button_save.Bind( wx.EVT_BUTTON, self.on_button_save )
        self.button_save.Bind( wx.EVT_UPDATE_UI, self.onUpdate_button_save )
        self.listCtrl_commands.Bind( wx.EVT_LIST_ITEM_ACTIVATED, self.on_listCtrl_commands_Activated )
        self.listCtrl_commands.Bind( wx.EVT_LIST_ITEM_SELECTED, self.on_listCtrl_commands_Selected )
        self.listCtrl_commands.Bind( wx.EVT_UPDATE_UI, self.onUpdate_listCtrl_commands )
        self.button_up.Bind( wx.EVT_BUTTON, self.on_button_up )
        self.button_up.Bind( wx.EVT_UPDATE_UI, self.onUpdate_button_up )
        self.button_down.Bind( wx.EVT_BUTTON, self.on_button_down )
        self.button_down.Bind( wx.EVT_UPDATE_UI, self.onUpdate_button_down )
        self.button_clear.Bind( wx.EVT_BUTTON, self.on_button_clear )
        self.button_clear.Bind( wx.EVT_UPDATE_UI, self.onUpdate_button_clear )
        self.parameterGrid.Bind( pg.EVT_PG_CHANGED, self.on_propertyGrid_Changed )

    def __del__( self ):
        pass


    # Virtual event handlers, override them in your derived class
    def on_InitDialog( self, event ):
        event.Skip()

    def on_choice_target( self, event ):
        event.Skip()

    def on_choice_saved_lists( self, event ):
        event.Skip()

    def on_TreeCommandActivated( self, event ):
        event.Skip()

    def on_TreeCommandSelChanged( self, event ):
        event.Skip()

    def on_button_add( self, event ):
        event.Skip()

    def onUpdate_button_add( self, event ):
        event.Skip()

    def on_button_remove( self, event ):
        event.Skip()

    def onUpdate_button_remove( self, event ):
        event.Skip()

    def on_button_open( self, event ):
        event.Skip()

    def on_button_save( self, event ):
        event.Skip()

    def onUpdate_button_save( self, event ):
        event.Skip()

    def on_listCtrl_commands_Activated( self, event ):
        event.Skip()

    def on_listCtrl_commands_Selected( self, event ):
        event.Skip()

    def onUpdate_listCtrl_commands( self, event ):
        event.Skip()

    def on_button_up( self, event ):
        event.Skip()

    def onUpdate_button_up( self, event ):
        event.Skip()

    def on_button_down( self, event ):
        event.Skip()

    def onUpdate_button_down( self, event ):
        event.Skip()

    def on_button_clear( self, event ):
        event.Skip()

    def onUpdate_button_clear( self, event ):
        event.Skip()

    def on_propertyGrid_Changed( self, event ):
        event.Skip()


