# IES-3 Data Analysis Pipeline

This project performs automated exploratory data analysis, metadata-driven statistical testing, and visualization on IES-3 survey data, generating reproducible reports and figures.

---

## Pipeline Overview

```mermaid
flowchart TD
    A[Load Data & Metadata] --> B[Perform EDA]
    B --> C[Generate Demographics]
    C --> D[Run Metadata-Driven Statistical Tests]
    D --> E[Apply Multiple Comparisons Correction (FDR)]
    E --> F[Perform Correlation Analysis]
    F --> G[Create Visualizations]
    G --> H[Generate Website Report]
```

---

## Analysis Plan

### 1. Data Loading and Preprocessing
- Load TSV data and variable definitions (metadata JSON).
- Convert categorical variables using metadata (labels, codes).
- Convert outcome variables to numeric.
- Handle missing values.
- Basic data validation.

### 2. Exploratory Data Analysis (EDA)
- Print dataset shape, columns, data types.
- Summarize missing values.
- Count unique values.
- Show distributions for categorical and numeric variables.
- Save EDA summary to file.

### 3. Demographics and Summary Statistics
- Use metadata to select demographic and independent variables.
- Generate counts and percentages for each category.
- Save demographics table to CSV.
- Summarize IES-3 total and subscale scores.
- Save score summaries.

### 4. Metadata-Driven Statistical Analysis
- Automatically select:
  - **Binary variables** (2 categories) for t-tests and point-biserial correlations.
  - **Multi-category variables** (>2 categories) for ANOVA and eta-squared.
  - **Outcome variables** (IES-3 total and subscales).
- Perform:
  - T-tests with Cohen’s d effect size.
  - One-way ANOVA with eta-squared effect size.
  - Point-biserial correlations.
  - Eta-squared calculations.
- Apply **False Discovery Rate (FDR)** correction across all p-values.
- Save all results to CSV files.

### 5. Correlation Analysis
- Compute Pearson and Spearman correlations among numeric variables.
- Compute Cramér’s V for categorical associations.
- Save correlation matrices and highlight significant/strong correlations.

### 6. Visualization
- Distribution plots for scores.
- Boxplots comparing groups.
- Correlation heatmaps.
- Pair plots colored by categories.
- Categorical association heatmaps.
- Save all plots as PNG files.

### 7. Automated Reporting (Planned)
- Generate a static website (MkDocs) with:
  - Overview and navigation.
  - Embedded tables and plots.
  - Highlights of significant results.
  - Download links for data and results.
- Automate build and deployment with GitHub Actions.

---

## Script Documentation

### `orchestrator.py`
- Coordinates the entire analysis pipeline.
- Loads data and metadata.
- Runs EDA.
- Generates demographics table.
- Performs unified metadata-driven statistical analysis.
- Creates visualizations.
- Saves all outputs to the `results/` directory.

### `data_loader.py`
- Loads data and variable definitions.
- Converts variables based on metadata.
- Provides helper functions:
  - `get_variables_by_type`
  - `get_outcome_variables`
  - `generate_demographics_table`

### `statistical_analysis.py`
- Contains a single unified function:
  - Performs t-tests, ANOVA, correlations, eta-squared.
  - Uses metadata to select variables.
  - Applies FDR correction.
  - Saves all results to CSV.
- Includes helper functions for effect size calculations.

### `visualization.py`
- Generates all plots:
  - Distributions
  - Boxplots
  - Heatmaps
  - Pair plots
  - Categorical association heatmaps
- Saves plots to PNG files.

---

## Expected Outputs

### Results Directory Structure
```
results/
├── demographics.csv
├── score_summary.csv
├── t_test_results.csv
├── anova_results.csv
├── *_correlation_*.csv
├── *_eta_squared_*.csv
├── pearson_correlations.csv
├── spearman_correlations.csv
├── correlation_p_values.csv
├── total_score_distribution.png
├── all_scores_by_categories.png
├── outcome_correlation_heatmap.png
├── categorical_associations_heatmap.png
├── key_variables_pair_plot.png
├── outcomes_by_*.png
└── [other generated plots]
```

---

## Dependencies

- pandas >= 1.3.0
- numpy >= 1.20.0
- scipy >= 1.7.0
- matplotlib >= 3.4.0
- seaborn >= 0.11.0
- statsmodels >= 0.12.0