__author__ = "Jianfeng Sun"
__version__ = "v1.0"
__copyright__ = "Copyright 2025"
__license__ = "GPL v3.0"
__email__="jianfeng.sunmt@gmail.com"

from bioaxis.dataset.Splitter import Splitter


def plot_distrib_size(
        df,
        ax,
        **kwargs,
):
    return Splitter(
        df,
        ax,
        **kwargs
    ).distrib_size()


def plot_dim_reduction(
        df,
        ax,
        **kwargs,
):
    return Splitter(
        df,
        ax,
        **kwargs
    ).dim_reduction()


def plot_mol_similairty(
        df,
        ax,
        **kwargs,
):
    return Splitter(
        df,
        ax,
        **kwargs
    ).mol_similairty()


def plot_num_clusters(
        df,
        ax,
        **kwargs,
):
    return Splitter(
        df,
        ax,
        **kwargs
    ).num_clusters()




