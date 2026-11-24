# Data Exercise: Day-Ahead Power Prices

**Time allowed:** 6 hours. Work in Python. No AI tools, but with internet.
**Afterwards:** a 45–60 minute discussion with a researcher about your work. Your model's accuracy matters much less than how you got there. Be ready to justify every decision.

---

## Setting

You work for a fund that trades electricity in a European power market.

- **Day-ahead market:** every day at **12:00** (local time), an auction sets the price for each of the **24 hours of the next day**. Prices are in EUR per MWh.
- **Your job:** every day at **10:00 on day D**, submit a forecast of all 24 hourly prices for **day D+1**.
- **Information available to you at 10:00 on day D:**
  - Day-ahead prices for every hour up to the end of day D (day D's prices were set on day D−1).
  - Actual load, wind, solar and temperature up to 09:00 on day D.
  - Day-ahead forecasts of load, wind and solar for each hour of D+1, issued at 09:00 on day D.

## Data

Three files, as delivered by different data vendors. Data runs from 2021-01-01 to 2023-12-31.

**`prices.csv`**
| column | description |
|---|---|
| timestamp | start of the delivery hour, local market time |
| price_eur_mwh | day-ahead price for that hour |
| daily_avg_price | average day-ahead price of that calendar day |

**`load.csv`**
| column | description |
|---|---|
| timestamp | start of the hour, local market time |
| load_actual_mw | realised electricity demand |
| load_forecast_mw | day-ahead demand forecast for that hour |
| load_actual_gw | realised demand in GW |

**`renewables_weather.csv`**
| column | description |
|---|---|
| time | start of the hour |
| temp_c, temp_f | population-weighted temperature |
| wind_actual_mw, wind_forecast_mw | realised and day-ahead forecast wind generation |
| solar_actual_mw, solar_forecast_mw | realised and day-ahead forecast solar generation |

---

## Part A: Analysis questions (suggested time: about 1.5 hours)

Answer each in your notebook with code, plots and short written explanations.

**A1.** Describe the distribution of hourly prices. Would you transform the price before modelling? Propose at least one transformation, explain what it does and does not fix, and justify your choice.

**A2.** Decompose the load series into trend and seasonal components. Which seasonal patterns are present? Which of these components (or alternatives) would you use as model inputs, and how would you compute them so that they are usable in the forecasting setting above?

**A3.** Examine the autocorrelation structure of hourly prices. Which lags carry information? Which of those lags can you actually use, given when the forecast is made?

## Part B: Forecasting (suggested time: about 4 hours)

Build a model that produces the forecast described in the Setting: at 10:00 on day D, the 24 hourly prices of day D+1.

You choose the target definition, features, model, validation scheme and evaluation metrics. Compare against at least one simple baseline.

## Deliverable

A notebook that runs top to bottom, ending with a short summary:
1. What you built and how well it works out of sample.
2. The data issues you found and what you did about each.
3. How you validated, and why you trust the result.
4. What drives the forecasts.
5. Limitations, and what you would do with more time.
