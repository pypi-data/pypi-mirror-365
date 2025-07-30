__author__ = "Jianfeng Sun"
__version__ = "v1.0"
__copyright__ = "Copyright 2025"
__license__ = "GPL-3.0"
__email__ = "jianfeng.sunmt@gmail.com"

import numpy as np
import pandas as pd

from tqdm.auto import tqdm

from rdkit.DataStructs import BulkTanimotoSimilarity
import useful_rdkit_utils as uru

from chembridger.util.Console import Console


class Splitting:

    def __init__(
            self,
            df,
            num_splits=5,
            num_repeats=1,
            verbose=True,
    ):
        """

        See Also
        --------
        Original author: Pat Walters
        Post: https://practicalcheminformatics.blogspot.com/2024/11/some-thoughts-on-splitting-chemical.html
        Raw code: https://github.com/PatWalters/practical_cheminformatics_posts/blob/main/splitting/dataset_splitting.ipynb

        Parameters
        ----------
        df
        num_repeats
        """
        self.df = df
        self.num_repeats = num_repeats
        self.num_splits = num_splits

        self.cluster_dict = {
            "random_cluster": uru.get_random_clusters,
            "butina_cluster": uru.get_butina_clusters,
            "umap_cluster": uru.get_umap_clusters,
            "scaffold_cluster": uru.get_bemis_murcko_clusters,
        }
        self.cluster_mets = [*self.cluster_dict.keys()]

        self.console = Console()
        self.console.verbose = verbose

        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=FutureWarning)

    def calc_cluster_sgl(self, cluster_met):
        self.df[cluster_met] = self.cluster_dict[cluster_met](self.df.SMILES)
        return self.df

    def calc_cluster_all(self, ):
        for cluster_met in self.cluster_mets:
            self.df[cluster_met] = self.cluster_dict[cluster_met](self.df.SMILES)
        return self.df

    def train_test_sample_ids(self, ):
        split_id_dict = {}
        for cluster_met in self.cluster_mets:

            self.console.print("===>cluster method: {}".format(cluster_met))

            split_id_dict[cluster_met] = {}
            for repeat_num in tqdm(range(self.num_repeats), desc=cluster_met):

                self.console.print("======>repeat time: {}".format(repeat_num))

                split_id_dict[cluster_met][repeat_num] = {}
                cluster_ids = self.cluster_dict[cluster_met](self.df.SMILES)
                gkfs = uru.GroupKFoldShuffle(n_splits=self.num_splits, shuffle=True)
                for i, (train_idx, test_idx) in enumerate(gkfs.split(X=self.df, groups=cluster_ids)):

                    self.console.print("=========>fold: {}".format(i))

                    split_id_dict[cluster_met][repeat_num][i] = [train_idx.tolist(), test_idx.tolist()]
        # print(split_id_dict)
        return split_id_dict

    def add_summary(
            self,
            split_id_dict,
    ):
        split_arr = []
        for cluster_met in self.cluster_mets:
            for repeat_num in range(self.num_repeats):
                for fold_i in range(self.num_splits):
                    train_size = len(split_id_dict[cluster_met][repeat_num][fold_i][0])
                    test_size = len(split_id_dict[cluster_met][repeat_num][fold_i][1])
                    split_arr.append([cluster_met, repeat_num, fold_i, train_size, test_size])
        return pd.DataFrame(
            split_arr,
            columns=[
                "cluster_met",
                "repeat_num",
                "fold_i",
                "train_size",
                "test_size",
            ]
        )

    def add_marks(
            self,
            split_id_dict,
            fold=0,
    ):
        df = pd.DataFrame()
        for cluster_met in self.cluster_mets:
            for repeat_num in range(self.num_repeats):
                for fold_i in range(self.num_splits):
                    attachment = cluster_met + '_r' + str(repeat_num) + '_s' + str(fold_i)
                    df[attachment] = ["train"] * self.df.shape[0]

                    self.console.print(split_id_dict[cluster_met][repeat_num][fold_i])

                    test_idx = split_id_dict[cluster_met][repeat_num][fold_i][1]

                    self.console.print(test_idx)

                    for t in test_idx:
                        df[attachment].at[t] = "test"
        return df

    def cluster_num_sel(
            self,
            cluster_met="umap_cluster",
            lower_bound=5,
            upper_bound=76,
            step=5,
    ):
        res = []
        for num_clus in tqdm(range(lower_bound, upper_bound, step)):
            for num_repeat in range(0, self.num_repeats):
                cluster_list = self.cluster_dict[cluster_met](self.df.SMILES, n_clusters=num_clus)
                gkfs = uru.GroupKFoldShuffle(n_splits=self.num_splits, shuffle=True)
                for train, test in gkfs.split(X=np.stack(self.df.fp), groups=cluster_list):
                    res.append([num_clus, len(test)])
        return pd.DataFrame(
            res,
            columns=[
                "num_clusters",
                "num_test_mols",
            ]
        )

    def tanimoto_one_vs_all(
            self,
            fp_arr1,
            fp_arr2,
            top_n=5,
    ):
        arr = []
        for fp2 in fp_arr2:
            sim_list = BulkTanimotoSimilarity(fp2, fp_arr1)
            sim_array = np.array(sim_list)
            idx = np.argpartition(np.array(sim_array), -top_n)[-top_n:]
            best_n_tanimoto = sim_array[idx]
            arr.append(best_n_tanimoto)
        return np.array(arr).flatten()

    def sim_test_train(
            self,
            split_id_dict,
            met='tanimoto',
            top_n=5,
    ):
        res = []
        for cluster_met in self.cluster_mets:
            for repeat_num in range(self.num_repeats):
                for fold_i in range(self.num_splits):
                    df_train =self.df.iloc[split_id_dict[cluster_met][repeat_num][fold_i][0]]
                    df_test =self.df.iloc[split_id_dict[cluster_met][repeat_num][fold_i][1]]
                    if met == 'tanimoto':
                        sim_vals = self.tanimoto_one_vs_all(
                            fp_arr1=df_train.fp.tolist(),
                            fp_arr2=df_test.fp.tolist(),
                            top_n=top_n,
                        )
                    idx = np.arange(0, len(sim_vals)) + fold_i * len(sim_vals)
                    sim_df = pd.DataFrame({"sim": sim_vals, "fold": fold_i, "cluster_met": cluster_met, "idx": idx})
                    res.append(sim_df)
        df_sim = pd.concat(res)
        # print(df_sim)
        return df_sim


if __name__ == "__main__":
    from chembridger.path import to

    df = pd.read_csv(to("data/protac/finalPROTAC.csv"))

    p = Splitting(
        df=df,
        num_repeats=1,
        num_splits=5,
    )