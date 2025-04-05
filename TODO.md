# TODO Checklist for Current Task

---

## Ground Rules

- **Do not check off any item until all its acceptance criteria are fully met.**
- **After each change, regenerate the report and rebuild the site.**
- **Inspect the generated HTML pages to validate the change.**
- **Update this checklist as work progresses.**
- **We will clear this file before starting the next task.**

---

## [x] 1. Split Demographics and Independents into separate tables **within** their headings

- Acceptance criteria:
  - Under "Demographics", each variable (e.g., Gender, School, Year) has its own small table with heading.
  - Under "Independent Variables", each variable (e.g., Eating disorder history, Told to change weight, Weight-sensitive sport, Endurance sport) has its own small table with heading.
  - Improves readability over one large table.

---

## [x] 2. Populate EDA, Explore, and Visualizations pages with appropriate plots

- Acceptance criteria:
  - **Data Summary** add univariate plots for each variable just below subheading
  - **EDA** contains multivariate plots like correlation heatmaps and categorical association heatmaps, pair plot, and Scores by XXX (do not remove any existing plots)
  - No pages are blank; all contain relevant, well-organized content.

---

## [x] 3. Fix Statistics page formatting

- Acceptance criteria:
  - T-test results are displayed if available; otherwise, a clear message.
  - ANOVA group stats are formatted as readable nested tables or lists, **not raw dicts**.
  - All tables are easy to read and interpret.

---

## [x] 4. Investigate missing t-test results

- Acceptance criteria:
  - Determine if t-test CSV is empty due to data or code issue.
  - If data issue, document it.
  - If code issue, fix so t-tests are performed and results saved.

---

## [ ] 5. Validate each item above after implementation

- Acceptance criteria:
  - After each change, regenerate the report.
  - Rebuild the site.
  - Check the relevant HTML pages to ensure criteria are met **before** marking the item as done.

---

<!--- #FIXME later:
[ ] Remove "- Selected Choice" from variable names
[ ] Mermaid diagram render
[ ] Pairplot histograms on the diagonal
[ ] Interactive plots, e.g., color by demographic/independent
--->