import pandas as pd
import numpy as np
import altair as alt
from scipy.stats import contingency

def create_visualizations(df, var_defs=None):
    """
    Create Altair-based visualizations of the data.
    Returns a dictionary of Altair chart objects.
    """
    if not var_defs:
        return {}

    # Get variables by type from metadata
    outcome_cols = [col for col, info in var_defs['variables'].items() if info['type'] == 'outcome']
    demographic_cols = [col for col, info in var_defs['variables'].items() if info['type'] == 'demographic']
    independent_cols = [col for col, info in var_defs['variables'].items() if info['type'] == 'independent']
    categorical_vars = demographic_cols + independent_cols

    charts = {}

    # Distribution plots for outcomes
    charts['distributions'] = {
        col: alt.Chart(df).mark_bar().encode(
            alt.X(col, bin=alt.Bin(maxbins=20), title=col),
            y='count()',
            tooltip=[col, 'count()']
        ).properties(title=f'Distribution of {col}', width=300, height=200).interactive()
        for col in outcome_cols
    }

    # Add bar plots for categorical variables
    for col in categorical_vars:
        try:
            chart = alt.Chart(df).mark_bar().encode(
                x=alt.X(f"{col}:N", title=col),
                y='count()',
                tooltip=[col, 'count()']
            ).properties(title=f'Distribution of {col}', width=300, height=200).interactive()
            charts['distributions'][col] = chart
        except Exception:
            continue

    # Boxplots
    df_melted = df.melt(
        id_vars=categorical_vars,
        value_vars=outcome_cols,
        var_name='Score Type',
        value_name='Score'
    )
    charts['boxplots'] = {
        cat: alt.Chart(df_melted).mark_boxplot().encode(
            x=alt.X('Score Type:N', title='Score Type'),
            y=alt.Y('Score:Q'),
            color=alt.Color(cat + ':N'),
            tooltip=['Score Type', 'Score', cat]
        ).properties(title=f'Scores by {cat}', width=300, height=300).interactive()
        for cat in categorical_vars
    }

    # Correlation heatmap
    corr = df[outcome_cols].corr()
    corr_reset = corr.reset_index().melt('index')
    corr_reset.columns = ['Variable1', 'Variable2', 'Correlation']
    charts['heatmap'] = alt.Chart(corr_reset).mark_rect().encode(
        x='Variable1:O',
        y='Variable2:O',
        color=alt.Color('Correlation:Q', scale=alt.Scale(scheme='redblue', domainMid=0)),
        tooltip=['Variable1', 'Variable2', 'Correlation']
    ).properties(title='Correlation Heatmap: Outcome Variables', width=300, height=300)

    # Cramér's V heatmap
    n_cats = len(categorical_vars)
    cramer_matrix = np.zeros((n_cats, n_cats))
    for i, var1 in enumerate(categorical_vars):
        for j, var2 in enumerate(categorical_vars):
            if i > j:
                try:
                    table = pd.crosstab(df[var1], df[var2])
                    v = contingency.association(table, method='cramer')
                    cramer_matrix[i, j] = v
                    cramer_matrix[j, i] = v
                except:
                    cramer_matrix[i, j] = 0
                    cramer_matrix[j, i] = 0
    cramer_df = pd.DataFrame(cramer_matrix, index=categorical_vars, columns=categorical_vars).reset_index().melt('index')
    cramer_df.columns = ['Variable1', 'Variable2', 'CramersV']
    charts['cramer'] = alt.Chart(cramer_df).mark_rect().encode(
        x='Variable1:O',
        y='Variable2:O',
        color=alt.Color('CramersV:Q', scale=alt.Scale(scheme='yelloworangered', domain=[0,1])),
        tooltip=['Variable1', 'Variable2', 'CramersV']
    ).properties(title="Categorical Associations (Cramér's V)", width=300, height=300)

    # Pair plot
    charts['pair_plot'] = alt.Chart(df).mark_point(filled=True, size=30).encode(
        x=alt.X(alt.repeat('column'), type='quantitative', scale=alt.Scale(zero=False)),
        y=alt.Y(alt.repeat('row'), type='quantitative', scale=alt.Scale(zero=False)),
        tooltip=[
            alt.Tooltip(alt.repeat('column'), type='quantitative'),
            alt.Tooltip(alt.repeat('row'), type='quantitative')
        ]
    ).repeat(
        row=outcome_cols,
        column=outcome_cols
    ).properties(title="Outcome Pair Plot")

    # Score boxplot
    df_scores = df[outcome_cols].melt(var_name='Score Type', value_name='Score')
    charts['score_boxplot'] = alt.Chart(df_scores).mark_boxplot().encode(
        x=alt.X('Score Type:N', title='Score Type'),
        y=alt.Y('Score:Q', title='Score'),
        color='Score Type:N'
    ).properties(
        title='Score Distributions',
        width=300,
        height=300
    )

    return charts