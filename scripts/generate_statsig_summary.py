#!/usr/bin/env python3

import pandas as pd
import numpy as np
from pathlib import Path
import re
import sys

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from scripts.statistical_analysis import perform_statistical_analysis
from scripts.data_loader import load_data

def generate_statsig_summary(ttest_results, anova_results, alpha=0.05):
    """Generate a markdown summary of statistically significant results"""
    summary = ["# Statistical Significance Summary\n"]
    
    # Process t-test results
    if ttest_results is not None and not ttest_results.empty:
        sig_ttests = ttest_results[ttest_results['p_value'] < alpha]
        if not sig_ttests.empty:
            summary.append("## Statistically Significant T-Test Results\n")
            for _, row in sig_ttests.iterrows():
                summary.append(f"### {row['Variable']} on {row['Outcome']}\n")
                summary.append(f"- t({row['degrees_of_freedom']}) = {row['t_statistic']:.3f}, p = {row['p_value']:.3f}")
                summary.append(f"- Cohen's d = {row['Cohens_d']:.3f}")
                summary.append(f"- {row['Group1']}: Mean = {row['Group1_Mean']:.3f}, SD = {row['Group1_SD']:.3f}")
                summary.append(f"- {row['Group2']}: Mean = {row['Group2_Mean']:.3f}, SD = {row['Group2_SD']:.3f}\n")
    
    # Process ANOVA results
    if anova_results is not None and not anova_results.empty:
        sig_anovas = anova_results[anova_results['p_value'] < alpha]
        if not sig_anovas.empty:
            summary.append("## Statistically Significant ANOVA Results\n")
            for _, row in sig_anovas.iterrows():
                summary.append(f"### {row['Variable']} on {row['Outcome']}\n")
                summary.append(f"- F = {row['F_statistic']:.3f}, p = {row['p_value']:.3f}")
                summary.append(f"- Partial η² = {row['partial_eta_squared']:.3f}\n")
    
    if len(summary) == 1:  # Only the title was added
        summary.append("No statistically significant results found at α = 0.05 (False Discovery Rate not considered in this statement).\n")
    
    return "\n".join(summary)

if __name__ == "__main__":
    # Load data and perform statistical analysis
    print("Loading data and performing statistical analysis...")
    df, var_defs = load_data()
    ttest_results, anova_results = perform_statistical_analysis(df, var_defs)
    
    # Generate summary
    print("Generating statistical significance summary...")
    summary = generate_statsig_summary(ttest_results, anova_results)
    print(summary) 