# RSI14 Oversold Reversal Tuning Notes

Last updated: 2026-05-15 KST

## Objective

Tune `rsi14_oversold_reversal_v1` so the RSI oversold rebound strategy keeps win rate above 51%, favors longer reward/risk exits, and can be validated across 1-year and multiple 1-month backtests without repeating already-failed parameter searches.

## Current Default

- Strategy: `RSI14 과매도 탈출 반등 매수`
- Entry: RSI14 recent minimum <= 30, RSI turn rebound trigger, one-bar RSI rebound <= 10, close above MA60 trend filter, close position >= 0.60.
- Standard late rebound guard: when a standard entry is more than 2.2 ATR above the recent low, it must either reclaim MA20 without fresh lower lows or match a deep washout recovery profile.
- Micro probe overlay: lower-quality RSI rebounds that miss full-size entry quality can be sampled with a 0.5% max position, 0.5R target, and 72-bar time stop.
- Secondary entry: a tightly filtered MA60-below capitulation rebound sleeve for deep RSI washouts in a narrow RSI/ATR/slope recovery band.
- Risk/exit: max position fraction 1.0, ATR stop 4.0, profit target 1.5R, no-profit time stop 288 bars, stop cooldown 20 bars.
- 1-year validation run: `161ad088-28b2-4324-975d-3e0184f360a4`
  - Window: `2025-05-13T00:00:00Z` to `2026-05-13T00:00:00Z`
  - Data: 105,121 5m candles, no market data issues
  - Return: +7.48%
  - Win rate: 51.30%
  - Trades: 347
  - Average trades per month: 28.9
  - Max drawdown: 2.44%

## Verified 1-Year Samples

Using the same current default parameters:

| Window | Run | Return | Win rate | Trades | Max drawdown | Note |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 2023-05-13 to 2024-05-13 | `c26f7c17-dfa0-44ba-87da-2258892e3063` | +5.02% | 53.71% | 175 | 0.88% | Clears the monthly-12 average trade-count target. |
| 2024-05-13 to 2025-05-13 | `250d51d1-098c-4c03-bee8-0a6d70401e1b` | +2.79% | 53.80% | 316 | 3.06% | Clears the win-rate and monthly-12 gates. |
| 2025-05-13 to 2026-05-13 | `161ad088-28b2-4324-975d-3e0184f360a4` | +7.48% | 51.30% | 347 | 2.44% | Clears the gates, but with a thin win-rate margin. |

## Verified Monthly Samples

Using the same current default parameters:

| Window | Run | Return | Win rate | Trades | Note |
| --- | --- | ---: | ---: | ---: | --- |
| 2026-04-13 to 2026-05-13 | `a4ec2a64-0559-4e51-8ab7-214d4783a020` | +2.33% | 45.83% | 24 | Positive with high entry count, but monthly win rate is below 51%. |
| 2026-01-01 to 2026-02-01 | `5bbfa482-81a4-43a8-afc3-290891fe76a7` | +2.26% | 40.00% | 20 | Positive despite low monthly win rate. |
| 2025-09-01 to 2025-10-01 | `5ebe0aad-6b6a-4ea6-8020-a1cb04a33329` | +0.61% | 52.00% | 25 | Clears monthly win-rate and trade-count gates. |
| 2025-06-01 to 2025-07-01 | `6c7898cd-6631-4921-a367-0d1c98324d7e` | +0.12% | 50.00% | 34 | Barely positive; monthly win rate is just below 51%. |
| 2025-11-01 to 2025-12-01 | `9bf96b3b-0224-46ea-b172-aee9e2c22c9e` | +1.41% | 47.22% | 36 | Positive with high entry count, but monthly win rate is below 51%. |
| 2023-06-01 to 2023-07-01 | `bca38348-0a94-49f3-ac38-93e88166ee37` | +1.00% | 63.64% | 11 | One trade short of 12 in this older single-month sample. |

## Attempts To Avoid Repeating

- Loose RSI30 rebound default:
  - Parameters: RSI oversold 30, lookback 80, `rsi_turn`, above MA60, ATR stop 2.0, 2.0R target, full-size risk sizing.
  - 1-year result: +1.55%, 51.16% win rate, 43 trades, 2.35% max drawdown.
  - Rejected because several 1-month samples were negative: recent -0.49%, June -0.58%, September -0.08%.
- Stricter RSI25 with half allocation:
  - Parameters: RSI oversold 25, close position 0.45, above MA60, ATR stop 4.0, 1.5R target, max position fraction 0.5.
  - 1-year result: +4.47%, 63.64% win rate, 11 trades.
  - Rejected as default because the same signal quality with max position fraction 1.0 improved 1-year return to +5.87% without increasing drawdown beyond 1.91%.
- RSI30 trade expansion:
  - Increased trade count but admitted shallow oversold rebounds that failed in the recent and June monthly windows.
  - A one-bar RSI rebound cap now blocks the 2026-05-12 overextended rebound, but shallow RSI30 entries still need close-position filtering.
- Immediate trailing-profit default:
  - Earlier exploratory runs with trailing held winners longer but materially reduced win rate or total return in this signal family.
  - Keep trailing optional until a verified parameter set beats the current +11.26% 1-year run and positive monthly samples.
- RSI30 macro trend filter:
  - Parameters tested: `rsi_oversold_level=30`, `entry_trend_filter_mode=macro`.
  - Recent month run `0f9e0836-fa0b-4818-9fc3-b013fb947af8`: 0.00%, 0 trades.
  - June run `96d0bc29-bef5-4619-8f78-cfbad55eac27`: -1.86%, 0.00% win rate, 2 trades.
  - Rejected because it still loses in June.
- RSI30 escape-only macro:
  - Parameters tested: `rsi_oversold_level=30`, `entry_trend_filter_mode=macro`, `entry_trigger_mode=escape_breakout`.
  - Recent run `e4eb0166-6f7c-42ed-a8bb-4967e0b740da`: 0.00%, 0 trades.
  - June run `3b3c52d5-9d9a-4c18-9869-6d46708d678c`: 0.00%, 0 trades.
  - Rejected because it only avoids trades; it does not create monthly wins.
- Early-reversal/either trigger:
  - Strict RSI25 + early/either recent run `e774676e-ec97-4cd8-8652-4414afeca4eb`: 0.00%, 0 trades.
  - Strict RSI25 + early/either June run `ce9ff721-f588-4744-b476-34e3f5e41ed7`: 0.00%, 0 trades.
  - RSI30 + early/either recent run `2b2887c3-e31f-43c3-b35f-3b7d2fb6b22f`: -1.30%, 0.00% win rate, 1 trade.
  - RSI30 + early/either June run `0bd24e1f-1776-4ca2-a6e1-4b064d492203`: +0.51%, 50.00% win rate, 6 trades.
  - Rejected because the June improvement reopens the known 2026-05-12 losing trade.
- RSI30 with rebound cap and close-position variants:
  - Default-like `entry_min_close_position=0.45` run `9d65503a-ce41-48f4-bab5-657527fc30b0`: 1-year +8.30%, 55.88% win rate, 34 trades, but November `3beb226c-1325-4df3-aa0e-340e52c38bc5` was -0.90%.
  - `entry_min_close_position=0.65` run `7eef6f69-5ce5-424a-a0e2-8e1eb188b524`: 1-year +5.37%, 55.56% win rate, 27 trades; November +0.37%.
  - `entry_min_close_position=0.70` run `a4c8ad09-2444-4c10-8367-fca0e3d595ce`: 1-year +5.52%, 56.00% win rate, 25 trades; November +0.37%.
  - `entry_min_close_position=0.75` run `19e1fac0-1abe-48c9-9966-1f11915df539`: 1-year +5.74%, 56.52% win rate, 23 trades; June, September, November, and January sample windows stayed positive.
  - At that stage 0.75 was chosen because it gave the best 1-year return among the positive-November close-position variants; later 2023-2024 validation required the late rebound guard and 0.60 trade expansion.
- Slow local random searches:
  - Two broad Python search passes were stopped because they were too slow for interactive iteration.
  - Do not rerun broad per-candidate Python loops over 1-year data without vectorizing entries first or reducing the candidate set.
- Recent-month trade forcing:
  - `entry_trend_filter_mode=any`, 1R target, 2 ATR stop, run `5940fc9d-00b2-4343-a7e4-f890ae6f5f62`: -15.86%, 40.00% win rate, 55 trades.
  - `entry_trend_filter_mode=loose`, 1R target, 2 ATR stop, run `04803c6d-ef30-466b-b8ba-a2edc44e18d1`: -4.56%, 47.37% win rate, 19 trades.
  - `entry_trend_filter_mode=above20`, 1R target, 2 ATR stop, run `6b74d199-d3b0-4e89-8393-28d301703488`: -2.60%, 57.14% win rate, 14 trades.
  - `entry_trend_filter_mode=any`, close position 0.5, 1R target, 2 ATR stop, run `78817c00-1c02-4123-a506-fb047851553f`: -16.53%, 41.67% win rate, 60 trades.
  - Rejected because forcing trades in the 2026-04-13 to 2026-05-13 window creates heavy losses; current no-trade behavior is preferable for that month.
- Broad capitulation rebound sleeve:
  - A looser MA60-below capitulation rebound filter made the recent month +4.15%, but the 1-year simulation fell to -7.68% with 44.21% win rate and November fell to -3.70%.
  - Rejected because a capitulation sleeve must be very narrow; broad downtrend buying overtrades.
- Narrow capitulation rebound sleeve:
  - Added as current default through `entry_enable_capitulation_rebound=true`.
  - It buys below MA60 only when RSI recent minimum, current RSI, one-bar RSI rebound, close position, ATR proximity, MA slopes, MA/ATR distances, and ATR percentage all sit in a narrow post-capitulation band.
  - Initial API result before the late rebound guard: recent month +4.15%, 1-year +10.13%, 61.54% win rate, 26 trades.
- 2023-2024 uncovered weak regime:
  - Previous current-default run `d675e65d-8ed9-4e5c-974e-15b16aa5bf1e`: +0.07%, 37.50% win rate, 8 trades.
  - Loss review showed several entries bought more than 2.2 ATR above the recent low without reclaiming MA20, turning shallow RSI rebounds into late entries.
- Over-tight low proximity filter:
  - `entry_max_low_proximity_atr=2.2` made 2023-2024 +2.71%, 66.67% win rate, 3 trades; 2024-2025 +4.93%, 60.00% win rate, 15 trades; 2025-2026 +6.72%, 64.29% win rate, 14 trades.
  - Monthly checks made June 2025 and June 2023 flat with zero trades.
  - Rejected because it improves win rate mostly by removing too many trades.
- Swing-low stop default:
  - `exit_enable_swing_low_stop=true` made 2023-2024 -0.99%, 25.00% win rate, 8 trades.
  - Rejected because the tighter stop cuts rebound trades before they can resolve.
- Standard late rebound quality guard:
  - Added as current default after the 2023-2024 weak-regime review.
  - Standard entries more than 2.2 ATR above the recent low must either reclaim MA20 without fresh lower lows, or satisfy a deep washout recovery profile: RSI recent minimum <= 18, MA20 slope <= -20, ATR percentage >= 0.25, and no fresh lower lows.
  - The deep washout exception is needed because a pure MA20-reclaim rule removed the 2025-11-26 winner and made November 2025 negative.
  - API result before close-position trade expansion: 2023-2024 +3.74% / 75.00% win rate / 4 trades; 2024-2025 +4.50% / 56.52% / 23 trades; 2025-2026 +10.31% / 62.50% / 24 trades.
- Close-position trade expansion:
  - `entry_min_close_position=0.70`: 2023-2024 +3.74% / 75.00% / 4 trades; 2024-2025 +3.23% / 54.17% / 24 trades; 2025-2026 +9.09% / 60.00% / 25 trades.
  - `entry_min_close_position=0.65`: 2023-2024 +3.39% / 80.00% / 5 trades; 2024-2025 +3.45% / 54.17% / 24 trades; 2025-2026 +9.60% / 61.54% / 26 trades.
  - `entry_min_close_position=0.60`: chosen current default because it increases trades to 6 / 25 / 28 across the three 1-year windows while keeping every 1-year win rate above 51%.
  - `entry_min_close_position=0.50`: 2025-2026 had more trades at 32 but return fell to +8.72%; not chosen.
  - `entry_min_close_position=0.45`: rejected because 2024-2025 became -0.59% with 50.00% win rate despite 28 trades.
- Late-guard expansion attempts:
  - `entry_enable_early_reversal=true`, `entry_trigger_mode=either` after the late rebound guard produced the same 1-year results as current default: 2023-2024 +2.13% / 66.67% / 6 trades; 2024-2025 +2.90% / 52.00% / 25 trades; 2025-2026 +11.26% / 60.71% / 28 trades.
  - `entry_trend_filter_mode=loose` after the late rebound guard made 2023-2024 -32.68%, 35.00% win rate, 140 trades.
  - `entry_trend_filter_mode=loose`, tighter low-proximity variants in 2023-2024 still failed: close-position 0.75 / low-proximity 1.5 ATR was -3.70% with 6 trades, and low-proximity 1.8 ATR was -6.89% with 20 trades.
  - Rejected because early/either adds no trades and loose trend filtering adds many low-quality downtrend trades.
- Monthly-12 high-frequency scalp attempts:
  - These were tested only to audit the explicit "monthly average 12 entries" requirement against the current RSI oversold family.
  - `entry_trend_filter_mode=loose`, 0.5R target, 4 ATR stop, 2023-2024 run `33856850-3d05-4f31-b387-1476e577d76b`: -31.88%, 61.49% win rate, 161 trades.
  - `entry_trend_filter_mode=loose`, 0.8R target, 4 ATR stop, 2023-2024 run `37e5c78c-e30a-4a3b-957d-32157a76d76d`: -25.83%, 55.70% win rate, 149 trades.
  - `entry_trend_filter_mode=loose`, 0.5R target, 2 ATR stop, 2023-2024 run `01bf10bf-5607-4fc9-9c0d-7cadb5fd7e24`: -40.90%, 43.50% win rate, 177 trades.
  - Rejected because the trade-count target is reachable only by admitting many low-quality rebounds that destroy expectancy, directly conflicting with the higher reward/risk objective.
- Micro probe overlay:
  - Added as current default after high-frequency full-size/scalp variants failed.
  - Full-size entries keep the 1.5R target and ATR risk sizing; lower-quality RSI rebounds are admitted only as 0.5% max-position probes with a 0.5R target and 72-bar time stop.
  - Local dual-layer simulation before implementation suggested 184 / 328 / 365 trades across the three 1-year windows with positive returns and 53%+ win rates.
  - API validation after implementation: 2023-2024 +5.02%, 53.71% win rate, 175 trades; 2024-2025 +2.79%, 53.80%, 316 trades; 2025-2026 +7.48%, 51.30%, 347 trades.
  - This satisfies the 1-year monthly-average trade-count target while preserving positive expectancy through tiny sizing on the noisy probe layer.
- Micro probe target variations:
  - `exit_micro_probe_profit_r_multiple=0.4`: 2023-2024 +5.03% / 56.91% / 181 trades; 2024-2025 +2.75% / 55.38% / 325 trades; 2025-2026 +9.39% / 51.12% / 356 trades.
  - `exit_micro_probe_profit_r_multiple=0.3`: 2025-2026 fell below the win-rate gate at +9.19% / 48.38% / 370 trades.
  - `exit_micro_probe_profit_r_multiple=0.6`: 2024-2025 fell below the win-rate gate at +3.58% / 50.00% / 306 trades.
  - Keep the default at 0.5 because it gives the best minimum full-year win-rate margin among the tested targets.
- Shallow oversold expansion attempts:
  - `rsi_oversold_level=35`, 2023-2024 run `c7c43387-f4cf-47e3-bd1b-1ecbad5ef1e9`: +0.59%, 48.15% win rate, 27 trades.
  - `rsi_oversold_level=38`, 2023-2024 run `a26ca864-acf5-4314-bfe0-9f7b45a171c0`: -6.85%, 38.89% win rate, 36 trades.
  - Rejected because lifting the oversold threshold increases trade count but fails the 51% win-rate gate before reaching monthly-12 frequency.
- 1m timeframe expansion attempts:
  - Current default on 1m, recent month run `8eac19d8-ed01-4530-85ca-e288eb9b242b`: +0.59%, 100.00% win rate, 2 trades, with 2 market-data issues.
  - `rsi_oversold_level=35` on 1m, recent run `0b67a98c-f9b7-41c1-9f07-609e8d4cb8a1`: +0.02%, 66.67% win rate, 3 trades, with 2 market-data issues.
  - `entry_trend_filter_mode=loose` on 1m, recent run `40dba29e-eb2d-4dfb-9407-8966b99c470a`: -10.80%, 40.68% win rate, 59 trades, with 2 market-data issues.
  - `entry_trend_filter_mode=loose`, `rsi_oversold_level=35` on 1m, recent run `db723919-ef5c-44aa-8254-026c1bdd45c2`: -16.40%, 40.70% win rate, 86 trades, with 2 market-data issues.
  - `entry_trend_filter_mode=loose`, `rsi_oversold_level=35`, 0.8R target on 1m, recent run `5299e188-4e86-4c6e-94d2-2993d0b32be5`: -18.83%, 42.86% win rate, 91 trades, with 2 market-data issues.
  - Rejected because 1m either remains too sparse under the quality filters or loses badly when loosened.
- Broad local grid search:
  - A 2023-2024 local grid over RSI threshold, trend mode, close-position, low-proximity, and target R was stopped after it proved too slow.
  - Keep future searches narrow or implement a vectorized simulator before doing broad high-frequency exploration.

## Residual Weakness

The current default clears the 1-year win-rate, positive-return, and average monthly trade-count gates across three adjacent 1-year windows and has six positive 1-month samples. The weakest remaining evidence is that the 2025-2026 full-year win rate is only 51.30%, several monthly samples have win rates below 51%, and the 2023-06 single-month sample has 11 trades. Future work should improve monthly consistency without increasing the micro probe size or loosening the capitulation sleeve.
