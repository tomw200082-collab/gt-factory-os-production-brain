# .audits — Retention Policy

**Owner:** monitoring / operations  
**Applies to:** `.audits/stock-accuracy/` and any future audit subdirectories

## Rules

- Keep all daily audit folders for **30 days** from their run date.
- Archive one folder per month as a monthly snapshot (keep the last run of each calendar month).
- Delete daily folders older than 30 days that are not a monthly snapshot.
- Never delete the most recent folder, regardless of age.

## What lives here

Timestamped stock-accuracy audit reports produced by the daily audit job.  
Each folder contains `report.md` with the audit output for that run.

## What never lives here

- Source code
- Migration files
- Governance documents
- Active operational state

## Archive location

Monthly snapshots: `.audits/stock-accuracy/archive/YYYY-MM/`

## Current state (2026-05-08)

62 folders present from 2026-05-05. These are within the 30-day window and are retained.  
First eligible cleanup date: 2026-06-04.
