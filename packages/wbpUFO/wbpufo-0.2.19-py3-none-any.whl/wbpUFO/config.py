"""
config
===============================================================================
"""
import wx

pluginName = "ufo"

NODESHAPE_CIRCLE = 0
NODESHAPE_SQUARE = 1
NODESHAPE_DIAMOND = 2
NODESHAPE_TRIANGLE = 3
NODESHAPE_STAR = 4

# read values pens and brushes from the config


def cfgBrush(name, default):
    cfg = wx.GetApp().config
    cfg.SetPath("/Plugin/%s/GlyphNodes/%s" % (pluginName, name))
    if cfg.HasEntry("brush"):
        try:
            r, g, b, a, style = [int(c) for c in cfg.Read("brush").split()]
            return wx.TheBrushList.FindOrCreateBrush(wx.Colour(r, g, b, a), style)
        except:
            return default
    return default


def cfgPen(name, default):
    cfg = wx.GetApp().config
    cfg.SetPath("/Plugin/%s/GlyphNodes/%s" % (pluginName, name))
    if cfg.HasEntry("pen"):
        try:
            r, g, b, a, width, style = [int(c) for c in cfg.Read("pen").split()]
            return wx.ThePenList.FindOrCreatePen(wx.Colour(r, g, b, a), width, style)
        except:
            return default
    return default


def cfgShape(name, default):
    cfg = wx.GetApp().config
    cfg.SetPath("/Plugin/%s/GlyphNodes/%s" % (pluginName, name))
    if cfg.HasEntry("shape"):
        try:
            return cfg.ReadInt("shape")
        except:
            return default
    return default


def cfgSize(name, default):
    cfg = wx.GetApp().config
    cfg.SetPath("/Plugin/%s/GlyphNodes/%s" % (pluginName, name))
    if cfg.HasEntry("size"):
        try:
            return cfg.ReadInt("size")
        except:
            return default
    return default


def cfgRedArrowOption():
    result = {}
    cfg = wx.GetApp().config
    cfg.SetPath("/Plugin/%s/RedArrow" % (pluginName))
    result["collinear_vectors_max_distance"] = cfg.ReadInt(
        "collinear_vectors_max_distance", 2
    )
    result["extremum_calculate_badness"] = cfg.ReadBool(
        "extremum_calculate_badness", True
    )
    result["extremum_ignore_badness_below"] = cfg.ReadInt(
        "extremum_ignore_badness_below", 1
    )
    result["fractional_ignore_point_zero"] = cfg.ReadBool(
        "fractional_ignore_point_zero", True
    )
    result["smooth_connection_max_distance"] = cfg.ReadInt(
        "smooth_connection_max_distance", 4
    )
    result["semi_hv_vectors_min_distance"] = cfg.ReadInt(
        "semi_hv_vectors_min_distance", 30
    )
    result["zero_handles_max_distance"] = cfg.ReadInt("zero_handles_max_distance", 0)
    return result


def cfgRedArrowTest():
    all_tests = [
        "test_extrema",
        "test_fractional_coords",
        "test_fractional_transform",
        "test_smooth",
        "test_empty_segments",
        "test_collinear",
        "test_semi_hv",
        "test_closepath",
        "test_zero_handles",
        "test_bbox_handles",
    ]
    result = []
    cfg = wx.GetApp().config
    cfg.SetPath("/Plugin/%s/RedArrow" % (pluginName))
    for name in all_tests:
        if cfg.ReadBool(name, True):
            result.append(name)
    return result
