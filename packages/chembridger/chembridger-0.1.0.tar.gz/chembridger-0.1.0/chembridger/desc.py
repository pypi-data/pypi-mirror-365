__version__ = "v1.0"
__copyright__ = "Copyright 2025"
__license__ = "GPL-3.0"
__developer__ = "Jianfeng Sun"
__maintainer__ = "Jianfeng Sun"
__email__="jianfeng.sunmt@gmail.com"

from chembridger.descriptor.Fingerprint import Fingerprint


def fingerprint(
        mols,
        met,
        **kwargs,
):
    return Fingerprint(
        mols=mols,
        met=met,
        **kwargs,
    ).get()


if __name__ == "__main__":
    from chembridger.path import to
    import pandas as pd

    df = pd.read_csv(to("data/protac/finalPROTAC.csv"))

    from smiles import to_mols
    df['mol'] = to_mols(
        smiles=df["SMILES"],
        verbose=True,
    )

    df['fp'] = fingerprint(
        mols=df["mol"].values.tolist(),
        met="Morgan",
    )
    print(df)