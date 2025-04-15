## Feedback

### False Discovery Rate (FDR) (Update not yet complete)
FDR controls the expected proportion of false positives among significant results when conducting multiple tests. When analyzing many variables simultaneously, the chance of finding "significant" results purely by chance increases substantially - this is known as the multiple comparisons problem. Unlike traditional Bonferroni correction which controls the probability of making even one false discovery, FDR is more powerful as it allows a small proportion of false positives while maintaining statistical rigor. 

The analysis includes (WIP: read "will include") two FDR approaches:

1. **Global FDR**: Applied across all tests (t-tests, ANOVAs, covariates) to provide the most conservative control against false positives.

2. **Research Question FDR**: Applied specifically to ANOVAs and their covariates, as these tests directly address the primary research questions about predictors of outcomes while controlling for demographics.

Both approaches use the Benjamini-Hochberg method, with the research question approach providing better statistical power while still controlling false discovery within the core analyses.

### Bivariate Relationships Tab
The Bivariate Relationships tab shows how variables relate to each other through:
1. Pair plots of outcome variables (scatterplots showing correlations)
2. Correlation heatmap (strength/direction of relationships between outcomes)
3. Categorical associations heatmap (Cramér's V between categorical variables)

These visualizations help identify patterns before formal testing and provide context for statistical findings.

### Gender Coding Correction (Complete, not published on website until FDR complete)
I've updated the variable definitions to correctly reflect that Males correspond to "2" and Females to "1" on the gender variable. This change has been implemented in the code and will be reflected in all future analyses and reports.

### Outliers in Graphs
Yes, the "o's" are outliers (points beyond 1.5×IQR from quartiles). We included these in all analyses as they may represent valid data points. We can exclude them if preferred, but this would require careful consideration of the impact on results.

### P-Value Differences with SPSS
Would you share your p-values? That might help me understand the differences. It'd be a good check on the methods to know where to double-check. P-value differences between our analysis and SPSS likely stem from:

1. **FDR Correction**: Our values are adjusted for multiple comparisons; SPSS shows raw p-values
2. **Implementation Differences**: Statistical algorithms vary between software packages
3. **Equal Variance Assumption**: Our t-tests assume equal variances by default

Note: While our code uses 'omit' for handling potential missing values, our analysis of the dataset shows no missing values in any of the analysis variables, so this is unlikely to contribute to p-value differences with SPSS.
