# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.1-0-g8feb16b3)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

from .fontInfoBase import FontInfoBasePage
import wx
import wx.xrc

###########################################################################
## Class FontInfoIdentificationUI
###########################################################################

class FontInfoIdentificationUI ( FontInfoBasePage ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,438 ), style = 0, name = u"FontInfoIdentification" ):
		FontInfoBasePage.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		self.SetBackgroundColour( wx.Colour( 255, 255, 255 ) )

		sizer = wx.BoxSizer( wx.VERTICAL )

		boxMain = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Main" ), wx.VERTICAL )

		gridMain = wx.FlexGridSizer( 0, 2, 0, 0 )
		gridMain.AddGrowableCol( 1 )
		gridMain.SetFlexibleDirection( wx.BOTH )
		gridMain.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.lbl_versionMajor = wx.StaticText( boxMain.GetStaticBox(), wx.ID_ANY, u"Version Major", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_versionMajor.Wrap( -1 )

		self.lbl_versionMajor.SetMinSize( wx.Size( 170,-1 ) )

		gridMain.Add( self.lbl_versionMajor, 0, wx.ALL, 5 )

		self.txtCrtl_versionMajor = wx.TextCtrl( boxMain.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"versionMajor" )
		gridMain.Add( self.txtCrtl_versionMajor, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.lbl_versionMinor = wx.StaticText( boxMain.GetStaticBox(), wx.ID_ANY, u"Version Minor", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_versionMinor.Wrap( -1 )

		gridMain.Add( self.lbl_versionMinor, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.txtCrtl_versionMinor = wx.TextCtrl( boxMain.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"versionMinor" )
		gridMain.Add( self.txtCrtl_versionMinor, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.lbl_year = wx.StaticText( boxMain.GetStaticBox(), wx.ID_ANY, u"Year", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_year.Wrap( -1 )

		gridMain.Add( self.lbl_year, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.txtCtrl_year = wx.TextCtrl( boxMain.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"year" )
		gridMain.Add( self.txtCtrl_year, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		boxMain.Add( gridMain, 1, wx.EXPAND, 5 )


		sizer.Add( boxMain, 0, wx.ALL|wx.EXPAND, 5 )

		boxOTname = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"OpenType Name Table" ), wx.VERTICAL )

		gridOTname = wx.FlexGridSizer( 0, 2, 0, 0 )
		gridOTname.AddGrowableCol( 1 )
		gridOTname.AddGrowableRow( 2 )
		gridOTname.AddGrowableRow( 3 )
		gridOTname.SetFlexibleDirection( wx.BOTH )
		gridOTname.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.lbl_openTypeNameVersion = wx.StaticText( boxOTname.GetStaticBox(), wx.ID_ANY, u"Version String", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_openTypeNameVersion.Wrap( -1 )

		self.lbl_openTypeNameVersion.SetMinSize( wx.Size( 170,-1 ) )

		gridOTname.Add( self.lbl_openTypeNameVersion, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.txtCrtl_openTypeNameVersion = wx.TextCtrl( boxOTname.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeNameVersion" )
		gridOTname.Add( self.txtCrtl_openTypeNameVersion, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )

		self.lbl_openTypeNameUniqueID = wx.StaticText( boxOTname.GetStaticBox(), wx.ID_ANY, u"Unique ID", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_openTypeNameUniqueID.Wrap( -1 )

		gridOTname.Add( self.lbl_openTypeNameUniqueID, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.txtCrtl_openTypeNameUniqueID = wx.TextCtrl( boxOTname.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeNameUniqueID" )
		gridOTname.Add( self.txtCrtl_openTypeNameUniqueID, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )

		self.lbl_openTypeNameDescription = wx.StaticText( boxOTname.GetStaticBox(), wx.ID_ANY, u"Description", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_openTypeNameDescription.Wrap( -1 )

		gridOTname.Add( self.lbl_openTypeNameDescription, 0, wx.ALL, 5 )

		self.txtCtrl_openTypeNameDescription = wx.TextCtrl( boxOTname.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE, wx.DefaultValidator, u"openTypeNameDescription" )
		gridOTname.Add( self.txtCtrl_openTypeNameDescription, 1, wx.ALL|wx.EXPAND, 5 )

		self.lbl_openTypeNameSampleText = wx.StaticText( boxOTname.GetStaticBox(), wx.ID_ANY, u"Sample Text", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_openTypeNameSampleText.Wrap( -1 )

		gridOTname.Add( self.lbl_openTypeNameSampleText, 0, wx.ALL, 5 )

		self.txtCtrl_openTypeNameSampleText = wx.TextCtrl( boxOTname.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE, wx.DefaultValidator, u"openTypeNameSampleText" )
		gridOTname.Add( self.txtCtrl_openTypeNameSampleText, 1, wx.ALL|wx.EXPAND, 5 )


		boxOTname.Add( gridOTname, 1, wx.EXPAND, 5 )


		sizer.Add( boxOTname, 1, wx.ALL|wx.EXPAND, 5 )

		boxPostScript = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"PostScript" ), wx.VERTICAL )

		gridPostScript = wx.FlexGridSizer( 0, 2, 0, 0 )
		gridPostScript.AddGrowableCol( 1 )
		gridPostScript.SetFlexibleDirection( wx.BOTH )
		gridPostScript.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.lbl_postscriptUniqueID = wx.StaticText( boxPostScript.GetStaticBox(), wx.ID_ANY, u"Unique ID", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_postscriptUniqueID.Wrap( -1 )

		self.lbl_postscriptUniqueID.SetMinSize( wx.Size( 170,-1 ) )

		gridPostScript.Add( self.lbl_postscriptUniqueID, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.txtCtrl_postscriptUniqueID = wx.TextCtrl( boxPostScript.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"postscriptUniqueID" )
		gridPostScript.Add( self.txtCtrl_postscriptUniqueID, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		boxPostScript.Add( gridPostScript, 1, wx.EXPAND, 5 )


		sizer.Add( boxPostScript, 0, wx.ALL|wx.EXPAND, 5 )


		self.SetSizer( sizer )
		self.Layout()

	def __del__( self ):
		pass


