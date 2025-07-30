__author__ = "Jianfeng Sun"
__version__ = "v1.0"
__copyright__ = "Copyright 2025"
__license__ = "GPL v3.0"
__email__="jianfeng.sunmt@gmail.com"

import matplotlib.pyplot as plt
import seaborn as sns


class Splitter:

    def __init__(
            self,
            df,
            ax,
            **kwargs,
    ):
        self.df = df
        self.ax = ax
        self.kwargs = kwargs
        print(self.kwargs)

        if 'num_rows' in self.kwargs.keys():
            self.num_rows = self.kwargs['num_rows']
        else:
            self.num_rows = 1
        if 'num_cols' in self.kwargs.keys():
            self.num_cols = self.kwargs['num_cols']
        else:
            self.num_cols = 1

        sns.set(font="Helvetica")
        sns.set_style("ticks")

    def distrib_size(self, ):
        # _, ax = plt.subplots(1, 1, figsize=(8, 4), sharey=True)
        bp = sns.boxplot(
            x="cluster_met",
            y=self.kwargs["test_size"],
            data=self.df,
            palette="Set2",
            fill=False,
            gap=.1,
            ax=self.ax,
        )
        bp.set_xlabel("Cluster method", fontsize=16)
        bp.set_ylabel("# of molecules (test)", fontsize=16)
        bp.spines['right'].set_color('none')
        bp.spines['top'].set_color('none')
        bp.tick_params(axis='both', which='both', bottom=True, top=False, labelsize=14)
        plt.setp(bp.get_xticklabels(), rotation=15)
        plt.tight_layout()
        # plt.show()

    def dim_reduction(self, ):
        # figure, ax = plt.subplots(len(self.cluster_mets), self.num_splits, figsize=(15, 12), sharey=True)
        for i, cluster_met in enumerate(self.kwargs['cluster_mets']):
            for j, num_split in enumerate(range(self.kwargs['num_splits'])):
                sp = sns.scatterplot(
                    x="x",
                    y="y",
                    data=self.df.query(f"{cluster_met + '_r0' + '_s' + str(num_split)} == 'train'"),
                    ax=self.ax[i, j],
                    color="lightblue",
                    alpha=0.3,
                    legend=False,
                )
                sns.scatterplot(
                    x="x",
                    y="y",
                    data=self.df.query(f"{cluster_met + '_r0' + '_s' + str(num_split)} == 'test'"),
                    ax=self.ax[i, j],
                    color="red",
                    alpha=0.5,
                    legend=False,
                )
                sp.set_title(cluster_met + ' fold ' + str(num_split))
                sp.set_xlabel("x-tSNE", fontsize=14)
                sp.set_ylabel("y-tSNE", fontsize=14)
                sp.spines['right'].set_color('none')
                sp.spines['top'].set_color('none')
        plt.tight_layout()
        # plt.show()

    def mol_similairty(self, ):
        # figure, ax = plt.subplots(1, 1, figsize=(10, 5), sharey=True)
        bp = sns.boxplot(
            data=self.df.query("fold < 10"),
            x="fold",
            y="sim",
            hue="cluster_met",
            palette="Set2",
            fill=False,
            gap=.1,
            ax=self.ax,
        )
        bp.legend(loc='upper left', bbox_to_anchor=(1.00, 0.75), ncol=1, fontsize=12)
        bp.set_xlabel("Cross-validation fold", fontsize=20)
        bp.set_ylabel("Tanimoto similairty score", fontsize=20)
        bp.spines['right'].set_color('none')
        bp.spines['top'].set_color('none')
        plt.tight_layout()
        # plt.show()

    def num_clusters(self, ):
        # _, ax = plt.subplots(1, 1, figsize=(10, 5), sharey=True)
        ax = sns.boxplot(
            x="num_clusters",
            y="num_test_mols",
            data=self.df,
            palette="Set2",
            fill=False,
            gap=.1,
            ax=self.ax,
        )
        ax.set_xlabel("# of clusters", fontsize=18)
        ax.set_ylabel("# of molecules (test)", fontsize=18)
        ax.spines['right'].set_color('none')
        ax.spines['top'].set_color('none')
        ax.tick_params(axis='both', which='both', bottom=True, top=False, labelsize=16)
        plt.tight_layout()
        # plt.show()