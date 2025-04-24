#!/usr/bin/env python3

import pandas as pd
from pathlib import Path
import os
import sys
import subprocess

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from scripts.data_loader import load_data, generate_demographics_table
from scripts.eda import perform_eda
from scripts.statistical_analysis import perform_statistical_analysis
from scripts.visualization import create_visualizations
from scripts.generate_statsig_summary import generate_statsig_summary


def main():
    import shutil

    # Clean results directory
    results_dir = project_root / "results"
    if results_dir.exists():
        shutil.rmtree(results_dir)
    results_dir.mkdir(exist_ok=True)

    # Clean site directory
    site_dir = project_root / "site"
    if site_dir.exists():
        shutil.rmtree(site_dir)
    site_dir.mkdir(exist_ok=True)
    """Main function to orchestrate the analysis"""
    print("Loading data...")
    df, var_defs = load_data()
    
    print("\nPerforming Exploratory Data Analysis...")
    perform_eda(df)
    
    print("\nGenerating Demographics and Summary Statistics...")
    # Create results directory if it doesn't exist
    results_dir = project_root / "results"
    results_dir.mkdir(exist_ok=True)
    
    # Generate demographics table using metadata-driven function
    demographics = generate_demographics_table(df, var_defs, save_path=results_dir / 'demographics.csv')
    
    print("\nPerforming Statistical Analysis...")
    
    # Perform statistical analysis
    t_test_df, anova_results = perform_statistical_analysis(df, var_defs)
    
    # Print t-test results
    print("\nT-Test Results:")
    for result in t_test_df.to_dict('records'):
        print(f"\nResults for {result['Variable']} on {result['Outcome']}:")
        print(f"  {result['Group1']}: Mean = {result['Group1_Mean']:.3f}, SD = {result['Group1_SD']:.3f}")
        print(f"  {result['Group2']}: Mean = {result['Group2_Mean']:.3f}, SD = {result['Group2_SD']:.3f}")
        # Use 'dof' from pingouin result if available, otherwise approximate
        dof_str = f"{result.get('dof', len(df)-2):.1f}"
        print(f"  t({dof_str}) = {result['t_statistic']:.3f}, raw_p = {result['raw_p_value']:.3f}, adj_p = {result['p_value']:.3f}")
        print(f"  Cohen's d = {result['Cohens_d']:.3f}")
    
    # Print ANOVA results
    print("\nANOVA Results:")
    for result in anova_results.to_dict('records'):
        print(f"\nResults for {result['Variable']} on {result['Outcome']}:")
        print(f"  F = {result['F_statistic']:.3f}, p = {result['p_value']:.3f}")
        print(f"  Partial Eta-squared = {result['partial_eta_squared']:.3f}")
        # print("  Group Statistics:")
        # print(f"  Group Stats: {result['Group_Stats']}")
    
    # Generate statistical significance summary
    print("\nGenerating Statistical Significance Summary...")
    summary = generate_statsig_summary(t_test_df, anova_results)
    
    print("\nCreating visualizations...")
    from scripts.visualization import create_visualizations
    charts = create_visualizations(df, var_defs)

    # Pass freshly computed stats to report generator

    from scripts.generate_report import generate_docs
    generate_docs(df, var_defs, charts, t_test_results=t_test_df, anova_results=anova_results)
    
    print("\nAnalysis complete! Results saved to CSV files in the results directory.")

    # Generate report markdown files
    print("\nGenerating report markdown files...")

    # Copy FEEDBACK.md to docs/feedback.md
    shutil.copy(project_root / "FEEDBACK.md", project_root / "docs" / "feedback.md")

    # Build MkDocs site
    print("\nBuilding MkDocs site...")
    subprocess.run(["mkdocs", "build"], check=True)


if __name__ == "__main__":
    main() 