#!/usr/bin/env python3

import pandas as pd
import numpy as np
from pathlib import Path

def calculate_descriptive_stats(df):
    """
    Calculate and save descriptive statistics for the dataset
    """
    results_dir = Path(__file__).parent.parent / "results"
    
    # Calculate basic statistics for numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    numeric_stats = df[numeric_cols].describe()
    
    # Calculate frequency tables for categorical columns
    categorical_cols = df.select_dtypes(include=['category']).columns
    categorical_stats = {}
    for col in categorical_cols:
        categorical_stats[col] = df[col].value_counts()
    
    # Save numeric statistics
    numeric_stats.to_csv(results_dir / "numeric_statistics.csv")
    
    # Save categorical statistics
    with open(results_dir / "categorical_statistics.txt", "w") as f:
        for col, stats in categorical_stats.items():
            f.write(f"\n{col}:\n")
            f.write(stats.to_string())
            f.write("\n" + "-"*50 + "\n")
    
    # Calculate correlation matrix
    correlation_matrix = df[numeric_cols].corr()
    correlation_matrix.to_csv(results_dir / "correlation_matrix.csv")
    
    # Print summary to console
    print("\nNumeric Statistics Summary:")
    print(numeric_stats)
    
    print("\nCategorical Variables Summary:")
    for col, stats in categorical_stats.items():
        print(f"\n{col}:")
        print(stats)
    
    print("\nCorrelation Matrix Summary:")
    print(correlation_matrix) 