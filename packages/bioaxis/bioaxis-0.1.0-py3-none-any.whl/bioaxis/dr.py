__author__ = "Jianfeng Sun"
__version__ = "v1.0"
__copyright__ = "Copyright 2025"
__license__ = "GPL v3.0"
__email__="jianfeng.sunmt@gmail.com"

from bioaxis.util.DimensionReduction import DimensionReduction


def get_2d_coords(
        feature,
        met='tsne',
        **kwargs,
):
    return DimensionReduction().get_2d_coords(
        feature=feature,
        met=met,
    )