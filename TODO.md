# TODO Checklist for Current Task

---

## Ground Rules

- **Do not check off any item until all its acceptance criteria are fully met.**
- **After each change, regenerate the report and rebuild the site.**
- **Inspect the generated HTML pages to validate the change.**
- **Update this checklist as work progresses.**
- **We will clear this file before starting the next task.**

---

## [ ] 1. Data Summary has two headers per var in Demographics and Independent
- Acceptance criteria:
  - Each variable has **only one header**.
  - The header is followed by the frequency table.
  - The univariate plot is **below** the table, not above or with its own header.

---

## [ ] 2. Score Distributions graph should be in the Score summaries section and should not have a separate header
- Acceptance criteria:
  - The score boxplot appears **inside** the Score Summaries section.
  - It does **not** have its own separate header.

---

## [ ] 3. Move all Data Summary graphs to be below their respective tables
- Acceptance criteria:
  - For each variable, the frequency table appears **first**.
  - The univariate plot appears **immediately below** the table.

---

## [ ] 4. t-tests should be separated by prediction variable, each with their own header. Move the scores vs XXX graphs below each respective table on this page
- Acceptance criteria:
  - The t-tests section is organized by predictor variable.
  - Each predictor has a header.
  - The t-test table for that predictor appears below the header.
  - The "Scores by XXX" plot appears **below** the table.

---

## [ ] 5. ANOVA still lists "Group stats unavailable" for everything. Feels like we're missing output
- Acceptance criteria:
  - ANOVA results include parsed group stats as nested tables.
  - No "Group stats unavailable" messages appear.

---

<!--- #FIXME later: DO NOT REMOVE
[ ] Remove "- Selected Choice" from variable names
[ ] Mermaid diagram render
[ ] Pairplot histograms on the diagonal
[ ] Interactive plots, e.g., color by demographic/independent
--->