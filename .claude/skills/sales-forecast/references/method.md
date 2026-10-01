# Sales forecast: method and evidence

The method below has an item-level error of 38.9%, against 41.8% for the best benchmark (the 12-month average) and 41.4% for the research brief's recipe. Its bias is −1.1%, where the 12-month average runs at −17% and same-month-last-year at −26%. Measured on 2026-09-28 with a rolling-origin backtest over 8 forecast origins (2025-07 to 2026-02), 6 months ahead, on items with at least 6 clean months at the origin, with the seasonal indices recomputed at each origin.

## 1. Demand

**Source.** Shopify `net_items_sold` per variant SKU per month, from ShopifyQL, starting 2024-07.
- It is the demand record because every order is a Shopify order.
- The ledger's `FG_OUT_PICK` misses 25–40% of picks (check of 2026-09-06), so it would under-forecast.

**Items.**
- Mapped through `integration_sku_map`, approved and active. Internal units = Shopify units × `internal_units_per_shopify_unit`; matcha 18g counts 22 bags per box.
- `GTCC-NM-SAN-3.85L` is read as a second SKU of `FG-NM-3850ML`. This is flagged: its mapping should be added.

**Out:**
- MTO and private-label items (`planning.demand.mto.*`);
- inactive and pending items;
- unmapped SKUs. The run lists each one with units. On 2026-09-28 the list included:
  - 0.3 L teas: 19,650 units in August 2026, one month only;
  - lines with no SKU: 3,600 units in six months;
  - the retired Muza private label.

## 2. Cleaning

**Rule.** A month is missing when it is negative, or below 30% of the median of the four months around it (with that median at 20 or more). Missing months are neither levels nor training data.

**Relaunch.** A run of 6 or more months without sales drops the history before it. Example: `FG-NAM-500ML` had one sale of 12 in 2024-07 and launched properly in 2026-02.

**What it catches:**
- **April 2026:** reversals booked that month took the main teas to near zero while orders stayed normal (Sales-Machine evidence 2026-09-02, U-037). That month is also never scored.
- **Stockout months:** e.g. `FG-DET-500ML` in Aug–Sep 2024 and `FG-CON-500ML` in Aug–Sep 2025.

**Why missing, not zero.** A stockout month is censored demand. Treating it as zero demand would teach the model a dip that customers never chose.

## 3. Effective working days

**Weights.** Sun–Thu days count 1. A chag counts 0: Rosh Hashana, Yom Kippur, the first day of Sukkot, Shemini Atzeret, the first and seventh days of Pesach, Shavuot and Independence Day. Chol hamoed and erev chag count 0.5. The source is python-holidays, Israel, public and optional categories. The system's `holidays_il` table starts only in April 2026.

**Why it matters.** Everything is modelled per effective day, so a holiday that moves between months does not move the seasonality.
- October 2024 had 17 effective days and October 2025 had 16: the Tishrei holidays fell in October.
- October 2026 has 20.5: the holidays fell in September.
- A same-month-last-year method would under-forecast October 2026 and over-forecast November.

## 4. Seasonality by group

**Groups:**
- **Cold teas:** Detox, Fresh, Revive, Calm, Energy, Consciousness, Desertea.
- **Chai:** Namastea.
- **Sangria:** Nonomimi sangria and the sangrias.
- **Powders, ODK and other:** no seasonality. Powders and ODK have under two clean cycles, and matcha's growth would read as seasonality.

**Estimation.** Each group's per-effective-day total, as a ratio to the 12-month window around it, averaged per calendar month and normalised to a mean of 1. The index is then shrunk 25% toward 1. In the backtest, shrinking by 0.75 beat 0.5 and 1.0.

**Estimated per-effective-day indices** (history to 2026-08, after shrinkage):

| Group | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Cold teas | 0.71 | 0.76 | 0.81 | 0.81 | 1.03 | 1.05 | 1.23 | 1.17 | 1.33 | 1.16 | 1.13 | 0.81 |
| Chai | 1.27 | 1.09 | 0.96 | 0.99 | 0.87 | 0.77 | 0.88 | 0.68 | 1.03 | 0.98 | 1.15 | 1.33 |
| Sangria | 1.56 | 1.21 | 1.12 | 0.78 | 0.86 | 0.83 | 0.48 | 0.75 | 1.03 | 0.89 | 0.98 | 1.50 |

## 5. The forecast

**The three forecasts.** Each is a forecast of the deseasonalised rate per effective day:
1. **Level:** the last 4 clean months, weighted 0.7 to the power of each month's age.
2. **SES:** simple exponential smoothing with an optimised alpha (`SimpleExponentialSmoothingOptimized`).
3. **Theta:** `AutoTheta`, season length 1, since the series is already seasonally adjusted. Theta was the strongest single method on monthly data in the M3 and M4 competitions.

**Combining.** The three are averaged, then multiplied back by the group index and the target month's effective days. Averaging methods beats picking one: this is the main M4 finding, and it held here too. The combo scored 40.0% against 39.2–42.0% for the parts, with the lowest bias and the lowest monthly-total error.

**Intermittent items** have an average inter-demand interval (ADI) above 1.32 months, the Syntetos–Boylan cut-off. They get the mean of SBA, TSB and IMAPA on the raw monthly series, with no calendar or seasonal scaling. On 2026-09-28 these were five accessories and dried fruit, each at 1–4 a month.

**Items with under 3 clean months:** units since the first sale, divided by the months since then, with the current partial month counted by its fraction. There is no trend. The item is flagged for a judgement.

## 6. Backtest (2026-09-28)

| Method | Item WAPE | Bias | Monthly-total WAPE | WAPE at horizon 1 / 3 / 6 |
|---|---|---|---|---|
| **Combo (used)** | **38.9%** | **−1.1%** | 25.3% | 41% / 40% / 40% |
| Research recipe: SES + damped ETS + Theta | 41.4% | +1.9% | 26.7% | 43% / 43% / 42% |
| Benchmark: 12-month average | 41.8% | −17.1% | 24.3% | 40% / 39% / 46% |
| Benchmark: same month last year | 42.8% | −26.3% | 31.3% | 39% / 41% / 47% |
| Benchmark: last 3 months | 48.5% | −0.2% | 28.5% | 39% / 47% / 53% |

**Rejected: averaging in the 12-month average.** It cut item error to 39.3% (0.8 points), but pushed bias to −10.8%. In a growing business a 12-month average always trails, and a persistent under-forecast is what buffers cannot cover. Bias is kept small by design.

**The run's gate.** `run_forecast.py` writes no draft unless the combo beats the best benchmark on item WAPE.

**How the backtest is scored:**
- WAPE is Σ|F−A| ÷ ΣA over item-months.
- The monthly-total WAPE compares each month's sum across items. That is the number that matters for shared raw materials.
- Items launched after the origin are not scored: they are handled by the new-item rule and a judgement, not by the method.

**Uncertainty per item-month.** Actual ÷ forecast has p10 about 0.4, a median of 0.9–1.0 and p90 about 1.8 at horizons 1–3, rising to about 2.1 at horizons 4–6. Single items are lumpy because one large order moves a month. Buffers should therefore be sized on the material totals, not per item.

**Where the error sits:**
- Matcha 18g carries about a fifth of all error. It went from nothing to 3,700 bags a month in 2026, and a few buyers drive it.
- New launches, such as Namastea 500 ml in 2026-02, have no history at earlier origins.

## 7. Judgement inputs (asked of Tom, logged per version)

These are the known events the history cannot show, and are the overrides that add value, as opposed to small tweaks:
- launches and their date, e.g. the American line and the new NS variants;
- one-off or recurring large orders, e.g. the 0.3 L teas;
- customers won or lost;
- changes at the few buyers behind matcha 18g.

Tom's answers, 2026-09-28 (D41):
- The 0.3 L teas are made to order, so they stay out (`KNOWN_OUT`).
- The NS variants are not launching.
- The American line may come around December. It stays at zero until he confirms a date.
- Matcha 18g: nothing known, so no override.

Each override is recorded with its reason. The next backtest shows whether it helped, which is Forecast Value Added.

## 8. The process around the numbers (research brief, 2026-09-28)

**What to forecast.** Sell-out, which here means Shopify orders.
- Trucks to the Distributor are transfers GT plans. They are never demand, because forecasting from a middleman's orders is a named cause of the bullwhip effect ([Lee, Padmanabhan & Whang](https://www2.isye.gatech.edu/~jvandeva/Classes/6203/2006/TheBullWhipEffectinSCsLee.pdf)).
- If demand history is ever rebuilt from stock outflows, exclude the Distributor's initial stock-up.
- Tag October–December 2026 as transition months and score them separately.

**Overrides.** Every override is logged with an author, a reason and an expiry.
- In 60,000+ forecasts at four supply-chain firms, small adjustments often made accuracy worse. Large ones, backed by real reasons, helped ([Fildes et al.](https://researchportal.bath.ac.uk/en/publications/effective-forecasting-and-judgmental-adjustments-an-empirical-eva/)).
- Upward adjustments were much less likely to help than downward ones, which the authors read as optimism.
- Forecast Value Added is measured with a stairstep: naive, then statistical, then adjusted, then approved ([SAS FVA](https://www.sas.com/content/dam/SAS/en_us/doc/whitepaper1/forecast-value-added-analysis-106186.pdf)).

**Review by exception.** Look at what changed since the last version, not at every number ([Oliver Wight](https://www.oliverwight-americas.com/wp-content/uploads/2022/11/eBrochure_IBP.pdf); [Forecast Pro](https://www.forecastpro.com/2014/03/managing-forecasts-by-exception/)).
- **Starting thresholds, summed over the purchasing window:** a change above 15% for A items, 25% for B and 40% for C, and at least one batch. Also flag a bias tracking signal beyond ±4.
- **Tuning:** aim for 5–10 exceptions a month. Widen a threshold when two-thirds of its flags end unchanged for two cycles.
- **As built (D40):** the thresholds run over the months both versions cover. A floor of 50 units stands in for "one batch" until batch sizes are in the system. When nothing is flagged, the run publishes by itself; a flagged line reaches Tom as a Decision. The tracking signal is not built yet.

**Cadence.**
- Recompute every two weeks and freeze every published version.
- Score accuracy on the version that was live when the purchase order was placed ([RELEX](https://www.relexsolutions.com/resources/measuring-forecast-accuracy/)).
- Repeated re-forecasting feeds the bullwhip effect. The later refinement: blend new and old numbers inside the lead-time window ([Godahewa et al.](https://arxiv.org/html/2310.17332)).

**Account-level forecasting.** It explains changes rather than replacing the SKU forecast.
- Across 966 firms, building sales up from customers beat totals by 2.65%, which was not significant ([Kim et al.](https://arxiv.org/abs/2608.02911)).
- It matters where a few accounts carry an SKU, as with matcha 18g.
- The sleeping rule: no order for more than twice the account's usual gap.

**Buffers.** Safety stock = z × σ, where σ is the RMSE of cumulative forecast error over lead time plus review period, measured at the material level after the BOM explosion.
- Never scale one-month error by √(lead time): errors within a lead time are correlated, and the shortcut leaves safety stock up to 30% short ([Prak et al.](https://research.rug.nl/en/publications/on-the-calculation-of-safety-stocks-when-demand-is-forecasted/)).
- Fixed service levels per ABC class are convention and far from cost-optimal ([Teunter et al.](https://research.rug.nl/en/publications/abc-classification-service-levels-and-inventory-costs)). Rank materials by the margin a shortage blocks.

**Monthly KPIs:**
- WAPE at lag 1 and at the lead-time lag;
- bias and tracking signal;
- FVA against naive: above 1 is worse than naive, and about 0.7 is the practical floor;
- stability between versions;
- exceptions raised, and how many were left unchanged;
- fill rate and material stockout days.

Survey reference throughout: Petropoulos et al., "Forecasting: theory and practice", IJF 2022 ([arXiv](https://arxiv.org/pdf/2012.03854)).

## 9. The statistical methods (research brief, 2026-09-28)

**What the research says, and what we did:**
- **Combinations win.** In M4 monthly, eight of the top 10 methods were combinations. Theta scored OWA 0.907 and Comb (SES/Holt/damped) 0.920, while seasonal naive scored 1.147 ([M4 ranks](https://raw.githubusercontent.com/Mcompetitions/M4-methods/master/Evaluation%20and%20Ranks.xlsx)). In M5, combinations did "better or equally well" than their parts ([M5](https://statmodeling.stat.columbia.edu/wp-content/uploads/2021/10/M5_accuracy_competition.pdf)).
  - **Done:** a three-method mean.
  - **The brief's recipe** (SES + damped ETS + Theta) lost to our variant here, 41.4% against 38.9%, so the level forecast stays in place of damped ETS.
- **Every M4 monthly series had at least 42 observations** ([data](https://raw.githubusercontent.com/Mcompetitions/M4-methods/master/Dataset/Train/Monthly-train.csv)); GT has 18–26. That is why seasonality is pooled by group and why every choice is backtested on GT's own data.
- **Pooled seasonal indices let noisy items borrow strength from their group** ([Mohammadipour et al.](https://link.springer.com/article/10.1057/jors.2012.126)). Reconciliation (MinT) is left out: with short series its covariance is hard to estimate ([2409.18550](https://arxiv.org/abs/2409.18550)).
- **Moving holidays.** Israel's Central Bureau of Statistics (CBS) adjusts for moving festival dates and trading days ([CBS](https://www.cbs.gov.il/he/publications/doclib/2024/yarhon0224/intro_e.pdf)). Done here as effective working days.
  - **Next refinement:** a pre-holiday regressor, the share of the 14 days before Pesach or Rosh Hashana that fall in the month. It matters from 2027-03 onward: Pesach 2027 starts 21 April ([hebcal](https://www.hebcal.com/holidays/pesach-2027)).
- **Intermittent items.** The Syntetos–Boylan classification (SBC) cut-offs choose SBA for ADI above 1.32 ([tsintermittent](https://rdrr.io/cran/tsintermittent/src/R/idclass.R)). Croston, SBA, TSB, ADIDA and IMAPA were near-identical in M5.
  - **Done:** the mean of SBA, TSB and IMAPA.
- **Forecast demand, not sales.** Stockout zeros are left out of fitting and scoring ([openforecast](https://openforecast.org/2024/11/18/why-zeroes-happen/)).
  - **Done:** such months are treated as missing.
  - **Next refinement:** customer-level one-off detection, meaning an order line above 3× that customer's median for the SKU. It needs per-customer data.
- **Backtest protocol:** rolling origin, h = 6, indices refit per fold. Beat the better of seasonal naive and a 12-month average ([FTP](https://arxiv.org/pdf/2012.03854) §2.5.5, §2.12.2).
  - **Done:** also compared against the last-3-months average and the brief's own recipe.
- **Intervals.** Per-item quantile models need a few hundred series ([Lokad](https://www.lokad.com/pinball-loss-function-definition/)). Use pooled, level-scaled backtest errors, taken on the lead-time sum for buffers.
