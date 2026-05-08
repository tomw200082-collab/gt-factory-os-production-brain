# Cleanup Audit — Planning Artifacts

> Generated: 2026-05-02T17:28:04.821Z
> Source: live Supabase Postgres (DATABASE_URL_POOLED) via `scripts/_audit_fake_planning.mjs`
> Mode: READ-ONLY (no DDL, no DML)

## Top-line counts

| Table | Total rows |
|---|---|
| planning_runs | 112 |
| planning_run_recommendations | 23244 |
| planning_run_exceptions | 2756 |
| production_plan | 1 |
| production_actual | 0 |

## 1. planning_runs

Total: **112**. REAL (produced converted-to-PO recs): **15**. SUSPECT: **97**.

### Per-status

| Status | Count |
|---|---|
| superseded | 79 |
| completed | 28 |
| running | 5 |

### Per-trigger_source

| trigger_source | Count |
|---|---|
| manual | 97 |
| scheduled | 15 |

### Per-actor

| Actor email | Count | classification |
|---|---|---|
| (null) | 30 | unknown_user |
| (null) | 18 | unknown_user |
| (null) | 15 | unknown_user |
| (null) | 12 | unknown_user |
| (null) | 6 | unknown_user |
| (null) | 5 | unknown_user |
| (null) | 4 | unknown_user |
| (null) | 3 | unknown_user |
| (null) | 3 | unknown_user |
| tom@gteveryday.com | 3 | REAL_USER |
| (null) | 2 | unknown_user |
| (null) | 2 | unknown_user |
| (null) | 2 | unknown_user |
| (null) | 2 | unknown_user |
| (null) | 2 | unknown_user |
| (null) | 1 | unknown_user |
| (null) | 1 | unknown_user |
| (null) | 1 | unknown_user |

### REAL planning_runs (15)

These runs each produced at least one recommendation that was converted to a real PO. Do NOT delete: cascade would orphan or SET-NULL real PO source links.

| run_id | status | executed_at | actor | trigger | recs |
|---|---|---|---|---|---|
| `45d5887b-29f5-477d-b2f6-91b7a3ae52cc` | completed | Sat May 02 2026 10:45:54 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-00000000aa01 | manual | 2 |
| `504385bf-3fa8-45e6-9b46-fdc0926d0533` | completed | Sat May 02 2026 10:45:54 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-0000000009c1 | manual | 1 |
| `e488b4c5-f43c-4b73-8e85-e92f728820a0` | completed | Sat May 02 2026 10:45:53 GMT+0300 (שעון ישראל (קיץ)) | eeeeeeee-0000-0000-0000-001107952903 | manual | 1 |
| `2ed66109-068e-46cd-b0cd-d9517556e3fe` | completed | Sun Apr 26 2026 13:38:37 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-0000000009c1 | manual | 1 |
| `86b6c568-d7a0-478e-b721-744bded2e51a` | completed | Sun Apr 26 2026 13:38:32 GMT+0300 (שעון ישראל (קיץ)) | cccccccc-0000-0000-0000-00000000ff01 | manual | 1 |
| `3f78bc5c-c1fd-47ed-859b-e757130ea727` | completed | Sun Apr 26 2026 13:38:26 GMT+0300 (שעון ישראל (קיץ)) | ffffffff-0000-0000-0000-00000000cc01 | manual | 3 |
| `243f635c-708d-4014-891d-0872dbc2b820` | completed | Sun Apr 26 2026 13:38:21 GMT+0300 (שעון ישראל (קיץ)) | eeeeeeee-0000-0000-0000-001199900501 | manual | 1 |
| `9df67cc4-d13c-4b3e-b244-e7b69b6daeae` | completed | Sun Apr 26 2026 13:38:16 GMT+0300 (שעון ישראל (קיץ)) | eeeeeeee-0000-0000-0000-00000000bb01 | manual | 1 |
| `851150ce-da96-4875-8c5c-754eea50d8e2` | completed | Sun Apr 26 2026 13:38:11 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-00000000aa01 | manual | 2 |
| `1d9016e3-a3b0-4c3b-af5f-99dc7ebe93a3` | completed | Sun Apr 26 2026 13:35:38 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-0000000009c1 | manual | 1 |
| `a6b8cd29-f8bb-4e7f-b706-ce2d2202e5fa` | completed | Sun Apr 26 2026 13:35:32 GMT+0300 (שעון ישראל (קיץ)) | cccccccc-0000-0000-0000-00000000ff01 | manual | 1 |
| `17ca6b4b-8a7d-4f54-98ac-04643d43a376` | completed | Sun Apr 26 2026 13:35:27 GMT+0300 (שעון ישראל (קיץ)) | ffffffff-0000-0000-0000-00000000cc01 | manual | 3 |
| `076ae8b1-bdf3-4b13-a6ba-acb6a308a878` | completed | Sun Apr 26 2026 13:35:23 GMT+0300 (שעון ישראל (קיץ)) | eeeeeeee-0000-0000-0000-001199722022 | manual | 1 |
| `71007303-e8fc-436f-afd6-7f8ef80590e5` | completed | Sun Apr 26 2026 13:35:17 GMT+0300 (שעון ישראל (קיץ)) | eeeeeeee-0000-0000-0000-00000000bb01 | manual | 1 |
| `ee2d6847-3d35-47ca-8f56-e65b8223e19b` | completed | Sun Apr 26 2026 13:35:13 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-00000000aa01 | manual | 2 |

### SUSPECT planning_runs (97)

These runs produced no converted-to-PO recommendations. Most are 'superseded' (replaced by a later run); the rest are pre-launch exploratory.

| run_id | status | executed_at | actor | trigger | recs | reasons |
|---|---|---|---|---|---|---|
| `5ac2f109-5e07-42d4-8323-161ca35e3ffa` | completed | Sat May 02 2026 09:21:24 GMT+0300 (שעון ישראל (קיץ)) | tom@gteveryday.com | manual | 936 | no recommendations from this run were ever converted to a PO |
| `7664bed4-fc24-4e71-b2fe-1cd8790009b5` | superseded | Sat May 02 2026 00:56:42 GMT+0300 (שעון ישראל (קיץ)) | ffff0002-0000-0000-0000-000000000e01 | manual | 0 | superseded; no recommendations from this run were ever converted to a PO |
| `b53bec68-7b99-4a6f-9c14-be61a136c612` | superseded | Sat May 02 2026 00:56:42 GMT+0300 (שעון ישראל (קיץ)) | ffff0002-0000-0000-0000-000000000e01 | manual | 0 | superseded; no recommendations from this run were ever converted to a PO |
| `1cc92fe6-078e-4cb0-9a58-869d69e00141` | superseded | Sat May 02 2026 00:56:42 GMT+0300 (שעון ישראל (קיץ)) | ffff0002-0000-0000-0000-000000000e01 | manual | 0 | superseded; no recommendations from this run were ever converted to a PO |
| `e5aff903-12aa-472c-907a-187849188594` | superseded | Sat May 02 2026 00:56:41 GMT+0300 (שעון ישראל (קיץ)) | ffff0002-0000-0000-0000-000000000e01 | manual | 0 | superseded; no recommendations from this run were ever converted to a PO |
| `52171abf-de08-4025-ac60-a8d3bb45d38b` | superseded | Sat May 02 2026 00:56:41 GMT+0300 (שעון ישראל (קיץ)) | ffff0002-0000-0000-0000-000000000e01 | manual | 0 | superseded; no recommendations from this run were ever converted to a PO |
| `57e8f757-5c31-4fdf-b192-78131dfefd78` | superseded | Sat May 02 2026 00:55:26 GMT+0300 (שעון ישראל (קיץ)) | ffff0002-0000-0000-0000-000000000e01 | manual | 0 | superseded; no recommendations from this run were ever converted to a PO |
| `29206228-fa53-4ddc-9454-cf7b5ba45abd` | superseded | Sat May 02 2026 00:55:26 GMT+0300 (שעון ישראל (קיץ)) | ffff0002-0000-0000-0000-000000000e01 | manual | 0 | superseded; no recommendations from this run were ever converted to a PO |
| `db5d0c9e-abbd-4248-95f6-9f88c5d254f4` | superseded | Sat May 02 2026 00:55:25 GMT+0300 (שעון ישראל (קיץ)) | ffff0002-0000-0000-0000-000000000e01 | manual | 0 | superseded; no recommendations from this run were ever converted to a PO |
| `ba42fa16-2de7-4654-862f-d60efcbd6517` | superseded | Sat May 02 2026 00:55:25 GMT+0300 (שעון ישראל (קיץ)) | ffff0002-0000-0000-0000-000000000e01 | manual | 0 | superseded; no recommendations from this run were ever converted to a PO |
| `7f3879fc-9fca-49f0-9647-ff9e2b920ab3` | superseded | Sat May 02 2026 00:55:25 GMT+0300 (שעון ישראל (קיץ)) | ffff0002-0000-0000-0000-000000000e01 | manual | 0 | superseded; no recommendations from this run were ever converted to a PO |
| `66532d62-a276-4449-b20b-47cb958bce5e` | superseded | Mon Apr 27 2026 11:00:36 GMT+0300 (שעון ישראל (קיץ)) | ffff0003-0000-0000-0000-000000000b01 | manual | 0 | superseded; no recommendations from this run were ever converted to a PO |
| `0d9e4064-3c9b-44ae-8efd-157ef52e2ae0` | superseded | Mon Apr 27 2026 11:00:35 GMT+0300 (שעון ישראל (קיץ)) | ffff0003-0000-0000-0000-000000000b01 | manual | 0 | superseded; no recommendations from this run were ever converted to a PO |
| `3ba6d81b-db36-4e2a-9007-5240b1d3b7a7` | superseded | Mon Apr 27 2026 10:54:15 GMT+0300 (שעון ישראל (קיץ)) | ffff0003-0000-0000-0000-000000000b01 | manual | 0 | superseded; no recommendations from this run were ever converted to a PO |
| `2ddf8ccd-0908-4e67-bb71-2c402a02a119` | superseded | Mon Apr 27 2026 10:54:14 GMT+0300 (שעון ישראל (קיץ)) | ffff0003-0000-0000-0000-000000000b01 | manual | 0 | superseded; no recommendations from this run were ever converted to a PO |
| `478ebd27-9546-4ec8-bce7-b6c6a5892316` | superseded | Sun Apr 26 2026 16:32:52 GMT+0300 (שעון ישראל (קיץ)) | ffff0002-0000-0000-0000-000000000e01 | manual | 0 | superseded; no recommendations from this run were ever converted to a PO |
| `bcdc45a2-1ef6-4988-9658-38b464023b4f` | superseded | Sun Apr 26 2026 16:32:51 GMT+0300 (שעון ישראל (קיץ)) | ffff0002-0000-0000-0000-000000000e01 | manual | 0 | superseded; no recommendations from this run were ever converted to a PO |
| `423ec65c-d814-45a1-9762-e91f2bf9ffed` | superseded | Sun Apr 26 2026 16:32:51 GMT+0300 (שעון ישראל (קיץ)) | ffff0002-0000-0000-0000-000000000e01 | manual | 0 | superseded; no recommendations from this run were ever converted to a PO |
| `22a613ca-eda9-43ee-8d43-cd5f79770cf1` | superseded | Sun Apr 26 2026 16:32:51 GMT+0300 (שעון ישראל (קיץ)) | ffff0002-0000-0000-0000-000000000e01 | manual | 0 | superseded; no recommendations from this run were ever converted to a PO |
| `dcf47793-45fa-4ba0-8320-669d68cecac5` | superseded | Sun Apr 26 2026 16:28:25 GMT+0300 (שעון ישראל (קיץ)) | ffff0002-0000-0000-0000-000000000e01 | manual | 0 | superseded; no recommendations from this run were ever converted to a PO |
| `6b22623a-a99a-4d7c-8655-eb3e4428f0f2` | superseded | Sun Apr 26 2026 16:28:25 GMT+0300 (שעון ישראל (קיץ)) | ffff0002-0000-0000-0000-000000000e01 | manual | 0 | superseded; no recommendations from this run were ever converted to a PO |
| `702ce557-755a-43ec-96b2-efc6308a5688` | superseded | Sun Apr 26 2026 16:28:25 GMT+0300 (שעון ישראל (קיץ)) | ffff0002-0000-0000-0000-000000000e01 | manual | 0 | superseded; no recommendations from this run were ever converted to a PO |
| `6045ed63-8031-4241-be0d-c69f7ce2dff7` | superseded | Sun Apr 26 2026 16:28:24 GMT+0300 (שעון ישראל (קיץ)) | ffff0002-0000-0000-0000-000000000e01 | manual | 0 | superseded; no recommendations from this run were ever converted to a PO |
| `96bb5dde-866c-48a2-aedb-6f45a6d2d5ed` | running | Sun Apr 26 2026 15:10:45 GMT+0300 (שעון ישראל (קיץ)) | eeeeeeee-0000-0000-0000-00000000e001 | manual | 0 | still running (may be stale); no recommendations from this run were ever converted to a PO |
| `ae90162c-3789-4a7a-b2ca-9b00b2f74c93` | running | Sun Apr 26 2026 15:10:45 GMT+0300 (שעון ישראל (קיץ)) | eeeeeeee-0000-0000-0000-00000000e001 | manual | 0 | still running (may be stale); no recommendations from this run were ever converted to a PO |
| `2185cc87-0172-454e-b92d-d9e78a760844` | running | Sun Apr 26 2026 15:10:44 GMT+0300 (שעון ישראל (קיץ)) | eeeeeeee-0000-0000-0000-00000000e001 | manual | 1 | still running (may be stale); no recommendations from this run were ever converted to a PO |
| `7c306104-7b3b-4746-bc33-75bb2dc4ad5f` | running | Sun Apr 26 2026 15:10:44 GMT+0300 (שעון ישראל (קיץ)) | eeeeeeee-0000-0000-0000-00000000e001 | manual | 0 | still running (may be stale); no recommendations from this run were ever converted to a PO |
| `43ea604e-402f-482c-a028-469ad9df6351` | running | Sun Apr 26 2026 15:10:43 GMT+0300 (שעון ישראל (קיץ)) | eeeeeeee-0000-0000-0000-00000000e001 | manual | 0 | still running (may be stale); no recommendations from this run were ever converted to a PO |
| `3efd1536-9e94-4821-aa3d-894942aacb01` | superseded | Sun Apr 26 2026 13:37:54 GMT+0300 (שעון ישראל (קיץ)) | eeeeeeee-0000-0000-0000-000000000f01 | manual | 871 | superseded; no recommendations from this run were ever converted to a PO |
| `ca5f4df6-0861-484f-ae2f-e24b34c3397d` | superseded | Sun Apr 26 2026 13:37:53 GMT+0300 (שעון ישראל (קיץ)) | eeeeeeee-0000-0000-0000-000000000f01 | manual | 871 | superseded; no recommendations from this run were ever converted to a PO |
| `8de1f911-83d7-45fd-8ae5-b4c267f8b08e` | superseded | Sun Apr 26 2026 13:37:49 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f01 | manual | 871 | superseded; no recommendations from this run were ever converted to a PO |
| `9afa36a0-1ba9-49fd-8ae2-1589781d74b8` | superseded | Sun Apr 26 2026 13:37:47 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f02 | scheduled | 871 | superseded; no recommendations from this run were ever converted to a PO |
| `5e22998f-eb5f-429c-ade1-ddd605fb2444` | superseded | Sun Apr 26 2026 13:37:46 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f01 | manual | 871 | superseded; no recommendations from this run were ever converted to a PO |
| `fe48b5cb-08de-4e88-9aad-8fd68c0c1b55` | completed | Sun Apr 26 2026 13:37:18 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-00000000e2e1 | manual | 1 | no recommendations from this run were ever converted to a PO |
| `516c0d3d-73ff-4168-ba65-1f1db3833b8e` | superseded | Sun Apr 26 2026 13:34:54 GMT+0300 (שעון ישראל (קיץ)) | eeeeeeee-0000-0000-0000-000000000f01 | manual | 871 | superseded; no recommendations from this run were ever converted to a PO |
| `b9da5a84-bb14-4a00-98f2-5fd4662378b2` | superseded | Sun Apr 26 2026 13:34:53 GMT+0300 (שעון ישראל (קיץ)) | eeeeeeee-0000-0000-0000-000000000f01 | manual | 871 | superseded; no recommendations from this run were ever converted to a PO |
| `4bd47ca7-29e6-45ec-9539-359beb427754` | superseded | Sun Apr 26 2026 13:34:49 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f01 | manual | 871 | superseded; no recommendations from this run were ever converted to a PO |
| `ed98b8d8-894b-4300-8dac-2eae0755605d` | superseded | Sun Apr 26 2026 13:34:48 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f02 | scheduled | 871 | superseded; no recommendations from this run were ever converted to a PO |
| `e7753259-e2e8-4a74-a128-45bf20068c39` | superseded | Sun Apr 26 2026 13:34:46 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f01 | manual | 871 | superseded; no recommendations from this run were ever converted to a PO |
| `eff1fd79-c894-4fcd-ae7e-701d3e67e93c` | superseded | Sun Apr 26 2026 13:34:29 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f01 | manual | 871 | superseded; no recommendations from this run were ever converted to a PO |
| `e2474c2e-cf71-4c66-80cf-71d018f5914c` | superseded | Sun Apr 26 2026 13:34:28 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f02 | scheduled | 871 | superseded; no recommendations from this run were ever converted to a PO |
| `9705afa8-2646-4746-bbd0-f11fdb1b6999` | superseded | Sun Apr 26 2026 13:34:25 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f01 | manual | 871 | superseded; no recommendations from this run were ever converted to a PO |
| `427eee6c-1293-4ce8-92f3-6459896b7209` | completed | Sun Apr 26 2026 13:34:18 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-00000000e2e1 | manual | 1 | no recommendations from this run were ever converted to a PO |
| `d59f4f53-e5b3-47cb-a645-563e79446c2e` | completed | Sun Apr 26 2026 13:32:59 GMT+0300 (שעון ישראל (קיץ)) | eeeeeeee-0000-0000-0000-000000000001 | manual | 0 | no recommendations from this run were ever converted to a PO |
| `df5e3460-16a8-4036-81c3-cf9f5a76da05` | completed | Sun Apr 26 2026 13:30:50 GMT+0300 (שעון ישראל (קיץ)) | eeeeeeee-0000-0000-0000-000000000001 | manual | 0 | no recommendations from this run were ever converted to a PO |
| `a960a0f3-33d8-48c9-9221-fc1de1fe0d92` | superseded | Fri Apr 24 2026 14:30:48 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f01 | manual | 320 | superseded; no recommendations from this run were ever converted to a PO |
| `c3a44e16-a186-45cf-91c8-35fd943c04a3` | superseded | Fri Apr 24 2026 14:30:46 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f02 | scheduled | 320 | superseded; no recommendations from this run were ever converted to a PO |
| `9d77c7c7-965d-4a9b-b406-d39a13583dfc` | superseded | Fri Apr 24 2026 14:30:45 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f01 | manual | 320 | superseded; no recommendations from this run were ever converted to a PO |
| `c9469cea-1139-4256-b2ec-61844ca8d324` | superseded | Fri Apr 24 2026 14:28:46 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f01 | manual | 320 | superseded; no recommendations from this run were ever converted to a PO |
| `6e8c8dc7-150d-4d86-a80e-a75257e79f53` | superseded | Fri Apr 24 2026 14:28:45 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f02 | scheduled | 320 | superseded; no recommendations from this run were ever converted to a PO |
| `3892ca02-e7eb-4060-930f-daa0b7344c26` | superseded | Fri Apr 24 2026 14:28:44 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f01 | manual | 320 | superseded; no recommendations from this run were ever converted to a PO |
| `93545163-617e-487d-9816-b2f545fbd1e7` | superseded | Fri Apr 24 2026 14:27:04 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f01 | manual | 320 | superseded; no recommendations from this run were ever converted to a PO |
| `b9f0e693-0986-449f-81b9-fef4d9650ed3` | superseded | Fri Apr 24 2026 14:27:02 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f02 | scheduled | 320 | superseded; no recommendations from this run were ever converted to a PO |
| `9cdd4fb7-9c90-4ac7-a2bf-67769bee2b63` | superseded | Fri Apr 24 2026 14:27:01 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f01 | manual | 320 | superseded; no recommendations from this run were ever converted to a PO |
| `7d785483-0fa9-41e6-bc91-73f66a7f8195` | superseded | Fri Apr 24 2026 14:26:47 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f01 | manual | 320 | superseded; no recommendations from this run were ever converted to a PO |
| `c49240c9-3ec3-432f-a597-00296dfdfbae` | superseded | Fri Apr 24 2026 14:26:46 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f02 | scheduled | 320 | superseded; no recommendations from this run were ever converted to a PO |
| `e631223a-f47a-4404-8bfd-f1c5e5f5c174` | superseded | Fri Apr 24 2026 14:26:44 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f01 | manual | 320 | superseded; no recommendations from this run were ever converted to a PO |
| `e498a9b6-0e3c-40ff-b34e-fb21b7b218e9` | completed | Thu Apr 23 2026 22:35:12 GMT+0300 (שעון ישראל (קיץ)) | tom@gteveryday.com | manual | 320 | no recommendations from this run were ever converted to a PO |
| `ac37edec-4978-4124-8787-bf98a6cfdb5f` | completed | Thu Apr 23 2026 22:21:54 GMT+0300 (שעון ישראל (קיץ)) | eeeeeeee-0000-0000-0000-000000000001 | manual | 0 | no recommendations from this run were ever converted to a PO |
| `0b53afb8-2687-4074-86e3-f1648fd07394` | completed | Thu Apr 23 2026 09:45:32 GMT+0300 (שעון ישראל (קיץ)) | tom@gteveryday.com | manual | 0 | no recommendations from this run were ever converted to a PO |
| `9d1ce324-d266-4f8f-bf62-377f505ba93a` | completed | Wed Apr 22 2026 01:17:01 GMT+0300 (שעון ישראל (קיץ)) | eeeeeeee-0000-0000-0000-000000000001 | manual | 0 | no recommendations from this run were ever converted to a PO |
| `c25e8b78-d8e6-4d0f-b32a-6c45924cd1a4` | completed | Wed Apr 22 2026 01:15:52 GMT+0300 (שעון ישראל (קיץ)) | eeeeeeee-0000-0000-0000-000000000001 | manual | 0 | no recommendations from this run were ever converted to a PO |
| `208ec24f-8d05-4561-9058-246cbb019d76` | completed | Wed Apr 22 2026 01:14:40 GMT+0300 (שעון ישראל (קיץ)) | eeeeeeee-0000-0000-0000-000000000001 | manual | 0 | no recommendations from this run were ever converted to a PO |
| `7c3772b9-ca59-40b3-862f-9da41fc965f5` | superseded | Tue Apr 21 2026 14:48:01 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f01 | manual | 240 | superseded; no recommendations from this run were ever converted to a PO |
| `3995b09e-1aeb-4167-b3fb-6e73710cb28f` | superseded | Tue Apr 21 2026 14:48:00 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f02 | scheduled | 240 | superseded; no recommendations from this run were ever converted to a PO |
| `283ef679-dbef-4d63-b7ba-c09017448078` | superseded | Tue Apr 21 2026 14:47:58 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f01 | manual | 240 | superseded; no recommendations from this run were ever converted to a PO |
| `0eae9fa0-61e3-4ff5-83b9-566d38d953da` | superseded | Tue Apr 21 2026 14:47:58 GMT+0300 (שעון ישראל (קיץ)) | eeeeeeee-0000-0000-0000-000000000f01 | manual | 240 | superseded; no recommendations from this run were ever converted to a PO |
| `25a3c7ce-4cc8-47d3-89f1-b3df55c6e230` | superseded | Tue Apr 21 2026 14:47:58 GMT+0300 (שעון ישראל (קיץ)) | eeeeeeee-0000-0000-0000-000000000f01 | manual | 240 | superseded; no recommendations from this run were ever converted to a PO |
| `41707614-ccca-4e4f-ae16-bb557f8c04e8` | superseded | Tue Apr 21 2026 14:45:41 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f01 | manual | 240 | superseded; no recommendations from this run were ever converted to a PO |
| `0d6b7f32-1231-4f45-8de2-18853680974f` | superseded | Tue Apr 21 2026 14:45:40 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f02 | scheduled | 240 | superseded; no recommendations from this run were ever converted to a PO |
| `1909c0f0-10f4-4ec2-aaac-03a849ea30f8` | superseded | Tue Apr 21 2026 14:45:39 GMT+0300 (שעון ישראל (קיץ)) | eeeeeeee-0000-0000-0000-000000000f01 | manual | 240 | superseded; no recommendations from this run were ever converted to a PO |
| `40d1ba06-8c33-4de2-b579-01a52aa385cd` | superseded | Tue Apr 21 2026 14:45:39 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f01 | manual | 240 | superseded; no recommendations from this run were ever converted to a PO |
| `d29eb7da-8dfd-471b-bead-c7c290c1ac5a` | superseded | Tue Apr 21 2026 14:45:38 GMT+0300 (שעון ישראל (קיץ)) | eeeeeeee-0000-0000-0000-000000000f01 | manual | 240 | superseded; no recommendations from this run were ever converted to a PO |
| `fbeb406a-5e9d-46bb-8141-448a0acf43b6` | completed | Sun Apr 19 2026 09:45:20 GMT+0300 (שעון ישראל (קיץ)) | 00000000-0000-0000-0000-00000000be91 | manual | 0 | no recommendations from this run were ever converted to a PO |
| `8dadb40a-032c-4c7f-9d78-80aaf4916b85` | completed | Sun Apr 19 2026 09:43:59 GMT+0300 (שעון ישראל (קיץ)) | 00000000-0000-0000-0000-00000000be91 | manual | 0 | no recommendations from this run were ever converted to a PO |
| `8307168f-0b31-4321-a8cb-6b8a97dde6ed` | superseded | Sun Apr 19 2026 08:31:25 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f01 | manual | 200 | superseded; no recommendations from this run were ever converted to a PO |
| `9a3b32a5-93cc-4345-be20-33d8fa2a729a` | superseded | Sun Apr 19 2026 08:31:24 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f02 | scheduled | 200 | superseded; no recommendations from this run were ever converted to a PO |
| `93a733af-15d7-4a44-a0bf-13001d865d6c` | superseded | Sun Apr 19 2026 08:31:23 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f01 | manual | 200 | superseded; no recommendations from this run were ever converted to a PO |
| `213c4dee-1c8e-4e41-a24c-a001a3bb3a52` | superseded | Sun Apr 19 2026 08:05:14 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f01 | manual | 200 | superseded; no recommendations from this run were ever converted to a PO |
| `eda66279-9485-4561-b3ad-b188b8591466` | superseded | Sun Apr 19 2026 08:05:13 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f02 | scheduled | 200 | superseded; no recommendations from this run were ever converted to a PO |
| `4ab00bef-9b36-4371-b374-7db32204b0bd` | superseded | Sun Apr 19 2026 08:05:12 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f01 | manual | 200 | superseded; no recommendations from this run were ever converted to a PO |
| `c1cdec63-7fe8-4b75-85ee-95adfaa3a4ef` | superseded | Sun Apr 19 2026 08:05:12 GMT+0300 (שעון ישראל (קיץ)) | eeeeeeee-0000-0000-0000-000000000f01 | manual | 200 | superseded; no recommendations from this run were ever converted to a PO |
| `18c02b3a-953a-4350-8adb-ebedc11ef539` | superseded | Sun Apr 19 2026 08:05:12 GMT+0300 (שעון ישראל (קיץ)) | eeeeeeee-0000-0000-0000-000000000f01 | manual | 200 | superseded; no recommendations from this run were ever converted to a PO |
| `ad2cab7d-aab9-499b-b8d3-a8b7c94388b2` | superseded | Sun Apr 19 2026 08:05:03 GMT+0300 (שעון ישראל (קיץ)) | eeeeeeee-0000-0000-0000-000000000f01 | manual | 200 | superseded; no recommendations from this run were ever converted to a PO |
| `85f86493-bffc-4448-96ee-093f68e93b31` | superseded | Sun Apr 19 2026 08:05:03 GMT+0300 (שעון ישראל (קיץ)) | eeeeeeee-0000-0000-0000-000000000f01 | manual | 200 | superseded; no recommendations from this run were ever converted to a PO |
| `94229ec9-4b5c-4c2b-a18e-942c2f7e255e` | superseded | Sun Apr 19 2026 08:04:14 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f01 | manual | 200 | superseded; no recommendations from this run were ever converted to a PO |
| `feae913b-238c-4f3f-b97b-7089e1a80262` | superseded | Sun Apr 19 2026 08:04:13 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f02 | scheduled | 200 | superseded; no recommendations from this run were ever converted to a PO |
| `54367adc-43a5-4ba9-9d96-01bdb60b9e08` | superseded | Sun Apr 19 2026 08:04:12 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f01 | manual | 200 | superseded; no recommendations from this run were ever converted to a PO |
| `9d729aae-0baa-4db9-b924-1ada3d8bbebc` | superseded | Sun Apr 19 2026 08:03:53 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f01 | manual | 200 | superseded; no recommendations from this run were ever converted to a PO |
| `99a76459-56d9-43f1-b1d0-9d164da07c48` | superseded | Sun Apr 19 2026 08:03:52 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f02 | scheduled | 200 | superseded; no recommendations from this run were ever converted to a PO |
| `4a205ac7-44ff-4f98-bd42-834512f83c99` | superseded | Sun Apr 19 2026 08:03:51 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f01 | manual | 200 | superseded; no recommendations from this run were ever converted to a PO |
| `fff4c144-5908-48e4-a2eb-135a47d84155` | superseded | Sun Apr 19 2026 08:03:43 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f01 | manual | 200 | superseded; no recommendations from this run were ever converted to a PO |
| `34160aa5-bad3-497a-904b-1a0338d6a760` | superseded | Sun Apr 19 2026 08:03:42 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f02 | scheduled | 200 | superseded; no recommendations from this run were ever converted to a PO |
| `18bafa9e-ebd6-4e05-b126-fce3695acce3` | superseded | Sun Apr 19 2026 08:03:41 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f01 | manual | 200 | superseded; no recommendations from this run were ever converted to a PO |
| `5d8a5875-4355-4979-bb86-c81961c73f23` | superseded | Sun Apr 19 2026 08:02:41 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f01 | manual | 200 | superseded; no recommendations from this run were ever converted to a PO |
| `b617329c-7f33-43cb-8426-ff68107375bb` | superseded | Sun Apr 19 2026 08:02:40 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f02 | scheduled | 200 | superseded; no recommendations from this run were ever converted to a PO |
| `6adac287-7bca-4bcf-98ca-4b8eb2edc20a` | superseded | Sun Apr 19 2026 08:02:39 GMT+0300 (שעון ישראל (קיץ)) | dddddddd-0000-0000-0000-000000000f01 | manual | 200 | superseded; no recommendations from this run were ever converted to a PO |

## 2. planning_run_recommendations

Total: **23244**.

### Per-status

| Status | Count |
|---|---|
| draft | 23220 |
| approved | 24 |

### Per-type

| Type | Count |
|---|---|
| production | 16195 |
| purchase | 7049 |

### Per type x status

| Type | Status | Count |
|---|---|---|
| production | draft | 16195 |
| purchase | approved | 24 |
| purchase | draft | 7025 |

### Recommendations CONVERTED to PO (REAL — must not be deleted)

| recommendation_id | run_id | status | type | item_id | qty | converted_to_po_id | approved_by |
|---|---|---|---|---|---|---|---|
| `2080ebc0-2d65-4a96-ac08-c4b39afb0d30` | `ee2d6847-3d35-47ca-8f56-e65b8223e19b` | approved | purchase | COMP-POC-1777199711907 | 10.00000000 | PO-2026-00106 |  |
| `de5ae691-2f12-48b0-8f5b-8ad0f509b5f2` | `ee2d6847-3d35-47ca-8f56-e65b8223e19b` | approved | purchase | COMP-POC-1777199711907 | 5.00000000 | PO-2026-00107 |  |
| `3b3fde3f-eecc-4728-85be-9ebf53a22719` | `71007303-e8fc-436f-afd6-7f8ef80590e5` | approved | purchase | COMP-GRR-1777199716223 | 100.00000000 | PO-2026-00111 |  |
| `f104bfd8-f03b-4037-89b5-226ef0e92784` | `076ae8b1-bdf3-4b13-a6ba-acb6a308a878` | approved | purchase | COMP-POH-1777199722022 | 12.00000000 | PO-2026-00112 |  |
| `6930bef9-258c-49b9-89bb-f21739b5466c` | `17ca6b4b-8a7d-4f54-98ac-04643d43a376` | approved | purchase | COMP-LCC-1777199726175 | 50.00000000 | PO-2026-00113 |  |
| `1804fe02-b8c5-4307-9d3b-eb0caf16c1b5` | `17ca6b4b-8a7d-4f54-98ac-04643d43a376` | approved | purchase | COMP-LCC-1777199726175 | 100.00000000 | PO-2026-00114 |  |
| `a2993d33-7cee-4769-89b4-69c9dda99351` | `17ca6b4b-8a7d-4f54-98ac-04643d43a376` | approved | purchase | COMP-LCC-1777199726175 | 20.00000000 | PO-2026-00115 |  |
| `e8ef6cdb-5cc9-4f48-86a8-8380b845f6b9` | `a6b8cd29-f8bb-4e7f-b706-ce2d2202e5fa` | approved | purchase | COMP-LU-1777199731523 | 100.00000000 | PO-2026-00116 |  |
| `649d28e4-78f4-4479-b75a-ee1d5de31cdd` | `1d9016e3-a3b0-4c3b-af5f-99dc7ebe93a3` | approved | purchase | COMP-POL-1777199736895 | 25.00000000 | PO-2026-00117 |  |
| `5576b35d-d2e8-44d4-b696-651d433c39b3` | `851150ce-da96-4875-8c5c-754eea50d8e2` | approved | purchase | COMP-POC-1777199890616 | 10.00000000 | PO-2026-00126 |  |
| `2bdbc051-f9e5-411a-bf90-37d8ddafa46f` | `851150ce-da96-4875-8c5c-754eea50d8e2` | approved | purchase | COMP-POC-1777199890616 | 5.00000000 | PO-2026-00127 |  |
| `8662745a-d871-44bf-b775-bb07c162e45b` | `9df67cc4-d13c-4b3e-b244-e7b69b6daeae` | approved | purchase | COMP-GRR-1777199894888 | 100.00000000 | PO-2026-00128 |  |
| `f80c1f42-13ba-4485-a804-ad6afefc5dde` | `243f635c-708d-4014-891d-0872dbc2b820` | approved | purchase | COMP-POH-1777199900501 | 12.00000000 | PO-2026-00129 |  |
| `b85c5ec8-791b-4cff-8b9d-80c42b4585b6` | `3f78bc5c-c1fd-47ed-859b-e757130ea727` | approved | purchase | COMP-LCC-1777199905261 | 50.00000000 | PO-2026-00130 |  |
| `518203a1-44d5-441b-a160-44b4449c06c1` | `3f78bc5c-c1fd-47ed-859b-e757130ea727` | approved | purchase | COMP-LCC-1777199905261 | 100.00000000 | PO-2026-00131 |  |
| `9dfde139-1025-4132-98db-7aa0fb66abdf` | `3f78bc5c-c1fd-47ed-859b-e757130ea727` | approved | purchase | COMP-LCC-1777199905261 | 20.00000000 | PO-2026-00132 |  |
| `9e0c746d-0ec1-43da-83f9-eb01a9595e40` | `86b6c568-d7a0-478e-b721-744bded2e51a` | approved | purchase | COMP-LU-1777199910957 | 100.00000000 | PO-2026-00133 |  |
| `60e50db7-8bdc-4d19-b405-39c3673e7a43` | `2ed66109-068e-46cd-b0cd-d9517556e3fe` | approved | purchase | COMP-POL-1777199916078 | 25.00000000 | PO-2026-00134 |  |
| `37fb2cb4-aa0e-47b3-9efe-73a4a6ad2435` | `e488b4c5-f43c-4b73-8e85-e92f728820a0` | approved | purchase | COMP-POH-1777707952903 | 12.00000000 | PO-2026-00152 |  |
| `8409cdf8-827a-4b2a-9a38-9183d3737e08` | `504385bf-3fa8-45e6-9b46-fdc0926d0533` | approved | purchase | COMP-POL-1777707952974 | 25.00000000 | PO-2026-00153 |  |
| `5be452f5-6f48-493e-8f32-4c7596ed3e22` | `45d5887b-29f5-477d-b2f6-91b7a3ae52cc` | approved | purchase | COMP-POC-1777707953056 | 10.00000000 | PO-2026-00154 |  |
| `f41ed88d-b1bc-4581-ae0f-1673652264d5` | `45d5887b-29f5-477d-b2f6-91b7a3ae52cc` | approved | purchase | COMP-POC-1777707953056 | 5.00000000 | PO-2026-00155 |  |

### Recommendations APPROVED but NOT YET converted (2)

| recommendation_id | run_id | type | item_id/component_id | qty | approved_at | approved_by |
|---|---|---|---|---|---|---|
| `b4c6aa50-c3fe-4086-a8a0-3f3952f458c4` | `fe48b5cb-08de-4e88-9aad-8fd68c0c1b55` | purchase | COMP-E2E-1777199837665 | 10.00000000 | Sun Apr 26 2026 13:37:18 GMT+0300 (שעון ישראל (קיץ)) |  |
| `cf762970-8438-4550-bbcd-33138cd1b85e` | `427eee6c-1293-4ce8-92f3-6459896b7209` | purchase | COMP-E2E-1777199656857 | 10.00000000 | Sun Apr 26 2026 13:34:18 GMT+0300 (שעון ישראל (קיץ)) |  |

## 3. planning_run_exceptions

Total: **2756**. (Append-only emission log; no `open/closed` status. Cascade-DELETE on parent run.)

### Per-category

| Category | Count |
|---|---|
| missing_supplier_mapping | 2378 |
| missing_bom | 353 |
| po_substrate_absent_supply_not_netted | 22 |
| impossible_lead_time | 2 |
| recommendation_below_trigger_threshold | 1 |

### Per-severity

| Severity | Count |
|---|---|
| warning | 2755 |
| info | 1 |

## 4. production_plan

Total: **1**. DELETE-CANDIDATE: **0**. SUSPECT: **1**.

### T3A test plan check (`875718c3-a95a-4e69-a158-a1fc8f868bd0`)

Confirmed gone from `production_plan`. 

### Per-status

| Status | Count |
|---|---|
| planned | 1 |

### Per-row classification

| plan_id | plan_date | item_id | qty | status | source_rec | created_by | classification | reasons |
|---|---|---|---|---|---|---|---|---|
| `9fff1835-c29d-4301-937b-99caa5a0d79a` | Sun Apr 26 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FG-DET-1L-NS | 500.00000000 | planned | (null) | tom@gteveryday.com | SUSPECT | hand-authored by real user; pre-launch — confirm before delete |

## 5. production_actual

Total: **0**. DELETE-CANDIDATE: **0**. SUSPECT: **0**.

> **Notable:** the table is **empty**, yet `stock_ledger` contains 78 `production_output` rows, 17 `production_scrap` rows, and 662 `production_consumption` rows from prior submissions. The parent submission rows have already been deleted (or never written) but their CONSUME deltas remain in the append-only ledger. This matches CURRENT_STATE.md: "all prior production_consumption rows were synthetic test data". Cleanup of the actuals table itself is therefore already complete; only the orphan ledger rows remain.

## 6. stock_ledger production_* rows (append-only — cannot be deleted)

The ledger is append-only. Every CONSUME / OUTPUT / SCRAP row written by a (now-removed) test production_actual submission remains historical and cannot be DELETEd. Use a documented anchor reset to realign stock truth if cleanup leaves drift.

| movement_type | Count | First event_at | Last event_at |
|---|---|---|---|
| production_consumption | 662 | Tue Apr 21 2026 19:46:22 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:27:42 GMT+0300 (שעון ישראל (קיץ)) |
| production_output | 78 | Tue Apr 21 2026 19:46:22 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:27:42 GMT+0300 (שעון ישראל (קיץ)) |
| production_scrap | 17 | Tue Apr 21 2026 19:46:22 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:26:08 GMT+0300 (שעון ישראל (קיץ)) |

### CONSUME rows pre vs post 2026-05-02

| Bucket | Count |
|---|---|
| post_two_head_fix | 550 |
| pre_two_head_fix | 112 |

### Orphan production_output rows: **78**

(production_output ledger rows whose parent submission no longer exists in production_actual.)

## 7. FK dependencies (cascade safety)

### FKs referencing planning_runs

| Dependent table | Column | delete_rule |
|---|---|---|
| private_core.planning_run_component_demand | run_id | CASCADE |
| private_core.planning_run_component_netting | run_id | CASCADE |
| private_core.planning_run_exceptions | run_id | CASCADE |
| private_core.planning_run_fg_coverage | run_id | CASCADE |
| private_core.planning_run_inputs | run_id | CASCADE |
| private_core.planning_run_recommendations | run_id | CASCADE |
| private_core.planning_runs | supersedes_run_id | NO ACTION |
| private_core.purchase_orders | source_run_id | SET NULL |

### FKs referencing planning_run_recommendations

| Dependent table | Column | delete_rule |
|---|---|---|
| private_core.production_plan | source_recommendation_id | SET NULL |
| private_core.purchase_order_lines | source_recommendation_id | SET NULL |
| private_core.purchase_orders | source_recommendation_id | SET NULL |

### FKs referencing production_plan

No incoming FKs found.

### FKs referencing production_actual

| Dependent table | Column | delete_rule |
|---|---|---|
| private_core.production_plan | completed_submission_id | SET NULL |

## 8. Users seen across planning artifacts

| Email | Name | id | classification |
|---|---|---|---|
| (null) |  | `` | unknown_user |
| (null) |  | `` | unknown_user |
| (null) |  | `` | unknown_user |
| (null) |  | `` | unknown_user |
| (null) |  | `` | unknown_user |
| (null) |  | `` | unknown_user |
| (null) |  | `` | unknown_user |
| (null) |  | `` | unknown_user |
| (null) |  | `` | unknown_user |
| (null) |  | `` | unknown_user |
| (null) |  | `` | unknown_user |
| (null) |  | `` | unknown_user |
| (null) |  | `` | unknown_user |
| (null) |  | `` | unknown_user |
| (null) |  | `` | unknown_user |
| (null) |  | `` | unknown_user |
| (null) |  | `` | unknown_user |
| tom@gteveryday.com |  | `0db008a9-05e3-4521-8b30-42e5d444818d` | REAL_USER |

### PO provenance (context)

| provenance | n |
|---|---|
| manual_or_other | 38 |
| from_run | 24 |

## 9. Actionable cleanup list

### A. SAFE to delete first (no PO/plan/actual blockers)

1. `planning_runs` SUSPECT and safely cascade-deletable — **97 of 97** runs:
   - Cascade will remove: planning_run_recommendations (CASCADE), planning_run_exceptions (CASCADE), planning_run_inputs (CASCADE), planning_run_component_demand (CASCADE), planning_run_component_netting (CASCADE), planning_run_fg_coverage (CASCADE).
   - purchase_orders.source_run_id is SET NULL on parent delete (so no real POs are dropped).
   - First 10 ids:
     - `5ac2f109-5e07-42d4-8323-161ca35e3ffa` (completed, executed_at=Sat May 02 2026 09:21:24 GMT+0300 (שעון ישראל (קיץ)))
     - `7664bed4-fc24-4e71-b2fe-1cd8790009b5` (superseded, executed_at=Sat May 02 2026 00:56:42 GMT+0300 (שעון ישראל (קיץ)))
     - `b53bec68-7b99-4a6f-9c14-be61a136c612` (superseded, executed_at=Sat May 02 2026 00:56:42 GMT+0300 (שעון ישראל (קיץ)))
     - `1cc92fe6-078e-4cb0-9a58-869d69e00141` (superseded, executed_at=Sat May 02 2026 00:56:42 GMT+0300 (שעון ישראל (קיץ)))
     - `e5aff903-12aa-472c-907a-187849188594` (superseded, executed_at=Sat May 02 2026 00:56:41 GMT+0300 (שעון ישראל (קיץ)))
     - `52171abf-de08-4025-ac60-a8d3bb45d38b` (superseded, executed_at=Sat May 02 2026 00:56:41 GMT+0300 (שעון ישראל (קיץ)))
     - `57e8f757-5c31-4fdf-b192-78131dfefd78` (superseded, executed_at=Sat May 02 2026 00:55:26 GMT+0300 (שעון ישראל (קיץ)))
     - `29206228-fa53-4ddc-9454-cf7b5ba45abd` (superseded, executed_at=Sat May 02 2026 00:55:26 GMT+0300 (שעון ישראל (קיץ)))
     - `db5d0c9e-abbd-4248-95f6-9f88c5d254f4` (superseded, executed_at=Sat May 02 2026 00:55:25 GMT+0300 (שעון ישראל (קיץ)))
     - `ba42fa16-2de7-4654-862f-d60efcbd6517` (superseded, executed_at=Sat May 02 2026 00:55:25 GMT+0300 (שעון ישראל (קיץ)))
     - …and 87 more — full list in section 1.

2. `production_actual` rows DELETE-CANDIDATE — **0** row(s).
   (Already clean — production_actual has 0 rows.)

3. `production_plan` rows DELETE-CANDIDATE — **0** row(s).

### B. SUSPECT (review before delete)

- `planning_runs` SUSPECT: 97. Of these, 97 are safely cascade-deletable; the rest depend on a recommendation that is referenced by a production_plan.
- `production_plan` SUSPECT: 1.
- `production_actual` SUSPECT: 0.

### C. CANNOT delete (append-only)

- `stock_ledger` rows of movement_type `production_consumption` (662), `production_output` (78), `production_scrap` (17). All from prior synthetic submissions. Their parent production_actual rows are already gone (table empty); the ledger artifacts remain forever.
- `change_log` rows referencing the T3A test plan_id (? rows) — inert audit history.

### D. Cascade safety reminders

- Before deleting a planning_runs row: planning_run_recommendations / inputs / demand / netting / fg_coverage / exceptions cascade. purchase_orders.source_run_id SET NULL.
- Before deleting a planning_run_recommendations row: production_plan.source_recommendation_id SET NULL; purchase_orders.source_recommendation_id SET NULL; purchase_order_lines.source_recommendation_id SET NULL.
- Before deleting a production_plan row: production_actual.from_plan_id (does not exist as FK in current schema; reference is via production_plan.completed_submission_id → production_actual.submission_id, SET NULL).
- Before deleting a production_actual row: production_plan.completed_submission_id SET NULL.
- The 22 converted-to-PO recommendations (PO-2026-00106..00155) are inside the 17 REAL planning_runs listed in section 1 — do **not** include those run_ids in any cleanup batch.
