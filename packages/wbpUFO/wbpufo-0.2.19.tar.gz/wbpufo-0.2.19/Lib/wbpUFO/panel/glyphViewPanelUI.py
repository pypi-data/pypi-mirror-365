# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.0-4761b0c)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

from .glyphViewCanvas import GlyphViewCanvas
import wx
import wx.xrc

###########################################################################
## Class GlyphViewPanelUI
###########################################################################

class GlyphViewPanelUI ( wx.Panel ):

    def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 696,300 ), style = wx.TAB_TRAVERSAL, name = u"GlyphViewPanel" ):
        wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

        sizer_main = wx.BoxSizer( wx.VERTICAL )

        sizer_controls = wx.BoxSizer( wx.HORIZONTAL )

        self.lbl_font_size = wx.StaticText( self, wx.ID_ANY, u"Font Size", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_font_size.Wrap( -1 )

        sizer_controls.Add( self.lbl_font_size, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.spinCtrl_font_size = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 1000, 100 )
        sizer_controls.Add( self.spinCtrl_font_size, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.lbl_line_space = wx.StaticText( self, wx.ID_ANY, u"Line Space", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_line_space.Wrap( -1 )

        sizer_controls.Add( self.lbl_line_space, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.spinCtrl_line_space = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 2000, 120 )
        sizer_controls.Add( self.spinCtrl_line_space, 0, wx.ALL, 5 )

        self.lbl_percent = wx.StaticText( self, wx.ID_ANY, u"%", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_percent.Wrap( -1 )

        sizer_controls.Add( self.lbl_percent, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.checkBox_showKerning = wx.CheckBox( self, wx.ID_ANY, u"Show Kerning", wx.DefaultPosition, wx.DefaultSize, 0 )
        sizer_controls.Add( self.checkBox_showKerning, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        sizer_controls.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.btn_clear = wx.Button( self, wx.ID_ANY, u"Clear", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
        sizer_controls.Add( self.btn_clear, 0, wx.ALL, 5 )


        sizer_main.Add( sizer_controls, 0, wx.EXPAND, 5 )

        self.glyphViewCanvas = GlyphViewCanvas( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.ALWAYS_SHOW_SB|wx.HSCROLL|wx.VSCROLL|wx.WANTS_CHARS )
        self.glyphViewCanvas.SetScrollRate( 1, 1 )
        sizer_main.Add( self.glyphViewCanvas, 1, wx.EXPAND, 0 )


        self.SetSizer( sizer_main )
        self.Layout()

        # Connect Events
        self.spinCtrl_font_size.Bind( wx.EVT_SPINCTRL, self.on_spinCtrl_font_size )
        self.spinCtrl_line_space.Bind( wx.EVT_SPINCTRL, self.on_spinCtrl_line_space )
        self.checkBox_showKerning.Bind( wx.EVT_CHECKBOX, self.on_checkBox_showKerning )
        self.btn_clear.Bind( wx.EVT_BUTTON, self.on_btn_clear )

    def __del__( self ):
        pass


    # Virtual event handlers, override them in your derived class
    def on_spinCtrl_font_size( self, event ):
        event.Skip()

    def on_spinCtrl_line_space( self, event ):
        event.Skip()

    def on_checkBox_showKerning( self, event ):
        event.Skip()

    def on_btn_clear( self, event ):
        event.Skip()


