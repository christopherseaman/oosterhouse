#!/usr/bin/env python3

import pandas as pd
import numpy as np
import statsmodels.api as sm
from pathlib import Path

def perform_regression_analysis(df):
    """
    Perform regression analysis to predict Total Score
    """
    results_dir = Path(__file__).parent.parent / "results"
    
    # Prepare the data
    # Drop columns with too many missing values
    df = df.drop(columns=['What is your gender? - Other - Text', 
                         'What school do you attend? - Other - Text',
                         'What is your year in school? - Other - Text'])
    
    # Convert categorical variables to dummy variables
    categorical_cols = df.select_dtypes(include=['category']).columns
    df_dummies = pd.get_dummies(df[categorical_cols], drop_first=True)
    
    # Select numeric predictors (excluding the target and derived variables)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    exclude_cols = ['Total Score', 'Total Score Avg', 'SS1 avg', 'SS2 avg', 'SS3 avg', 'SS4 avg']
    numeric_predictors = [col for col in numeric_cols if col not in exclude_cols]
    
    # Combine predictors and ensure numeric types
    X = pd.concat([df[numeric_predictors], df_dummies], axis=1)
    X = X.astype(float)  # Convert all predictors to float
    y = df['Total Score'].astype(float)  # Ensure target is float
    
    # Handle remaining missing values
    X = X.fillna(X.mean())  # Fill numeric missing values with mean
    y = y.fillna(y.mean())  # Fill target missing values with mean
    
    # Add constant term
    X = sm.add_constant(X)
    
    # Fit the model
    model = sm.OLS(y, X)
    results = model.fit()
    
    # Save results
    with open(results_dir / "regression_results.txt", "w") as f:
        f.write(results.summary().as_text())
    
    # Print results
    print("\nRegression Results:")
    print(results.summary())
    
    # Calculate and save standardized coefficients
    standardized_coef = pd.DataFrame({
        'Variable': X.columns,
        'Coefficient': results.params,
        'Std Error': results.bse,
        't-value': results.tvalues,
        'p-value': results.pvalues
    })
    standardized_coef.to_csv(results_dir / "standardized_coefficients.csv", index=False)
    
    # Print significant predictors
    print("\nSignificant Predictors (p < 0.05):")
    significant_predictors = standardized_coef[standardized_coef['p-value'] < 0.05]
    print(significant_predictors)
    
    # Calculate and save model diagnostics
    diagnostics = pd.DataFrame({
        'R-squared': [results.rsquared],
        'Adj. R-squared': [results.rsquared_adj],
        'F-statistic': [results.fvalue],
        'Prob (F-statistic)': [results.f_pvalue],
        'AIC': [results.aic],
        'BIC': [results.bic]
    })
    diagnostics.to_csv(results_dir / "model_diagnostics.csv", index=False)
    
    print("\nModel Diagnostics:")
    print(diagnostics) 