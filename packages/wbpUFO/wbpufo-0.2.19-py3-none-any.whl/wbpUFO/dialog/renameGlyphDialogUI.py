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
## Class RenameGlyphDialogUI
###########################################################################

class RenameGlyphDialogUI ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Rename Glyph", pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.CAPTION|wx.RESIZE_BORDER|wx.STAY_ON_TOP )

        self.SetSizeHints( wx.Size( 400,-1 ), wx.DefaultSize )

        sizer = wx.BoxSizer( wx.VERTICAL )

        sbSizerNameCurrent = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Current Name and Unicode" ), wx.VERTICAL )

        fgSizerNameCurrent = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizerNameCurrent.AddGrowableCol( 1 )
        fgSizerNameCurrent.SetFlexibleDirection( wx.HORIZONTAL )
        fgSizerNameCurrent.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.labelNameCurrent = wx.StaticText( self, wx.ID_ANY, u"Name", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.labelNameCurrent.Wrap( -1 )

        fgSizerNameCurrent.Add( self.labelNameCurrent, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.textCtrlNameCurrent = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.textCtrlNameCurrent.Enable( False )

        fgSizerNameCurrent.Add( self.textCtrlNameCurrent, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.labelUniCurrent = wx.StaticText( self, wx.ID_ANY, u"Unicode", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.labelUniCurrent.Wrap( -1 )

        fgSizerNameCurrent.Add( self.labelUniCurrent, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.textCtrlUniCurrent = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.textCtrlUniCurrent.Enable( False )

        fgSizerNameCurrent.Add( self.textCtrlUniCurrent, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )


        sbSizerNameCurrent.Add( fgSizerNameCurrent, 0, wx.EXPAND, 5 )


        sizer.Add( sbSizerNameCurrent, 0, wx.ALL|wx.EXPAND, 5 )

        sbSizerNameNew = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"New Name and Unicode" ), wx.VERTICAL )

        fgSizerNameNew = wx.FlexGridSizer( 0, 3, 0, 0 )
        fgSizerNameNew.AddGrowableCol( 1 )
        fgSizerNameNew.SetFlexibleDirection( wx.HORIZONTAL )
        fgSizerNameNew.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.labelNameNew = wx.StaticText( self, wx.ID_ANY, u"Name", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.labelNameNew.Wrap( -1 )

        fgSizerNameNew.Add( self.labelNameNew, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.textCtrlNameNew = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.textCtrlNameNew.SetMaxLength( 63 )
        fgSizerNameNew.Add( self.textCtrlNameNew, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )

        self.buttonAutoName = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )

        self.buttonAutoName.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_TIP, wx.ART_BUTTON ) )
        fgSizerNameNew.Add( self.buttonAutoName, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.labelUniNew = wx.StaticText( self, wx.ID_ANY, u"Unicode", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.labelUniNew.Wrap( -1 )

        fgSizerNameNew.Add( self.labelUniNew, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.textCtrlUniNew = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizerNameNew.Add( self.textCtrlUniNew, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )

        self.buttonAutoUni = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )

        self.buttonAutoUni.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_TIP, wx.ART_BUTTON ) )
        fgSizerNameNew.Add( self.buttonAutoUni, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        sbSizerNameNew.Add( fgSizerNameNew, 0, wx.EXPAND, 5 )


        sizer.Add( sbSizerNameNew, 0, wx.ALL|wx.EXPAND, 5 )

        sbSizerOptions = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Options" ), wx.VERTICAL )

        bSizer8 = wx.BoxSizer( wx.VERTICAL )

        self.checkBoxReplaceExisting = wx.CheckBox( sbSizerOptions.GetStaticBox(), wx.ID_ANY, u"Replace existing glyph with the same name", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer8.Add( self.checkBoxReplaceExisting, 0, wx.ALL|wx.EXPAND, 5 )

        self.checkBoxKeepReplaced = wx.CheckBox( sbSizerOptions.GetStaticBox(), wx.ID_ANY, u"Keep replaced glyph with the new name", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer8.Add( self.checkBoxKeepReplaced, 0, wx.ALL|wx.EXPAND, 5 )

        radioBoxKeepReplacedChoices = [ u"Keep replaced glyph with new name", u"Remove replaced glyph from composites, kerning, groups and all layers" ]
        self.radioBoxKeepReplaced = wx.RadioBox( sbSizerOptions.GetStaticBox(), wx.ID_ANY, u"Replaced glyph", wx.DefaultPosition, wx.DefaultSize, radioBoxKeepReplacedChoices, 1, wx.RA_SPECIFY_COLS )
        self.radioBoxKeepReplaced.SetSelection( 0 )
        bSizer8.Add( self.radioBoxKeepReplaced, 0, wx.ALL, 5 )

        self.staticline = wx.StaticLine( sbSizerOptions.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer8.Add( self.staticline, 0, wx.BOTTOM|wx.EXPAND|wx.TOP, 5 )

        self.checkBoxInComposites = wx.CheckBox( sbSizerOptions.GetStaticBox(), wx.ID_ANY, u"Rename glyph in all composites", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer8.Add( self.checkBoxInComposites, 0, wx.ALL|wx.EXPAND, 5 )

        self.checkBoxInKerning = wx.CheckBox( sbSizerOptions.GetStaticBox(), wx.ID_ANY, u"Rename glyph in all kerning pairs", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer8.Add( self.checkBoxInKerning, 0, wx.ALL|wx.EXPAND, 5 )

        self.checkBoxInGroups = wx.CheckBox( sbSizerOptions.GetStaticBox(), wx.ID_ANY, u"Rename glyph in all groups", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer8.Add( self.checkBoxInGroups, 0, wx.ALL|wx.EXPAND, 5 )

        self.checkBoxInFeatures = wx.CheckBox( sbSizerOptions.GetStaticBox(), wx.ID_ANY, u"Rename glyph in feature code", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer8.Add( self.checkBoxInFeatures, 0, wx.ALL|wx.EXPAND, 5 )

        self.checkBoxAllLayers = wx.CheckBox( sbSizerOptions.GetStaticBox(), wx.ID_ANY, u"Rename glyph on all layers", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer8.Add( self.checkBoxAllLayers, 0, wx.ALL, 5 )


        sbSizerOptions.Add( bSizer8, 0, wx.EXPAND, 5 )


        sizer.Add( sbSizerOptions, 0, wx.ALL|wx.EXPAND, 5 )

        buttonSizer = wx.StdDialogButtonSizer()
        self.buttonSizerOK = wx.Button( self, wx.ID_OK )
        buttonSizer.AddButton( self.buttonSizerOK )
        self.buttonSizerCancel = wx.Button( self, wx.ID_CANCEL )
        buttonSizer.AddButton( self.buttonSizerCancel )
        buttonSizer.Realize();

        sizer.Add( buttonSizer, 0, wx.ALL|wx.EXPAND, 5 )


        self.SetSizer( sizer )
        self.Layout()
        sizer.Fit( self )

        self.Centre( wx.BOTH )

        # Connect Events
        self.buttonAutoName.Bind( wx.EVT_BUTTON, self.on_buttonAutoName )
        self.buttonAutoName.Bind( wx.EVT_UPDATE_UI, self.update_buttonAutoName )
        self.buttonAutoUni.Bind( wx.EVT_BUTTON, self.on_buttonAutoUni )
        self.buttonAutoUni.Bind( wx.EVT_UPDATE_UI, self.update_buttonAutoUni )
        self.checkBoxReplaceExisting.Bind( wx.EVT_UPDATE_UI, self.update_checkBoxReplaceExisting )
        self.checkBoxKeepReplaced.Bind( wx.EVT_UPDATE_UI, self.update_checkBoxKeepReplaced )
        self.radioBoxKeepReplaced.Bind( wx.EVT_UPDATE_UI, self.update_radioBoxKeepReplaced )
        self.checkBoxInComposites.Bind( wx.EVT_UPDATE_UI, self.update_checkBoxInComposites )
        self.checkBoxInKerning.Bind( wx.EVT_UPDATE_UI, self.update_checkBoxInKerning )
        self.checkBoxInGroups.Bind( wx.EVT_UPDATE_UI, self.update_checkBoxInGroups )
        self.checkBoxInFeatures.Bind( wx.EVT_UPDATE_UI, self.update_checkBoxInFeatures )
        self.buttonSizerOK.Bind( wx.EVT_BUTTON, self.on_buttonOK )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def on_buttonAutoName( self, event ):
        event.Skip()

    def update_buttonAutoName( self, event ):
        event.Skip()

    def on_buttonAutoUni( self, event ):
        event.Skip()

    def update_buttonAutoUni( self, event ):
        event.Skip()

    def update_checkBoxReplaceExisting( self, event ):
        event.Skip()

    def update_checkBoxKeepReplaced( self, event ):
        event.Skip()

    def update_radioBoxKeepReplaced( self, event ):
        event.Skip()

    def update_checkBoxInComposites( self, event ):
        event.Skip()

    def update_checkBoxInKerning( self, event ):
        event.Skip()

    def update_checkBoxInGroups( self, event ):
        event.Skip()

    def update_checkBoxInFeatures( self, event ):
        event.Skip()

    def on_buttonOK( self, event ):
        event.Skip()


