# Data Exercise: Short-Horizon Signal for Index Futures

**Time allowed:** 3.5 hours. Work in Python. No AI tools, but with internet.
**Afterwards:** a 45–60 minute discussion with a researcher about your work. Your model's accuracy matters much less than how you got there. Be ready to justify every decision.

The data is synthetic. All instruments are fictional.

---

## Setting

You join a systematic trading desk that trades three equity index futures on the same exchange: **KST**, **HRN** and **PLV**. They are contracts on related stock indices and trade in the same session (09:30–16:00 exchange time; occasionally the exchange closes early).

The desk wants a **signal that, at the end of each minute, predicts how the mid price will move over the next few minutes**. It will be used from July 2024 to decide when to buy or sell.

**Costs:** every trade crosses the spread. You buy at the ask and sell at the bid, so each trade pays half the spread relative to the mid. On top of that, there is an exchange fee of **0.25 bps of notional per trade**.

**Decision time:** the end of each minute. At decision time *t* you may use any data that would have been available at *t*.

## Data

Three files, extracted on **2024-07-01**, covering 2024-01-02 to 2024-06-28. All timestamps are exchange local time. Tick sizes: KST 0.25, HRN 0.10, PLV 0.05.

**`bars.csv`**: one row per instrument per minute, aggregated from trades

| column | description |
|---|---|
| ts | end of the one-minute interval: the row covers (ts − 1 min, ts] |
| instrument | KST, HRN or PLV |
| mid_close | mid price at ts |
| spread_close | ask − bid at ts, in price units |
| last_price | price of the last trade in the interval |
| buy_volume | contracts bought by aggressive buyers during the interval |
| sell_volume | contracts sold by aggressive sellers during the interval |
| n_trades | number of trades during the interval |

**`book.csv`**: top two levels of the order book, one snapshot per instrument per minute

| column | description |
|---|---|
| minute | the minute during which the snapshot was taken; snapshots are taken at the last instant of that minute |
| instrument | KST, HRN or PLV |
| bid_px1, ask_px1 | best bid and best ask prices |
| bid_sz1, ask_sz1 | resting size at the best bid / best ask |
| bid_sz2, ask_sz2 | resting size at the second-best bid / ask |

**`vendor_signal.csv`**: a short-horizon signal sold by an external vendor, on trial with the desk

| column | description |
|---|---|
| published_at | when the vendor published the value; usable from that time onwards |
| instrument | KST, HRN or PLV |
| signal | standardised signal; positive means an expected up move |

The vendor has delivered the signal live since 2024-04-01. Values before that date were delivered as a history file when the trial started.

---

## Part A: Analysis questions (suggested time: about 1 hour)

Answer each in your notebook with code, plots and short written explanations.

**A1.** Describe the one-minute mid-price returns of each instrument. How does volatility vary within the day and across days? Would you normalise returns before modelling, and how?

**A2.** Construct an order-flow imbalance measure from `bars.csv` and a book imbalance measure from `book.csv`. (Definitions: *order-flow imbalance* is net aggressive buying in an interval, e.g. (buy_volume − sell_volume) / (buy_volume + sell_volume). *Book imbalance* is the tilt of resting size towards one side, e.g. (bid size − ask size) / (bid size + ask size), using level 1 or levels 1–2.) How does each relate to the mid-price return over the same minute, and over the following 1, 5, 15 and 30 minutes? Explain what you find.

**A3 (optional).** How do the three instruments move together? If you look at this, you may do it as part of choosing features in Part B instead of as a separate answer.

## Part B: Signal (suggested time: about 2.5 hours)

Build the signal the desk asked for, for **one instrument and one horizon** (between 1 and 30 minutes), both of your choice. You choose the target definition, features, model, validation scheme and evaluation metrics. Compare against at least one simple baseline. No hyperparameter tuning is expected.

Then:
1. Assess whether the vendor signal adds value for your instrument.
2. Using a single threshold rule (trade only when the signal is strong enough), show whether your signal would make money after costs.

## Deliverable

A notebook that runs top to bottom, ending with a short summary:
1. What you built and how well it works out of sample.
2. The data issues you found and what you did about each.
3. How you validated, and why you trust the result.
4. What drives the predictions.
5. Would you trade it, and under what conditions? Limitations, and what you would do with more time.
