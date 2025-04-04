#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os
from scipy.stats import contingency

def create_visualizations(df, var_defs=None):
    """
    Create various visualizations of the data
    Args:
        df: pandas DataFrame containing the data
        var_defs: optional dictionary containing variable definitions and mappings
    """
    results_dir = Path(__file__).parent.parent / "results"
    
    # Set style
    plt.style.use('seaborn-v0_8')
    
    # Create results directory if it doesn't exist
    os.makedirs(results_dir, exist_ok=True)
    
    # Define key variable groups
    outcome_cols = ['Total Score Avg', 'SS1 avg', 'SS2 avg', 'SS3 avg', 'SS4 avg']
    demographic_cols = [
        'What is your gender? - Selected Choice',
        'What school do you attend? - Selected Choice',
        'What is your year in school? - Selected Choice'
    ]
    independent_cols = [
        'Have you ever been diagnosed with an eating disorder?',
        'Have you every been told you should change your weight?',
        'Weight-sensitive sport',
        'Endurance sport'
    ]
    
    # All key variables for analysis
    analysis_cols = demographic_cols + independent_cols + outcome_cols
    
    # Columns to exclude
    exclude_cols = [
        # Inclusion criteria
        'Are you age 18 or older?',
        'Are you a current NCAA athlete?',
        'Can you read and write in English?',
        # Text columns
        'What is your gender? - Other - Text',
        'What school do you attend? - Other - Text',
        'What is your year in school? - Other - Text',
        'What sport do you participate in?',
        # Individual questions and raw subscales
        'Q1', 'Q2', 'Q3', 'SS1',
        'Q4', 'Q5', 'Q6', 'SS2',
        'Q7', 'Q8', 'Q9', 'SS3',
        'Q10', 'Q11', 'Q12', 'SS4',
        'Total Score'  # Using Total Score Avg instead
    ]
    
    # 1. Distribution of Total Score
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df, x='Total Score Avg', bins=20)
    plt.title('Distribution of Total IES-3 Score')
    plt.xlabel('Total Score Average')
    plt.ylabel('Count')
    plt.savefig(results_dir / 'total_score_distribution.png')
    plt.close()
    
    # 2. Box plots for all categorical variables vs outcomes
    n_cats = len(demographic_cols + independent_cols)
    n_outcomes = len(outcome_cols)
    fig, axes = plt.subplots(n_cats, 1, figsize=(15, 5*n_cats))
    fig.suptitle('Score Distributions by Categorical Variables', y=1.02, fontsize=16)
    
    # Create melted dataframe for box plots
    df_melted = df.melt(
        id_vars=demographic_cols + independent_cols,
        value_vars=outcome_cols,
        var_name='Score Type',
        value_name='Score'
    )
    
    for idx, var in enumerate(demographic_cols + independent_cols):
        sns.boxplot(data=df_melted, x='Score Type', y='Score', 
                    hue=var, ax=axes[idx])
        axes[idx].set_title(f'Scores by {var}')
        axes[idx].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig(results_dir / 'all_scores_by_categories.png', bbox_inches='tight', dpi=300)
    plt.close()
    
    # 3. Correlation heatmap for outcome variables only
    plt.figure(figsize=(10, 8))
    sns.heatmap(df[outcome_cols].corr(method='pearson'), annot=True, cmap='coolwarm', center=0,
                xticklabels=True, yticklabels=True, fmt='.2f')
    plt.title('Correlation Heatmap: Outcome Variables')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(results_dir / 'outcome_correlation_heatmap.png', bbox_inches='tight', dpi=300)
    plt.close()
    
    # 4. Categorical associations visualization
    # Create a matrix to store Cramer's V values
    n_cats = len(demographic_cols + independent_cols)
    cramer_matrix = np.zeros((n_cats, n_cats))
    cat_vars = demographic_cols + independent_cols
    
    # Calculate Cramer's V for each pair of categorical variables
    for i, var1 in enumerate(cat_vars):
        for j, var2 in enumerate(cat_vars):
            if i > j:  # Only calculate for upper triangle
                try:
                    # Create contingency table
                    contingency_table = pd.crosstab(df[var1], df[var2])
                    # Calculate Cramer's V using scipy
                    v = contingency.association(contingency_table, method='cramer')
                    cramer_matrix[i, j] = v
                    cramer_matrix[j, i] = v  # Matrix is symmetric
                except:
                    # If calculation fails, set to 0
                    cramer_matrix[i, j] = 0
                    cramer_matrix[j, i] = 0
    
    # Plot Cramer's V heatmap
    plt.figure(figsize=(12, 10))
    mask = np.triu(np.ones_like(cramer_matrix), k=1)  # Mask upper triangle
    sns.heatmap(cramer_matrix, annot=True, cmap='YlOrRd', center=0,
                xticklabels=[x.split(' - ')[0] for x in cat_vars],
                yticklabels=[x.split(' - ')[0] for x in cat_vars],
                mask=mask, fmt='.2f', vmin=0, vmax=1)
    plt.title("Categorical Associations (Cramer's V)")
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(results_dir / 'categorical_associations_heatmap.png', bbox_inches='tight', dpi=300)
    plt.close()
    
    # 5. Create comprehensive pair plot with key variables
    plt.figure(figsize=(20, 20))
    comprehensive_pair = sns.pairplot(
        df[analysis_cols],
        diag_kind='hist',
        plot_kws={'alpha': 0.6},
        height=2.5
    )
    comprehensive_pair.fig.suptitle('Comprehensive Pair Plot: Key Variables', y=1.02)
    comprehensive_pair.savefig(results_dir / 'key_variables_pair_plot.png', bbox_inches='tight', dpi=300)
    plt.close()
    
    # 6. Create separate outcome pair plots colored by each categorical variable
    for cat_var in demographic_cols + independent_cols:
        plt.figure(figsize=(15, 15))
        outcome_pair = sns.pairplot(
            df[outcome_cols + [cat_var]],
            diag_kind='hist',
            plot_kws={'alpha': 0.6},
            hue=cat_var,
            height=2.5
        )
        outcome_pair.fig.suptitle(f'Outcome Variables by {cat_var}', y=1.02)
        # Create a safe filename
        safe_filename = cat_var.lower().replace(" ", "_").replace("?", "").replace("-", "_")
        outcome_pair.savefig(results_dir / f'outcomes_by_{safe_filename}.png', bbox_inches='tight', dpi=300)
        plt.close()
    
    print("\nVisualizations have been saved to the 'results' directory.") 