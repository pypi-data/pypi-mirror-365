__version__ = "v1.0"
__copyright__ = "Copyright 2024"
__license__ = "GPL v3.0"
__developer__ = "Jianfeng Sun"
__maintainer__ = "Jianfeng Sun"
__email__="jianfeng.sunmt@gmail.com"

from chembridger.molecule.SMILES import SMILES


def to_mols(
        smiles,
        verbose=True,
):
    return SMILES(
        smiles=smiles,
        verbose=verbose,
    ).mols


if __name__ == "__main__":
    from chembridger.path import to
    import pandas as pd

    df = pd.read_csv(to("data/protac/finalPROTAC.csv"))
    # loader_p = loader(
    #     smiles=df["SMILES"],
    #     verbose=False,
    # )
    df['mol'] = to_mols(
        smiles=df["SMILES"],
        verbose=False,
    )
    print(df['mol'])
