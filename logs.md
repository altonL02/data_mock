# Misses log: Squarepoint mock (A1–A3, Part B)

## Night-before summary: the 7 rules

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

# Mock 2: used-boat suggested price (boat_BRIEF.md / boat_main.ipynb)

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
