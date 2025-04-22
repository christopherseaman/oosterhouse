## Feedback

### False Discovery Rate (FDR) Correction

FDR controls the expected proportion of false positives among significant results when conducting multiple tests. When analyzing many variables simultaneously, the chance of finding "significant" results purely by chance increases substantially - this is known as the multiple comparisons problem. Unlike traditional Bonferroni correction which controls the probability of making even one false discovery, FDR is generally more powerful as it allows a small proportion of false positives while maintaining statistical rigor.

Our analysis now implements a **family-wise FDR correction** using the Benjamini-Hochberg method. This means we apply the correction separately to logical groups ("families") of tests:

1. **T-test Family:** All independent samples t-tests comparing groups (e.g., Gender, Eating Disorder History) on outcome variables are corrected together.
2. **ANCOVA Family:** All ANCOVA results (both the main effects of independent variables and the effects of demographic covariates) are corrected together.

This approach is less conservative than applying a single global correction across all tests, potentially increasing the power to detect true effects within each family of analyses while still appropriately controlling the overall false discovery rate. The analysis report will show both the raw p-values and these family-wise adjusted p-values.

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

P-value differences between our analysis and the original SPSS results likely stem from several factors:

1. **FDR Correction**: Our primary reported p-values are adjusted for multiple comparisons using family-wise FDR (Benjamini-Hochberg), while the SPSS results appear to be uncorrected (raw) p-values. The raw p-values from our analysis are also available for comparison.
2. **T-test Type (Variance Assumption)**\*: Our Python analysis now uses **Welch's t-test** (via `pingouin.ttest(correction=True)`), which does *not* assume equal variances between groups. This is generally considered a more robust approach when variances might differ. If the original SPSS analysis used the standard Student's t-test (which *does* assume equal variances), this could lead to minor differences in the raw p-values, especially if group variances are unequal. However, Welch's test often yields similar results when variances are equal. The close match between our raw p-values and the SPSS p-values suggests SPSS likely also used Welch's test or a similar method robust to unequal variances.
3. **Implementation Differences**: Minor variations in the underlying numerical algorithms between statistical packages (Python libraries vs. SPSS) can sometimes lead to small differences in p-values, even when the same conceptual test is performed.

\* *Welch's t-test adjusts the degrees of freedom when calculating the p-value to account for potential differences in variance between the groups, making it more reliable than Student's t-test when the assumption of equal variances is violated.*

*Note: While our code uses 'omit' for handling potential missing values during calculations, our review of the dataset shows no missing values in any of the variables used in the t-tests or ANCOVAs, so this is unlikely to contribute to p-value differences with SPSS.*

### Final Status and Recommendations (April 19, 2025)

Following a detailed review and update process:

1. **Methodology Update:** The Python analysis pipeline (`scripts/statistical_analysis.py`) has been updated to use robust and standard methods:
    * **T-tests:** Welch's t-test (assuming unequal variances) is consistently used via `pingouin.ttest(correction=True)`, which also provides the appropriate Cohen's d effect size.
    * **ANCOVA:** Continues to use `pingouin.ancova`.
    * **Multiple Comparisons:** Benjamini-Hochberg False Discovery Rate (FDR) correction is applied family-wise (t-tests corrected together, ANCOVAs corrected together). This is a standard approach that is less conservative than a global correction.
2. **SPSS Comparison:**
    * Raw p-values from the Python Welch's t-tests generally align well with the provided SPSS p-values.
    * Investigation using Student's t-test in Python strongly suggests that the larger discrepancies observed previously were due to the original SPSS analysis likely using Student's t-test (equal variances assumed). The Python code now consistently uses the more appropriate Welch's test.
    * The table below provides a detailed comparison of raw p-values from Python (using both Welch's and Student's t-tests) against the original SPSS values:

        | Independent Variable                      | Outcome Variable   | Python Raw P-Value (Welch's) | Python Raw P-Value (Student's) | SPSS Raw P-Value | Notes                                                                 |
        | :---------------------------------------- | :----------------- | :--------------------------- | :----------------------------- | :--------------- | :-------------------------------------------------------------------- |
        | **Gender**                                | SS1 avg            | 0.048                        | 0.045                          | 0.045            | Welch's close; Student's matches SPSS exactly.                        |
        |                                           | SS2 avg            | 0.223                        | 0.193                          | 0.223            | Welch's matches SPSS exactly.                                         |
        |                                           | SS3 avg            | 0.161                        | 0.148                          | 0.148            | Welch's close; Student's matches SPSS exactly.                        |
        |                                           | SS4 avg            | 0.535                        | 0.509                          | 0.536            | Welch's very close to SPSS.                                           |
        |                                           | Total Score Avg    | 0.058                        | 0.045                          | 0.059            | Welch's very close to SPSS; Student's p < 0.05.                       |
        | **History of eating disorder**            | SS1 avg            | 0.007                        | 0.011                          | 0.011            | Welch's close; Student's matches SPSS exactly. Both p < 0.05.         |
        |                                           | SS2 avg            | 0.871                        | 0.858                          | 0.862            | Both very close to SPSS.                                              |
        |                                           | SS3 avg            | 0.030                        | 0.011                          | 0.011            | Welch's p < 0.05; Student's matches SPSS exactly (p < 0.05).          |
        |                                           | SS4 avg            | 0.036                        | **0.160**                      | **0.159**        | Welch's p < 0.05; **Student's matches SPSS very closely (p > 0.05).** |
        |                                           | Total Score Avg    | 0.044                        | **0.102**                      | **0.102**        | Welch's p < 0.05; **Student's matches SPSS exactly (p > 0.05).**      |
        | **Prior recommendation to change weight** | SS1 avg            | 0.128                        | 0.126                          | 0.126            | Welch's close; Student's matches SPSS exactly.                        |
        |                                           | SS2 avg            | 0.422                        | 0.418                          | 0.416            | Both very close to SPSS.                                              |
        |                                           | SS3 avg            | 0.154                        | 0.152                          | 0.153            | Both very close to SPSS.                                              |
        |                                           | SS4 avg            | 0.150                        | 0.149                          | 0.150            | Both match SPSS almost exactly.                                       |
        |                                           | Total Score Avg    | 0.065                        | 0.064                          | 0.065            | Both match SPSS almost exactly.                                       |
        | **Weight-sensitive sport**                | SS1 avg            | 0.807                        | 0.802                          | 0.803            | Both very close to SPSS.                                              |
        |                                           | SS2 avg            | 0.576                        | 0.558                          | 0.556            | Both very close to SPSS.                                              |
        |                                           | SS3 avg            | 0.480                        | 0.478                          | 0.479            | Both match SPSS almost exactly.                                       |
        |                                           | SS4 avg            | 0.078                        | 0.090                          | 0.091            | Both close to SPSS.                                                   |
        |                                           | Total Score Avg    | 0.592                        | 0.578                          | 0.581            | Both close to SPSS.                                                   |
        | **Endurance sport**                       | SS1 avg            | 0.735                        | 0.729                          | 0.731            | Both very close to SPSS.                                              |
        |                                           | SS2 avg            | 0.501                        | **0.477**                      | **0.737**        | **Notable difference persists** for both Welch's and Student's.       |
        |                                           | SS3 avg            | 0.668                        | 0.676                          | 0.678            | Both very close to SPSS.                                              |
        |                                           | SS4 avg            | 0.057                        | 0.065                          | 0.066            | Both very close to SPSS.                                              |
        |                                           | Total Score Avg    | 0.446                        | 0.436                          | 0.438            | Both very close to SPSS.                                              |

    * One notable raw p-value discrepancy remains for "Endurance sport / SS2 avg", potentially due to data handling or transcription issues in the original comparison data.
3. **Dependencies & Execution:** The project dependencies (`requirements.txt`) have been updated (`mkdocs-charts-plugin` added), and the full pipeline (`scripts/orchestrator.py`) runs successfully, generating results and building the documentation site.

**Recommendation:**

* Proceed with the analysis using the current state of the code.
* When reporting results, clearly state the methods (Welch's t-test, ANCOVA, family-wise FDR), report both raw and adjusted p-values, and focus interpretation on effect sizes alongside the adjusted p-values.
* Use the information in `PYTHON_SPSS_PVALUE_COMPARISON.md` to explain differences compared to the original SPSS analysis if needed.
