# Forecast findings log — daily-ops-guardian

Append-only. date | item | signal | evidence (live SQL, run date) | direction. Log only — forecast edits via weekly/monthly proposals (V6).

## 2026-07-03 (first guardian run; forecast version 369f5cb1 published 2026-06-08, 25d old 🟡)

| item | signal | evidence (14d window) | direction |
|---|---|---|---|
| FG-MAT-30G | committed > forecast | committed 300 vs forecast 177.3 | forecast under-estimates matcha B2B demand; raise |
| GTCC-MUZ-SMAR-1L | committed > forecast ×2.4 | committed 14 vs forecast 5.9 | Muza spicy margarita under-forecast |
| ADD-MUZ-HER-1L | committed ≈ forecast, zero stock | committed 4, forecast 5.9, on-hand 0 | confirm Muza line status (parked) — real orders exist |
| FG-CON-1L | forecast demand w/o supply plan | forecast 175 /14d, on-hand 105, planned 0 | not a forecast miss — planning gap; handed to Thursday ritual |
| FG-SAN-WHI-750ML | forecast w/o production | forecast 40.9, on-hand 12, planned 0 | check if sangria forecast still realistic (summer) |

Data-quality flags (not forecast): negative on-hand — FG-SAN-RED-3850ML −1, FG-SAN-BAB-RED/WHI-750ML −6/−6, ADD-GAR-ORA-DRY −16, EXCLUDED-NONSTOCK −346. rebuild_verifier=0 ∴ ledger-consistent negatives = unrecorded production/receipt events.
