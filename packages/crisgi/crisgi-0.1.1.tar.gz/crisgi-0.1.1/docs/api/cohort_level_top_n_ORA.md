# cohort_level_top_n_ORA

## Function

```python
crisgi_obj.cohort_level_top_n_ORA(
    n_top_interactions=None,
    top_percentage=0.05,
    method='prod',
    gene_sets=[
        'KEGG_2021_Human',
        'GO_Molecular_Function_2023',
        'GO_Cellular_Component_2023',
        'GO_Biological_Process_2023',
        'MSigDB_Hallmark_2020'
    ],
    background=None,
    organism='human',
    plot=True,
)
```

Performs cohort-level over-representation analysis (ORA) for the top-*n* interactions in the dataset, across multiple samples. This method filters the interactions based on two criteria: the percentage of top interactions for each sample and the number of top ineractions ranking across the occurrences. It then performs enrichment analysis using the specified gene sets and method.

## Parameters

| Name                | Type      | Description                                                                                   |
|---------------------|-----------|-----------------------------------------------------------------------------------------------|
| n_top_interactions  | int, optional | Number of top interactions to consider. If None, uses all available interactions.         |
| top_percentage      | float, optional | Percentage of top interactions to consider. Default is `0.05`, meaning 5% of interactions. |
| method              | str, optional | Method used for scoring interactions (e.g., `'prod'`). Default is `'prod'`.               |
| gene_sets           | list of str, optional | List of gene set names to use for enrichment analysis. Default includes several common sets. |
| background          | list or None, optional | Background gene set for enrichment. If None, uses all genes in the dataset.      |
| organism            | str, optional | Organism name (e.g., `'human'`). Default is `'human'`.                                    |
| plot                | bool, optional | Whether to generate plots for the enrichment results. Default is `True`.                 |

## Return type

`None`

## Returns

This function does not return a value. It saves the enrichment results to a CSV file and updates the object's attributes with the results.

## Attributes Set

- `self.edata.uns[f'{method}_cohort_enrich_res']`: Dictionary mapping top N values to enrichment results.
- `self.edata.uns[f'{method}_cohort_enrich_df']`: DataFrame containing concatenated enrichment results for all top N values.

## Example

```python
# Assuming `obj` is an instance of the class containing this method

obj.cohort_level_top_n_ORA(
    n_top_interactions=100,
    method='prod',
    gene_sets=['KEGG_2021_Human', 'GO_Biological_Process_2023'],
    organism='human',
    plot=True
)

# After execution, enrichment results are saved to a CSV file in obj.out_dir,
# and results are accessible via:
# obj.edata.uns['prod_cohort_enrich_res']
# obj.edata.uns['prod_cohort_enrich_df']
```
