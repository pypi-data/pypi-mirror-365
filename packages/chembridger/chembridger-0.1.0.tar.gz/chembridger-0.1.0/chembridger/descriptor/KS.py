import numpy as np
import pandas as pd
# from statsmodels.stats.multitest import multipletests
# from joblib import Parallel, delayed

class KSScorer:
    def __init__(self, ref_matrix, gene_names=None, sample_names=None):
        if isinstance(ref_matrix, pd.DataFrame):
            self.ref_matrix = ref_matrix.to_numpy()
            self.gene_names = ref_matrix.index.to_numpy()
            self.sample_names = ref_matrix.columns.to_numpy()
        else:
            self.ref_matrix = ref_matrix
            self.gene_names = gene_names or np.array([f"gene{i+1}" for i in range(ref_matrix.shape[0])])
            self.sample_names = sample_names or np.array([f"sample{i+1}" for i in range(ref_matrix.shape[1])])
        self.ranked_lists = self._matrix_to_ranked_lists()

    def _matrix_to_ranked_lists(self):
        return [list(self.gene_names[np.argsort(-self.ref_matrix[:, i])]) for i in range(self.ref_matrix.shape[1])]

    def _ks_score(self, ref_list, query):
        len_ref = len(ref_list)
        query_rank = np.array([ref_list.index(gene) + 1 for gene in query if gene in ref_list])
        query_rank.sort()
        len_query = len(query_rank)
        if len_query == 0:
            return 0.0
        d = np.arange(1, len_query + 1) / len_query - query_rank / len_ref
        a = np.max(d)
        b = -np.min(d) + 1 / len_query
        return a if a > b else -b

    def _ks(self, ref_list, query_up, query_down):
        score_up = self._ks_score(ref_list, query_up)
        score_down = self._ks_score(ref_list, query_down)
        return score_up - score_down if score_up * score_down <= 0 else 0.0

    def compute(self, query_up, query_down, permute_num=1000, p_adj_method="fdr_bh", n_jobs=1):
        query_up = [gene for gene in query_up if gene in self.gene_names]
        query_down = [gene for gene in query_down if gene in self.gene_names]

        scores = Parallel(n_jobs=n_jobs)(
            delayed(self._ks)(ref_list, query_up, query_down) for ref_list in self.ranked_lists
        )
        scores = np.array(scores)

        permute_scores = np.zeros((self.ref_matrix.shape[1], permute_num))
        for n in range(permute_num):
            boot_up = np.random.choice(self.gene_names, size=len(query_up), replace=False)
            boot_down = np.random.choice(self.gene_names, size=len(query_down), replace=False)
            permute_scores[:, n] = Parallel(n_jobs=n_jobs)(
                delayed(self._ks)(ref_list, boot_up, boot_down) for ref_list in self.ranked_lists
            )

        permute_scores = np.nan_to_num(permute_scores)
        p_values = np.mean(np.abs(permute_scores) >= np.abs(scores[:, np.newaxis]), axis=1)
        p_adjusted = multipletests(p_values, method=p_adj_method)[1]

        result = pd.DataFrame({
            "Score": scores,
            "pValue": p_values,
            "pAdjValue": p_adjusted
        }, index=self.sample_names)

        return result
