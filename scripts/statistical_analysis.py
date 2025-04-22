#!/usr/bin/env python3
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests
from pathlib import Path
import pingouin as pg
from scripts.data_loader import get_outcome_variables, get_variables_by_type

def perform_glm_analysis(df, var_defs, cat_col, outcome_cols, demographic_covariates):
    """
    Simplest ANCOVA using pingouin. Returns flat list of results.
    """
    results = []
    for outcome_col in outcome_cols:
        data = df[[cat_col, outcome_col] + demographic_covariates].dropna()
        if len(data) <= len(demographic_covariates) + 2:
            continue
        try:
            ancova = pg.ancova(data=data, dv=outcome_col, between=cat_col, covar=demographic_covariates)
            main = ancova[ancova['Source'] == cat_col]
            if not main.empty:
                f_val = main['F'].values[0]
                p_val = main['p-unc'].values[0]
                partial_eta_sq = main['np2'].values[0]
            else:
                f_val = p_val = partial_eta_sq = float('nan')
            covariate_effects = {}
            for cov in demographic_covariates:
                cov_row = ancova[ancova['Source'] == cov]
                if not cov_row.empty:
                    covariate_effects[cov] = {
                        'F': float(cov_row['F'].values[0]),
                        'p_value': float(cov_row['p-unc'].values[0]),
                        'partial_eta_sq': float(cov_row['np2'].values[0])
                    }
            results.append({
                'Variable': cat_col,
                'Outcome': outcome_col,
                'F_statistic': float(f_val),
                'p_value': float(p_val),
                'partial_eta_squared': float(partial_eta_sq),
                'Covariate_Effects': covariate_effects,
                'Analysis_Type': 'ANCOVA'
            })
        except Exception as e:
            print(f"Error in ANCOVA for {cat_col} on {outcome_col}: {e}")
            continue
    return results

def perform_statistical_analysis(df, var_defs):
    """
    Minimal orchestration: t-tests, ANCOVA, FDR correction. No CSV output.
    """
    outcome_cols = get_outcome_variables(var_defs)
    demographic_vars = get_variables_by_type(var_defs, 'demographic', 'categorical')
    independent_vars = get_variables_by_type(var_defs, 'independent', 'categorical')

    binary_vars = [col for col in demographic_vars + independent_vars
                   if len(var_defs['variables'][col]['values']) == 2]
    cat_vars = [col for col in demographic_vars + independent_vars
                if len(var_defs['variables'][col]['values']) > 2]

    t_test_results = []
    anova_results = []
    
    # Lists to collect p-values for separate FDR corrections
    t_test_raw_p_values = []
    anova_raw_p_values = []
    anova_p_value_sources = [] # Tracks source (main/covariate) for mapping ANOVA adjusted p-values

    # T-tests
    for var in binary_vars:
        for outcome in outcome_cols:
            groups = df[var].dropna().unique()
            if len(groups) != 2:
                continue
            group1 = df[df[var] == groups[0]][outcome]
            group2 = df[df[var] == groups[1]][outcome]
            # Perform Welch's t-test using pingouin (handles NaNs, provides Cohen's d)
            # correction=True enables Welch's test (unequal variances)
            ttest_res = pg.ttest(group1, group2, correction=True)
            
            # Extract results from the pingouin DataFrame
            t_stat = ttest_res['T'].iloc[0]
            raw_p_val = ttest_res['p-val'].iloc[0]
            cohens_d = ttest_res['cohen-d'].iloc[0]
            dof = ttest_res['dof'].iloc[0] # Degrees of freedom might be useful too
            
            t_test_raw_p_values.append(raw_p_val) # Collect raw p-value for t-test FDR
            
            t_test_results.append({
                'Variable': var,
                'Outcome': outcome,
                # Store raw p-value, will be adjusted later
                'raw_p_value': raw_p_val,
                'p_value': raw_p_val, # Placeholder, overwritten later
                'Group1': groups[0],
                'Group2': groups[1],
                'Group1_Mean': group1.mean(),
                'Group2_Mean': group2.mean(),
                'Group1_SD': group1.std(),
                'Group2_SD': group2.std(),
                't_statistic': t_stat,
                'dof': dof,
                'Cohens_d': cohens_d
            })

    # ANCOVA grouped by independent variable, covariates = demographics
    independent_vars = [v for v, meta in var_defs['variables'].items() if meta.get('type') == 'independent']
    for indep_var in independent_vars:
        # Prepare covariates: one-hot encode demographics
        covariate_df = pd.DataFrame(index=df.index)
        for c in demographic_vars:
            if pd.api.types.is_numeric_dtype(df[c]):
                covariate_df[c] = df[c]
            else:
                dummies = pd.get_dummies(df[c], prefix=c, drop_first=True)
                covariate_df = pd.concat([covariate_df, dummies], axis=1)
        covariate_cols = list(covariate_df.columns)
        df_with_covs = pd.concat([df, covariate_df], axis=1)
        glm_res = perform_glm_analysis(df_with_covs, var_defs, indep_var, outcome_cols, covariate_cols)
        for res in glm_res:
            # Store raw p-value from main effect, adjust later
            raw_main_p = res['p_value'] # Assumes perform_glm returns raw p-unc
            res['raw_p_value'] = raw_main_p
            res['p_value'] = raw_main_p # Placeholder, overwritten later
            res['Group_By_Independent'] = indep_var
            anova_results.append(res)

            # Track main effect p-value for ANOVA FDR
            anova_raw_p_values.append(raw_main_p)
            anova_p_value_sources.append(('main', len(anova_results) - 1))

            # Track covariate p-values for ANOVA FDR
            for cov_name, cov_eff in res['Covariate_Effects'].items():
                raw_cov_p = cov_eff['p_value'] # Assumes perform_glm returns raw p-unc
                cov_eff['raw_p_value'] = raw_cov_p
                cov_eff['p_value'] = raw_cov_p # Placeholder, overwritten later
                anova_raw_p_values.append(raw_cov_p)
                anova_p_value_sources.append(('covariate', len(anova_results) - 1, cov_name))

    # Apply FDR correction separately for t-tests
    if t_test_raw_p_values:
        _, t_test_corrected_pvals, _, _ = multipletests(t_test_raw_p_values, method='fdr_bh')
    else:
        t_test_corrected_pvals = []

    # Apply FDR correction for ANOVAs (main effects and covariates together)
    if anova_raw_p_values:
        _, anova_corrected_pvals, _, _ = multipletests(anova_raw_p_values, method='fdr_bh')
    else:
        anova_corrected_pvals = []

    # Store FDR-adjusted p-values for t-tests
    if t_test_raw_p_values:
        for i, result in enumerate(t_test_results):
            # Raw p-value was already stored during collection
            result['adj_p_value'] = t_test_corrected_pvals[i]
            result['p_value'] = result['adj_p_value'] # Update main p-value field

    # Store FDR-adjusted p-values for ANOVAs
    if anova_raw_p_values:
        for i, (source_type, *source_idx) in enumerate(anova_p_value_sources):
            # Raw p-value was already stored during collection
            adj_p = anova_corrected_pvals[i]

            if source_type == 'main':
                idx = source_idx[0]
                anova_results[idx]['adj_p_value'] = adj_p
                anova_results[idx]['p_value'] = adj_p # Update main p-value field
            elif source_type == 'covariate':
                anova_idx, cov_name = source_idx
                anova_results[anova_idx]['Covariate_Effects'][cov_name]['adj_p_value'] = adj_p
                anova_results[anova_idx]['Covariate_Effects'][cov_name]['p_value'] = adj_p # Update main p-value field

    print("Analysis complete.")
    t_test_df = pd.DataFrame(t_test_results)
    anova_df = pd.DataFrame(anova_results)
    return t_test_df, anova_df