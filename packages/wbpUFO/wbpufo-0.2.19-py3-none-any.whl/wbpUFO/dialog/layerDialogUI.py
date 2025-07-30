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
## Class LayerDialogUI
###########################################################################

class LayerDialogUI ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Layer", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.CAPTION )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        sizer = wx.FlexGridSizer( 0, 2, 0, 0 )
        sizer.AddGrowableCol( 1 )
        sizer.SetFlexibleDirection( wx.BOTH )
        sizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.lbl_name = wx.StaticText( self, wx.ID_ANY, u"Name", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_name.Wrap( -1 )

        sizer.Add( self.lbl_name, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.textCtrl_name = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.textCtrl_name.SetMinSize( wx.Size( 150,-1 ) )

        sizer.Add( self.textCtrl_name, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.lbl_Color = wx.StaticText( self, wx.ID_ANY, u"Color", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_Color.Wrap( -1 )

        sizer.Add( self.lbl_Color, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.colourPicker = wx.ColourPickerCtrl( self, wx.ID_ANY, wx.Colour( 255, 255, 255 ), wx.DefaultPosition, wx.DefaultSize, wx.CLRP_DEFAULT_STYLE )
        sizer.Add( self.colourPicker, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )


        sizer.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        sizer_button = wx.StdDialogButtonSizer()
        self.sizer_buttonOK = wx.Button( self, wx.ID_OK )
        sizer_button.AddButton( self.sizer_buttonOK )
        self.sizer_buttonCancel = wx.Button( self, wx.ID_CANCEL )
        sizer_button.AddButton( self.sizer_buttonCancel )
        sizer_button.Realize();

        sizer.Add( sizer_button, 1, wx.ALL|wx.EXPAND, 5 )


        self.SetSizer( sizer )
        self.Layout()
        sizer.Fit( self )

        self.Centre( wx.BOTH )

    def __del__( self ):
        pass


