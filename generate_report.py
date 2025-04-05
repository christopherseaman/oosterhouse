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
    content = "# Data Summary\n\n"

    # Demographics and Independents
    sections = {
        "Demographics": [
            "What is your gender? - Selected Choice",
            "What school do you attend? - Selected Choice",
            "What is your year in school? - Selected Choice"
        ],
        "Independent Variables": [
            "Have you ever been diagnosed with an eating disorder?",
            "Have you every been told you should change your weight?",
            "Weight-sensitive sport",
            "Endurance sport"
        ]
    }

    for section, vars_list in sections.items():
        content += f"## {section}\n\n"
        for var in vars_list:
            # Embed univariate plot if available
            safe_var = var.replace("?", "").replace("-", "").replace(" ", "_").replace("/", "_").replace("\\", "_")
            chart = charts.get('distributions', {}).get(var) or charts.get('distributions', {}).get(safe_var)
            if chart:
                spec = chart.to_json()
                content += f"### Distribution of {var}\n\n"
                content += f"```vegalite\n{spec}\n```\n\n"

            # Add table for this variable
            if 'Variable' in df.columns:
                subset = df[df['Variable'] == var]
                content += f"### {var}\n\n"
                if not subset.empty:
                    content += subset.to_markdown(index=False) + "\n\n"
                else:
                    content += "_No data available._\n\n"

    # Score distributions
    score_cols = ["Total Score Avg", "SS1 avg", "SS2 avg", "SS3 avg", "SS4 avg"]
    df_scores = df[score_cols] if all(c in df.columns for c in score_cols) else pd.DataFrame()

    if not df_scores.empty:
        # Boxplot
        boxplot = charts.get('score_boxplot')
        if boxplot:
            spec = boxplot.to_json()
            content += "### Score Distributions (Boxplot)\n\n"
            content += f"```vegalite\n{spec}\n```\n\n"

        # Layered histogram
        layered_hist = charts.get('score_layered_hist')
        if layered_hist:
            spec = layered_hist.to_json()
            content += "### Layered Histograms of Scores\n\n"
            content += f"```vegalite\n{spec}\n```\n\n"

        # Score summary table
        content += "## Score Summaries\n\n"
        content += df_scores.describe().transpose().to_markdown() + "\n\n"

    (DOCS_DIR / "data_summary.md").write_text(content)

def write_eda(df, var_defs, charts):
    content = "# Exploratory Data Analysis\n\n"

    # Pair plot
    pair_plot = charts.get('pair_plot')
    if pair_plot:
        spec = pair_plot.to_json()
        content += "## Outcome Pair Plot\n\n"
        content += f"```vegalite\n{spec}\n```\n\n"

    # Correlation heatmap
    corr_heatmap = charts.get('correlation_heatmap')
    if corr_heatmap:
        spec = corr_heatmap.to_json()
        content += "## Correlation Heatmap\n\n"
        content += f"```vegalite\n{spec}\n```\n\n"

    # Categorical associations heatmap
    cat_assoc = charts.get('categorical_associations_heatmap')
    if cat_assoc:
        spec = cat_assoc.to_json()
        content += "## Categorical Associations\n\n"
        content += f"```vegalite\n{spec}\n```\n\n"

    # Scores by categories
    scores_by = charts.get('scores_by', {})
    for var, chart in scores_by.items():
        spec = chart.to_json()
        content += f"## Scores by {var}\n\n"
        content += f"```vegalite\n{spec}\n```\n\n"

    (DOCS_DIR / "eda.md").write_text(content)

def write_analysis(df, var_defs, charts, t_test_results=None, anova_results=None):
    content = "# Statistical Analysis\n\n"

    # T-tests
    content += "## T-Tests\n\n"
    if t_test_results is not None and not t_test_results.empty:
        content += t_test_results.to_markdown(index=False) + "\n\n"
    else:
        content += "_No t-test results available._\n\n"

    # ANOVA
    content += "## ANOVA\n\n"
    if anova_results is not None and not anova_results.empty:
        content += anova_results.to_markdown(index=False) + "\n\n"
    else:
        content += "_No ANOVA results available._\n\n"

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
