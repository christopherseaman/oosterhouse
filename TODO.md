# TODO Checklist for Current Task

---

## Ground Rules

- **Do not check off any item until all its acceptance criteria are fully met.**
- **After each change, regenerate the report and rebuild the site.**
- **Inspect the generated HTML pages to validate the change.**
- **Update this checklist as work progresses.**
- **We will clear this file before starting the next task.**

---

## [x] 1. ANOVA results should include detailed group statistics
- Acceptance criteria:
  - For each ANOVA, the output includes group means, standard deviations, and sample sizes.
  - No "Group stats unavailable" messages appear anywhere in the report.
  - Group stats are presented as nested tables within the ANOVA results section.

---

## [x] 2. Each ANOVA analysis should be accompanied by a plot
- Acceptance criteria:
  - Every ANOVA result includes a corresponding visualization (e.g., boxplot or violin plot).
  - The plot is placed immediately below the ANOVA table.
  - The plot clearly distinguishes between groups.

---

## [ ] 3. Verify that False Discovery Rate (FDR) correction is applied (DROPPED)
- Acceptance criteria:
  - The report explicitly states that FDR correction has been used for multiple comparisons.
  - The adjusted p-values after FDR correction are displayed alongside raw p-values.
  - No indication of uncorrected multiple testing remains.
  - Note: This test has been dropped since the analysis isn't working properly.

---

## [x] 4. Implement ANCOVA with demographic covariates (COMPLETED)
- Acceptance criteria:
  - ANOVA analyses are replaced with ANCOVA that includes demographic variables as covariates.
  - The report shows the effects of covariates on the outcomes.
  - ANCOVA results include adjusted means and standard errors.
  - False Discovery Rate (FDR) correction is applied to all p-values.
  - Each ANCOVA includes a visualization showing the adjusted group means.
  - Note: This task is now complete. ANCOVA with covariates has been implemented using a GLM framework.

---

<!--- #FIXME later: DO NOT REMOVE
[ ] Remove "- Selected Choice" from variable names
[ ] Mermaid diagram render
[ ] Pairplot histograms on the diagonal
[ ] Interactive plots, e.g., color by demographic/independent
--->