#!/usr/bin/env python3

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

def perform_correlation_analysis(df):
    """
    Perform correlation analysis between variables
    """
    results_dir = Path(__file__).parent.parent / "results"
    
    # Select numeric columns for correlation analysis
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    # Initialize results dictionary
    correlation_results = {
        'pearson': pd.DataFrame(index=numeric_cols, columns=numeric_cols),
        'spearman': pd.DataFrame(index=numeric_cols, columns=numeric_cols),
        'p_values': pd.DataFrame(index=numeric_cols, columns=numeric_cols)
    }
    
    # Calculate correlations
    for i, col1 in enumerate(numeric_cols):
        for j, col2 in enumerate(numeric_cols):
            if i <= j:  # Only calculate once for each pair
                # Pearson correlation
                pearson_corr, pearson_p = stats.pearsonr(df[col1], df[col2])
                correlation_results['pearson'].loc[col1, col2] = pearson_corr
                correlation_results['pearson'].loc[col2, col1] = pearson_corr
                
                # Spearman correlation
                spearman_corr, spearman_p = stats.spearmanr(df[col1], df[col2])
                correlation_results['spearman'].loc[col1, col2] = spearman_corr
                correlation_results['spearman'].loc[col2, col1] = spearman_corr
                
                # P-values (using Pearson's p-value)
                correlation_results['p_values'].loc[col1, col2] = pearson_p
                correlation_results['p_values'].loc[col2, col1] = pearson_p
    
    # Save results
    correlation_results['pearson'].to_csv(results_dir / "pearson_correlations.csv")
    correlation_results['spearman'].to_csv(results_dir / "spearman_correlations.csv")
    correlation_results['p_values'].to_csv(results_dir / "correlation_p_values.csv")
    
    # Print significant correlations
    print("\nSignificant Correlations (p < 0.05):")
    significant_correlations = correlation_results['pearson'][
        correlation_results['p_values'] < 0.05
    ]
    print(significant_correlations)
    
    # Print strongest correlations
    print("\nStrongest Correlations (|r| > 0.5):")
    strong_correlations = correlation_results['pearson'][
        abs(correlation_results['pearson']) > 0.5
    ]
    print(strong_correlations) 