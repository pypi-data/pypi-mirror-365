# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Oct 26 2018)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

from ..control.findGlyphListCtrl import FindGlyphListCtrl
import wx
import wx.xrc

###########################################################################
## Class FindGlyphDialogUI
###########################################################################

class FindGlyphDialogUI ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Find Glyph", pos = wx.DefaultPosition, size = wx.Size( 400,400 ), style = wx.CAPTION|wx.RESIZE_BORDER )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		sizerMain = wx.FlexGridSizer( 0, 1, 0, 0 )
		sizerMain.AddGrowableCol( 0 )
		sizerMain.AddGrowableRow( 1 )
		sizerMain.SetFlexibleDirection( wx.BOTH )
		sizerMain.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		sizerTop = wx.BoxSizer( wx.HORIZONTAL )

		choice_findAttrChoices = [ u"Name", u"Unicode" ]
		self.choice_findAttr = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choice_findAttrChoices, 0 )
		self.choice_findAttr.SetSelection( 0 )
		sizerTop.Add( self.choice_findAttr, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		choice_findCompareChoices = [ u"equals to", u"starts with", u"ends with", u"contains" ]
		self.choice_findCompare = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choice_findCompareChoices, 0 )
		self.choice_findCompare.SetSelection( 1 )
		sizerTop.Add( self.choice_findCompare, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.textCtrl_findValue = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		sizerTop.Add( self.textCtrl_findValue, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		sizerMain.Add( sizerTop, 0, wx.EXPAND, 5 )

		sizerCenter = wx.BoxSizer( wx.HORIZONTAL )

		self.listCtrl_glyphs = FindGlyphListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_NO_HEADER|wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_SORT_ASCENDING|wx.LC_VIRTUAL )
		sizerCenter.Add( self.listCtrl_glyphs, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )

		self.bitmapGlyph = wx.StaticBitmap( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( 72,72 ), 0 )
		sizerCenter.Add( self.bitmapGlyph, 0, wx.LEFT|wx.RIGHT, 5 )


		sizerMain.Add( sizerCenter, 1, wx.EXPAND, 5 )

		self.staticline = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		sizerMain.Add( self.staticline, 0, wx.BOTTOM|wx.EXPAND|wx.TOP, 5 )

		sizerBottom = wx.BoxSizer( wx.HORIZONTAL )

		self.checkBox_create = wx.CheckBox( self, wx.ID_ANY, u"Create unexisting", wx.DefaultPosition, wx.DefaultSize, 0 )
		sizerBottom.Add( self.checkBox_create, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.buttonSelect = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )

		self.buttonSelect.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_TICK_MARK, wx.ART_BUTTON ) )
		self.buttonSelect.Enable( False )
		self.buttonSelect.SetToolTip( u"Select all glyphs in the list" )

		sizerBottom.Add( self.buttonSelect, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		sizerDialogButtons = wx.StdDialogButtonSizer()
		self.sizerDialogButtonsOK = wx.Button( self, wx.ID_OK )
		sizerDialogButtons.AddButton( self.sizerDialogButtonsOK )
		self.sizerDialogButtonsCancel = wx.Button( self, wx.ID_CANCEL )
		sizerDialogButtons.AddButton( self.sizerDialogButtonsCancel )
		sizerDialogButtons.Realize();

		sizerBottom.Add( sizerDialogButtons, 1, wx.ALIGN_CENTER_VERTICAL, 5 )


		sizerMain.Add( sizerBottom, 0, wx.EXPAND, 5 )


		self.SetSizer( sizerMain )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.choice_findAttr.Bind( wx.EVT_CHOICE, self.onfindAttr_CHOICE )
		self.choice_findCompare.Bind( wx.EVT_CHOICE, self.onfindCompare_CHOICE )
		self.textCtrl_findValue.Bind( wx.EVT_TEXT, self.on_TEXT )
		self.textCtrl_findValue.Bind( wx.EVT_TEXT_ENTER, self.on_TEXT_ENTER )
		self.listCtrl_glyphs.Bind( wx.EVT_LIST_ITEM_ACTIVATED, self.on_LIST_ITEM_ACTIVATED )
		self.listCtrl_glyphs.Bind( wx.EVT_LIST_ITEM_SELECTED, self.on_LIST_ITEM_SELECTED )
		self.buttonSelect.Bind( wx.EVT_BUTTON, self.on_buttonSelect )
		self.buttonSelect.Bind( wx.EVT_UPDATE_UI, self.update_buttonSelect )

	def __del__( self ):
		pass


	# Virtual event handlers, overide them in your derived class
	def onfindAttr_CHOICE( self, event ):
		event.Skip()

	def onfindCompare_CHOICE( self, event ):
		event.Skip()

	def on_TEXT( self, event ):
		event.Skip()

	def on_TEXT_ENTER( self, event ):
		event.Skip()

	def on_LIST_ITEM_ACTIVATED( self, event ):
		event.Skip()

	def on_LIST_ITEM_SELECTED( self, event ):
		event.Skip()

	def on_buttonSelect( self, event ):
		event.Skip()

	def update_buttonSelect( self, event ):
		event.Skip()


