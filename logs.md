# Misses log: Squarepoint mock (A1–A3, Part B)

**Contents** (Ctrl+F works too)
- [Exam playbook: start here](#exam-playbook-start-here): timeline, Part A template, Part B decisions, summary template
- [Code snippets (tested)](#code-snippets-tested-copy-and-adapt): [S1 profile](#s1-profile-a-file-first-30-minutes) · [S2 merge](#s2-merge-with-checks) · [S3 lags / forward values by time](#s3-value-at-another-time-looked-up-by-time-lags-forward-values-safe-across-gaps) · [S4 as-of join](#s4-latest-value-published-at-or-before-t-as-of-join-same-day-only) · [S5 splits](#s5-splits) · [S6 walk-forward](#s6-walk-forward) · [S7 models](#s7-models) · [S8 results and breakdowns](#s8-results-table-and-breakdowns-baseline-column-always-alongside) · [S9 drivers](#s9-drivers-group-ablation-coefficients-across-folds-permutation-importance-partial-dependence) · [S10 signal checks](#s10-signal-checks-low-signal--trading-data) · [S11 index / composition](#s11-index--composition-cross-sectional-has-the-level-changed) · [S12 ACF with gaps](#s12-acf-with-gaps-keep-the-time-grid-never-dropna) · [S13 final fit and submission](#s13-final-fit-and-submission-when-there-is-a-hidden-test-set-to-predict)
- [If the exam format differs from my mocks](#7-if-the-format-differs-from-my-mocks)
- [The 10 rules](#night-before-summary-the-10-rules)
- [Trap catalogue](#trap-catalogue-for-an-unseen-dataset) · [First 30 minutes](#first-30-minutes-of-the-exam)
- [Building good features](#building-good-features-general)
- Lessons by mock: [power A1](#a1-price-distribution-and-transformation) · [power Part B](#part-b-forecasting) · [boats](#mock-2-used-boat-suggested-price) · [order flow](#mock-3-short-horizon-signal-for-index-futures-debrief) · [low-signal modelling sequence](#the-modelling-sequence-for-a-low-signal-problem-exam-version)

# Exam playbook: start here

The sequence for exam day. The detailed lessons are in the sections below; this part only says *what to do when*. **Code for each step is in the snippets section (S0–S12); paste it, then still check the printed counts.**

## Timeline (6 hours)

| Step | Time | Output |
|---|---|---|
| 0. Read the brief, write the information-set table and the mechanism sentence | 15 min | markdown cell |
| 1. Data routine on every file | 30–40 min | a running **data issues table** |
| 2. Part A, about 20 min per question | 60 min | answer + evidence + decision per question |
| 3. Part B | 3 h 15 | results table, breakdowns, drivers, choice |
| 4. Summary, then Restart & Run All | 30 min | the 5 points |
| Buffer | 15 min | |

## 0. Before any code (15 min)
- **Decision moment:** when is the prediction made, and what is one row (one prediction)?
- **Information-set table:** for every column, write down when it's known relative to the decision moment and what its lag is. The timing table below is the power version. Re-read the brief's "information available" list *twice*: I missed the vendor load forecast three times.
- **Mechanism sentence:** how is the target generated? → candidate features (see "Building good features").
- **Target and unit:** what exactly is predicted, in what units, and what metric matters for the use case?

## 1. Data routine (30–40 min)
Run "First 30 minutes of the exam" (trap catalogue section) and ask the five questions (rule 9) of every column. Code: **S1** (profile), **S2** (merges with checks), **S3/S4** (time-based lookups).

Keep a **data issues table** as you go: *issue · evidence (a number) · decision · expected effect on results*. Summary point 2 is then just copying this table.

## 2. Part A: answer template for each question
1. **First sentence = the direct answer.**
2. **Evidence:** one plot plus the numbers that support it, broken down (by year, hour, group), not only pooled.
3. **What it doesn't fix / caveat**, and what I checked to rule out a data problem (rule 1).
4. **Implication for Part B:** the decision this answer leads to (transform, feature, window).
5. **Checkpoint (2 min):** every sentence matches an output above it.

## 3. Part B: decisions to make and write down
| Decision | Default rule | Detail in |
|---|---|---|
| Target and transform | match it to the metric; trailing (not full-sample) scaling; know what the back-transform gives (median vs mean) | A1 (power), A1 (boat) |
| Validation | time-ordered walk-forward; **training cutoff = when the label is known**; gap ≥ horizon if labels overlap; refit cadence = how it would be deployed; choose on validation, **test once** | Part B (power), Part B (boat), Mock 3 |
| Baseline | naive persistence, group median, zero, or simple OLS, scored on **identical rows** | Part B (power), Part B (boat) |
| Metric | **training loss matches the metric** (MAE ↔ median/absolute error); MAE + RMSE together; % error for money; correlation + net P&L for trading signals | Evaluation (power), A1 (boat), Mock 3 |
| Models | one linear + one tree, everything that gets fitted inside the pipeline, the model passed in as a function | Walk-forward skeleton |
| Missing values | drop only rows that can't be scored; the model must serve every row (flag + fallback) | Mock 2 rule 7 |
| Evaluation | breakdown by hour / month / condition **with the baseline column**; `describe()` of predictions (plausible?) | Evaluation (power) |
| Drivers | group ablation (value) + coefficients across folds or partial dependence (direction) | Drivers (power), Feature selection (boat) |
| Anomalies | one `describe()`, one comparison, a written mechanism, a decision, then move on | Evaluation (power) |

For signal or trading data, switch to "The modelling sequence for a low-signal problem" (Mock 3).

Code: **S5** splits → **S6** walk-forward → **S7** models → **S8** results and breakdowns → **S9** drivers. Trading signals: **S10**. "Has the level changed?" questions: **S11**. Autocorrelation: **S12**.

## 4. Summary template (the 5 points)
1. **What I built and how well it works:** model vs baseline on the test set, with numbers (MAE/RMSE or correlation/net P&L), plus *where* it wins and loses.
2. **Data issues:** the data issues table (issue · evidence · decision · effect).
3. **Validation and why I trust it:** the split design and the cutoff rule, leak checks done (lags written next to features, one row checked by hand, "too good = alarm"), test touched once.
4. **What drives the predictions:** ablation numbers + direction (coefficients / partial dependence), tied back to the mechanism sentence.
5. **Limitations and more time:** each item comes from a weakness I found (a segment where the baseline wins, an extrapolation risk, an untested assumption).

## 5. Discussion habits (from the mock interview)
- Answer as **decision → reason tied to this data → evidence, or how I'd check → caveat.** My first answers were generic ("it's a trade-off") until pushed.
- **Answer every part** of a multi-part question. "I didn't check; here's the 5-minute check" beats skipping it.
- **Quantify, or say how I'd measure it.** "It depends on the coefficient" sounds like dodging; "rerun without the leaked block and compare June MAE" doesn't.
- If unsure what's asked, **restate the question first** (I answered "yes" while arguing "no").
- Be ready to link accuracy to money: a reference price, P&L = sign(forecast − ref) × (actual − ref), split by segment, plus tail risk.

## 6. Coding habits (from the drills)
- **Run the counts every time:** row count after every merge (`validate='1:1'` / `'m:1'`), number of folds and prediction rows after the walk-forward. Two silent bugs (`date_range` without `freq='MS'` → 700 overlapping folds; duplicate rows → a many-to-many merge) only showed up in the counts.
- **Clean placeholders (−9999 etc.) before building lags,** or they spread into the features.
- **Write functions that return new frames;** don't modify and rename in place (re-running the cell breaks).
- **Keep "features" and "columns to keep" as separate lists.** Adding lists together duplicated `hour` and broke `predict`.
- **Look up forward values by time** (shift the timestamp, merge on key + time), not by shifting rows. `ret.shift(-5)` is one minute, not five.
- **Store `fold` and the baseline column in the walk-forward output,** so breakdowns need no re-joining.

## 7. If the format differs from my mocks
My mocks guessed the format ("Part A questions + open Part B + 5-point summary"). Read the brief for *what is graded*, then adapt. The core order stays the same: decision moment → data routine → analysis → model → written conclusions.

| If the brief… | Then |
|---|---|
| **has no Part A** (just "predict X" or "here is data") | Write a short Part A yourself anyway (about 45 min): target distribution and transform, 2–3 key relationships, time structure, data issues table. The researcher will ask about all of it. |
| **gives a hidden test set to predict and submit** | Keep my own walk-forward for model choice and the written evaluation. Then refit the chosen model on *all* labelled data and predict **every** test row (S13). Check the row count, the ids, no missing values, and that the predictions look like the training target. Read the required file format twice. |
| **is exploratory** ("what can you find?", no target) | Choose 2–3 questions a decision-maker would care about. Answer each with the Part A template; rank findings by size and robustness. Same data routine first. |
| **asks for a report or slides, not a notebook** | The summary template becomes the document: findings first, each with one figure and one number; method and data issues after. Keep the notebook runnable as the appendix. |
| **is shorter (3–4 h) or a multi-day take-home** | Short: cut tuning and extra models first, never the data routine, the validation design or the written conclusions. Take-home: same order, but expect more depth on robustness and a cleaner write-up. |
| **gives a metric or baseline** | Use theirs as the headline. Add mine only if it answers a different question (e.g. % error next to dollar MAE). |
| **says what the model is for** (trading, pricing, ops) | Evaluate in that currency: P&L after costs for trading, % error for pricing, worst-case misses for operations. |

---

## Night-before summary: the 10 rules

1. **A surprising result is a data or code problem until proven otherwise.** It happened three times: the corrupted GW column (no daily cycle), NaNs making the ACF all-NaN (looked like "weak autocorrelation"), and the DST explanation that didn't match the dates. Ask: *does this contradict physics or common sense? Is there a NaN, an outlier, or a wrong column?*
2. **Re-read the information set before designing anything.** I missed the D+1 vendor load forecast three times while building a weaker version myself. List what is known at 10:00 on day D before writing features.
3. **Check every claim against the data before writing it down.** "This is DST" (it wasn't); "negative prices are real because the daily average is also negative" (only true for 60%).
4. **Justify with a mechanism, not a coincidence.** Negative prices are real because renewables are about 4x normal in those hours. Then **test the mechanism**: "lag 168 helps on Mondays" sounded right but didn't hold in this data (see A3).
5. **Turn every "I'm not sure" into "I checked X, and found Y".** Bound the doubt with a test (e.g. are the remaining exact zeros consistent with chance?).
6. **Every method needs a "what it does NOT fix" and a "how I'd judge whether it worked".** Transformation: QQ-plot, skew and kurtosis, λ stability, then out-of-sample error in EUR. Decomposition: the residual ACF.
7. **Write the conclusion.** Plots without a written takeaway don't count.
8. **Rules only help if I apply them at fixed checkpoints.** In the boat mock I broke rules 3 and 7 even though they were already written here (see the boat section). At the end of every Part A question: a 2-minute pass checking each markdown sentence against an output above it. Restart & Run All after Part A *and* at the end.
9. **Ask five questions of every column and row** (they catch traps I haven't seen yet):
   1. What is it, and in what units?
   2. When is it known, relative to the prediction?
   3. Relative to what (a date, a currency, the extraction snapshot)?
   4. What other column can check it?
   5. For each row: does the outcome actually exist?
10. **A good feature is a mechanism written as a column.** Before writing feature code, write one sentence on how the target is generated, then turn each part of it into a feature (see "Building good features" at the end).

### Timing table (index by delivery day t = D+1, forecast made at 10:00 on t−1)

| information | latest usable | lag |
|---|---|---|
| actual load / wind / solar (known to 09:00 on D) | complete day t−2 | **2 days** |
| day-ahead prices (D set on D−1) | hour 23 of D | 1 day; hourly: lag ≥ h+1 for hour h |
| same weekday | t−7 | 7 days |
| vendor forecasts for D+1 (issued 09:00 on D) | t itself | 0 |

Exam-feasible leak checks (a full rebuild-and-corrupt test is too slow to write in 6 hours):
1. **Write each feature's lag next to it** (comment or markdown table), checked against the table above.
2. **Spot-check one row by hand:** print each feature next to the raw value it should come from. This catches shift bugs (my `shift(6*24)` inside `groupby('hour')` was 144 *days*).
3. **Treat a result that's too good as an alarm:** if the model beats the naive baseline by a suspicious margin, look for leakage first.

Being careful alone isn't enough: careful reasoning missed 3 timing bugs in my first frame (144-day shift, target normalised with D+1 prices, forecast errors shifted only 1 day).

---

## A1: price distribution and transformation

### Data checks I missed
- **Use redundant columns as checksums.** `daily_avg_price` matched the recomputed mean on every complete day (max |diff| 0.005). That proved the spikes were real and let me **reconstruct** each -9999 hour exactly: `n × avg − sum(others)`, error ≤ 0.12. Reconstructing ≠ imputing with the daily average.
- **Check rows per day and the share of abnormal rows** before looking at values.
- **Don't drop rows from an hourly series.** It breaks `shift(24)` = "same hour yesterday". Set NaN and keep the grid.
- **Round maximum (3000) = likely price cap.** The value is real but **censored**; say so.
- **Negative prices:** justify with renewables (a mechanism), not with the daily average.

### Describing the distribution
- Break it down **by year, by hour, by weekday**, not just one pooled histogram. The pooled skew is partly a **regime level shift** (the 2022 median is about 2x the others).
- Give numbers: QQ-plot, skewness, kurtosis (excess kurtosis about 98, so heavy tails on **both** sides).

### Transformation
- **Yeo-Johnson isn't shift/scale invariant.** It switches branch at 0, so z-scoring first changes what it does. My per-year λs jumped partly because of that.
- **Why YJ fails here:** λ = 0.06 on positive prices, but 0.90 once the 4% of negative hours are included. Exponent 2−λ on negative values means compressing the right tail stretches the left. *A single power can't fix heavy tails on both sides.*
- **Better:** asinh((price − trailing 28-day median) / trailing 28-day MAD). Kurtosis falls from 98 to 1; quarterly std ratio from 4.7 to 1.4. Most of the gain comes from removing the moving level. Trailing window = usable in real time.
- **Fit λ / scaling inside each walk-forward fold** (it's fine on the full sample for description only; say so).
- **Back-transformation bias:** inverting a transformed-space prediction gives roughly the **median**, not the mean. The gap is about 71 EUR on spike days vs 3 on normal days. Fine for MAE, biased low for RMSE or mean-based P&L. Report errors in EUR.
- **Trade-off to state:** compressing spikes down-weights the hours where P&L can be largest.

---

## A2: load decomposition

- **Corrupted column:** `load_actual_gw` had 260 rows that were 10x off, which wiped out the ACF (lag-1 ACF of 0.02 for hourly load is physically impossible). Use `load_actual_mw`. I should have run the MW-vs-GW ratio check *before* analysing.
- **Find the seasonal patterns from data, don't assume them.** Daily (24h), weekly (7d) and annual. Check the profile *shape* by weekday and by month, not just the level.
- **Explaining the daily ACF (lags 1, 6, 7, 8):** a weekday/weekend pattern means ρ(k) = ρ(7−k) = ρ(7+k). The share of same-type day pairs is 7/7 at lag 7, 5/7 at lags 1, 6 and 8, and 3/7 at lags 2–5. Lag 1 ≈ lag 6 means little persistence beyond the weekly pattern; a flat floor at lags 2–5 means similar weekday levels.
- **Trend window = a multiple of 7**, otherwise the weekly cycle leaks into the trend. A trailing average **lags** at turning points.
- **Seasonality must be per (weekday, hour), 168 slots.** My version was one number per day, so the intraday shape stayed in the residual.
- **Keep description and features separate.** Centered windows / MSTL are fine for describing; only model inputs need to be trailing.
- **The main load input is the vendor forecast for D+1**, which already contains trend, seasonality, weather and holidays. The decomposition is for description, a baseline, normalisation and a fallback. Good interview move: compare the history-based estimate's error against the vendor forecast's error.
- **Leakage trap:** `load_forecast_mw == load_actual_mw` for **1–21 June 2022 (504 h)**.
  - *How to verify a forecast is genuine:* exact zero errors should be rare (count them and see *when* they occur), rolling error should be stable over time, and error by hour should make sense (relative error flat at about 2% means it just scales with load).
  - *Effect:* the backtest is **optimistic**, and the model overweights the load forecast. State the **direction** and size, and run a sensitivity check without the block.
  - *Handling:* set to NaN, add a `forecast_missing` flag, fall back to a point-in-time history estimate.
  - *Trust:* forecasts can't be cross-checked against another source, so testing the error's statistical properties is the only defence. The vendor doesn't keep **point-in-time / as-of (vintage)** data; in production, save your own snapshot at 09:00.
- **Timing bug:** `trend.shift(24)` leaked day D. Daily aggregates of actuals need a **2-day** lag. Do lags on the daily series or with `groupby().shift`, not by row count after `dropna()`.

---

## A3: price autocorrelation

- **The NaN trap:** 18 NaNs make `plot_acf` return all NaN (only the lag-0 bar shows). Use `missing='conservative'`, interpolate, or reconstruct. Never `dropna()` (it misaligns the lags).
- **"Lag 1 is usable" is wrong for most hours.** For delivery hour h of D+1, usable lags are ≥ h+1. Only **lags ≥ 24** work for every hour. Hour 18: the most recent price is hour 23 of D (lag 19), and the same-hour price is lag 24.
- **The raw ACF is understated by spikes** (lag 1: 0.46 raw vs 0.83 transformed). Prefer the transformed ACF because the raw one is distorted, not just "because the target is transformed". It measures dependence beyond the trailing level. **Both agree on which lags matter (24, 168), so the feature decision is the same either way.**
- **Why lag 168 (hypothesis):** for a Monday, lag 24 is a Sunday, a different type of day. **Checked:** in this data, a week-old price beats yesterday's only on **Saturdays** (MAE 50.5 vs 59.7). On Mondays and Sundays yesterday's price still wins, because persistence of the price level dominates the weekday effect. So the literature's "weekly naive" rule (lag 7 days for Mon/Sat/Sun) is worse overall here (MAE 57.8 vs 56.3 for "same hour on D"). Lag 168 can still help *as a feature* next to lag 24, even though it loses as a standalone forecast.
- **Lesson:** a mechanism that sounds right (even one from Claude, or from the literature) is a hypothesis until you've checked it on *this* data.
- **Per-hour view:** treat each hour as its own daily series (ACF in days), and check how strongly hour 23 of D correlates with each hour of D+1.
- Neither ACF answers "does a spike predict a spike?" If that matters, check the conditional spike frequency separately.

---

## Part B: forecasting

### Order of work (a plan to reuse, about 4 hours)
1. **Frame:** one row per (issue day D, hour h); target = price of (D+1, h). Write the lag next to every feature, checked against the timing table. *(45 min)*
2. **Baseline first** ("same hour on D"), scored on the same rows the models will use. *(10 min)*
3. **Generic walk-forward** (skeleton below), plus one linear model and one tree. *(45 min)*
4. **Results table:** MAE, RMSE and ratio to baseline, for validation and test. *(15 min)*
5. **Break the errors down** by hour, by month and by condition, with the baseline column alongside. *(30 min)*
6. **Drivers:** coefficient stability and group ablation. *(30 min)*
7. **Anomalies:** one comparison, a mechanism, a decision. *(20 min)*
8. **Choose the model on validation, then run the test once.** Tune only if there's time left.
9. **Write the 5-point summary, then Restart & Run All.** *(30 min)*

### Walk-forward skeleton (write it from memory)
```python
def monthly_splits(df, start, end, train_months):
    for m in pd.date_range(start, end, freq='MS'):
        test  = (df['date'] >= m) & (df['date'] < m + pd.DateOffset(months=1))
        train = (df['date'] >= m - pd.DateOffset(months=train_months)) & (df['date'] < m)
        yield m, train, test

def walk_forward(df, features, make_model, target, **split_kw):
    out = []
    for m, tr, te in monthly_splits(df, **split_kw):
        model = make_model().fit(df.loc[tr, features], df.loc[tr, target])
        pred = df.loc[te, ['date', 'hour', 'price_tgt']].copy()
        pred['pred_eur'] = to_eur(model.predict(df.loc[te, features]), df.loc[te])
        out.append(pred)
    return pd.concat(out)

make_lasso = lambda: make_pipeline(SimpleImputer(strategy='median'), StandardScaler(), Lasso(alpha=0.01))
make_tree  = lambda: HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05)   # handles NaN itself
```
- **The model is an argument:** a function that returns a *fresh, unfitted* estimator. Any model plugs in.
- **Everything that gets fitted goes inside the pipeline** (imputer, scaler, transform parameters), so it's refitted on each fold's training data only.
- **Splitting on issue day is fine:** every target before month m is known at 10:00 on the first day of m.
- **Choose the start date to leave a full training window after feature warm-up** (the 28-day level). `start='2021-01-01'` gave an empty first fold.

### Evaluation
- **Break every result into parts and look at each one, with the baseline next to it.** One overall MAE hides where the model wins and loses. Standard cuts: by hour, by month (regime), and by condition (negative-price hours, spike hours, known data-problem periods). Here the overall numbers (tree 43 vs baseline 62) hid three things:
  - the tree is *worse* than the baseline on negative hours (95 vs 81)
  - lasso is worse than the baseline at night (hours 0–4: about 53 vs 38)
  - no model beats the baseline on spike hours (about 720 for all three), so the whole gain comes from normal hours (36 vs 55)

  Pattern: `pd.DataFrame({'tree': e_tree, 'lasso': e_lasso, 'base': e_base, 'key': key}).groupby('key').mean()`, where `key` is hour, month, or a True/False condition.
- **Score everything on identical rows** (use `df.loc[res.index, ...]` for the baseline). Report MAE and RMSE together: a large gap between them means a few huge errors drive the result.
- **Look at the predictions themselves, not just the errors.** `describe()` on `pred_eur` showed a minimum of −3,329 EUR, which is impossible. Ask whether every prediction is physically plausible.
- **A linear model plus an exponential back-transform risks blow-ups.**
  - Lasso extrapolates linearly when a feature is far outside its training range: residual load was −23.6k on those rows vs +34k on average.
  - `sinh` turns a moderate miss in model space into thousands of EUR.
  - A tree's predictions are averages of training targets, so it stays flat beyond the data.
  - Two windy months (2022-01, 2022-09) explained about 2/3 of the gap between tree and lasso.
- **Investigate an anomaly at exam depth:** one `describe()`, one comparison against the full sample, a written mechanism, a decision. Then move on.

### Choosing and validating
- **Choose on validation and look at the test once.** Write down the choice and its reason before running the test. On test the ensemble looked best (31.8); picking it then would have meant using 2023 to choose the model.
- **When the test disagrees with your choice, have the "why not X?" answer ready.** Lasso beat the tree on test (33.3 vs 34.0), but on average they tie, 2023 had no out-of-range days, and I chose the tree for its worst case.
- **Tune last, and only a little.** When the data keeps changing regime, the training window (3/6/12 months) is the setting worth discussing: a short window adapts to new regimes, a long one includes more rare events. Treat a gain under about 1 EUR as noise and call the model "insensitive to this choice" rather than "better".

### Drivers
- **There are two kinds of evidence, and they answer different questions.**
  - **Lasso coefficients across all folds** (median, share non-zero, share positive) show *direction and stability*. A single fold misleads: `roll_forecast_error` was −0.10 in one fold but positive in only half of them.
  - **Group ablation** (re-run the walk-forward without one group) shows *value in EUR*: without fundamentals 55.8, without prices 49.9, without calendar 43.1, full model 43.0.
- **With collinear features, read groups, not single coefficients.** `resid_load = load − wind − solar` exactly, so a wind coefficient near zero doesn't mean wind is unimportant. Ablation must remove the whole group, including raw *and* transformed versions of the same feature. I left the raw prices in at first.
- **How features are represented depends on the model.**
  - Linear: hour and weekday as dummies, and price features on the target's scale. The model only sees the columns you list.
  - Tree: raw columns are fine, and it handles NaN itself.

### Code hygiene (silent bugs)
- **Every written conclusion should cite a number from an output above it.** Three of my markdown cells were contradicted by the numbers: ensemble RMSE "higher than both", "for lasso the hour doesn't matter", and negative hours judged without a baseline.

### Data check to add to the start-of-exam routine
- **Count how often each column hits its maximum and minimum.** A round value repeated many times is a cap or censoring. Examples here: the 3,000 price cap, and `wind_actual_mw` sitting at exactly 55,000 MW for 661 hours (median price −64, while the forecast goes up to 85 GW).
  `for c in num_cols: print(c, (df[c] == df[c].max()).sum(), (df[c] == df[c].min()).sum())`

### For the discussion
- **Connect accuracy to trading.** MAE rewards forecasting the median, but P&L is concentrated in spike hours, where no model beat the baseline. Say what you'd change if the goal were P&L (mention only: e.g. a separate model for the probability of a spike).
- **Each "with more time" item should come from a weakness you found:**
  - separate models per hour, because lasso uses one slope for every hour
  - a longer window or more weight for negative hours
  - a wind feature capped at 55 GW
  - a holiday calendar


---
---

# Mock 2: used-boat suggested price

A cross-sectional pricing problem with time drift, the opposite shape to the power mock. The lessons below are written as general rules. Boat facts appear only as examples.

## Transferable rules from this mock

1. **A field derived "as of extraction" must be recomputed relative to each row's event date.** `age_years = 2025 − year_built` was age on the extraction date, not at sale. I *proved* that identity (cell 28) but didn't draw the implication. With year fixed effects, using it turns the price index into market change **plus depreciation** (2024: −3% vs +16% with age at sale). Whenever a column is a function of other columns, ask: *relative to when?*
2. **No outcome is not the same as a missing outcome.** Withdrawn and active listings never sold, so there is no label to recover. Filling their sale price with the asking price creates a label from a different quantity. Compare the 132 sold rows with sale price 0 or 1: a real sale with an unrecorded price, where filling is defensible (but list price runs about +10%, so scale it or drop the rows).
   - "Dropping a third of the data" isn't the worry. 26k labels is plenty. **The worry is selection:** the withdrawal rate ranged from 17% to 37% by year, and withdrawn boats were listed about 9% *below* sold ones with the same specs.
   - **Truncation at the sample edges:** listings from late 2024 that have already sold are the fast sellers (median 24 days vs 68), and fast sellers sell about 11% above the model's prediction. Grouping by sale date moves the same effect to the start (2019 Q1 sales: median 22 days).
   - The dropped rows are still useful: the withdrawal rate per year is itself a market indicator.
3. **The training cutoff is when the label becomes known, not when the row started.** Train on `sale_date < cutoff`, not `listing_date < cutoff`. This applies to anything with a delayed outcome: loans, claims, orders.
4. **Anything decided after the prediction is not a feature.** The seller sets `list_price` *after* seeing the suggested price. Post-listing fields (`final_list_price`, `days_on_market`, `n_price_drops`, `status`) are leakage. This is a variant of rule 2 in the night-before summary.
5. **Decide what the model assumes about the price level in the forecast period, and state it.** With an expanding window, set `year = last training year` for validation and test rows. A tree does this automatically (a future year falls into the latest year's branch). For OLS, use `C(year)` dummies (a linear trend extrapolates the boom badly) and set the year in the prediction frame, otherwise statsmodels errors on an unseen level. The one-sentence assumption: *next year's level = the latest observed level.*
6. **Yearly folds mean yearly refits.** The validation design should match how the model would actually be run.
7. **The model must serve every row.** My A3 formula silently dropped 30% of rows with missing condition or engine hours. At prediction time you can't skip a listing: use a missing category, or median imputation plus a flag, fitted inside the pipeline on the training fold only.
8. **Interaction terms need their main effects.** `age:C(type)` without `C(type)` forces one intercept on every type, so level differences get pushed into the slopes (catamaran −0.7%/yr vs −3.8% correct; the ranking changed). Use `age * C(type)`.

## A1: transforming a money target

- **Why log:** features act multiplicatively (+x%, not +$x), and errors scale with price. Not "to make it normal": OLS doesn't need a normal target.
- **`exp(log prediction)` gives the median, not the mean.** That is consistent with dollar MAE, which is minimised by the median, so no bias correction is needed for MAE. If you want the mean, the log-normal correction is `exp(σ²/2)`, derived from first principles; with σ ≈ 0.2 it's about +2%.
- **Metric:** dollar MAE is dominated by the expensive items (a 10% miss on a $5M yacht = a thousand 10% misses on $50k boats). Report median absolute % error (or MAE of log) **alongside** dollar MAE, because sellers experience % error.
- **Currency:** compare predictions and actuals in the same currency. FX at which date (listing or sale)?

## A2: relationships and coefficients

- **Interpret log-model coefficients as %:** −0.0365 means about −3.6% per year of age, holding length fixed. Never compare coefficients with different units ("age is smaller than length" is meaningless).
- **A flat raw relationship can hide a strong conditional one (confounding).** Raw price was flat across age deciles because older boats on the market are longer (30.8 → 37 ft). Conditional on length, about −3.6% per year. Explain the contradiction rather than writing two sentences that disagree.
- **Check the functional form with residuals by bin.** Depreciation is front-loaded (residual +0.34 at age 0, −0.15 at 20–25, then rising for old boats), so use age bins. In the oldest bin, the **year_built = 1900 placeholder** showed up as a residual of +3.7 log.
- `log(length)` fits better than length (R² 0.884 vs 0.859). Its coefficient is an elasticity (about 2.5–3 ≈ volume scaling). For trees, monotone transforms don't matter.
- "Is it the same across types?" → interactions with main effects, plus one plot. Here it wasn't: sail about −3%/yr vs bowrider about −7%/yr.

## A3: price index vs raw median (composition vs level)

- **Year fixed effects remove composition**, even though they're "an average within each year": they average `log p − β·X`, the price of a fixed boat.
- **The identity to remember:** `mean(log p)_t = δ_t + β·X̄_t`. Raw change = market change + composition change. The gap between the raw series and the index is exactly `β·(X̄_t − X̄_base)`; with year dummies the residuals average zero within each year, so this is an exact decomposition. Build both series from **the same rows**.
- **What I got wrong:** I wrote "the median doesn't differ a lot" under an output going from 11.46 to 11.67, i.e. **+0.22 log ≈ +24%**. I compared log *levels* with coefficients (differences). Put both on one scale (base = 100) and plot them. The story was the *shape*: the median missed the 2021 boom (+4% vs +28%) and showed 2024 as the peak, while the index was 12 points below its peak.
- "Significant" doesn't answer the question; magnitude and shape do.
- **The controls make the index:** characteristics of the item only. Never control for the price itself or for market outcomes (list price, days on market), because they absorb the time effect.
- **Stopping rule for controls:** add them in blocks and print δ_t after each block; stop when it stops moving.
- USD vs local currency: a USD index mixes in FX moves (small here because about 70% of sales are in the US, but give it one sentence).

## Part B: what changed vs mock 1

The skeleton is the same as mock 1. The new parts:
```python
def yearly_splits(df, start, end):
    for y in range(start, end + 1):                      # int years: no Timestamp vs int comparison
        cutoff = pd.Timestamp(f'{y}-01-01')
        train = pd.to_datetime(df['sale_date']) < cutoff  # label known before the cutoff
        test  = df['year'] == y                           # listed in year y
        yield y, train, test
# inside the loop: X_te = df.loc[te, features].copy(); X_te['year'] = y - 1
# validation: start=2021, end=2023; test: start=2024, end=2024, run once
```
- Pandas trap: `pd.DateOffset(year=1)` **sets** the year to 1; `years=1` adds one.
- **Baseline:** the Part A OLS model, turned into an sklearn pipeline (imputer with `add_indicator=True` + `OneHotEncoder(handle_unknown='ignore')` + `LinearRegression`) so it goes through the same loop. Optional floor: median per type × length bucket × age bucket.
- **Small error analysis (15 min):** (1) mean signed log error per fold, which tests the "latest level" assumption (predict which fold is biased, and in which direction, before looking); (2) % error by type and by price band; (3) permutation importance.
- **Caveat on the test set:** 2024 is biased toward fast sellers because active listings are excluded.

## Feature selection and drivers for trees

- **Formal feature selection isn't worth exam time.** GBMs barely suffer from a few weak features at this size. The selection that matters is the **information set**, plus **ID-like features with many levels** (seller_id = memorisation; model name is legitimate but target-encode it inside the fold).
- **Group ablation** = how much a group is worth. Caveats: correlated features substitute for each other (ablate groups, not single features); show the result per fold and call changes smaller than the fold-to-fold spread "no detectable effect"; choosing on validation = model selection, so run the test once.
- **Partial dependence** = which direction a feature pushes (`PartialDependenceDisplay.from_estimator`). It checks the model learned sensible shapes; a wrong shape points to a data problem.
- **"Why not built-in importances?"** Impurity importance is computed on the training set and biased toward continuous and high-cardinality features (HistGB doesn't provide it). Permutation importance on validation is better, but still understates correlated features.

## Data issues in this mock (each is an example of a general trap type)

| Trap type | Boat example |
|---|---|
| Placeholders | list price 99999999, engine hours 99999, sale/list price 0 or 1, year_built 1900 |
| Digit typos | year_built 2051/2081/2091 (= 2015/2018/2019 with digits swapped) |
| Redundant columns as checksums | length_ft vs length_m (1.4% mismatched); currency vs region (missing currency recoverable) |
| Category variants | 28 boat_type labels for about 9 types (CC, MY, SAILBOAT, Sail, Centre Console, ...) |
| Exact duplicates | 150 duplicate listing rows |
| Model year ahead of calendar | built = sale year + 1: real new boats listed Aug–Dec, **keep**; built ≥ year + 2: drop |
| Derived as of extraction | age_years relative to 2025 |
| Censoring | days_on_market capped at 300 |
| No outcome | withdrawn and active listings |
| Not in scope? | condition "new" on a used-boat marketplace (dealer stock) |

---

# Trap catalogue for an unseen dataset

Tags: [P] power mock, [B] boat mock, [new] not met yet.

**1. What is it, and in what units?**
- Placeholders [P][B] → `value_counts().sort_index()` head and tail
- Scale errors in some rows (10x, 100x, 1000x) [P] → ratio against a redundant column; bumps one decade apart on a log histogram
- Caps or censoring (a round maximum that repeats) [P][B] → count rows at the max and min
- Category variants [B] → `value_counts()` on every string column
- Mixed currencies or units [B] → cross-tab against region or source
- [new] **The meaning or unit of a column changes on a date** (system migration) → **plot the monthly median and null rate of every key column**

**2. When is it known?**
- Fields only known after the outcome [B]; fields decided after the prediction [B]; a "forecast" that equals the actual [P]; a delayed label [B]
- [new] Revised data (final values, not the values available at the time); [new] counts accumulated up to the extraction date

**3. Relative to what?**
- Timezone and DST [P]; fields derived as of extraction [B]; level drift or regime [P][B]
- [new] A target that combines different things (incl. or excl. tax or commission; mixed contract types) → look for two humps

**4. What other column can check it?**
- Redundant pairs [P][B]
- [new] Logical constraints: sale date before listing date, `sale − listing ≠ days_on_market`, engine hours falling on a relisting, output above capacity → one assert per constraint, then count the violations

**5. Does the outcome exist / is each row what it claims?**
- Duplicates [P][B]; no outcome vs missing outcome [B]; truncation at the sample edges [B]; outage gaps [P]
- [new] **A merge that multiplies or drops rows** → `merge(..., validate='m:1')` and assert the row count
- [new] Near-duplicates (relisted under a new ID); [new] the same entity in train and test (leaks under random CV, not under a time split); [new] survivorship in a lookup table

**6. Traps in my own code:** preprocessing fitted on the whole dataset; dropping rows at prediction time; interactions without main effects; categories at prediction time that training never saw; a linear model extrapolating, then blowing up through exp or sinh; a stale kernel.

## First 30 minutes of the exam
1. Per file: `shape`, `dtypes`, `duplicated()`, nulls, `describe()`, and the count of rows at the min and max of each column.
2. `value_counts()` on every string column, plus the top and bottom values of every numeric column.
3. Every redundant pair and logical constraint as an assert, with the number of violations.
4. Monthly medians and null rates of the key columns, plotted over time.
5. Merges with `validate=` and a row-count assert.
6. A table of every column: known before or after the prediction · relative to what · decision.


---
---

# Mock 3: short-horizon signal for index futures (debrief)

I stopped partway through Part A. The workflow felt like mock 1. These are the planted traps and the parts that really are different, written as general rules.

## Traps that carry over to any dataset

Already caught in my notebook (not repeated here): the timestamp offset between bars and book, duplicate rows, the missing HRN book day, the PLV halt, and returns computed within each day.

1. **Only backtest on point-in-time data. Vendor history delivered at onboarding is suspect.** Before go-live, the vendor signal's 15-min correlation was 0.12–0.14 for *every* instrument. From go-live it was about 0.01–0.02 (monthly: 0.14, 0.10, 0.15 | 0.02, 0.01, 0.01).
   - Spot it: correlation **by month**, with the go-live date marked.
   - Conclusion: judge it on live data only. It adds nothing for KST/HRN; for PLV it's marginal (about 0.04 at 1–5 min) and is a noisy copy of the KST lead, so it's redundant with my own feature. Don't pay for performance that only exists in the backfill.
   - Mechanics: a 5-min cadence means `merge_asof` (backward), not an exact merge.
2. **Contemporaneous ≠ predictive.** Order-flow imbalance correlates 0.69 with the *same* minute's return (price impact: it *describes* the move) but only 0.01–0.03 with the next minutes. Always show the same-minute and forward relationships side by side.
3. **A signal can be real and still not worth trading.** Book imbalance (correctly aligned) is the strongest short-term predictor: about 0.055 at 1 min, 0.03 at 5 min, 0.01–0.02 at 15 min. But the move it predicts is smaller than the round-trip cost, so it loses money at every threshold. It's more useful for **execution timing** (cross the spread now or wait) than as alpha.
4. **The cross-asset lead is where the money is.** KST leads HRN/PLV by 1–2 min (KST(t−1) vs PLV(t): 0.054; reverse about 0; gone by 3–4 min). That's only tradable for PLV, and only on the strongest signals.

## Misses in my own notebook
- **`shift(-k)` on 1-minute returns is NOT the k-minute forward return.** `ret.shift(-5)` is the single minute from t+4 to t+5. The 5-minute forward return is `mid(t+5) / mid(t) − 1`, i.e. log mid shifted by −5 minus log mid now, or a time-based lookup. My decay analysis was measuring "one minute, k minutes later", not "the next k minutes".
- **A fix applied to a side frame doesn't reach the main frame.** I reindexed PLV over the halt in `plv_ret`, but `df` (used in A2) still had the gap, so row shifts there still span the halt.
- **"Volatility within the day" means the profile by time of day** (std of returns grouped by minute-of-day, across all days), not each day's std. Std per day is the across-day variation. Label which one a cell computes.

## Correct conclusions on costs

| | Round-trip cost (spread + 2 × 0.25 bps) |
|---|---|
| KST | about 1.08 bps |
| HRN | about 1.65 bps |
| PLV | about 1.89 bps |

- Book imbalance alone: net negative at every threshold.
- KST→PLV lead alone (5-min hold): net +0.6 bps per trade at the top 5% of signals, +1.4 at the top 1%, negative at the median.
- Combined linear model (vol-normalised; train Jan–Mar, test Apr–Jun; 5 min): PLV test correlation 0.051, net +0.5 bps (top 20%) to +3.2 bps (top 1%), **mostly earned in the April stress weeks**. HRN and KST: not profitable.
- The verdict to give: *trade PLV only, only on strong signals, small size. P&L is concentrated in high-volatility periods, so monitor it, and expect limited capacity.*

Light value trap not caught: 30 crossed book snapshots (ask ≤ bid). Add `assert (ask > bid)` (or count the violations) to the routine.

## How the modelling really differs from mock 1

| | Mock 1 (power, day-ahead) | Mock 3 (order flow, minutes) |
|---|---|---|
| Signal strength | high (beat baseline by about 30%) | out-of-sample R² about 0.3%; correlation 0.03–0.05 |
| Horizon | fixed by the setting | **chosen**: decay of the signal vs cost |
| Labels | one per delivery hour, no overlap | H-min forward returns **overlap** → gap at fold boundaries; t-stats from daily correlations |
| Main metric | MAE vs baseline | daily correlation (mean, t-stat, % positive days), decile plot, **net P&L per trade by threshold** |
| What "works" means | beats the naive forecast | **beats costs** after thresholding |
| Main risk | blow-ups from extrapolation | overfitting noise; P&L concentrated in one regime |
| Where the effort goes | model and features | **signal research before modelling** + alignment + costs; the model just combines 3–5 signals |

### The modelling sequence for a low-signal problem (exam version)
1. **Signal research, per feature (before any model):** correlation with the forward return at H = 1, 5, 15, 30 (decay curve); same-minute correlation alongside it; correlation per day → mean, t-stat, % of days positive; correlation by month (stability); mean forward return by feature decile (monotone? symmetric?).
2. **Choose the horizon** where the predicted move is largest relative to the round-trip cost, not where the correlation is highest (that's usually 1 min, where the move is smallest).
3. **Model:** linear on vol-normalised, clipped features. Trees only shallow, with early stopping, and expect small gains. A large jump = suspect leakage.
4. **Evaluation:** walk-forward with a gap of ≥ H; daily correlation; decile plot of realised vs predicted; a **gross / cost / net per trade + number of trades** table by threshold; the same table by regime and time of day.
5. **Verdict:** where net > 0, how concentrated it is, turnover and capacity, and what would change the conclusion (e.g. posting limit orders instead of crossing the spread changes the cost side completely).

### Normalising returns (the question I got wrong at first)
- Cross-sectional alpha work already normalises implicitly (z-scores or ranks within each date, rank correlation, returns relative to a risk model).
- For a single instrument over time nothing does it for you. Raw least squares weights each period by its variance, so the open and the stress weeks dominate.
- It's a **choice**: raw returns ≈ weighted like dollar P&L; returns ÷ trailing vol = every period equal, stable coefficients, consistency-style correlation. Multiply the prediction back by the trailing vol for position sizing. Name the trade-off and pick one.


---
---

# Building good features (general)

**A good feature is a mechanism written as a column.** `resid_load` works because the price is set by the most expensive plant still needed once wind and solar (near-zero running cost) are used up. Load − wind − solar *is* the demand those plants have to cover. Given load, wind and solar separately, a linear model only finds the subtraction if the coefficients happen to line up, and a tree approximates it with many staircase splits. Hand the model the mechanism: fewer parameters, more stable, explainable.

## Step 1: one sentence on how the target is generated (10 min, before any feature code)

| Data | Mechanism | Features it suggests |
|---|---|---|
| Power | price = cost of the most expensive plant still needed, given demand not covered by renewables | `resid_load`, recent price level, residual load vs its usual level |
| Boats | price = value when new × depreciation with age × condition | age at listing, log length (≈ volume), age × type, condition |
| Order flow | price moves when resting orders lean to one side; news reaches liquid markets first | book imbalance, the leader's lagged return, leader move − follower move |

## Step 2: combine inputs the way the mechanism does
- **Differences:** load − renewables; actual − expected (a surprise); leader − follower (not yet priced).
- **Ratios and shares:** spread / mid = bps; volume ÷ its usual level at that time of day; imbalance (a − b) / (a + b), bounded and unit-free.
- **Interactions:** age × type, when the mechanism says the effect differs by group.

## Step 3: keep features comparable over time
The model is used on the future, so a feature whose distribution drifts forces extrapolation (lasso blow-ups: wind forecast 85 GW vs a training max of 44 GW).
- Scale-free versions (ratios, bps, imbalances) instead of raw levels.
- Relative to a trailing level (z-score vs the last 28 days; volume vs its average for that time of day).
- Clip extremes, with bounds from the training data only.

## Step 4: reference point and timing
- Measure relative to the event (age at listing, not at extraction).
- Every feature has a written lag, checked against what's known at decision time. A same-period value like order-flow imbalance describes the move, it doesn't predict it.
- Aggregation windows match the target's horizon (1, 5, 15 min for a 5-min target), past data only.

## Step 5: shape it for the model
- **Linear:** log multiplicative effects, bins for curved relationships, explicit interactions.
- **Trees:** monotone transforms change nothing, but differences and ratios still help (a tree splits on one variable at a time).
- **Both:** missing-value flags; calendar and session structure (time of day, weekday, start or end of session); a regime indicator (volatility level).

## Checking a candidate feature in about 5 minutes
1. **Shape:** mean target by decile of the feature. Monotone, and in the direction the mechanism predicts? If not, suspect the data.
2. **Adds anything?** Correlate it with the residual of a model that already has the other features, or run an ablation in the walk-forward.
3. **Stability:** its correlation by month or year.
4. **Information set:** its lag, and where it comes from at prediction time.
5. **Range:** does the test period go beyond the training range?

## Don't
- Hundreds of automatic lags or interactions (noise I can't explain in the interview).
- Z-scores using full-sample statistics (leakage).
- Near-duplicate features without grouping them (unreadable coefficients; ablate them as a group).

**In the interview, for every feature:** why it exists (the mechanism) → what I expected → whether the data confirmed it → what I dropped and why. *"I built residual load because prices follow the most expensive plant still needed; removing it raised the error from X to Y."*


---
---

# Code snippets (tested, copy and adapt)

Every block below was run end to end on the mock data (power: `clean/*.csv`, order flow: `mock3_data/*.csv`). Usage lines show the power example; change the column names to fit the new data. **After pasting, still check the printed counts.**

### S0. Imports
```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
from statsmodels.tsa.stattools import acf
from sklearn.pipeline import make_pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Lasso, Ridge, LinearRegression
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.inspection import permutation_importance, PartialDependenceDisplay
```

### S1. Profile a file (first 30 minutes)
```python
def profile(df, name=''):
    print(f'== {name}: shape={df.shape}, exact duplicate rows={df.duplicated().sum()}')
    nulls = df.isna().sum()
    print(nulls[nulls > 0].to_string() if nulls.any() else 'no nulls')
    for c in df.select_dtypes('number'):
        s = df[c]
        print(f'{c:>20}: min={s.min():.6g} (n={int((s == s.min()).sum())})  '
              f'max={s.max():.6g} (n={int((s == s.max()).sum())})  top={s.value_counts().head(3).to_dict()}')
    for c in df.select_dtypes(exclude='number'):
        print(f'{c:>20}: {df[c].nunique()} unique, top={df[c].value_counts().head(5).to_dict()}')

prices = pd.read_csv('clean/prices.csv', parse_dates=['timestamp'])
load = pd.read_csv('clean/load.csv', parse_dates=['timestamp'])
ren = pd.read_csv('clean/renewables_weather.csv', parse_dates=['timestamp'])
profile(prices, 'prices')
print(prices.groupby(prices['timestamp'].dt.date).size().value_counts())   # rows per day: expect one value
```

### S2. Merge with checks
```python
def merge_checked(left, right, on, how='left', validate='1:1'):
    out = left.merge(right, on=on, how=how, validate=validate)
    if how == 'left':
        assert len(out) == len(left), f'row count changed: {len(left)} -> {len(out)}'
    new = [c for c in right.columns if c not in on]
    print(f'rows={len(out)}, rows with no match on the right={out[new].isna().all(axis=1).sum()}')
    return out

prices.loc[prices['price_eur_mwh'] == -9999, 'price_eur_mwh'] = np.nan     # placeholders -> NaN BEFORE any lags
df = merge_checked(prices[['timestamp', 'price_eur_mwh', 'daily_avg_price']],
                   load[['timestamp', 'load_forecast_mw']], on=['timestamp'])
df = merge_checked(df, ren[['timestamp', 'wind_forecast_mw', 'solar_forecast_mw']], on=['timestamp'])
```

### S3. Value at another time, looked up by time (lags, forward values; safe across gaps)
```python
def value_at_offset(df, col, offset, time_col='timestamp', by=(), name=None):
    """New column = value of `col` at time t + offset, for the same `by` keys (NaN if that time doesn't exist).
    offset = -pd.Timedelta(days=1) -> lag of one day;  +pd.Timedelta(minutes=5) -> value 5 minutes ahead."""
    by = list(by)
    src = df[by + [time_col, col]].copy()
    src[time_col] = src[time_col] - offset            # the row stamped t now carries the value from t + offset
    name = name or f'{col}_at_{offset}'
    return df.merge(src.rename(columns={col: name}), on=by + [time_col], how='left', validate='1:1')

df = value_at_offset(df, 'price_eur_mwh', -pd.Timedelta(days=1), name='p_lag1')
df = value_at_offset(df, 'price_eur_mwh', -pd.Timedelta(days=7), name='p_lag7')
df['date'], df['hour'] = df['timestamp'].dt.normalize(), df['timestamp'].dt.hour
daily = df.groupby('date')['daily_avg_price'].first()
df['lvl28'] = df['date'].map(daily.shift(1).rolling(28).median())        # days T-28 .. T-1 only
df['resid_fc'] = df['load_forecast_mw'] - df['wind_forecast_mw'] - df['solar_forecast_mw']
df = df.rename(columns={'price_eur_mwh': 'price'})
print(df.loc[(df['date'] == '2022-03-15') & (df['hour'] == 18), ['price', 'p_lag1', 'p_lag7', 'lvl28', 'resid_fc']])
```

### S4. Latest value published at or before t (as-of join), same day only
```python
def asof_join(left, right, left_time, right_time, by, same_day=True):
    l, r, by = left.sort_values(left_time), right.sort_values(right_time), list(by)
    if same_day:
        l = l.assign(_day=l[left_time].dt.normalize())
        r = r.assign(_day=r[right_time].dt.normalize())
        by = by + ['_day']
    out = pd.merge_asof(l, r, left_on=left_time, right_on=right_time, by=by, direction='backward')
    return out.drop(columns='_day', errors='ignore')
```

### S5. Splits
```python
def monthly_splits(dates, start, end, train_months=None, gap=pd.Timedelta(0)):
    """dates: Series of dates aligned to the frame. train_months=None -> expanding window.
    gap: leave out training rows within `gap` of the test start (use the label horizon when labels overlap)."""
    for m in pd.date_range(start, end, freq='MS'):                      # freq='MS' is essential
        test = (dates >= m) & (dates < m + pd.DateOffset(months=1))
        lo = dates.min() if train_months is None else m - pd.DateOffset(months=train_months)
        train = (dates >= lo) & (dates < m - gap)
        yield m, train, test

def yearly_splits(df, start, end, label_time, event_year):
    """Train on rows whose LABEL was known before Jan 1 of year y; test on rows whose event is in year y."""
    for y in range(start, end + 1):
        yield y, df[label_time] < pd.Timestamp(f'{y}-01-01'), df[event_year] == y
```

### S6. Walk-forward
```python
def walk_forward(df, features, make_model, target, make_splits, keep=(), drop_missing_features=True, return_models=False):
    """make_model(): returns a fresh, unfitted model.  make_splits(rows): yields (fold, train_mask, test_mask).
    keep: extra columns carried to the output (baseline, hour, ...). Drops only rows that can't be used."""
    rows = df.dropna(subset=features + [target]) if drop_missing_features else df.dropna(subset=[target])
    keep_cols = list(dict.fromkeys([target, *keep]))                   # no duplicate columns
    out, models = [], {}
    for fold, tr, te in make_splits(rows):
        if tr.sum() == 0 or te.sum() == 0:
            continue
        model = make_model().fit(rows.loc[tr, features], rows.loc[tr, target])
        pred = rows.loc[te, keep_cols].copy()
        pred['pred'] = model.predict(rows.loc[te, features])
        pred['fold'] = fold
        out.append(pred)
        models[fold] = model
    res = pd.concat(out)
    assert res.index.is_unique, 'test folds overlap'
    print(f"folds={res['fold'].nunique()}, prediction rows={len(res)}")
    return (res, models) if return_models else res

splits = lambda d: monthly_splits(d['date'], '2022-01-01', '2023-12-01', train_months=3)
```

### S7. Models
```python
def make_linear(num, cat=(), model=None):
    """Numeric: median impute (+ missing flags) and scale. Categorical: one-hot. Everything is refitted per fold."""
    parts = [('num', make_pipeline(SimpleImputer(strategy='median', add_indicator=True), StandardScaler()), list(num))]
    if len(cat):
        parts.append(('cat', OneHotEncoder(handle_unknown='ignore'), list(cat)))
    return make_pipeline(ColumnTransformer(parts), model if model is not None else Ridge(alpha=1.0))

num, cat = ['p_lag1', 'p_lag7', 'lvl28', 'resid_fc'], ['hour']
features = num + cat
make_lasso = lambda: make_linear(num, cat, Lasso(alpha=0.1, max_iter=20000))
make_tree = lambda: HistGradientBoostingRegressor(random_state=0)    # loss='absolute_error' targets the median (MAE)

res_l, models_l = walk_forward(df, features, make_lasso, 'price', splits, keep=['p_lag1', 'hour'], return_models=True)
res_t = walk_forward(df, features, make_tree, 'price', splits)
assert res_l.index.equals(res_t.index)                               # identical rows
res = res_l.rename(columns={'pred': 'lasso'}).assign(tree=res_t['pred'])
```

### S8. Results table and breakdowns (baseline column always alongside)
```python
def scores(res, target, cols, baseline):
    t = pd.DataFrame({c: {'MAE': (res[c] - res[target]).abs().mean(),
                          'RMSE': np.sqrt(((res[c] - res[target]) ** 2).mean()),
                          'bias': (res[c] - res[target]).mean()} for c in cols}).T
    t['MAE_vs_baseline'] = t['MAE'] / t.loc[baseline, 'MAE']
    return t.round(3)

def breakdown(res, target, cols, key):
    """MAE by key: a column name (hour, fold) or a Series aligned to res (e.g. res['price'] < 0)."""
    k = res[key] if isinstance(key, str) else key
    err = pd.DataFrame({c: (res[c] - res[target]).abs() for c in cols})
    return err.groupby(k).mean().assign(n=err.groupby(k).size()).round(2)

cols = ['lasso', 'tree', 'p_lag1']
print(scores(res, 'price', cols, baseline='p_lag1'))
print(breakdown(res, 'price', cols, 'hour'))
print(breakdown(res, 'price', cols, 'fold'))
print(breakdown(res, 'price', cols, (res['price'] < 0).rename('negative_price')))
print(res[['lasso', 'tree']].describe().round(1))                     # are the predictions plausible?
```

### S9. Drivers: group ablation, coefficients across folds, permutation importance, partial dependence
```python
def ablation(df, groups, all_features, make_model_for, target, make_splits):
    """make_model_for(features) -> fresh model. Every run uses the same rows (selected with all_features)."""
    rows = df.dropna(subset=all_features + [target])
    out = {}
    for name, dropped in [('full', [])] + list(groups.items()):
        feats = [f for f in all_features if f not in dropped]
        r = walk_forward(rows, feats, lambda: make_model_for(feats), target, make_splits)
        out['full' if name == 'full' else f'without {name}'] = (r['pred'] - r[target]).abs().mean()
    return pd.Series(out).round(2)

lasso_for = lambda feats: make_linear([f for f in feats if f in num], [f for f in feats if f in cat],
                                      Lasso(alpha=0.1, max_iter=20000))
print(ablation(df, {'prices': ['p_lag1', 'p_lag7', 'lvl28'], 'fundamentals': ['resid_fc'], 'calendar': ['hour']},
               features, lasso_for, 'price', splits))

def coef_table(models):
    c = pd.DataFrame({f: pd.Series(m[-1].coef_, index=m[:-1].get_feature_names_out()) for f, m in models.items()}).T
    return pd.DataFrame({'median': c.median(), 'share_nonzero': (c != 0).mean(), 'share_positive': (c > 0).mean()}).round(3)
print(coef_table(models_l).head(8))

last = max(models_l)
idx = res.index[res['fold'] == last]
pi = permutation_importance(models_l[last], df.loc[idx, features], df.loc[idx, 'price'],
                            scoring='neg_mean_absolute_error', n_repeats=5, random_state=0)
print(pd.Series(pi.importances_mean, index=features).sort_values(ascending=False).round(2))
PartialDependenceDisplay.from_estimator(models_l[last], df.loc[idx, features], ['resid_fc', 'p_lag1'])
```

### S10. Signal checks (low-signal / trading data)
```python
def decile_table(x, y, q=10):
    d = pd.DataFrame({'x': x, 'y': y}).dropna()
    d['bin'] = pd.qcut(d['x'], q, labels=False, duplicates='drop')
    return d.groupby('bin').agg(x_mean=('x', 'mean'), y_mean=('y', 'mean'), n=('y', 'size'))

def daily_corr(df, x, y, date_col='date'):
    """One correlation per day -> mean, t-stat, share of positive days (handles overlapping labels within a day)."""
    c = df.dropna(subset=[x, y]).groupby(date_col)[[x, y]].corr().xs(x, level=1)[y]
    return pd.Series({'mean': c.mean(), 't_stat': c.mean() / c.std() * np.sqrt(c.count()),
                      'share_positive': (c > 0).mean(), 'days': c.count()}).round(3)

def threshold_pnl(signal, fwd_ret, cost, quantiles=(0.5, 0.8, 0.9, 0.95, 0.99)):
    """Trade sign(signal) when |signal| is above its quantile. fwd_ret and round-trip cost in the same units.
    Choose the threshold on training/validation data, not on the test set."""
    d = pd.DataFrame({'s': signal, 'r': fwd_ret, 'c': cost}).dropna()
    out = {}
    for q in quantiles:
        t = d[d['s'].abs() >= d['s'].abs().quantile(q)]
        gross = (np.sign(t['s']) * t['r']).mean()
        out[q] = {'n_trades': len(t), 'gross': gross, 'cost': t['c'].mean(), 'net': gross - t['c'].mean(),
                  'hit_rate': (np.sign(t['s']) == np.sign(t['r'])).mean()}
    return pd.DataFrame(out).T.round(3)

bars = pd.read_csv('mock3_data/bars.csv', parse_dates=['ts']).drop_duplicates()
book = pd.read_csv('mock3_data/book.csv', parse_dates=['minute'])
vendor = pd.read_csv('mock3_data/vendor_signal.csv', parse_dates=['published_at'])
bars['lmid'] = np.log(bars['mid_close'])
bars = value_at_offset(bars, 'lmid', pd.Timedelta(minutes=5), time_col='ts', by=['instrument'], name='lmid_fwd5')
bars['fwd5_bps'] = (bars['lmid_fwd5'] - bars['lmid']) * 1e4
book['ts'] = book['minute'] + pd.Timedelta(minutes=1)              # align conventions, then CHECK with a shared column
x = merge_checked(bars, book.drop(columns='minute'), on=['ts', 'instrument'])
print('mid match rate:', np.isclose((x['bid_px1'] + x['ask_px1']) / 2, x['mid_close']).mean())
x['bi'] = (x['bid_sz1'] - x['ask_sz1']) / (x['bid_sz1'] + x['ask_sz1'])
x['date'] = x['ts'].dt.normalize()
x = asof_join(x, vendor, 'ts', 'published_at', by=['instrument'])
k = x[x['instrument'] == 'KST']
print(decile_table(k['bi'], k['fwd5_bps']))
print(daily_corr(k, 'bi', 'fwd5_bps'))
cost_bps = (k['spread_close'] / k['mid_close']) * 1e4 + 2 * 0.25   # approx: entry spread used for exit too
print(threshold_pnl(k['bi'], k['fwd5_bps'], cost_bps))
```

### S11. Index / composition (cross-sectional "has the level changed?")
```python
def index_vs_raw(data, y, period, controls_formula):
    """Hedonic index (period dummies + controls) vs raw mean, on the SAME rows; gap = composition effect."""
    m = smf.ols(f'{y} ~ C({period}) + {controls_formula}', data).fit(cov_type='HC1')
    used = data.loc[m.model.data.row_labels]
    periods = sorted(used[period].unique())
    delta = pd.Series([0.0] + [m.params[f'C({period})[T.{p}]'] for p in periods[1:]], index=periods)
    raw = used.groupby(period)[y].mean()
    out = pd.DataFrame({'index_log': delta, 'raw_log': raw - raw.iloc[0]})
    out['composition'] = out['raw_log'] - out['index_log']          # exact: residuals average 0 within each period
    return out.round(3)

def plot_index(series, ylabel='first period = 100'):
    fig, ax = plt.subplots(figsize=(8, 4))
    for name, s in series.items():                                  # s in log points relative to the first period
        ax.plot(s.index, 100 * np.exp(s), marker='o', label=name)
    ax.axhline(100, color='grey', lw=0.8)
    ax.set_ylabel(ylabel)
    ax.legend()
    return ax

df['year'] = df['date'].dt.year
t = index_vs_raw(df.dropna(subset=['price', 'resid_fc']).query('price > 0').assign(lp=lambda d: np.log(d['price'])),
                 'lp', 'year', 'resid_fc + C(hour)')
print(t)
plot_index({'raw mean': t['raw_log'], 'index': t['index_log']})
```

### S12. ACF with gaps (keep the time grid, never `dropna()`)
```python
s = df.set_index('timestamp')['price']                              # complete hourly grid, NaN kept
r = pd.Series(acf(s, nlags=200, missing='conservative'))
print(r.loc[[1, 24, 48, 168]].round(3))
```

### S13. Final fit and submission (when there is a hidden test set to predict)
```python
def final_submission(train_df, test_df, features, make_model, target, id_cols, path='submission.csv'):
    """Refit the CHOSEN model on all labelled data, predict EVERY test row, check, save."""
    rows = train_df.dropna(subset=[target])                      # keep rows with missing features: the pipeline handles them
    model = make_model().fit(rows[features], rows[target])
    sub = test_df[id_cols].copy()
    sub['prediction'] = model.predict(test_df[features])
    assert len(sub) == len(test_df), 'lost test rows'
    assert sub['prediction'].notna().all(), 'missing predictions'
    assert not sub.duplicated(id_cols).any(), 'duplicate ids'
    print(pd.DataFrame({'train target': rows[target].describe(), 'test prediction': sub['prediction'].describe()}).round(2))
    sub.to_csv(path, index=False)
    return sub

sub = final_submission(df[df['date'] < '2023-12-01'], df[df['date'] >= '2023-12-01'],
                       features, make_lasso, 'price', id_cols=['timestamp'])
```
