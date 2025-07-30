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
## Class ApplyGlyphConstructionDialogUI
###########################################################################

class ApplyGlyphConstructionDialogUI ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Apply Glyph-Construction", pos = wx.DefaultPosition, size = wx.Size( 450,300 ), style = wx.CAPTION|wx.RESIZE_BORDER )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        sizer = wx.BoxSizer( wx.VERTICAL )

        self.label = wx.StaticText( self, wx.ID_ANY, u"Select Gylph-Construction File", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.label.Wrap( -1 )

        sizer.Add( self.label, 0, wx.ALL, 5 )

        self.filePicker_ConstructionPath = wx.FilePickerCtrl( self, wx.ID_ANY, wx.EmptyString, u"Select Gylph-Construction File", u"*.glyphConstruction", wx.DefaultPosition, wx.DefaultSize, wx.FLP_FILE_MUST_EXIST|wx.FLP_OPEN|wx.FLP_SMALL|wx.FLP_USE_TEXTCTRL )
        sizer.Add( self.filePicker_ConstructionPath, 0, wx.ALL|wx.EXPAND, 5 )

        sizerOptions = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Options" ), wx.VERTICAL )

        self.checkBox_NewGlyphs = wx.CheckBox( self, wx.ID_ANY, u"Create New Glyphs", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.checkBox_NewGlyphs.SetValue(True)
        sizerOptions.Add( self.checkBox_NewGlyphs, 0, wx.ALL|wx.EXPAND, 5 )

        self.checkBox_ReplaceOutline = wx.CheckBox( self, wx.ID_ANY, u"Replace Existing Outline", wx.DefaultPosition, wx.DefaultSize, 0 )
        sizerOptions.Add( self.checkBox_ReplaceOutline, 0, wx.ALL|wx.EXPAND, 5 )

        sizerSave = wx.BoxSizer( wx.HORIZONTAL )


        sizerSave.Add( ( 20, 0), 0, wx.EXPAND, 5 )

        self.checkBox_SaveOutline = wx.CheckBox( self, wx.ID_ANY, u"Save Existing Outline on Background Layer", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.checkBox_SaveOutline.Enable( False )

        sizerSave.Add( self.checkBox_SaveOutline, 0, wx.ALL, 5 )


        sizerOptions.Add( sizerSave, 0, wx.EXPAND, 0 )

        self.checkBox_ReplaceComposite = wx.CheckBox( self, wx.ID_ANY, u"Replace Existing Composites", wx.DefaultPosition, wx.DefaultSize, 0 )
        sizerOptions.Add( self.checkBox_ReplaceComposite, 0, wx.ALL|wx.EXPAND, 5 )

        sizerMark = wx.BoxSizer( wx.HORIZONTAL )

        self.checkBox_Mark = wx.CheckBox( self, wx.ID_ANY, u"Mark", wx.DefaultPosition, wx.DefaultSize, 0 )
        sizerMark.Add( self.checkBox_Mark, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.colourPicker_Mark = wx.ColourPickerCtrl( self, wx.ID_ANY, wx.BLACK, wx.DefaultPosition, wx.DefaultSize, wx.CLRP_DEFAULT_STYLE )
        self.colourPicker_Mark.Enable( False )

        sizerMark.Add( self.colourPicker_Mark, 0, wx.ALIGN_CENTER_VERTICAL, 0 )


        sizerOptions.Add( sizerMark, 1, wx.EXPAND, 5 )


        sizer.Add( sizerOptions, 1, wx.ALL|wx.EXPAND, 5 )

        buttons = wx.StdDialogButtonSizer()
        self.buttonsOK = wx.Button( self, wx.ID_OK )
        buttons.AddButton( self.buttonsOK )
        self.buttonsCancel = wx.Button( self, wx.ID_CANCEL )
        buttons.AddButton( self.buttonsCancel )
        buttons.Realize();

        sizer.Add( buttons, 1, wx.ALL|wx.EXPAND, 5 )


        self.SetSizer( sizer )
        self.Layout()

        self.Centre( wx.BOTH )

        # Connect Events
        self.checkBox_SaveOutline.Bind( wx.EVT_UPDATE_UI, self.update_SaveOutline )
        self.colourPicker_Mark.Bind( wx.EVT_UPDATE_UI, self.update_Mark )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def update_SaveOutline( self, event ):
        event.Skip()

    def update_Mark( self, event ):
        event.Skip()


