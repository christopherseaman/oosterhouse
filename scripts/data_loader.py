#!/usr/bin/env python3

import json
import pandas as pd
from pathlib import Path

def load_variable_definitions():
    """Load variable definitions from JSON file"""
    var_def_path = Path(__file__).parent.parent / "data" / "variable_definitions.json"
    with open(var_def_path) as f:
        return json.load(f)

def load_data():
    """
    Load and preprocess the data from data.tsv using variable definitions
    Returns:
    - DataFrame with processed data
    - Dictionary with variable metadata
    """
    # Get paths
    data_path = Path(__file__).parent.parent / "data" / "data.tsv"
    
    # Load variable definitions
    var_defs = load_variable_definitions()
    
    # Load the data
    df = pd.read_csv(data_path, sep='\t')
    
    # Process variables according to their type
    for col, info in var_defs['variables'].items():
        if col not in df.columns:
            continue

        # Pre-map common string labels to integer codes if needed
        if info.get('format') == 'categorical' and isinstance(info.get('values'), dict):
            value_map = {v: int(k) for k, v in info['values'].items()}
            # Only remap if data contains string labels
            if df[col].dtype == object or pd.api.types.is_categorical_dtype(df[col]):
                df[col] = df[col].replace(value_map)

        # Process based on variable type and format
        if info['type'] in ['demographic', 'independent'] and info['format'] == 'categorical':
            # Convert to categorical with codes and labels
            codes = [int(k) for k in info['values'].keys()]
            labels = list(info['values'].values())
            df[col] = pd.Categorical(df[col],
                                     categories=codes,
                                     ordered=True).rename_categories(labels)
            # For analysis, we can use .codes to get numeric values (0-based)
            # and .astype(str) to get labels

        elif info['type'] == 'outcome':
            # Ensure numeric type for outcomes
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df, var_defs

def get_variables_by_type(var_defs, var_type, format_type=None):
    """Helper function to get variables of a specific type and optionally format"""
    return [col for col, info in var_defs['variables'].items() 
            if info['type'] == var_type and 
            (format_type is None or info.get('format') == format_type)]

def get_outcome_variables(var_defs):
    """Get all outcome variables in order (subscales then total)"""
    outcomes = get_variables_by_type(var_defs, 'outcome')
    # Sort so subscales come first, then total score
    return sorted(outcomes, key=lambda x: 'Total' in x)

def generate_demographics_table(df, var_defs, save_path=None):
    """
    Generate a demographics table with counts and percentages for categorical variables.
    Saves to CSV if save_path is provided.
    Returns the demographics DataFrame.
    """
    demo_vars = get_variables_by_type(var_defs, 'demographic', 'categorical')
    indep_vars = get_variables_by_type(var_defs, 'independent', 'categorical')
    categorical_cols = demo_vars + indep_vars

    demographics_data = []
    total = len(df)

    for col in categorical_cols:
        if col not in df.columns:
            continue
        value_counts = df[col].value_counts(dropna=False)
        for value, count in value_counts.items():
            percentage = round((count / total) * 100, 2)
            demographics_data.append({
                'Variable': col,
                'Category': value,
                'Count': count,
                'Percentage': percentage
            })

    demographics_df = pd.DataFrame(demographics_data)
    demographics_df = demographics_df.sort_values(['Variable', 'Category']).reset_index(drop=True)

    if save_path:
        demographics_df.to_csv(save_path, index=False)

    return demographics_df