import numpy as np
import pandas as pd
from crisgi.cnn.CNNModel import CNNModel
from crisgi.logistic.LogisticModel import LogisticModel
import scanpy as sc
import anndata as ad
from scipy.sparse import csr_matrix, coo_matrix
from scipy.stats import ttest_1samp, wilcoxon
from pyseat.SEAT import SEAT
import seaborn as sns
import matplotlib.pyplot as plt
import pickle
import os
import pickle
from crisgi.simplecnn.SimpleCNNModel import SimpleCNNModel
from sksurv.nonparametric import kaplan_meier_estimator
from sksurv.compare import compare_survival
from itertools import chain, permutations
import gseapy as gp
from gseapy import gseaplot
import pymannkendall as mk
from multiprocessing import Pool
from concurrent.futures import ProcessPoolExecutor, as_completed
from collections import Counter
import warnings

from crisgi.startpoint_detection import detect_start_point
warnings.filterwarnings('ignore')

pd.options.mode.copy_on_write = True

from crisgi.util import print_msg, get_array, set_adata_var, set_adata_obs


def load_crisgi(pk_fn):
    crisgi_obj = pickle.load(open(pk_fn, 'rb'))
    print_msg(f'[Input] CRISGI object stored at {pk_fn} has been loaded.')
    return crisgi_obj

class CRISGI():

    # CRISGI
    def __init__(self, adata, bg_net=None, bg_net_score_cutoff=850,
                 genes=None,
                 n_hvg=5000, n_pcs=30,
                 interactions=None,
                 n_threads=5,
                 interaction_methods=['prod'],
                 organism='human',
                 class_type='time',
                 dataset='test',
                 out_dir='./out'
                 ):

        adata = adata.copy()
        adata.obs['i'] = range(adata.shape[0])
        adata.var['i'] = range(adata.shape[1])
        self.adata = adata
        self.interaction_methods = interaction_methods
        self.organism = organism
        self.n_threads = n_threads
        self.dataset = dataset
        self.class_type = class_type
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        self.out_dir = out_dir

        if n_hvg is not None:
            self.preprocess_adata(n_hvg=n_hvg, n_pcs=n_pcs)

        self.load_bg_net(bg_net, bg_net_score_cutoff, interactions, genes)

    def load_bg_net(self, bg_net, bg_net_score_cutoff, interactions, genes):
        self.bg_net_score_cutoff = bg_net_score_cutoff

        if interactions is not None:
            bg_net = self.load_bg_net_from_interactions(interactions)
            self.adata.varm['bg_net'] = bg_net

        if 'bg_net' not in self.adata.varm:
            if bg_net is None:
                if genes is None:
                    if 'highly_variable' in self.adata.var:
                        genes = self.adata.var_names[self.adata.var['highly_variable']]
                    else:
                        genes = self.adata.var_names
                    
                self.adata = self.adata[:, self.adata.var_names.isin(genes)]
                genes = np.array(list(set(genes).intersection(self.adata.var_names)))
                genes = np.sort(genes)
                self.adata = self.adata[:, genes]
                self.adata.var['i'] = range(self.adata.shape[1])
                bg_net, _ = self.load_bg_net_from_genes(genes)
        else:
            bg_net = csr_matrix(np.triu(self.adata.varm['bg_net']))
        self.adata.varm['bg_net'] = bg_net 
        print_msg(f'The number of edge for bg_net is {bg_net.count_nonzero()}.')

    # CRISGI
    def init_edata(self, test_obss, headers):
        adata = self.adata
        test_obss_is = [adata[test_obs, :].obs.i.tolist() for test_obs in test_obss]
        adata = self.adata
        bg_net = adata.varm['bg_net']
        row, col = bg_net.nonzero()
        target_n = len(test_obss_is)
        interaction_n = bg_net.count_nonzero()
        edata = ad.AnnData(np.zeros((target_n, interaction_n)))
        test_obs = list(chain.from_iterable(test_obss))
        df = adata[test_obs, :].obs[headers].copy().drop_duplicates()
        df.index = df['test']
        edata.obs = df
        edata.var_names = adata.var_names[row].astype(str) + '_' + adata.var_names[col].astype(str)
        edata.var['gene1'] = adata.var_names[row]
        edata.var['gene2'] = adata.var_names[col]
        edata.var['gene1_i'] = row
        edata.var['gene2_i'] = col
        edata.var['i'] = range(interaction_n)
        self.edata = edata
        print_msg(f'Init edata with obs {edata.shape[0]} and interaction {edata.shape[1]}')

    # CRISGI
    def save(self):
        pk_fn = f'{self.out_dir}/{self.dataset}_crisgi_obj.pk'
        pickle.dump(self, open(pk_fn, 'wb'))
        print_msg(f'[Output] CRISGI object has benn saved to:\n{pk_fn}')

    # CRISGI
    def load_bg_net_from_interactions(self, interactions):
        print_msg('load bg_net by looping interactions.')
        genes = np.array([r.split('_') for r in interactions]).reshape(-1)
        genes = list(set([g for g in genes if g in self.adata.var_names]))
        if not genes:
            raise ValueError('The genes in given interactions do not exists in adata!')

        genes = np.sort(genes)
        self.adata = self.adata[:, genes]
        gene2i = {g: i for i, g in enumerate(genes)}

        bg_net = np.zeros((len(genes), len(genes)))
        for r in interactions:
            gene1, gene2 = r.split('_')
            if gene1 in genes and gene2 in genes:
                bg_net[gene2i[gene1], gene2i[gene2]] = 1
        return bg_net

    # CRISGI
    def load_bg_net_from_genes(self, genes):
        if (genes != np.sort(genes)).any():
            raise ValueError('The genes should be sorted!')

        print('input gene', len(genes))
        dir = os.path.abspath(os.path.dirname( __file__ ))
        ref_gb_net = pickle.load(open(f"{dir}/stringdb_{self.organism}_v12_gb_net.pk","rb"))
        ref_genes = pickle.load(open(f"{dir}/stringdb_{self.organism}_v12_genes.pk","rb"))
        self.adata.uns['stringdb_genes'] = ref_genes

        if ref_gb_net.count_nonzero() > len(genes)*len(genes):
            bg_net, interactions = self._loop_gene(genes, ref_genes, ref_gb_net)
        else:
            bg_net, interactions = self._loop_bg_net(genes, ref_genes, ref_gb_net)

        bg_net = np.triu(bg_net)
        bg_net = csr_matrix(bg_net)
        print('output interactions after bg_net', len(interactions))
        return bg_net, interactions

    # CRISGI
    def _loop_gene(self, genes, ref_genes, ref_gb_net):
        print_msg('load bg_net by looping genes.')
        ref_genes2i = {g:i for i, g in enumerate(ref_genes)}
        interactions = []
        bg_net = np.zeros((len(genes), len(genes)))
        for i, gene1 in enumerate(genes):
            if gene1 not in ref_genes:
                continue
            for j, gene2 in enumerate(genes):
                if gene2 not in ref_genes:
                    continue
                if i > j:
                    continue
                ref_gene1_i = ref_genes2i[gene1]
                ref_gene2_i = ref_genes2i[gene2]
                if ref_gb_net[ref_gene1_i, ref_gene2_i] >= self.bg_net_score_cutoff:
                    bg_net[i, j] = ref_gb_net[ref_gene1_i, ref_gene2_i]
                    interactions.append(f'{gene1}_{gene2}')
        return bg_net, interactions

    # CRISGI
    def _loop_bg_net(self, genes, ref_genes, ref_gb_net):
        print_msg('load bg_net by looping bg_net.')
        genes2i = {g:i for i, g in enumerate(genes)}
        interactions = []
        bg_net = np.zeros((len(genes), len(genes)))
        row, col = ref_gb_net.nonzero()
        for ref_gene1_i, ref_gene2_i in zip(row, col):
            gene1, gene2 = ref_genes[ref_gene1_i], ref_genes[ref_gene2_i]
            if (gene1 not in genes) or (gene2 not in genes):
                continue
            if ref_gb_net[ref_gene1_i, ref_gene2_i] >= self.bg_net_score_cutoff:
                i, j = genes2i[gene1], genes2i[gene2]
                bg_net[i, j] = ref_gb_net[ref_gene1_i, ref_gene2_i]
                interactions.append(f'{gene1}_{gene2}')
        return bg_net, interactions

    # CRISGI
    def preprocess_adata(self, n_hvg=5000, random_state=0, n_pcs=30, n_neighbors=10):
        adata = self.adata
        #sc.pp.scale(adata)
        sc.pp.highly_variable_genes(adata, n_top_genes=n_hvg, flavor='cell_ranger')
        sc.tl.pca(adata)
        sc.pp.neighbors(adata, n_pcs=n_pcs, n_neighbors=n_neighbors)
        sc.tl.umap(adata, random_state=random_state)

    # CRISGI
    def _prod(self, X, obs_is, row, col, obs_cutoff=100):
        _, M = X.shape
        if len(obs_is) > obs_cutoff:
            X_tmp = X[obs_is,:]
            R = np.dot(X_tmp.T, X_tmp)
        else:
            R = np.zeros((M, M))
            for i in obs_is:
                for j, k in zip(row, col):
                    R[j, k] += X[i, j] * X[i, k]
        return R

    # CRISGI
    def sparseR2entropy(self, R, row, col):
        R_sum = R.sum(axis=0)
        R_sum[R_sum == 0] = 1  # TBD, speed up
        prob = R/R_sum
        prob_row, prob_col = prob.nonzero()
        tmp = np.array(prob.todense()[prob_row, prob_col]).reshape(-1)
        val = - tmp * np.log(tmp)
        entropy_matrix = csr_matrix((val, (prob_row, prob_col)), shape = R.shape)
        n_neighbors = np.array((R != 0).sum(axis=0))
        norm = np.log(n_neighbors)
        norm[n_neighbors == 0] = 1
        norm[n_neighbors == 1] = 1
        gene_entropy = (np.array(entropy_matrix.sum(axis=0))/norm).reshape(-1)
        interaction_entropy = (gene_entropy[row]+gene_entropy[col])/2
        return interaction_entropy

    # CRISGI
    def _std(self, adata):
        X = get_array(adata, layer='log1p')
        set_adata_var(adata, 'std', X.std(axis=0))

    # CRISGI
    def _scale(self, adata, axis=0):
        X = get_array(adata, layer='log1p')
        N = X.shape[axis]
        mean = X.mean(axis=axis, keepdims=True)
        X = X - mean
        std = np.sqrt(np.power(X, 2).sum(axis=axis, keepdims=True)/N)
        std[std == 0] = 1
        X = X / std
        adata.X = X
        adata.layers['scale'] = X.copy()
        adata.var['mean'] = mean.reshape(-1)
        adata.var['std'] = std.reshape(-1)

    # CRISGI
    def test_DER(self, groupby, target_group=None, test_method="wilcoxon", method='prod'):
        mytarget_group = target_group
        groups = self.adata.obs[groupby].unique()
        self.groups = groups
        self.groupby = groupby
        edata = self.edata

        df_list = []
        mean_df = pd.DataFrame(index=edata.var_names)
        for ref_group in groups:
            if self.class_type == 'time':
                edata_layer_ref = self.ref_time
            else:
                edata_layer_ref = ref_group
            group_X = edata[edata.obs[groupby] == ref_group].layers[f'{edata_layer_ref}_{method}_entropy']
            mean_df[ref_group] = np.nansum(group_X, axis=0)
        for ref_group in groups:
            if self.class_type == 'time':
                edata_layer_ref = self.ref_time
            else:
                edata_layer_ref = ref_group
            sc.tl.rank_genes_groups(edata, layer=f'{edata_layer_ref}_{method}_entropy',
                                        groupby=groupby, reference=ref_group,
                                        method=test_method)
            for target_group in groups:
                if mytarget_group is not None and mytarget_group != target_group:
                    continue
                if ref_group == target_group:
                    continue

                df = sc.get.rank_genes_groups_df(edata, group=target_group)
                df['ref_group'] = ref_group
                df['target_group'] = target_group
                df['method'] = method
                df['ref_group_mean'] = df['names'].apply(lambda x: mean_df[ref_group].to_dict()[x])
                df['target_group_mean'] = df['names'].apply(lambda x: mean_df[target_group].to_dict()[x])
                edata.uns[f'{method}_rank_genes_groups_{ref_group}_{target_group}'] = edata.uns['rank_genes_groups']
                df_list.append(df)

        df = pd.concat(df_list)
        edata.uns[f'rank_genes_groups_df'] = df
        return df

    #CRISGI
    def get_DER(self, target_group=None, n_top_interactions=None, method='prod', 
                p_adjust=True, p_cutoff=0.05, fc_cutoff=1, sortby='scores',
                ):
        mytarget_group = target_group
        edata = self.edata
        df_list = []

        for ref_group, target_group in permutations(self.groups, 2):
            if mytarget_group is not None and mytarget_group != target_group:
                continue
            df = sc.get.rank_genes_groups_df(edata, group=target_group,
                                             key=f'{method}_rank_genes_groups_{ref_group}_{target_group}')
            df['target_group'] = target_group
            df['ref_group'] = ref_group
            df['method'] = method
            if p_adjust:
                p_method = 'pvals_adj'
            else:
                p_method = 'pvals'

            df['DER'] = (df[p_method] < p_cutoff) & (df['logfoldchanges'] > fc_cutoff)
            df_list.append(df)

        df = pd.concat(df_list)
        tmp = df[df['DER']][['names', 'target_group', 'method']]
        count_df = tmp.value_counts()
        count_df = count_df[count_df == (len(self.groups) - 1)]
        count_df = count_df.reset_index()
        for target_group in self.groups:
            if mytarget_group is not None and mytarget_group != target_group:
                continue
            if target_group not in count_df['target_group'].unique():
                interactions = []
                tmp_df = pd.DataFrame()
            else:
                tmp = count_df[(count_df['target_group'] == target_group) & (count_df['method'] == method)]
                interactions = tmp.names.tolist()
                tmp_df = df[(df['target_group'] == target_group) & df['names'].isin(interactions)]
                if sortby in ['logfoldchanges', 'scores']:
                    tmp_df = tmp_df.sort_values(by=['DER', sortby], ascending=False)
                else:
                    tmp_df = tmp_df.sort_values(by=['DER', sortby], ascending=[False, True])
                interactions = tmp_df.names.drop_duplicates().tolist()
                if n_top_interactions is not None:
                    interactions = interactions[: n_top_interactions]
            edata.uns[f'{method}_{self.groupby}_{target_group}_DER'] = interactions
            edata.uns[f'{method}_{self.groupby}_{target_group}_DER_df'] = tmp_df
            fn = f'{self.out_dir}/{method}_{self.groupby}_{target_group}_DER.csv'
            tmp_df.to_csv(fn, index=False)
            print_msg(f'[Output] The differential expressed interaction (DER) {len(interactions)} statistics are saved to:\n{fn}')
        return

    # CRISGI
    def _test_trend(self, interaction, edata, layer, p_cutoff=0.05):
        sorted_samples = edata.obs.sort_values(by=['time']).index.tolist()
        val = edata[sorted_samples, interaction].layers[layer].reshape(-1)
        res = mk.original_test(val, alpha=p_cutoff)
        # https://pypi.org/project/pymannkendall/
        res = {
            'interaction': interaction, 'layer': layer,
            'trend': res.trend, 'h': res.h, 'p': res.p, 'z': res.z,
            'Tau': res.Tau, 's': res.s, 'var_s': res.var_s, 'slope': res.slope, 'intercept': res.intercept
        }
        return res

    # CRISGI
    def _test_zero_trend(self, interaction, edata, layer):
        #sorted_samples = edata.obs.sort_values(by=['time']).index.tolist()
        val = edata[:, interaction].layers[layer].reshape(-1)
        t_statistic, p_value = ttest_1samp(val, 0)
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_1samp.html
        res = {'interaction': interaction, 'layer': layer,
               't_statistic': t_statistic, 'p_value': p_value}
        return res

    def cohort_level_top_n_ORA(self,n_top_interactions=None,top_percentage=0.05,method='prod',
                               gene_sets=['KEGG_2021_Human',
                                        'GO_Molecular_Function_2023', 
                                        'GO_Cellular_Component_2023', 
                                        'GO_Biological_Process_2023',
                                        'MSigDB_Hallmark_2020'],
                                background=None,
                                organism='human', plot=True):
        data = self.edata.X
        top_k = int(data.shape[1] * top_percentage)
        partitioned_indices = np.argpartition(-data, top_k, axis=1)[:, :top_k]
        col_names = np.array(self.edata.var_names)
        top_interactions_counts = col_names[partitioned_indices].flatten().tolist()
        top_interactions_counts = Counter(top_interactions_counts).most_common()
        self.edata.uns[f'top_interactions_count'] = dict(top_interactions_counts)
        interaction_list = list(dict(top_interactions_counts).keys())

        if n_top_interactions is None:
            n_top_interactions = len(interaction_list)

        top_n, enr, enrich_df = self._enrich_for_top_n(n_top_interactions, interaction_list, gene_sets, organism, background)

        fn = f'{self.out_dir}/{method}_cohort_enrich.csv'
        enrich_df.to_csv(fn, index=False)

        print_msg(f'[Output] The {method} cohort-level enrich statistics are saved to:\n{fn}')
    
        self.edata.uns[f'{method}_cohort_enrich_res'] = enr
        self.edata.uns[f'{method}_cohort_enrich_df'] = enrich_df
                

    # CRISGI
    def _enrich_for_top_n(self, top_n, interaction_list, gene_sets, organism, background):
        print('_enrich_for_top_n', top_n)
        gene_list = list(set(np.array([x.split('_') for x in interaction_list[:top_n]]).reshape(-1)))
        enr = gp.enrichr(gene_list=gene_list, gene_sets=gene_sets,
                         background=background,
                         organism=organism,
                         outdir=None)
        df = enr.results
        df['n_gene'] = df['Genes'].apply(lambda x: len(x.split(';')))
        df['top_n'] = top_n
        df['top_n_ratio'] = df['n_gene'] / top_n
        return top_n, enr, df

    # CRISGI pathwau_enrich -> pheno_level_accumulated_top_n_ORA
    def pheno_level_accumulated_top_n_ORA(self, target_group, n_top_interactions=None, n_space=10,
                       method='prod', test_type='TER',
                       gene_sets=['KEGG_2021_Human',
                                  'GO_Molecular_Function_2023', 'GO_Cellular_Component_2023', 'GO_Biological_Process_2023',
                                  'MSigDB_Hallmark_2020'],
                       background=None,
                       organism='human', plot=True):
        interaction_list = self.edata.uns[f'{method}_{self.groupby}_{target_group}_{test_type}']
        enr_dict = {}
        df_list = []

        if n_top_interactions is None:
            n_top_interactions = len(interaction_list)

        for top_n in range(10, n_top_interactions + 1, n_space):
            try:
                top_n, enr, df = self._enrich_for_top_n(top_n, interaction_list, gene_sets, organism, background)
                enr_dict[top_n] = enr
                df_list.append(df)
            except Exception as exc:
                print(f'Top_n {top_n} generated an exception: {exc}')

        df = pd.concat(df_list)
        fn = f'{self.out_dir}/{method}_{self.groupby}_{target_group}_{test_type}_enrich.csv'
        df.to_csv(fn, index=False)
        print_msg(f'[Output] The {method} {self.groupby} {target_group} {test_type} enrich statistics are saved to:\n{fn}')

        self.edata.uns[f'{method}_{self.groupby}_{target_group}_{test_type}_enrich_res'] = enr_dict
        self.edata.uns[f'{method}_{self.groupby}_{target_group}_{test_type}_enrich_df'] = df

    # CRISGI prerank_enrich_gene -> pheno_level_CT_rank
    def pheno_level_CT_rank(self, ref_group, target_group, sortby='pvals_adj', n_top_interactions=None,
                       gene_sets=['KEGG_2021_Human',
                                  'GO_Molecular_Function_2023', 'GO_Cellular_Component_2023', 'GO_Biological_Process_2023',
                                  'MSigDB_Hallmark_2020'], 
                        prefix = 'test',                            
                       min_size=5, max_size=1000, permutation_num=1000, seed=0,
                       ):
        if n_top_interactions is None:
            n_top_interactions = len(self.edata.uns['rank_genes_groups_df'])
        if n_top_interactions > len(self.edata.uns['rank_genes_groups_df']):
            n_top_interactions = len(self.edata.uns['rank_genes_groups_df'])
        if n_top_interactions < 1:
            n_top_interactions = 1
                
        df = self.edata.uns['rank_genes_groups_df']
        df = df[(df['ref_group'] == ref_group) & (df['target_group'] == target_group)]
        df = df.sort_values(by=[sortby], ascending=False)
        df = df[0:n_top_interactions]
        df = df[['names', sortby]]
        df['gene1'] = df['names'].apply(lambda x: x.split('_')[0])
        df['gene2'] = df['names'].apply(lambda x: x.split('_')[1])
        df1 = df[['gene1', sortby]]
        df2 = df[['gene2', sortby]]
        df1.columns = ['gene', sortby]
        df2.columns = ['gene', sortby]
        df = pd.concat([df1, df2])
        df = df.groupby('gene').sum()
        df = df.reset_index()
        rank_df = df.sort_values(sortby, ascending=False)
        rank_df = rank_df.reset_index()
        del rank_df['index']
        res = gp.prerank(rnk=rank_df,
                         gene_sets=gene_sets,
                         threads=self.n_threads,
                         min_size=min_size, max_size=max_size,
                         permutation_num=permutation_num,
                         outdir=f'{self.out_dir}/{prefix}_{ref_group}_{target_group}',
                         seed=seed,
                         verbose=True
                         )
        self.gp_res = res
        
        for term in res.results.keys():
            rank_df[f'{term} hits'] = [1 if x in res.results[term]['hits'] else 0 for x in rank_df.index]
            rank_df[f'{term} RES'] = res.results[term]['RES']
            # gseaplot(rank_metric=res.ranking, term=term, ofname=f'{self.out_dir}/{prefix}_{ref_group}_{target_group}/{term}.pdf', **res.results[term])
        rank_df.to_csv(f'{self.out_dir}/{prefix}_{ref_group}_{target_group}/rank.csv')
        
    
    # CRISGI prerank_gsva_interaction -> obs_level_CT_rank
    def obs_level_CT_rank(self, gene_sets, prefix='test',
                              min_size=5,
                       ):
        df = pd.DataFrame(self.edata.X.T, columns=self.edata.obs_names,
                        index=self.edata.var_names)
        es = gp.gsva(data=df, gene_sets=gene_sets, min_size=min_size,
                     outdir=self.out_dir + '/' + prefix)
        df = es.res2d
        if 'groupby' in self.__dict__:
            df[self.groupby] = df['Name'].apply(lambda x: self.edata.obs[self.groupby].to_dict()[x])
        #df['subject'] = df['Name'].apply(lambda x: x.split(' ')[0])
        #df['time'] = df['Name'].apply(lambda x: int(x.split(' ')[1]))
        df = df.sort_values(by=['ES'])
        df.to_csv(f'./{self.out_dir}/{prefix}/prerank_gsva_interaction.csv')
        
        self.gp_es = es        
        '''
        for term in gene_sets.keys():
            term_df = df[df['Term'] == term]
            sns.lineplot(term_df, x='time', y='ES', hue=self.groupby, 
                        units='subject', estimator=None)
          
            plt.title(term)
            plt.show()
            sns.barplot(term_df, x='Name', y='ES', hue=self.groupby)
            plt.title(term)
            plt.xticks([])
            plt.xlabel(None)
            plt.show()
        '''
        return df
    
    # CRISGI
    def check_common_diff(self, top_n, target_group, layer='log1p', 
                          method='prod', test_type='TER', 
                          interactions=None, unit_header='subject',
                          out_dir=None):
        edata = self.edata
        adata = self.adata
        mytarget_group = target_group

        if interactions is None:
            key = f'{method}_{self.groupby}_{target_group}_{test_type}'
            myinteractions = edata.uns[key]
        else:
            myinteractions = [x for x in interactions if x in edata.var_names]
        
        if self.class_type == 'time':
            edata_layer_ref = self.ref_time
        #else:
            #edata_layer_ref = ref_group

        X = edata.layers[f'{edata_layer_ref}_{method}_entropy']
        top_indices = np.argsort(X, axis=1)[:, -top_n:]
        top_interactions = np.array(edata.var_names)[top_indices]
        top_values = np.take_along_axis(X, top_indices, axis=1)
        #X = edata[:, myinteractions].layers[f'{edata_layer_ref}_{method}_entropy']
        #plt.show()
        #sns.heatmap(X)
        overlap_stats = []
        for row in top_interactions:
            overlap_count = len(set(row).intersection(myinteractions))
            overlap_stats.append(overlap_count)

        edata.obs[f'top_{top_n}_overlap'] = overlap_stats
        edata.obs[f'top_{top_n}_overlap_ratio'] = np.array(overlap_stats) / top_n
        pd.DataFrame(edata.obs).to_csv(f'./{out_dir}/top_{top_n}_overlap.csv')

    # CRISGI
    def find_interaction_module(self, target_group, layer='log1p',
                          method='prod', test_type='TER', 
                          interactions=None, unit_header='subject',
                          out_dir=None, label_df=None,
                          n_neighbors=10, strategy='bottom_up'):
        edata = self.edata
        adata = self.adata
        mytarget_group = target_group

        if interactions is None:
            key = f'{method}_{self.groupby}_{target_group}_{test_type}'
            myinteractions = edata.uns[key]
        else:
            myinteractions = [x for x in interactions if x in edata.var_names]

        genes1 = [x.split('_')[0] for x in myinteractions]
        genes2 = [x.split('_')[1] for x in myinteractions]

        sub_adata = adata[(adata.obs[self.groupby] == mytarget_group)]
        sub_adata = sub_adata[sub_adata.obs.sort_values(by=[unit_header, 'time']).index]

        X = np.multiply(sub_adata[:, genes1].layers[layer], 
                                    sub_adata[:, genes2].layers[layer]).T
        df = pd.DataFrame(X, columns=sub_adata.obs.test, index=myinteractions)

        seat = SEAT(affinity="gaussian_kernel",
                    sparsification="knn_neighbors_from_X",
                    objective="SE",
                    n_neighbors=n_neighbors,
                    strategy=strategy,
                    verbose=False)
        seat.fit_predict(X)

        if label_df is None:
            label_df = pd.DataFrame()
            label_df.index = myinteractions
        label_df['community'] = seat.labels_
        label_df['module'] = seat.clubs
        for col in label_df.columns:
            label = label_df[col]
            label_colors = dict(zip(set(label), sns.color_palette('Spectral', len(set(label)))))
            label_colors = [label_colors[l] for l in label]
            label_df[col] = label_colors

        units = sub_adata.obs[unit_header].unique()
        col_colors = dict(zip(units, sns.color_palette('Spectral', len(units))))
        col_colors = [col_colors[x] for x in sub_adata.obs[unit_header]]
        
        sns.clustermap(df,
                    row_linkage=seat.Z_,
                    col_cluster=False,
                    row_colors=label_df,
                    col_colors=col_colors,
                    cmap='YlGnBu')

        if out_dir is None:
            out_dir = self.out_dir
        fn = f'{out_dir}/{method}_{self.groupby}_{target_group}_{test_type}{len(myinteractions)}_interaction_matrix.csv'
        df.to_csv(fn)
        print_msg(f'[Output] The {method} {self.groupby} {target_group} {test_type}{len(myinteractions)} interaction matrix are saved to:\n{fn}')

        df = pd.DataFrame({'interaction':myinteractions,
                          'community':seat.labels_,
                          'module':seat.clubs})

        df.index = df.interaction
        df = df.drop(columns=['interaction'])
        fn = f'{out_dir}/{method}_{self.groupby}_{target_group}_{test_type}{len(myinteractions)}_interaction_community_module.csv'
        df.to_csv(fn)
        print_msg(f'[Output] The {method} {self.groupby} {target_group} {test_type}{len(myinteractions)} interaction community & module are saved to:\n{fn}')

        fn = f'{out_dir}/{method}_{self.groupby}_{target_group}_{test_type}{len(myinteractions)}_interaction_hierarchy.nwk'        
        with open(fn, 'w') as f:
            f.write(seat.newick)
        print_msg(f'[Output] The {method} {self.groupby} {target_group} {test_type}{len(myinteractions)} interaction hierarchy are saved to:\n{fn}')
        return df

    def network_analysis(self, target_group, layer='log1p',
                          method='prod', test_type='TER', 
                          interactions=None, unit_header='subject',
                          out_dir=None,    
                          n_neighbors=10, strategy='bottom_up'):
        edata = self.edata
        adata = self.adata
        mytarget_group = target_group

        if interactions is None:
            key = f'{method}_{self.groupby}_{target_group}_{test_type}'
            myinteractions = edata.uns[key]
        else:
            myinteractions = [x for x in interactions if x in edata.var_names]

        print(len(myinteractions))

        sedata = edata[:, myinteractions]
        print(sedata)

    # CRISGI
    def _assign_score_group(self, df, x, by='mean'):
        if by == 'median':
            cutoff = df['score'].quantile(0.5)
        else:
            cutoff = df['score'].mean()
        if x <= cutoff:
            return f'<= {by}'
        return f'> {by}'

    # CRISGI
    def survival_analysis(self, ref_group,
                        target_group,
                        interactions=None,
                        groupbys=[],
                        survival_types = ['os', 'pfs'],
                        time_unit = 'time',
                        test_type='DER', method='prod',
                        title=''):

        edata = self.edata
        if interactions is None:
            interactions = edata.uns[f'{method}_{self.groupby}_{target_group}_{test_type}']
        else:
            interactions = [x for x in interactions if x in edata.var_names]
        if len(interactions) == 0:
            return
        edata.obs['score'] = np.nansum(edata[:, interactions].layers[f'{ref_group}_{method}_entropy'], axis=1)  # check OV nan value
        edata.obs['score_group'] = edata.obs['score'].apply(lambda x: self._assign_score_group(edata.obs, x))
        df = edata.obs.copy()
        for survival in survival_types:
            if survival not in df.columns:
                continue
            df = df[~df[f'{survival}_status'].isna()]
            df = df[~df[survival].isna()]
            df[f"{survival}_status"] = df[f"{survival}_status"].astype(bool)
            if df[[f"{survival}_status", 'score_group']].value_counts().shape[0] < 2:
                continue

            for groupby in ['score_group'] + groupbys:
                for score_group in df[groupby].unique():
                    mask_group = df[groupby] == score_group
                    time_treatment, survival_prob_treatment, conf_int = kaplan_meier_estimator(
                        df[f"{survival}_status"][mask_group],
                        df[survival][mask_group],
                        conf_type="log-log",
                    )
                    if groupby == 'score_group':
                        if score_group.startswith('<'):
                            color = 'steelblue'
                        else:
                            color = 'red'
                    else:
                        color = None
                    plt.step(time_treatment, survival_prob_treatment, where="post", label=score_group, color=color)
                    plt.fill_between(time_treatment, conf_int[0], conf_int[1], alpha=0.25, step="post", color=color)

                dt = np.dtype([(f"{survival}_status", bool), (survival, float)])
                y = [(df.iloc[i][f"{survival}_status"], df.iloc[i][survival]) for i in range(df.shape[0])]
                y = np.array(y, dtype=dt)
                chi2, p_value = compare_survival(y, df[groupby])

                plt.ylim(0, 1)
                plt.ylabel(r"est. probability of survival $\hat{S}(t)$")
                plt.xlabel(f"{survival.upper()} {time_unit} $t$")
                plt.legend(loc="best")
                plt.title(f'{title} {method}_{self.groupby}_{target_group}_{len(interactions)}{test_type}s\nlog-rank test\nchi2: {round(chi2, 2)}, p-value: {p_value}')
                plt.show()
                fn = f'{self.out_dir}/{method}_{self.groupby}_{target_group}_{len(interactions)}{test_type}s_{survival.upper()}_surv.png'
                print_msg(f'[Output] The survival plot are saved to:\n{fn}')

    def detect_startpoint(self, symptom_types = ["Symptomatic"]):
        """
            Perform start point detection on samples with specified symptom types,
            and store the predicted CT_time in the 'CT_time' column of edata.obs.

            Parameters
            ----------
            symptom_types : list of str
                A list of symptom types to filter samples by.
                These values should correspond to those in edata.obs['symptom'], 
                for example: ["Symptomatic"].

        """
        edata = self.edata

        mask = edata.obs['symptom'].isin(["Symptomatic"])

        symp_edata = ad.AnnData(
            X=edata.X[mask],
            obs=edata.obs.loc[mask].copy(),
            var=edata.var.copy(),
            layers={k: v[mask] for k, v in edata.layers.items()}  # 只拷贝layers
        )

        for sample in symp_edata.obs['subject'].unique():
            sample_edata = symp_edata[symp_edata.obs['subject'] == sample]

            df = sample_edata.to_df()
            df.index = sample_edata.obs['time'].values

            df = df.dropna(how='all', axis=0)
            df = df.dropna(how='all', axis=1)

            if df.shape[0] * df.shape[1] == 0:
                print("DataFrame is empty after dropping rows and columns.")

            df = df.T

            signals_matrix = df.to_numpy()
            n_col = 100
            last_col = signals_matrix[:, -1].reshape(-1, 1)

            signals_matrix = np.hstack((signals_matrix, np.zeros((signals_matrix.shape[0], n_col))))
            sample_rate = signals_matrix.shape[1]

            start_sample = detect_start_point(signals_matrix, sample_rate, frame_size_ms=25, hop_size_ms=10)
            predict_time = df.columns.values[start_sample]

            # print(f"{sample} predict time: {predict_time}")

            edata.obs.loc[edata.obs['subject'] == sample, 'CT_time'] = predict_time

        self.edata = edata

    def predict(self, *args, **kwargs):
        raise NotImplementedError("Subclasses should implement predict()")
    

    def train(self, *args, **kwargs):
        raise NotImplementedError("Subclasses should implement predict()")



    
class CRISGITime(CRISGI):

    def __init__(self, adata, class_type='time',device='cpu', model_type="cnn", ae_path=None, mlp_path=None, model_path=None, **kwargs,):
        super().__init__(adata, class_type='time', **kwargs)
        self.device = device
        self.model = None
        self.model_type = None  

        self.set_model_type(model_type, ae_path=ae_path, mlp_path=mlp_path, model_path=model_path)


    # CRISGITime
    def calculate_entropy(self, ref_obs, test_obss, groupby, ref_time, layer='log1p'):
        print('reference observations', len(ref_obs))
        print('test population', len(test_obss))
        self.ref_time = ref_time
        self.init_edata(test_obss, headers=['test', 'subject', 'time', groupby])

        for method in self.interaction_methods:
            if method in ['prod']:
                self._calculate_entropy_by_prod(ref_obs, test_obss, method=method)
            else:
                raise ValueError(f"Unknown method: {method}")

    # CRISGITime
    def _calculate_entropy_by_prod(self, ref_obs, test_obss, method='prod', layer='log1p', obs_cutoff=100):
        
        adata = self.adata
        edata = self.edata

        bg_net = adata.varm['bg_net']
        row, col = bg_net.nonzero()

        ref_obs_is = adata[ref_obs, :].obs.i.tolist()
        ref_n = len(ref_obs_is)
        test_obss_is = [adata[test_obs, :].obs.i.tolist() for test_obs in test_obss]
        X = get_array(adata, layer=layer)
        N, M = X.shape

        gene_std = X[ref_obs_is].std(axis=0)
        ref_interaction_std = (gene_std[row]+gene_std[col])/2

        print_msg(f'---Calculating the entropy for reference group')
        
        ref_R_sum = self._prod(X, ref_obs_is, row, col, obs_cutoff=obs_cutoff)

        ref_R_sparse = csr_matrix((ref_R_sum[row, col]/(ref_n), (row, col)), shape = (M, M))
        ref_interaction_entropy = self.sparseR2entropy(ref_R_sparse, row, col)

        for test_i, test_obs_is in enumerate(test_obss_is):
            print_msg(f'---Calculating the entropy for test population {test_i}, observations {len(test_obs_is)}')

            R = self._prod(X, test_obs_is, row, col, obs_cutoff=obs_cutoff)
            
            R = csr_matrix(((R[row, col]+ref_R_sum[row, col])/(ref_n + len(test_obs_is)), (row, col)), shape = (M, M))
            test_interaction_entropy = self.sparseR2entropy(R, row, col)
            delta_entropy = np.abs(test_interaction_entropy - ref_interaction_entropy)

            gene_std = X[ref_obs_is + test_obs_is].std(axis=0)
            test_interaction_std = (gene_std[row]+gene_std[col])/2
            delta_std = np.abs(test_interaction_std - ref_interaction_std)
            edata.X[test_i, :] = delta_entropy * delta_std
        
        edata.layers[f'{self.ref_time}_{method}_entropy'] = edata.X
        self.edata = edata


    # CRISGITime
    def test_TER(self, target_group=None, p_cutoff=0.05, method='prod', groups=None):
        mytarget_group = target_group
        edata = self.edata

        if groups is None:
            groups = self.groups
        for target_group in groups:
            if mytarget_group is not None and mytarget_group != target_group:
                continue
            trend_list = []
            interactions = edata.uns[f'{method}_{self.groupby}_{target_group}_DER']
            filtered_interactions = []
            for interaction in interactions:
                target_edata = edata[edata.obs[self.groupby] == target_group, :]
                layer = f'{self.ref_time}_{method}_entropy'
                trend_res = self._test_trend(interaction, target_edata, layer, p_cutoff=p_cutoff)
                is_target_trend = trend_res['trend'] != 'no trend'

                ref_edata = edata[edata.obs[self.groupby] != target_group, :]
                zero_res = self._test_zero_trend(interaction, ref_edata, layer)
                is_ref_zero = zero_res['p_value'] < p_cutoff
                trend_res.update(zero_res)

                is_TER = is_target_trend and is_ref_zero
                trend_res['TER'] = is_TER
                trend_res['target_group'] = target_group
                if is_TER:
                    filtered_interactions.append(interaction)
                trend_list.append(trend_res)

            print(f'{method}_{self.groupby}_{target_group}', 'DER', len(interactions), 'TER', len(filtered_interactions))
            edata.uns[f'{method}_{self.groupby}_{target_group}_TER'] = filtered_interactions

            df = pd.DataFrame(trend_list)
            fn = f'{self.out_dir}/{method}_{self.groupby}_{target_group}_TER.csv'
            df.to_csv(fn, index=False)
            print_msg(f'[Output] The trend expressed interaction (TER) statistics are saved to:\n{fn}')
            edata.uns[f'{method}_{self.groupby}_{target_group}_TER_df'] = df
        return

    # CRISGITime
    def test_val_trend_entropy(self, interactions, method='prod',
                               p_cutoff=0.05,
                               out_prefix='./test'):
        edata = self.edata
        candidates = []
        trend_list = []
        for interaction in interactions:
            if interaction not in self.edata.var_names:
                continue            
            layer = f'{self.ref_time}_{method}_entropy'
            trend_res = self._test_trend(interaction, edata, layer, p_cutoff=p_cutoff)
            is_trend = trend_res['trend'] != 'no trend'
            zero_res = self._test_zero_trend(interaction, edata, layer)
            is_zero = zero_res['p_value'] < p_cutoff
            trend_res.update(zero_res)

            is_TER = is_trend or is_zero
            trend_res['TER'] = is_TER

            trend_list.append(trend_res)
            if is_TER:
                candidates.append(interaction)

        print(method, 'val trend before', len(interactions), 'after', len(candidates))

        df = pd.DataFrame(trend_list)
        fn = f'{out_prefix}_TER.csv'
        df.to_csv(fn, index=False)
        print_msg(f'[Output] The validation trend expressed interaction (TER) statistics are saved to:\n{fn}')

        return candidates

    # CRISGITime
    def obs_level_CT_rank(self, gene_sets, **kwargs):
        super(CRISGITime, self).obs_level_CT_rank(gene_sets=gene_sets, **kwargs)
    def pheno_level_CT_rank(self, ref_group, target_group, **kwargs):
        super(CRISGITime, self).pheno_level_CT_rank(ref_group=ref_group, target_group=target_group, **kwargs)
    def pheno_level_accumulated_top_n_ORA(self, target_group, **kwargs):
        super(CRISGITime, self).pheno_level_accumulated_top_n_ORA(target_group=target_group, **kwargs)

    def set_model_type(self, model_type, ae_path=None, mlp_path=None, model_path=None,device='cpu'):
        self.model_type = model_type
        self.device = device
        
        if model_type == "cnn":
            self.model = CNNModel(self.device, ae_path=ae_path, mlp_path=mlp_path)
        elif model_type == "simple_cnn":
            self.model = SimpleCNNModel(self.device, ae_path=ae_path, mlp_path=mlp_path)
        elif model_type == "logistic":
            self.model = LogisticModel(model_path=model_path)
        else:
            raise ValueError(f"Unsupported model_type: {model_type}")

        print(f"Model type set to '{model_type}'.")

    def train(self, train_loader , epochs=10):
        if self.model_type == "logistic":
            return self.model.train(train_loader)
        else:
            return self.model.train(train_loader, epochs=epochs)
        
    def predict(self, data_loader):
        return self.model.predict(data_loader)


SNIEETime = CRISGITime
