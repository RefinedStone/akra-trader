# RSI14 Oversold Reversal Tuning Notes

Last updated: 2026-05-15 KST

## Objective

Tune `rsi14_oversold_reversal_v1` so the RSI oversold rebound strategy keeps win rate above 51%, favors longer reward/risk exits, and can be validated across 1-year and multiple 1-month backtests without repeating already-failed parameter searches.

## Current Default

- Strategy: `RSI14 과매도 탈출 반등 매수`
- Entry: RSI14 recent minimum <= 30, RSI turn rebound trigger, one-bar RSI rebound <= 10, close above MA60 trend filter, close position >= 0.75.
- Secondary entry: a tightly filtered MA60-below capitulation rebound sleeve for deep RSI washouts in a narrow RSI/ATR/slope recovery band.
- Risk/exit: max position fraction 1.0, ATR stop 4.0, profit target 1.5R, no-profit time stop 288 bars, stop cooldown 20 bars.
- 1-year validation run: `1e5a8d03-d8a2-4bfa-94d3-1da8ecd7d05a`
  - Window: `2025-05-13T00:00:00Z` to `2026-05-13T00:00:00Z`
  - Data: 105,121 5m candles, no market data issues
  - Return: +10.13%
  - Win rate: 61.54%
  - Trades: 26
  - Max drawdown: 4.46%

## Verified Monthly Samples

Using the same current default parameters:

| Window | Run | Return | Win rate | Trades | Note |
| --- | --- | ---: | ---: | ---: | --- |
| 2026-04-13 to 2026-05-13 | `258ea3c0-4bb4-4587-baa3-e9f299f4dd96` | +4.15% | 100.00% | 3 | Positive; capitulation sleeve caught the April/May rebound cluster while avoiding 2026-05-12. |
| 2026-01-01 to 2026-02-01 | `803913d3-e22d-4a18-8f3a-4615394fb292` | +0.95% | 50.00% | 4 | Positive return. |
| 2025-09-01 to 2025-10-01 | `909953a5-7976-4b2f-bffc-82c5e6cb6653` | +1.41% | 50.00% | 4 | Positive return. |
| 2025-06-01 to 2025-07-01 | `3ab7c3eb-78f9-47f2-a298-b9a2a273f875` | +0.05% | 50.00% | 4 | Barely positive; still the weakest monthly sample. |
| 2025-11-01 to 2025-12-01 | `369e2b10-a3be-4275-bd44-403ac57fb3fe` | +0.37% | 66.67% | 3 | Positive. |

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
  - Keep trailing optional until a verified parameter set beats the current +5.74% 1-year run and positive monthly samples.
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
  - Current default chooses 0.75 because it gives the best 1-year return among the positive-November close-position variants.
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
  - API result: recent month +4.15%, 1-year +10.13%, 61.54% win rate, 26 trades.

## Residual Weakness

The current default clears the 1-year win-rate and positive-return gates and has five positive 1-month samples. The weakest sample remains June 2025 at +0.05%, and several monthly win rates are 50%, so future work should focus on improving the weak months without loosening the capitulation sleeve.
