# Data Exercise: Suggested Prices for Used Boats

**Time allowed:** 6 hours. Work in Python. No AI tools, but with internet.
**Afterwards:** a 45–60 minute discussion with a researcher about your work. Your model's accuracy matters much less than how you got there. Be ready to justify every decision.

The data is synthetic. All manufacturer and model names are fictional.

---

## Setting

You work with an online marketplace for used boats in the US, the UK and Europe.

When a seller creates a listing, the steps are:
1. The seller selects their boat and enters its current condition and engine hours, and uploads photos.
2. **The marketplace shows a suggested price:** an estimate of the price the boat will sell for.
3. The seller then chooses their own asking price and the listing goes live.

**Your job:** build the model behind the suggested price in step 2. It will be used for new listings from January 2025 onwards.

## Data

Three files, extracted from different internal systems on **2025-01-01**. Listings run from 2019-01-01 to 2024-12-31.

**`listings.csv`**: one row per listing

| column | description |
|---|---|
| listing_id | listing identifier |
| boat_id | boat identifier (hull identification number) |
| seller_id | seller identifier |
| seller_type | dealer or private seller |
| region | region where the boat is located |
| listing_date | date the listing went live |
| currency | currency of the listing's prices |
| list_price | asking price when the listing went live |
| engine_hours | total engine hours reported by the seller |
| condition | condition reported by the seller |
| n_photos | number of photos uploaded |
| n_price_drops | number of times the asking price was reduced |
| final_list_price | asking price when the listing ended |
| days_on_market | days between going live and the end of the listing |
| status | sold, withdrawn, or active |
| sale_date | date of sale |
| sale_price | agreed sale price |

**`boats.csv`**: one row per boat, from the hull registry

| column | description |
|---|---|
| boat_id | boat identifier |
| manufacturer, model | builder and model name |
| boat_type | type of boat |
| year_built | model year |
| age_years | age of the boat in years |
| length_ft, length_m | length overall |
| beam_ft | width at the widest point |
| hull_material, fuel_type, engine_count | construction and propulsion |

**`fx_rates.csv`**: monthly average exchange rates (US dollars per euro and per pound)

---

## Part A: Analysis questions (suggested time: about 1.5 hours)

Answer each in your notebook with code, plots and short written explanations.

**A1.** Describe the distribution of sale prices. Would you transform the target before modelling? Explain how your choice affects the way you convert predictions back and evaluate them.

**A2.** How does price depend on length and on age? Is the relationship the same across boat types? Support your answer with plots and a simple model, and interpret the coefficients.

**A3.** Has the market price level changed between 2019 and 2024? Build a measure of the price level over time that is not distorted by changes in which boats are being sold, and compare it with a simple median sale price per period. Explain any differences.

## Part B: Suggested-price model (suggested time: about 4 hours)

Build the model behind the suggested price, as described in the Setting.

You choose the target definition, the training data, features, model, validation scheme and evaluation metrics. Compare against at least one simple baseline.

## Deliverable

A notebook that runs top to bottom, ending with a short summary:
1. What you built and how well it works out of sample.
2. The data issues you found and what you did about each.
3. How you validated, and why you trust the result.
4. What drives the predictions.
5. Limitations, and what you would do with more time.
