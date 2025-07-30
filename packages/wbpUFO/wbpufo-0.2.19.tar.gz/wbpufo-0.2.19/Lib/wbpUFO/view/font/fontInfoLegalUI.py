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
## Class FontInfoLegalUI
###########################################################################

class FontInfoLegalUI ( FontInfoBasePage ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,544 ), style = 0, name = u"FontInfoLegal" ):
		FontInfoBasePage.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		self.SetBackgroundColour( wx.Colour( 255, 255, 255 ) )

		sizer = wx.BoxSizer( wx.VERTICAL )

		boxMain = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Main" ), wx.VERTICAL )

		gridMain = wx.FlexGridSizer( 0, 2, 0, 0 )
		gridMain.AddGrowableCol( 1 )
		gridMain.AddGrowableRow( 0 )
		gridMain.AddGrowableRow( 1 )
		gridMain.SetFlexibleDirection( wx.HORIZONTAL )
		gridMain.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.lbl_copyright = wx.StaticText( self, wx.ID_ANY, u"Copyright", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_copyright.Wrap( -1 )

		self.lbl_copyright.SetMinSize( wx.Size( 170,-1 ) )

		gridMain.Add( self.lbl_copyright, 0, wx.ALL, 5 )

		self.txtCtrl_copyright = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE, wx.DefaultValidator, u"copyright" )
		gridMain.Add( self.txtCtrl_copyright, 1, wx.ALL|wx.EXPAND, 5 )

		self.lbl_trademark = wx.StaticText( self, wx.ID_ANY, u"Trademark", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_trademark.Wrap( -1 )

		gridMain.Add( self.lbl_trademark, 0, wx.ALL, 5 )

		self.txtCtrl_trademark = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE, wx.DefaultValidator, u"trademark" )
		gridMain.Add( self.txtCtrl_trademark, 1, wx.ALL|wx.EXPAND, 5 )


		boxMain.Add( gridMain, 1, wx.EXPAND, 5 )


		sizer.Add( boxMain, 1, wx.ALL|wx.EXPAND, 5 )

		boxOpentype = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"OpenType" ), wx.VERTICAL )

		gridOpenType = wx.FlexGridSizer( 0, 2, 0, 0 )
		gridOpenType.AddGrowableCol( 1 )
		gridOpenType.AddGrowableRow( 5 )
		gridOpenType.SetFlexibleDirection( wx.BOTH )
		gridOpenType.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.lbl_openTypeNameDesigner = wx.StaticText( boxOpentype.GetStaticBox(), wx.ID_ANY, u"Designer Name", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_openTypeNameDesigner.Wrap( -1 )

		self.lbl_openTypeNameDesigner.SetMinSize( wx.Size( 170,-1 ) )

		gridOpenType.Add( self.lbl_openTypeNameDesigner, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.txtCtrl_openTypeNameDesigner = wx.TextCtrl( boxOpentype.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeNameDesigner" )
		gridOpenType.Add( self.txtCtrl_openTypeNameDesigner, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )

		self.lbl_openTypeNameDesignerURL = wx.StaticText( boxOpentype.GetStaticBox(), wx.ID_ANY, u"Designer URL", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_openTypeNameDesignerURL.Wrap( -1 )

		gridOpenType.Add( self.lbl_openTypeNameDesignerURL, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.txtCtrl_openTypeNameDesignerURL = wx.TextCtrl( boxOpentype.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeNameDesignerURL" )
		gridOpenType.Add( self.txtCtrl_openTypeNameDesignerURL, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )

		self.lbl_openTypeNameManufacturer = wx.StaticText( boxOpentype.GetStaticBox(), wx.ID_ANY, u"Manufacturer Name", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_openTypeNameManufacturer.Wrap( -1 )

		gridOpenType.Add( self.lbl_openTypeNameManufacturer, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.txtCtrl_openTypeNameManufacturer = wx.TextCtrl( boxOpentype.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeNameManufacturer" )
		gridOpenType.Add( self.txtCtrl_openTypeNameManufacturer, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )

		self.lbl_openTypeNameManufacturerURL = wx.StaticText( boxOpentype.GetStaticBox(), wx.ID_ANY, u"Manufacturer URL", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_openTypeNameManufacturerURL.Wrap( -1 )

		gridOpenType.Add( self.lbl_openTypeNameManufacturerURL, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.txtCtrl_openTypeNameManufacturerURL = wx.TextCtrl( boxOpentype.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeNameManufacturerURL" )
		gridOpenType.Add( self.txtCtrl_openTypeNameManufacturerURL, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )

		self.lbl_openTypeOS2VendorID = wx.StaticText( boxOpentype.GetStaticBox(), wx.ID_ANY, u"Vendor ID", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_openTypeOS2VendorID.Wrap( -1 )

		gridOpenType.Add( self.lbl_openTypeOS2VendorID, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.txtCtrl_openTypeOS2VendorID = wx.TextCtrl( boxOpentype.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeOS2VendorID" )
		gridOpenType.Add( self.txtCtrl_openTypeOS2VendorID, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.lbl_openTypeNameLicense = wx.StaticText( boxOpentype.GetStaticBox(), wx.ID_ANY, u"License Text", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_openTypeNameLicense.Wrap( -1 )

		gridOpenType.Add( self.lbl_openTypeNameLicense, 0, wx.ALL, 5 )

		self.txtCtrl_openTypeNameLicense = wx.TextCtrl( boxOpentype.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE, wx.DefaultValidator, u"openTypeNameLicense" )
		gridOpenType.Add( self.txtCtrl_openTypeNameLicense, 1, wx.ALL|wx.EXPAND, 5 )

		self.lbl_openTypeNameLicenseURL = wx.StaticText( boxOpentype.GetStaticBox(), wx.ID_ANY, u"License URL", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_openTypeNameLicenseURL.Wrap( -1 )

		gridOpenType.Add( self.lbl_openTypeNameLicenseURL, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.txtCtrl_openTypeNameLicenseURL = wx.TextCtrl( boxOpentype.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"openTypeNameLicenseURL" )
		gridOpenType.Add( self.txtCtrl_openTypeNameLicenseURL, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )


		boxOpentype.Add( gridOpenType, 1, wx.EXPAND, 5 )


		sizer.Add( boxOpentype, 2, wx.ALL|wx.EXPAND, 5 )


		self.SetSizer( sizer )
		self.Layout()

	def __del__( self ):
		pass


