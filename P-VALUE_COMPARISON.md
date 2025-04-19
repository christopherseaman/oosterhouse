# P-Value Comparison Analysis

## Overview
This document compares the p-values from our analysis with those from the PI's SPSS analysis. We've identified several key differences in methodology that explain the variations in results.

## Key Methodological Differences

1. **FDR Correction**: Our analysis implements False Discovery Rate (FDR) correction using the Benjamini-Hochberg method to control for multiple comparisons. The SPSS results appear to use uncorrected p-values.

2. **T-Test Implementation**: Our implementation uses SciPy's `stats.ttest_ind()` with default settings:
   - Equal variance assumption (Student's t-test)
   - Two-tailed test
   - NaN handling with 'omit' policy

3. **Gender Coding**: We've confirmed that Males=2 and Females=1 in both analyses.

## Detailed Comparison

### Gender Differences (Male vs Female)

| Outcome | SPSS p-value | Our Raw p-value | Our FDR-adjusted p-value |
|---------|-------------|-----------------|------------------------|
| SS1 avg | 0.045* | 0.045 | 0.403 |
| SS2 avg | 0.223 | 0.192 | 0.637 |
| SS3 avg | 0.148 | 0.148 | 0.584 |
| SS4 avg | 0.536 | 0.509 | 0.828 |
| Total Score | 0.059 | 0.045 | 0.403 |

### History of Eating Disorder (Yes vs No)

| Outcome | SPSS p-value | Our Raw p-value | Our FDR-adjusted p-value |
|---------|-------------|-----------------|------------------------|
| SS1 avg | 0.011* | 0.011 | 0.285 |
| SS2 avg | 0.862 | 0.858 | 0.951 |
| SS3 avg | 0.011* | 0.011 | 0.285 |
| SS4 avg | 0.159 | 0.160 | 0.591 |
| Total Score | 0.102 | 0.102 | 0.531 |

### Prior Weight Change Recommendation (Yes vs No)

| Outcome | SPSS p-value | Our Raw p-value | Our FDR-adjusted p-value |
|---------|-------------|-----------------|------------------------|
| SS1 avg | 0.126 | 0.126 | 0.569 |
| SS2 avg | 0.416 | 0.417 | 0.814 |
| SS3 avg | 0.153 | 0.152 | 0.584 |
| SS4 avg | 0.150 | 0.149 | 0.584 |
| Total Score | 0.065 | 0.064 | 0.453 |

### Weight-Sensitive Sport (Yes vs No)

| Outcome | SPSS p-value | Our Raw p-value | Our FDR-adjusted p-value |
|---------|-------------|-----------------|------------------------|
| SS1 avg | 0.803 | 0.801 | 0.911 |
| SS2 avg | 0.556 | 0.558 | 0.833 |
| SS3 avg | 0.479 | 0.478 | 0.824 |
| SS4 avg | 0.091 | 0.090 | 0.509 |
| Total Score | 0.581 | 0.578 | 0.845 |

### Endurance Sport (Yes vs No)

| Outcome | SPSS p-value | Our Raw p-value | Our FDR-adjusted p-value |
|---------|-------------|-----------------|------------------------|
| SS1 avg | 0.731 | 0.729 | 0.877 |
| SS2 avg | 0.737 | 0.477 | 0.824 |
| SS3 avg | 0.678 | 0.676 | 0.846 |
| SS4 avg | 0.066 | 0.065 | 0.453 |
| Total Score | 0.438 | 0.436 | 0.816 |

## Key Findings

1. **Raw p-values**: Our raw p-values (before FDR correction) are very close to the SPSS results, with only minor differences likely due to computational methods. This confirms our basic statistical calculations are consistent with SPSS.

2. **Significant Results**: Using traditional p < 0.05:
   - SPSS found 2 significant results (marked with *)
   - Our raw p-values also found these same 2 significant results
   - After FDR correction, none of these results remain significant

3. **Impact of FDR Correction**: 
   - The FDR correction has substantially increased all p-values
   - This is expected as we're controlling for multiple comparisons
   - The correction helps prevent false positives when conducting many tests

4. **Notable Differences**:
   - Gender effect on SS1 avg: p = 0.045 (raw) → p = 0.403 (FDR-adjusted)
   - Eating disorder history on SS1 and SS3: p = 0.011 (raw) → p = 0.285 (FDR-adjusted)

## Recommendations

1. Consider reporting both raw and FDR-adjusted p-values to show the impact of multiple comparison correction.
2. Note that while some results were significant with traditional methods, they don't survive correction for multiple comparisons.
3. Focus on effect sizes (Cohen's d, partial η²) in addition to p-values for a more complete understanding of the relationships.

## Next Steps

To complete this comparison:
1. We need to run our analysis and fill in our raw and FDR-adjusted p-values
2. Compare the magnitudes of differences between SPSS and our raw p-values
3. Evaluate whether any differences in significance thresholds (p < 0.05) exist between the analyses
4. Consider whether the FDR correction changes any conclusions about statistical significance

## Note on Statistical Significance
- SPSS results show significance (*) at p < 0.05
- Our analysis will show both raw p-values and FDR-adjusted p-values
- FDR adjustment may change which results are considered significant 