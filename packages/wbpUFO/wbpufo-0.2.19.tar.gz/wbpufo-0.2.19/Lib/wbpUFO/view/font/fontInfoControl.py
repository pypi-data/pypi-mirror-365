"""
fontInfoControl
===============================================================================

"""
import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin, TextEditMixin


class BitList(wx.CheckListBox):
    def __init__(
        self,
        parent: wx.Window,
        id: int = wx.ID_ANY,
        pos: wx.Point = wx.DefaultPosition,
        size: wx.Size = wx.DefaultSize,
        choices=None,
        style: int = wx.LB_EXTENDED | wx.LB_NEEDED_SB,
        validator: wx.Validator = wx.DefaultValidator,
        name: str = "BitList",
    ):
        if not choices:
            choices = []
        super().__init__(parent, id, pos, size, choices, style, validator, name)

    def GetValue(self):
        return list(self.GetCheckedItems())

    def SetValue(self, bitList):
        self.SetCheckedItems(bitList)

    Value = property(GetValue, SetValue)


class CodePageBitList(BitList):
    def __init__(
        self,
        parent: wx.Window,
        id: int = wx.ID_ANY,
        pos: wx.Point = wx.DefaultPosition,
        size: wx.Size = wx.DefaultSize,
        choices=None,
        style: int = wx.LB_EXTENDED | wx.LB_MULTIPLE | wx.LB_NEEDED_SB,
        validator: wx.Validator = wx.DefaultValidator,
        name: str = "openTypeOS2CodePageRanges",
    ):
        choices = [
            "Latin 1 (1252)",
            "Latin 2 Eastern Europe (1250)",
            "Cyrillic (1251)",
            "Greek (1253)",
            "Turkish (1254)",
            "Hebrew (1255)",
            "Arabic (1256)",
            "Windows Baltic (1257)",
            "Vietnamese (1258)",
            "Reserved for Alternate ANSI",
            "Reserved for Alternate ANSI",
            "Reserved for Alternate ANSI",
            "Reserved for Alternate ANSI",
            "Reserved for Alternate ANSI",
            "Reserved for Alternate ANSI",
            "Reserved for Alternate ANSI",
            "Thai (874)",
            "JIS/Japan (932)",
            "Chinese Simplified PRC and Singapore (936)",
            "Korean Wansung (949)",
            "Chinese Traditional Taiwan and Hong Kong (950)",
            "Korean Johab (1361)",
            "Reserved for Alternate ANSI & OEM",
            "Reserved for Alternate ANSI & OEM",
            "Reserved for Alternate ANSI & OEM",
            "Reserved for Alternate ANSI & OEM",
            "Reserved for Alternate ANSI & OEM",
            "Reserved for Alternate ANSI & OEM",
            "Reserved for Alternate ANSI & OEM",
            "Macintosh Character Set (US Roman)",
            "OEM Character Set",
            "Symbol Character Set",
            "Reserved for OEM",
            "Reserved for OEM",
            "Reserved for OEM",
            "Reserved for OEM",
            "Reserved for OEM",
            "Reserved for OEM",
            "Reserved for OEM",
            "Reserved for OEM",
            "Reserved for OEM",
            "Reserved for OEM",
            "Reserved for OEM",
            "Reserved for OEM",
            "Reserved for OEM",
            "Reserved for OEM",
            "Reserved for OEM",
            "Reserved for OEM",
            "IBM Greek (869)",
            "MS-DOS Russian ()",
            "MS-DOS Nordic (866)",
            "Arabic (864)",
            "MS-DOS Canadian French (863)",
            "Hebrew (862)",
            "MS-DOS Icelandic (861)",
            "MS-DOS Portuguese (860)",
            "IBM Turkish (857)",
            "IBM Cyrillic; primarily Russian (855)",
            "Latin 2 (852)",
            "MS-DOS Baltic (775)",
            "Greek; former 437 G (737)",
            "Arabic; ASMO 708 (708)",
            "WE/Latin 1 (850)",
            "US (437)",
        ]

        super().__init__(parent, id, pos, size, choices, style, validator, name)


class UnicodeRangeBitList(BitList):
    def __init__(
        self,
        parent: wx.Window,
        id: int = wx.ID_ANY,
        pos: wx.Point = wx.DefaultPosition,
        size: wx.Size = wx.DefaultSize,
        choices=None,
        style=wx.LB_EXTENDED | wx.LB_MULTIPLE | wx.LB_NEEDED_SB,
        validator: wx.Validator = wx.DefaultValidator,
        name: str = "openTypeOS2UnicodeRanges",
    ):
        choices = [
            "Basic Latin",
            "Latin-1 Supplement",
            "Latin Extended-A",
            "Latin Extended-B",
            "IPA Extensions",
            "Spacing Modifier Letters",
            "Combining Diacritical Marks",
            "Greek and Coptic",
            "Coptic",
            "Cyrillic",
            "Armenian",
            "Hebrew",
            "Vai",
            "Arabic",
            "NKo",
            "Devanagari",
            "Bengali",
            "Gurmukhi",
            "Gujarati",
            "Oriya",
            "Tamil",
            "Telugu",
            "Kannada",
            "Malayalam",
            "Thai",
            "Lao",
            "Georgian",
            "Balinese",
            "Hangul Jamo",
            "Latin Extended Additional",
            "Greek Extended",
            "General Punctuation",
            "Superscripts And Subscripts",
            "Currency Symbols",
            "Combining Diacritical Marks For Symbols",
            "Letterlike Symbols",
            "Number Forms",
            "Arrows",
            "Mathematical Operators",
            "Miscellaneous Technical",
            "Control Pictures",
            "Optical Character Recognition",
            "Enclosed Alphanumerics",
            "Box Drawing",
            "Block Elements",
            "Geometric Shapes",
            "Miscellaneous Symbols",
            "Dingbats",
            "CJK Symbols And Punctuation",
            "Hiragana",
            "Katakana",
            "Bopomofo",
            "Hangul Compatibility Jamo",
            "Phags-pa",
            "Enclosed CJK Letters And Months",
            "CJK Compatibility",
            "Hangul Syllables",
            "Non-Plane 0 *",
            "Phoenician",
            "CJK Unified Ideographs",
            "Private Use Area (plane 0)",
            "CJK Strokes",
            "Alphabetic Presentation Forms",
            "Arabic Presentation Forms-A",
            "Combining Half Marks",
            "Vertical Forms",
            "Small Form Variants",
            "Arabic Presentation Forms-B",
            "Halfwidth And Fullwidth Forms",
            "Specials",
            "Tibetan",
            "Syriac",
            "Thaana",
            "Sinhala",
            "Myanmar",
            "Ethiopic",
            "Cherokee",
            "Unified Canadian Aboriginal Syllabics",
            "Ogham",
            "Runic",
            "Khmer",
            "Mongolian",
            "Braille Patterns",
            "Yi Syllables and Radicals",
            "Tagalog, Hanunoo, Buhid, Tagbanwa",
            "Old Italic",
            "Gothic",
            "Deseret",
            "Musical Symbols Byzantine and Ancient Greek",
            "Mathematical Alphanumeric Symbols",
            "Private Use (plane 15 and 16)",
            "Variation Selectors",
            "Tags",
            "Limbu",
            "Tai Le",
            "New Tai Lue",
            "Buginese",
            "Glagolitic",
            "Tifinagh",
            "Yijing Hexagram Symbols",
            "Syloti Nagri",
            "Linear B Syllabary and Ideograms",
            "Ancient Greek Numbers",
            "Ugaritic",
            "Old Persian",
            "Shavian",
            "Osmanya",
            "Cypriot Syllabary",
            "Kharoshthi",
            "Tai Xuan Jing Symbols",
            "Cuneiform",
            "Counting Rod Numerals",
            "Sundanese",
            "Lepcha",
            "Ol Chiki",
            "Saurashtra",
            "Kayah Li",
            "Rejang",
            "Cham",
            "Ancient Symbols",
            "Phaistos Disc",
            "Carian, Lycian, Lydian",
            "Domino and Mahjong Tiles",
            "Reserved for process-internal usage",
            "Reserved for process-internal usage",
            "Reserved for process-internal usage",
            "Reserved for process-internal usage",
            "Reserved for process-internal usage",
        ]

        super().__init__(parent, id, pos, size, choices, style, validator, name)


class BlueListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin, TextEditMixin):
    maxItems = 7

    def __init__(
        self,
        parent: wx.Window,
        id: int = wx.ID_ANY,
        pos: wx.Point = wx.DefaultPosition,
        size: wx.Size = wx.DefaultSize,
        style: int = wx.LC_REPORT | wx.LC_VIRTUAL,
        name: str = "BlueListCtrl",
    ):
        wx.ListCtrl.__init__(self, parent, id, pos, size, style, name=name)
        self._font = None
        ListCtrlAutoWidthMixin.__init__(self)
        self.InsertColumn(0, "Top")
        self.InsertColumn(1, "Bottom")
        self.InsertColumn(2, "Width")
        self.SetItemCount(0)
        TextEditMixin.__init__(self)
