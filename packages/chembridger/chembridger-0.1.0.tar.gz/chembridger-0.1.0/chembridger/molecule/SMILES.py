__author__ = "Jianfeng Sun"
__version__ = "v1.0"
__copyright__ = "Copyright 2024"
__license__ = "GPL v3.0"
__email__ = "jianfeng.sunmt@gmail.com"

import pandas as pd
from rdkit import Chem
from chembridger.util.Console import Console


class SMILES:

    def __init__(
            self,
            smiles,
            verbose=True,
            **kwargs,
    ):
        self.smiles = smiles
        self.df = pd.DataFrame(self.smiles, columns=["SMILES"])

        self.console = Console()
        self.console.verbose = verbose

    @property
    def mols(self, ):
        return self.df.SMILES.apply(Chem.MolFromSmiles)

