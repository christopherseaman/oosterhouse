#!/usr/bin/env python3

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
from data_loader import get_variables_by_type, get_outcome_variables
from statsmodels.stats.multitest import multipletests

def point_biserial_correlation(df, var_defs, binary_col, outcome_cols):
    """Calculate point-biserial correlation between binary and continuous variables"""
    results = []
    var_info = var_defs['variables'][binary_col]
    
    for outcome_col in outcome_cols:
        outcome_info = var_defs['variables'][outcome_col]
        # Use categorical codes (0-based) for correlation
        r, p_val = stats.pointbiserialr(df[binary_col].cat.codes, df[outcome_col])
        results.append({
            'Outcome': outcome_col,
            'Outcome_Description': outcome_info.get('description', ''),
            'Variable': binary_col,
            'Correlation': r,
            'p_value': p_val,
            'Group_Means': {
                label: df[df[binary_col] == label][outcome_col].mean()
                for label in df[binary_col].cat.categories
            },
            'Group_SDs': {
                label: df[df[binary_col] == label][outcome_col].std()
                for label in df[binary_col].cat.categories
            }
        })
    return pd.DataFrame(results)

def eta_squared(df, var_defs, cat_col, outcome_cols):
    """Calculate eta-squared (η²) for categorical-continuous correlation"""
    results = []
    var_info = var_defs['variables'][cat_col]
    
    for outcome_col in outcome_cols:
        outcome_info = var_defs['variables'][outcome_col]
        # Calculate total sum of squares
        total_mean = df[outcome_col].mean()
        total_ss = np.sum((df[outcome_col] - total_mean) ** 2)
        
        # Calculate between-group sum of squares using observed=True to avoid warning
        group_means = df.groupby(cat_col, observed=True)[outcome_col].mean()
        group_counts = df.groupby(cat_col, observed=True)[outcome_col].count()
        between_ss = np.sum(group_counts * (group_means - total_mean) ** 2)
        
        # Calculate eta-squared
        eta_sq = between_ss / total_ss
        
        # Calculate F-statistic and p-value
        k = len(group_means)  # number of groups
        n = len(df)  # total sample size
        df_between = k - 1
        df_within = n - k
        f_stat = (between_ss / df_between) / ((total_ss - between_ss) / df_within)
        p_val = 1 - stats.f.cdf(f_stat, df_between, df_within)
        
        results.append({
            'Outcome': outcome_col,
            'Outcome_Description': outcome_info.get('description', ''),
            'Variable': cat_col,
            'Eta_squared': eta_sq,
            'F_statistic': f_stat,
            'p_value': p_val,
            'Group_Means': dict(df.groupby(cat_col, observed=True)[outcome_col].mean()),
            'Group_SDs': dict(df.groupby(cat_col, observed=True)[outcome_col].std())
        })
    return pd.DataFrame(results)

def perform_statistical_analysis(df, var_defs):
    """
    Unified statistical analysis using metadata.
    Performs t-tests, ANOVA, point-biserial correlations, and eta squared calculations.
    Applies FDR correction across all p-values.
    Saves results to CSV files.
    """
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)

    # Get outcome variables (subscales and total score)
    outcome_cols = get_outcome_variables(var_defs)

    # Get categorical variables by type
    demographic_vars = get_variables_by_type(var_defs, 'demographic', 'categorical')
    independent_vars = get_variables_by_type(var_defs, 'independent', 'categorical')

    # Binary variables (2 categories) - based on metadata
    binary_vars = [col for col in demographic_vars + independent_vars
                   if len(var_defs['variables'][col]['values']) == 2]

    # Multi-category variables (>2 categories)
    cat_vars = [col for col in demographic_vars + independent_vars
                if len(var_defs['variables'][col]['values']) > 2]

    # Initialize results containers
    t_test_results = []
    anova_results = []
    all_p_values = []

    # --- T-tests for binary variables ---
    print(f"Binary variables for t-tests: {binary_vars}")
    for var in binary_vars:
        print(f"\nProcessing t-tests for: {var}")
        for outcome in outcome_cols:
            print(f"  Outcome: {outcome}")
            groups = df[var].dropna().unique()
            print(f"    Unique groups found: {groups}")
            if len(groups) != 2:
                print(f"    Skipping: Expected 2 groups, found {len(groups)}")
                continue  # skip if not exactly 2 groups
            group1_data = df[df[var] == groups[0]][outcome]
            group2_data = df[df[var] == groups[1]][outcome]

            t_stat, p_val = stats.ttest_ind(group1_data, group2_data, nan_policy='omit')
            all_p_values.append(p_val)

            # Effect size (Cohen's d)
            n1, n2 = len(group1_data), len(group2_data)
            var1, var2 = np.var(group1_data, ddof=1), np.var(group2_data, ddof=1)
            pooled_se = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
            cohens_d = (np.mean(group1_data) - np.mean(group2_data)) / pooled_se

            t_test_results.append({
                'Variable': var,
                'Outcome': outcome,
                'Group1': groups[0],
                'Group2': groups[1],
                'Group1_Mean': np.mean(group1_data),
                'Group2_Mean': np.mean(group2_data),
                'Group1_SD': np.std(group1_data, ddof=1),
                'Group2_SD': np.std(group2_data, ddof=1),
                't_statistic': t_stat,
                'p_value': p_val,
                'Cohens_d': cohens_d
            })

    # --- ANOVA for multi-category variables ---
    for var in cat_vars:
        for outcome in outcome_cols:
            groups = [group for _, group in df.groupby(var, observed=True)[outcome]]
            if len(groups) <= 1:
                continue  # skip if only one group

            f_stat, p_val = stats.f_oneway(*groups)
            all_p_values.append(p_val)

            # Effect size (eta squared)
            groups_data = df.groupby(var, observed=True)[outcome]
            ss_between = sum(len(group) * (group.mean() - df[outcome].mean()) ** 2 for _, group in groups_data)
            ss_total = sum((df[outcome] - df[outcome].mean()) ** 2)
            eta_sq = ss_between / ss_total

            # Group stats
            group_stats = {}
            for name, group in df.groupby(var, observed=True)[outcome]:
                group_stats[name] = {
                    'n': int(len(group)),
                    'mean': float(group.mean()),
                    'std': float(group.std())
                }

            anova_results.append({
                'Variable': var,
                'Outcome': outcome,
                'F_statistic': f_stat,
                'p_value': p_val,
                'eta_squared': eta_sq,
                'Group_Stats': group_stats
            })

    # --- Point-biserial correlations ---
    print("\nPerforming point-biserial correlations...")
    for var in binary_vars:
        results = point_biserial_correlation(df, var_defs, var, outcome_cols)
        # Save individual results
        var_type = var_defs['variables'][var]['type']
        var_file = f"{var_type}_correlation_{var.lower().replace(' ', '_').replace('?', '').replace('-', '_')}.csv"
        results.to_csv(results_dir / var_file, index=False)
        all_p_values.extend(results['p_value'].tolist())

    # --- Eta squared calculations ---
    print("\nPerforming eta-squared calculations...")
    for var in cat_vars:
        results = eta_squared(df, var_defs, var, outcome_cols)
        # Save individual results
        var_type = var_defs['variables'][var]['type']
        var_file = f"{var_type}_eta_squared_{var.lower().replace(' ', '_').replace('?', '').replace('-', '_')}.csv"
        results.to_csv(results_dir / var_file, index=False)
        all_p_values.extend(results['p_value'].tolist())

    # --- Apply FDR correction ---
    _, corrected_p_values, _, _ = multipletests(all_p_values, method='fdr_bh')

    # Update p-values in t-test and ANOVA results
    idx = 0
    for result in t_test_results:
        result['p_value'] = corrected_p_values[idx]
        idx += 1
    for result in anova_results:
        result['p_value'] = corrected_p_values[idx]
        idx += 1

    # Save t-test results
    pd.DataFrame(t_test_results).to_csv(results_dir / 't_test_results.csv', index=False)

    # Save ANOVA results
    anova_df = pd.DataFrame(anova_results)
    anova_df['Group_Stats'] = anova_df['Group_Stats'].apply(str)
    anova_df.to_csv(results_dir / 'anova_results.csv', index=False)

    # Save score summary
    score_summary = df[outcome_cols].agg(['mean', 'std', 'min', 'max']).round(3)
    score_summary.to_csv(results_dir / "score_summary.csv")

    print("\nAnalysis complete! Results saved to CSV files in the results directory.")

    # Convert results to DataFrames
    t_test_df = pd.DataFrame(t_test_results)
    anova_df = pd.DataFrame(anova_results)

    return t_test_df, anova_df
    return t_test_results, anova_results

def perform_statistical_analysis_with_var_defs(df, var_defs):
    """
    Perform statistical analysis using variable definitions
    """
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)
    
    # Get outcome variables (subscales and total score)
    outcome_cols = get_outcome_variables(var_defs)
    
    # Get categorical variables by type
    demographic_vars = get_variables_by_type(var_defs, 'demographic', 'categorical')
    independent_vars = get_variables_by_type(var_defs, 'independent', 'categorical')
    
    # Binary variables for point-biserial correlation (both demographic and independent)
    binary_vars = [col for col in demographic_vars + independent_vars 
                  if len(var_defs['variables'][col]['values']) == 2]
    
    # Multi-category variables for eta-squared
    cat_vars = [col for col in demographic_vars + independent_vars 
                if len(var_defs['variables'][col]['values']) > 2]
    
    # Perform point-biserial correlations
    print("\nPerforming point-biserial correlations...")
    for var in binary_vars:
        results = point_biserial_correlation(df, var_defs, var, outcome_cols)
        print(f"\nResults for {var}:")
        print(results)
        # Save individual results with type-based filename
        var_type = var_defs['variables'][var]['type']
        var_file = f"{var_type}_correlation_{var.lower().replace(' ', '_').replace('?', '').replace('-', '_')}.csv"
        results.to_csv(results_dir / var_file, index=False)
    
    # Perform eta-squared calculations
    print("\nPerforming eta-squared calculations...")
    for var in cat_vars:
        results = eta_squared(df, var_defs, var, outcome_cols)
        print(f"\nResults for {var}:")
        print(results)
        # Save individual results with type-based filename
        var_type = var_defs['variables'][var]['type']
        var_file = f"{var_type}_eta_squared_{var.lower().replace(' ', '_').replace('?', '').replace('-', '_')}.csv"
        results.to_csv(results_dir / var_file, index=False)
    
    # Calculate and save score summary
    score_summary = df[outcome_cols].agg(['mean', 'std', 'min', 'max']).round(3)
    print("\nScore Summary:")
    print(score_summary)
    score_summary.to_csv(results_dir / "score_summary.csv")
    
    print("\nAnalysis complete! Results saved to CSV files in the results directory.") 