__version__ = "v1.0"
__copyright__ = "Copyright 2024"
__license__ = "GPL v3.0"
__developer__ = "Jianfeng Sun"
__maintainer__ = "Jianfeng Sun"
__email__="jianfeng.sunmt@gmail.com"

from chembridger.dataset.Splitting import Splitting


def loader(
        df,
        num_splits=5,
        num_repeats=1,
        verbose=True,
):
    return Splitting(
        df=df,
        num_repeats=num_repeats,
        num_splits=num_splits,
        verbose=verbose,
    )


def calc_cluster(
        loader,
        cluster_met='random_cluster',
):
    return loader.calc_cluster_sgl(
        cluster_met=cluster_met,
    )


def calc_clusters(
        loader,
):
    return loader.calc_cluster_all()


def calc_train_test_ids(
        loader,
):
    return loader.train_test_sample_ids()


def generate_summary(
        loader,
        train_test_ids,
):
    return loader.add_summary(
        split_id_dict=train_test_ids,
    )


def generate_mark(
        loader,
        train_test_ids,
):
    return loader.add_marks(
        split_id_dict=train_test_ids,
    )


def cluster_num_selection(
        loader,
        cluster_met="umap_cluster",
        lower_bound=5,
        upper_bound=76,
        step=5,
):
    return loader.cluster_num_sel(
        cluster_met=cluster_met,
        lower_bound=lower_bound,
        upper_bound=upper_bound,
        step=step,
    )


def sim_test_train(
        loader,
        train_test_ids,
        met='tanimoto',
        top_n=5,
):
    return loader.sim_test_train(
        split_id_dict=train_test_ids,
        met=met,
        top_n=top_n,
    )




if __name__ == "__main__":
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    from chembridger.path import to
    import bioaxis as ba

    df = pd.read_csv(to("data/protac/finalPROTAC.csv"))

    # df = df.sample(frac=0.8, replace=True).reset_index(drop=True)
    # print(df)

    loader_p = loader(
        df=df,
        num_repeats=1,
        num_splits=5,
        verbose=False,
    )

    split_id_dict = calc_train_test_ids(
        loader=loader_p,
    )
    # print(split_id_dict)

    df_split_summary = generate_summary(
        loader=loader_p,
        train_test_ids=split_id_dict,
    )
    # print(df_split_summary)

    ### /*** plot distribution size ***/
    # _, ax = plt.subplots(1, 1, figsize=(8, 4), sharey=True)
    # ba.ds.plot_distrib_size(
    #     df=df_split_summary,
    #     ax=ax,
    #     # num_rows=4,
    #     # num_cols=5,
    # )
    # plt.show()

    df_split_mark = generate_mark(
        loader=loader_p,
        train_test_ids=split_id_dict,
    )
    # print(df_split_mark)

    df_cluster = calc_cluster(
        loader=loader_p,
    )
    # print(df_cluster)

    df_clusters = calc_clusters(
        loader=loader_p,
    )
    # print(df_clusters)

    ### /*** mols ***/
    from smiles import to_mols
    df['mol'] = to_mols(
        smiles=df["SMILES"],
        verbose=True,
    )

    ### /*** fps ***/
    from desc import fingerprint
    df['fp'] = fingerprint(
        mols=df["mol"].values.tolist(),
        met="Morgan",
    )

    # df_clus_sel = cluster_num_selection(
    #     loader=loader_p,
    #     cluster_met="umap_cluster",
    #     lower_bound=5,
    #     upper_bound=76,
    #     step=5,
    # )
    # print(df_clus_sel)

    ### /*** plot num_clusters ***/
    # _, ax = plt.subplots(1, 1, figsize=(10, 5), sharey=True)
    # ba.ds.plot_num_clusters(
    #     df=df_clus_sel,
    #     ax=ax,
    #     # num_rows=4,
    #     # num_cols=5,
    # )
    # plt.show()


    x_coord, y_coord = ba.dr.get_2d_coords(
        feature=np.stack(df['fp']),
        met="tsne",
    )
    df['x'] = x_coord
    df['y'] = y_coord
    # print(df)

    df = pd.concat([df_split_mark, df], axis=1).reset_index(drop=True)
    # print(df)

    ### /*** plot dim reduction ***/
    _, ax = plt.subplots(4, 5, figsize=(15, 12), sharey=True)
    ba.ds.plot_dim_reduction(
        df=df,
        ax=ax,
        # num_rows=4,
        # num_cols=5,
        cluster_mets=loader_p.cluster_mets,
        num_splits=5,
    )
    plt.show()

    ### /*** plot mol similairty ***/
    # df_sim = sim_test_train(
    #     loader=loader_p,
    #     train_test_ids=split_id_dict,
    #     met='tanimoto',
    # )
    # print(df_sim)
    #
    # _, ax = plt.subplots(1, 1, figsize=(10, 5), sharey=True)
    # ba.ds.plot_mol_similairty(
    #     df=df_sim,
    #     ax=ax,
    # )
    # plt.show()