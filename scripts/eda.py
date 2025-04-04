#!/usr/bin/env python3

import pandas as pd
import numpy as np
from pathlib import Path

def perform_eda(df):
    """
    Perform exploratory data analysis on the dataset
    """
    # Create results directory
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)
    
    # Basic information
    print("\n=== Basic Information ===\n")
    print("Dataset Shape:", df.shape)
    print("\nColumns:")
    for col in df.columns:
        print("-", col)
    
    # Data types
    print("\n=== Data Types ===")
    print(df.dtypes)
    
    # Missing values
    print("\n=== Missing Values ===")
    print(df.isnull().sum())
    
    # Unique values per column
    print("\n=== Unique Values per Column ===")
    unique_counts = pd.Series({
        col: df[col].nunique() 
        for col in df.columns
    })
    print(unique_counts)
    
    # Value distributions
    print("\n=== Value Distributions ===\n")
    for col in df.columns:
        print(f"\n{col}:")
        if pd.api.types.is_categorical_dtype(df[col]):
            # For categorical columns, show value counts with labels
            print(df[col].value_counts())
        elif pd.api.types.is_numeric_dtype(df[col]):
            # For numeric columns, show top 5 most frequent values
            print(df[col].value_counts().head())
    
    # Numeric columns summary
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        print("\n=== Numeric Columns Summary ===")
        print(df[numeric_cols].describe())
    
    # Categorical columns summary
    cat_cols = df.select_dtypes(include=['category']).columns
    if len(cat_cols) > 0:
        print("\n=== Categorical Columns Summary ===")
        for col in cat_cols:
            print(f"\n{col}:")
            print(df[col].value_counts())
    
    # Save summary to file
    with open(results_dir / "eda_summary.txt", "w") as f:
        f.write("=== Basic Information ===\n")
        f.write(f"\nDataset Shape: {df.shape}\n")
        f.write("\nColumns:\n")
        for col in df.columns:
            f.write(f"- {col}\n")
        
        f.write("\n=== Data Types ===\n")
        f.write(str(df.dtypes))
        
        f.write("\n\n=== Missing Values ===\n")
        f.write(str(df.isnull().sum()))
        
        f.write("\n\n=== Unique Values per Column ===\n")
        f.write(str(unique_counts))
        
        f.write("\n\n=== Value Distributions ===\n")
        for col in df.columns:
            f.write(f"\n{col}:\n")
            if pd.api.types.is_categorical_dtype(df[col]):
                f.write(str(df[col].value_counts()))
            elif pd.api.types.is_numeric_dtype(df[col]):
                f.write(str(df[col].value_counts().head()))
        
        if len(numeric_cols) > 0:
            f.write("\n\n=== Numeric Columns Summary ===\n")
            f.write(str(df[numeric_cols].describe()))
        
        if len(cat_cols) > 0:
            f.write("\n\n=== Categorical Columns Summary ===\n")
            for col in cat_cols:
                f.write(f"\n{col}:\n")
                f.write(str(df[col].value_counts()))

if __name__ == "__main__":
    from data_loader import load_data
    df = load_data()
    perform_eda(df) 