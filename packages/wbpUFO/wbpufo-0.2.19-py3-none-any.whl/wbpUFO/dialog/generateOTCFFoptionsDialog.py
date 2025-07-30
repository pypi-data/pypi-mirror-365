"""
generateOTCFFoptionsDialog
===============================================================================
"""
from .generateOTCFFoptionsDialogUI import GenerateOTCFFoptionsDialogUI


class GenerateOTCFFoptionsDialog(GenerateOTCFFoptionsDialogUI):
    @property
    def autohint(self):
        return self.checkBox_autohint.Value

    @property
    def cffcompress(self):
        return self.choice_cffcompress.Selection

    @property
    def removeOverlaps(self):
        return self.checkBox_removeOverlap.Value

    @property
    def useProductionNames(self):
        return self.checkBox_useProductionNames.Value

    @property
    def writeKernFeature(self):
        return self.checkBox_writeKernFeature.Value

    @property
    def writeMarkFeature(self):
        return self.checkBox_writeMarkFeature.Value
