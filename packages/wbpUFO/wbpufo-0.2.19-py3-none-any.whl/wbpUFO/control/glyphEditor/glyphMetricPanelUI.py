# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 4.2.1-0-g80c4cb6)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class GlyphMetricPanelUI
###########################################################################

class GlyphMetricPanelUI ( wx.Panel ):

    def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.BORDER_NONE|wx.TAB_TRAVERSAL, name = u"GlyphMetricPanel" ):
        wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

        sizer = wx.BoxSizer( wx.HORIZONTAL )

        self.label_lsb = wx.StaticText( self, wx.ID_ANY, u"LSB", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.label_lsb.Wrap( -1 )

        sizer.Add( self.label_lsb, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.spinCtrlDouble_LSB = wx.SpinCtrlDouble( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT|wx.SP_ARROW_KEYS, -100000, 100000, 0.000000, 1 )
        self.spinCtrlDouble_LSB.SetDigits( 0 )
        self.spinCtrlDouble_LSB.Enable( False )

        sizer.Add( self.spinCtrlDouble_LSB, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5 )

        self.label_width = wx.StaticText( self, wx.ID_ANY, u"Width", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.label_width.Wrap( -1 )

        sizer.Add( self.label_width, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.spinCtrlDouble_width = wx.SpinCtrlDouble( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT|wx.SP_ARROW_KEYS, -100000, 100000, 0, 1 )
        self.spinCtrlDouble_width.SetDigits( 0 )
        self.spinCtrlDouble_width.Enable( False )

        sizer.Add( self.spinCtrlDouble_width, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.label_RSB = wx.StaticText( self, wx.ID_ANY, u"RSB", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.label_RSB.Wrap( -1 )

        sizer.Add( self.label_RSB, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.spinCtrlDouble_RSB = wx.SpinCtrlDouble( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT|wx.SP_ARROW_KEYS, -100000, 100000, 0, 1 )
        self.spinCtrlDouble_RSB.SetDigits( 0 )
        self.spinCtrlDouble_RSB.Enable( False )

        sizer.Add( self.spinCtrlDouble_RSB, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5 )


        self.SetSizer( sizer )
        self.Layout()
        sizer.Fit( self )

        # Connect Events
        self.spinCtrlDouble_LSB.Bind( wx.EVT_SPINCTRLDOUBLE, self.on_spinCtrlDouble_LSB )
        self.spinCtrlDouble_LSB.Bind( wx.EVT_UPDATE_UI, self.onUpdate_spinCtrlDouble_LSB )
        self.spinCtrlDouble_width.Bind( wx.EVT_SPINCTRLDOUBLE, self.on_spinCtrlDouble_width )
        self.spinCtrlDouble_width.Bind( wx.EVT_UPDATE_UI, self.onUpdate_spinCtrlDouble_width )
        self.spinCtrlDouble_RSB.Bind( wx.EVT_SPINCTRLDOUBLE, self.on_spinCtrlDouble_RSB )
        self.spinCtrlDouble_RSB.Bind( wx.EVT_UPDATE_UI, self.onUpdate_spinCtrlDouble_RSB )

    def __del__( self ):
        pass


    # Virtual event handlers, override them in your derived class
    def on_spinCtrlDouble_LSB( self, event ):
        event.Skip()

    def onUpdate_spinCtrlDouble_LSB( self, event ):
        event.Skip()

    def on_spinCtrlDouble_width( self, event ):
        event.Skip()

    def onUpdate_spinCtrlDouble_width( self, event ):
        event.Skip()

    def on_spinCtrlDouble_RSB( self, event ):
        event.Skip()

    def onUpdate_spinCtrlDouble_RSB( self, event ):
        event.Skip()


