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
    all_p_values = []

    # T-tests
    for var in binary_vars:
        for outcome in outcome_cols:
            groups = df[var].dropna().unique()
            if len(groups) != 2:
                continue
            group1 = df[df[var] == groups[0]][outcome]
            group2 = df[df[var] == groups[1]][outcome]
            t_stat, p_val = stats.ttest_ind(group1, group2, nan_policy='omit')
            all_p_values.append(p_val)
            # Calculate Cohen's d
            n1, n2 = len(group1), len(group2)
            var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
            pooled_sd = np.sqrt(((n1 - 1)*var1 + (n2 - 1)*var2) / (n1 + n2 - 2))
            cohens_d = (np.mean(group1) - np.mean(group2)) / pooled_sd if pooled_sd > 0 else 0
            t_test_results.append({
                'Variable': var,
                'Outcome': outcome,
                'Group1': groups[0],
                'Group2': groups[1],
                'Group1_Mean': group1.mean(),
                'Group2_Mean': group2.mean(),
                'Group1_SD': group1.std(),
                'Group2_SD': group2.std(),
                't_statistic': t_stat,
                'p_value': p_val,
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
            res['Group_By_Independent'] = indep_var
            anova_results.append(res)
            all_p_values.append(res['p_value'])
            for cov_eff in res['Covariate_Effects'].values():
                all_p_values.append(cov_eff['p_value'])

    # FDR correction
    _, corrected_pvals, _, _ = multipletests(all_p_values, method='fdr_bh')
    idx = 0
    for res in t_test_results:
        res['p_value'] = corrected_pvals[idx]
        idx += 1
    for res in anova_results:
        res['p_value'] = corrected_pvals[idx]
        idx += 1

    print("Analysis complete.")
    t_test_df = pd.DataFrame(t_test_results)
    anova_df = pd.DataFrame(anova_results)
    return t_test_df, anova_df