#!/usr/bin/env python3

import os
from pathlib import Path
import pandas as pd
import altair as alt

RESULTS_DIR = Path("results")
DOCS_DIR = Path("docs")
ASSETS_DIR = DOCS_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
TABLES_DIR = ASSETS_DIR / "tables"

def setup_dirs():
    for d in [DOCS_DIR, IMAGES_DIR, TABLES_DIR]:
        d.mkdir(parents=True, exist_ok=True)

def copy_assets():
    # Copy CSVs only
    if RESULTS_DIR.exists():
        for file in RESULTS_DIR.glob("*.csv"):
            dest = TABLES_DIR / file.name
            dest.write_bytes(file.read_bytes())

def write_index():
    readme_path = Path("README.md")
    readme_content = ""
    if readme_path.exists():
        readme_content = readme_path.read_text()

    nav_content = ""

    content = readme_content + nav_content
    (DOCS_DIR / "index.md").write_text(content)

def write_data_summary(df, var_defs, charts):
    content = "# Variable Summary\n\n"

    # Get variables by type from metadata
    demographic_cols = [col for col, info in var_defs['variables'].items() if info['type'] == 'demographic']
    independent_cols = [col for col, info in var_defs['variables'].items() if info['type'] == 'independent']
    outcome_cols = [col for col, info in var_defs['variables'].items() if info['type'] == 'outcome']

    # Demographics section
    content += "## Demographics\n\n"
    for var in demographic_cols:
        content += f"### {var}\n\n"
        chart = charts.get('distributions', {}).get(var)
        if chart:
            content += f"```vegalite\n{chart.to_json()}\n```\n\n"
        if var in df.columns:
            freq = df[var].value_counts(dropna=False).reset_index()
            freq.columns = [var, 'Count']
            content += freq.to_markdown(index=False) + "\n\n"
        else:
            content += "_No data available._\n\n"

    # Independent Variables section
    content += "## Independent Variables\n\n"
    for var in independent_cols:
        content += f"### {var}\n\n"
        chart = charts.get('distributions', {}).get(var)
        if chart:
            content += f"```vegalite\n{chart.to_json()}\n```\n\n"
        if var in df.columns:
            freq = df[var].value_counts(dropna=False).reset_index()
            freq.columns = [var, 'Count']
            content += freq.to_markdown(index=False) + "\n\n"
        else:
            content += "_No data available._\n\n"

    # Score distributions
    df_scores = df[outcome_cols] if all(c in df.columns for c in outcome_cols) else pd.DataFrame()

    if not df_scores.empty:
        content += "## Score Summaries\n\n"
        
        # Add boxplot
        boxplot = charts.get('score_boxplot')
        if boxplot:
            content += f"```vegalite\n{boxplot.to_json()}\n```\n\n"

        # Add layered histogram if available
        layered_hist = charts.get('score_layered_hist')
        if layered_hist:
            content += f"```vegalite\n{layered_hist.to_json()}\n```\n\n"

        # Add score summary table
        content += df_scores.describe().transpose().to_markdown() + "\n\n"

    (DOCS_DIR / "data_summary.md").write_text(content)

def write_eda(df, var_defs, charts):
    content = "# Bivariate Relationships\n\n"

    # Pair plot
    pair_plot = charts.get('pair_plot')
    if pair_plot:
        spec = pair_plot.to_json()
        content += "## Outcome Pair Plot\n\n"
        content += f"```vegalite\n{spec}\n```\n\n"

    # Correlation heatmap
    corr_heatmap = charts.get('heatmap')
    if corr_heatmap:
        spec = corr_heatmap.to_json()
        content += "## Correlation Heatmap\n\n"
        content += f"```vegalite\n{spec}\n```\n\n"

    # Categorical associations heatmap
    cat_assoc = charts.get('cramer')
    if cat_assoc:
        spec = cat_assoc.to_json()
        content += "## Categorical Associations\n\n"
        content += f"```vegalite\n{spec}\n```\n\n"

    (DOCS_DIR / "eda.md").write_text(content)

def write_analysis(df, var_defs, charts, t_test_results=None, anova_results=None):
    content = "# Statistical Analysis\n\n"

    # T-tests
    content += "## t-tests\n\n"
    if t_test_results is not None and not t_test_results.empty:
        predictors = t_test_results['Variable'].unique()
        for predictor in predictors:
            content += f"### {predictor}\n\n"
            subset = t_test_results[t_test_results['Variable'] == predictor].drop(columns=['Variable'], errors='ignore')

            # Embed plot above table
            scores_by = charts.get('boxplots', {})
            for key, chart in scores_by.items():
                if key.strip().lower() == predictor.strip().lower():
                    spec = chart.to_json()
                    content += f"```vegalite\n{spec}\n```\n\n"

            content += subset.to_markdown(index=False) + "\n\n"
    else:
        content += "_No t-test results available._\n\n"

    # ANCOVA with demographic covariates
    content += "## ANCOVA with Demographic Covariates\n\n"
    content += "_Note: All p-values are adjusted using False Discovery Rate (FDR) correction to control for multiple comparisons._\n\n"
    
    if anova_results is not None and not anova_results.empty:
        grouped = {}
        for row in anova_results.to_dict('records'):
            group = row.get('Group_By_Independent', 'Other')
            grouped.setdefault(group, []).append(row)

        for indep_var, rows in grouped.items():
            content += f"### {indep_var}\n\n"
            for row in rows:
                effect_size_name = 'partial_eta_squared'
                effect_size_value = row.get(effect_size_name, 0)
                
                content += f"#### {row['Outcome']}\n\n"
                
                # Embed ANCOVA plot (boxplot) for this variable immediately after heading
                boxplots = charts.get('boxplots', {})
                for key, chart in boxplots.items():
                    if key.strip().lower() == str(row['Variable']).strip().lower():
                        spec = chart.to_json()
                        content += f"```vegalite\n{spec}\n```\n\n"
                        break

                content += f"- **F** = {row['F_statistic']:.3f}\n"
                content += f"- **p** = {row['p_value']:.3f} (FDR-adjusted)\n"
                content += f"- **{effect_size_name.replace('_', ' ').title()}** = {effect_size_value:.3f}\n\n"

                # Add covariate effects table without heading
                covariate_effects = row.get('Covariate_Effects', {})
                if covariate_effects:
                    content += "| Covariate | F | p-value (FDR-adjusted) | Partial η² |\n"
                    content += "|-----------|---|------------------------|------------|\n"
                    for cov, effect in covariate_effects.items():
                        content += f"| {cov} | {effect['F']:.3f} | {effect['p_value']:.3f} | {effect['partial_eta_sq']:.3f} |\n"
                    content += "\n"
    else:
        content += "_No ANCOVA results available._\n\n"

    # Drill-down chart
    drilldown = charts.get('drilldown_chart')
    if drilldown:
        spec = drilldown.to_json()
        content += "## Drill-down Chart\n\n"
        content += f"```vegalite\n{spec}\n```\n\n"

    (DOCS_DIR / "analysis.md").write_text(content)

def generate_docs(df, var_defs, charts, t_test_results=None, anova_results=None):
    setup_dirs()
    copy_assets()
    write_index()
    write_data_summary(df, var_defs, charts)
    write_eda(df, var_defs, charts)
    write_analysis(df, var_defs, charts, t_test_results, anova_results)
