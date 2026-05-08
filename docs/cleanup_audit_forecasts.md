# Cleanup Audit — Fake / Test Forecasts

Generated: 2026-05-02T17:23:06.738Z
Scope: `private_core.forecast_versions` + `private_core.forecast_lines` (read-only)

## Headline

- Total `forecast_versions`: **510**
- Total `forecast_lines`: **30728**
- Distinct items represented: 82
- Bucket horizon: Sun Apr 12 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) → Mon Sep 06 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ))
- qty range: min=0.00000000, max=2000.00000000, avg=2.1463811507419943
- Suspect versions: **506** of 510
- Real-candidate versions: 4

## Status distribution

| status | count |
|---|---|
| discarded | 415 |
| draft | 7 |
| published | 77 |
| superseded | 11 |

## Currently published forecast_versions

| version_id | cadence | horizon_start | published_at | published_by | notes |
|---|---|---|---|---|---|
| `d3122b1e-8376-470c-b761-1be290353ebc` | monthly | Sun Nov 01 2026 00:00:00 GMT+0200 (שעון ישראל (חורף)) | Sat May 02 2026 18:39:29 GMT+0300 (שעון ישראל (קיץ)) | FCM planner | FCM-TEST-Chunk3 |
| `c8b49e39-cd32-44d3-b739-0474e8b6b321` | monthly | Thu Oct 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 18:39:28 GMT+0300 (שעון ישראל (קיץ)) | FCM planner | FCM-TEST-Chunk3 |
| `3bc3ae80-c72d-4d8f-b6d1-d33285403e3b` | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 18:39:27 GMT+0300 (שעון ישראל (קיץ)) | FCM planner | FCM-TEST-Chunk3 |
| `d1414cab-e9df-4469-b664-12ebb94caa5d` | weekly | Mon Jun 08 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 18:39:17 GMT+0300 (שעון ישראל (קיץ)) | FCM weekly fixture | FCM-TEST-weekly-regression |
| `a82259cf-ac46-417b-9cc7-1ef81177d382` | monthly | Sun Apr 26 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:53:11 GMT+0300 (שעון ישראל (קיץ)) | Test admin |  |
| `c51f3502-59da-4620-aa07-08e21df417fd` | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:51:32 GMT+0300 (שעון ישראל (קיץ)) | Test planner | FC-TEST-seed |
| `cd6306fe-d52b-4917-b67a-26a25da096a9` | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:50:44 GMT+0300 (שעון ישראל (קיץ)) | Test planner | FC-TEST-seed |
| `95322bb2-a55d-49c4-af30-426a526ae19b` | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:50:40 GMT+0300 (שעון ישראל (קיץ)) | FCSEED T6 publish | FCSEED-TEST-seed |
| `d93de89e-239f-4c75-8f08-f0f83538d509` | monthly | Mon Jun 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:50:18 GMT+0300 (שעון ישראל (קיץ)) | parity-1777733417728 |  |
| `ef6db32d-8d2c-48eb-94fd-73c672defe4b` | monthly | Sun Nov 01 2026 00:00:00 GMT+0200 (שעון ישראל (חורף)) | Sat May 02 2026 17:50:11 GMT+0300 (שעון ישראל (קיץ)) | FCM planner | FCM-TEST-Chunk3 |
| `cd54f93d-3c1e-4d59-ad3c-d478381a7e7e` | monthly | Thu Oct 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:50:09 GMT+0300 (שעון ישראל (קיץ)) | FCM planner | FCM-TEST-Chunk3 |
| `250220d8-d673-4dfa-963f-10d623791810` | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:50:08 GMT+0300 (שעון ישראל (קיץ)) | FCM planner | FCM-TEST-Chunk3 |
| `30526c20-8b6d-4456-a44b-75fac7e820b2` | weekly | Mon Jun 08 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:49:56 GMT+0300 (שעון ישראל (קיץ)) | FCM weekly fixture | FCM-TEST-weekly-regression |
| `71cf40cc-98af-41a4-98e8-474c3f794747` | monthly | Sun Nov 01 2026 00:00:00 GMT+0200 (שעון ישראל (חורף)) | Sat May 02 2026 17:48:09 GMT+0300 (שעון ישראל (קיץ)) | FCM planner | FCM-TEST-Chunk3 |
| `f19d7a29-bbcf-4ace-830e-4e860ae4881d` | monthly | Thu Oct 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:48:07 GMT+0300 (שעון ישראל (קיץ)) | FCM planner | FCM-TEST-Chunk3 |
| `82263079-54f4-4839-91b6-1d1f8c9bd6de` | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:48:05 GMT+0300 (שעון ישראל (קיץ)) | FCM planner | FCM-TEST-Chunk3 |
| `4074e68a-56ed-4465-8984-c6132a893546` | weekly | Mon Jun 08 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:47:54 GMT+0300 (שעון ישראל (קיץ)) | FCM weekly fixture | FCM-TEST-weekly-regression |
| `c9cbb602-91bf-4e63-b5dc-711209b36eaf` | monthly | Sun Nov 01 2026 00:00:00 GMT+0200 (שעון ישראל (חורף)) | Sat May 02 2026 17:47:46 GMT+0300 (שעון ישראל (קיץ)) | FCM planner | FCM-TEST-Chunk3 |
| `cd91bab3-3537-4779-b13b-bdd50ae630db` | monthly | Thu Oct 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:47:45 GMT+0300 (שעון ישראל (קיץ)) | FCM planner | FCM-TEST-Chunk3 |
| `4902139f-8437-41a2-ba46-d2cb5ea847a3` | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:47:43 GMT+0300 (שעון ישראל (קיץ)) | FCM planner | FCM-TEST-Chunk3 |
| `39b8dcb0-b315-4ee1-8fc2-8af180bce37e` | weekly | Mon Jun 08 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:47:32 GMT+0300 (שעון ישראל (קיץ)) | FCM weekly fixture | FCM-TEST-weekly-regression |
| `e433a9fc-58c6-4c2d-8558-6e25673b3f04` | monthly | Sun Nov 01 2026 00:00:00 GMT+0200 (שעון ישראל (חורף)) | Sat May 02 2026 17:47:24 GMT+0300 (שעון ישראל (קיץ)) | FCM planner | FCM-TEST-Chunk3 |
| `e1def1d6-1347-4bd1-8796-6d4107709643` | monthly | Thu Oct 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:47:23 GMT+0300 (שעון ישראל (קיץ)) | FCM planner | FCM-TEST-Chunk3 |
| `db00590d-f916-44bf-ad93-3a8494d6ce56` | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:47:21 GMT+0300 (שעון ישראל (קיץ)) | FCM planner | FCM-TEST-Chunk3 |
| `0aee3a9b-71f6-484d-a565-e50dc7c434c3` | weekly | Mon Jun 08 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:47:09 GMT+0300 (שעון ישראל (קיץ)) | FCM weekly fixture | FCM-TEST-weekly-regression |
| `afbdbea4-bfe8-445f-b713-b76981d9d0b6` | monthly | Sun Nov 01 2026 00:00:00 GMT+0200 (שעון ישראל (חורף)) | Sat May 02 2026 17:46:42 GMT+0300 (שעון ישראל (קיץ)) | FCM planner | FCM-TEST-Chunk3 |
| `440944cb-322a-4c6e-bf73-358857ad7ee4` | monthly | Thu Oct 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:46:41 GMT+0300 (שעון ישראל (קיץ)) | FCM planner | FCM-TEST-Chunk3 |
| `a2f64133-5f85-46aa-a975-73533a8c8020` | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:46:39 GMT+0300 (שעון ישראל (קיץ)) | FCM planner | FCM-TEST-Chunk3 |
| `6d6d82f1-1eef-4edd-a737-9545c56e7eb1` | weekly | Mon Jun 08 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:46:33 GMT+0300 (שעון ישראל (קיץ)) | FCM weekly fixture | FCM-TEST-weekly-regression |
| `d70cb6b3-5f2f-4ff2-9e32-540a49ce6a4c` | monthly | Sun Nov 01 2026 00:00:00 GMT+0200 (שעון ישראל (חורף)) | Sat May 02 2026 17:46:25 GMT+0300 (שעון ישראל (קיץ)) | FCM planner | FCM-TEST-Chunk3 |
| `37cbcc4d-1c66-42d1-bd42-521b8d2bef14` | monthly | Thu Oct 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:46:24 GMT+0300 (שעון ישראל (קיץ)) | FCM planner | FCM-TEST-Chunk3 |
| `edbf350b-d2d9-432b-a35d-895414fca1af` | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:46:22 GMT+0300 (שעון ישראל (קיץ)) | FCM planner | FCM-TEST-Chunk3 |
| `07daba3c-b4ae-4b3b-bc56-b99351dc8afb` | weekly | Mon Jun 08 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:46:16 GMT+0300 (שעון ישראל (קיץ)) | FCM weekly fixture | FCM-TEST-weekly-regression |
| `f07cc43b-aab8-4b35-89a4-f87dca737f2b` | monthly | Sun Nov 01 2026 00:00:00 GMT+0200 (שעון ישראל (חורף)) | Sat May 02 2026 17:46:07 GMT+0300 (שעון ישראל (קיץ)) | FCM planner | FCM-TEST-Chunk3 |
| `b0f71d5c-94af-4cb9-9dd2-02d7228e0c1e` | monthly | Thu Oct 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:46:05 GMT+0300 (שעון ישראל (קיץ)) | FCM planner | FCM-TEST-Chunk3 |
| `412c42ef-3e79-4611-b579-cfa7bedc68f6` | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:46:04 GMT+0300 (שעון ישראל (קיץ)) | FCM planner | FCM-TEST-Chunk3 |
| `ca960ec1-b069-4f43-8a3d-49527c3cb45f` | weekly | Mon Jun 08 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:45:58 GMT+0300 (שעון ישראל (קיץ)) | FCM weekly fixture | FCM-TEST-weekly-regression |
| `07d4f6fd-dd2d-429e-b400-4c8bb6b09d52` | weekly | Mon Jun 08 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:45:31 GMT+0300 (שעון ישראל (קיץ)) | FCM weekly fixture | FCM-TEST-weekly-regression |
| `958e2280-d592-4152-84ea-b6e39754938f` | weekly | Mon Jun 08 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:45:23 GMT+0300 (שעון ישראל (קיץ)) | FCM weekly fixture | FCM-TEST-weekly-regression |
| `3fdba978-64f6-4226-aa95-48536be1fd32` | weekly | Mon Jun 08 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:45:15 GMT+0300 (שעון ישראל (קיץ)) | FCM weekly fixture | FCM-TEST-weekly-regression |
| `e7f0ff94-cf69-4b26-bfb7-c500807d5ea8` | weekly | Mon Jun 08 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:45:05 GMT+0300 (שעון ישראל (קיץ)) | FCM weekly fixture | FCM-TEST-weekly-regression |
| `8f0f59e4-63e2-4abc-ac4e-d44aa9b2d902` | monthly | Mon Jun 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:44:47 GMT+0300 (שעון ישראל (קיץ)) | parity-1777733086512 |  |
| `450c0cc0-c9af-4876-9238-dc336c45b531` | monthly | Mon Jun 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:44:08 GMT+0300 (שעון ישראל (קיץ)) | parity-1777733047761 |  |
| `ab85551b-84fb-42e0-87ad-bef145bc3297` | monthly | Mon Jun 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:43:43 GMT+0300 (שעון ישראל (קיץ)) | parity-1777733022613 |  |
| `8a558b6f-936a-4357-85e7-51fac07e2784` | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:41:19 GMT+0300 (שעון ישראל (קיץ)) | FCSEED T6 publish | FCSEED-TEST-seed |
| `d8d076ef-6b1b-40ba-96b5-34bc58186d69` | monthly | Sun Apr 26 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:40:03 GMT+0300 (שעון ישראל (קיץ)) | Test admin |  |
| `d82fe5c2-fb6e-4045-9448-cfcbb04cac6d` | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:38:28 GMT+0300 (שעון ישראל (קיץ)) | Test planner | FC-TEST-seed |
| `f6291347-13f2-4fd9-afb6-b3c30636e441` | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:37:42 GMT+0300 (שעון ישראל (קיץ)) | Test planner | FC-TEST-seed |
| `2d925797-c3fa-486a-9f00-b62e27a8c9c1` | monthly | Sun Apr 26 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:37:00 GMT+0300 (שעון ישראל (קיץ)) | Test admin |  |
| `08698d0b-daa9-40aa-8a8d-71a43902c9ec` | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:35:25 GMT+0300 (שעון ישראל (קיץ)) | Test planner | FC-TEST-seed |
| `f00ce4de-a54e-46b6-b5bd-a3c27d24de0e` | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:34:40 GMT+0300 (שעון ישראל (קיץ)) | Test planner | FC-TEST-seed |
| `1134ef58-0640-4970-a53f-07590c2cbde1` | monthly | Sun Apr 26 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:34:25 GMT+0300 (שעון ישראל (קיץ)) | Test admin |  |
| `29a17eca-9773-4255-b971-adf08e1ca906` | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:32:48 GMT+0300 (שעון ישראל (קיץ)) | Test planner | FC-TEST-seed |
| `2bb2308f-91ea-43e4-83d4-37ea0cd2162e` | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:32:02 GMT+0300 (שעון ישראל (קיץ)) | Test planner | FC-TEST-seed |
| `0891e49a-cd2c-4e9b-bc0d-ac14628cfc9d` | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 17:28:16 GMT+0300 (שעון ישראל (קיץ)) | Test planner | FC-TEST-seed |
| `c597c53f-fa65-4268-a8c2-2ef5f7a04e8a` | monthly | Sun Apr 26 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 10:32:04 GMT+0300 (שעון ישראל (קיץ)) | Test admin |  |
| `964e7881-2803-4e08-a661-db1a6b37fbff` | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 10:30:24 GMT+0300 (שעון ישראל (קיץ)) | Test planner | FC-TEST-seed |
| `153cd6ac-cc64-4319-9a11-f7a899eed4a5` | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 10:29:18 GMT+0300 (שעון ישראל (קיץ)) | FCSEED T6 publish | FCSEED-TEST-seed |
| `53678e22-bb58-4617-8d64-b7de0353e590` | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat May 02 2026 10:27:33 GMT+0300 (שעון ישראל (קיץ)) | FCSEED T6 publish | FCSEED-TEST-seed |
| `d54262f6-884d-45f2-928d-e8f9ed326d67` | monthly | Sun Apr 19 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sun Apr 26 2026 13:35:39 GMT+0300 (שעון ישראל (קיץ)) | Test admin |  |
| `74a14e91-354a-4b0d-a83b-4e00eb3f28e8` | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sun Apr 26 2026 13:34:18 GMT+0300 (שעון ישראל (קיץ)) | Test planner | FC-TEST-seed |
| `4a9438b3-77ac-4255-b299-fe5595364f87` | monthly | Sun Apr 19 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Tue Apr 21 2026 14:54:44 GMT+0300 (שעון ישראל (קיץ)) | Test admin |  |
| `5fa57b5c-e04b-4b85-91a0-fe4405af70d3` | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Tue Apr 21 2026 14:53:13 GMT+0300 (שעון ישראל (קיץ)) | Test planner | FC-TEST-seed |
| `feddcf6e-3b6d-43f0-a94c-d2142d184c93` | monthly | Mon Apr 20 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Tue Apr 21 2026 14:51:54 GMT+0300 (שעון ישראל (קיץ)) | Test admin | FC-TEST-T26-published-A |
| `d50b7e52-4f03-4df0-a7de-0ff3555d3ede` | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Tue Apr 21 2026 14:51:07 GMT+0300 (שעון ישראל (קיץ)) | Test planner | FC-TEST-seed |
| `ee61d61f-bf65-4796-b65d-911814f87d7a` | monthly | Sun Apr 19 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Tue Apr 21 2026 14:47:37 GMT+0300 (שעון ישראל (קיץ)) | Test admin |  |
| `71f835af-3d78-4cbf-927d-4fbe3bd3b5d1` | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Tue Apr 21 2026 14:46:13 GMT+0300 (שעון ישראל (קיץ)) | Test planner | FC-TEST-seed |
| `6e2b2226-3f10-4f9f-999f-fe52876e9b9a` | monthly | Sun Apr 12 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat Apr 18 2026 19:07:32 GMT+0300 (שעון ישראל (קיץ)) | Test admin |  |
| `2e752458-34a0-4662-8ff3-0c16bf80460b` | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat Apr 18 2026 19:06:18 GMT+0300 (שעון ישראל (קיץ)) | Test planner | FC-TEST-seed |
| `501665c6-1ee8-4aec-8ec9-1be221d97c02` | monthly | Sun Apr 12 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat Apr 18 2026 19:04:52 GMT+0300 (שעון ישראל (קיץ)) | Test admin |  |
| `29604242-2ddb-4144-a4f7-930b9b89dc6d` | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat Apr 18 2026 19:03:38 GMT+0300 (שעון ישראל (קיץ)) | Test planner | FC-TEST-seed |
| `d63b110c-1c6b-41a1-bd05-594d75a28d12` | monthly | Sun Apr 12 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat Apr 18 2026 18:59:19 GMT+0300 (שעון ישראל (קיץ)) | Test admin |  |
| `7303fabc-085e-47a1-aef8-17dfbfbad2d1` | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat Apr 18 2026 18:58:06 GMT+0300 (שעון ישראל (קיץ)) | Test planner | FC-TEST-seed |
| `13c7650b-8af3-424e-ab65-40a629832361` | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat Apr 18 2026 18:05:15 GMT+0300 (שעון ישראל (קיץ)) | Test planner | FC-TEST-seed |
| `4eb624a7-f3e0-4edc-a957-657b4bff7bc2` | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat Apr 18 2026 18:03:45 GMT+0300 (שעון ישראל (קיץ)) | Test planner | FC-TEST-seed |
| `0fbc609f-c39e-4b54-ab3c-72fcfb84a902` | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat Apr 18 2026 18:02:52 GMT+0300 (שעון ישראל (קיץ)) | Test planner | FC-TEST-seed |
| `ee47516d-bd08-4360-9e71-233168a7eee3` | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Sat Apr 18 2026 18:01:59 GMT+0300 (שעון ישראל (קיץ)) | Test planner | FC-TEST-seed |

## Planning-engine consumption of forecasts

`planning_runs` references forecast versions — see raw dump section I.3 for usage distribution.

## Per-version table

| version_id | status | cadence | horizon_start | created_by | created_at | lines | notes | suspect | reason |
|---|---|---|---|---|---|---|---|---|---|
| `d3122b1e-8376-470c-b761-1be290353ebc` | published | monthly | Sun Nov 01 2026 00:00:00 GMT+0200 (שעון ישראל (חורף)) | FCM-Chunk3-seed | 2026-05-02T15:39:28.949Z | 1 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot |
| `c8b49e39-cd32-44d3-b739-0474e8b6b321` | published | monthly | Thu Oct 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T15:39:27.658Z | 1 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot |
| `3bc3ae80-c72d-4d8f-b6d1-d33285403e3b` | published | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T15:39:26.295Z | 2 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot |
| `9421e357-bcf8-4c86-9f33-22e066db5175` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T15:39:25.151Z | 3 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `d2c901dc-195d-45e9-b76b-a9d912e3f2eb` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T15:39:23.869Z | 4 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `5beed049-023c-4b12-a583-1d052b6b6a2c` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T15:39:23.054Z | 2 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `27634619-34f3-4aca-ad73-607c894c770a` | discarded | monthly | Sat Aug 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM planner | 2026-05-02T15:39:22.715Z | 0 |  | YES | status=discarded |
| `2af43cc4-b4bb-4c6e-a901-eb92dac5cffa` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T15:39:20.477Z | 10 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `eaa99565-1ab8-4d04-bb9f-d8e0c93cb5b0` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T15:39:20.204Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `154f6207-2f58-48f2-ac13-62be69927811` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T15:39:19.319Z | 1 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `cc2b44e0-af15-41d7-9aa0-faa76fd62dfb` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T15:39:18.258Z | 2 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `d1414cab-e9df-4469-b664-12ebb94caa5d` | published | weekly | Mon Jun 08 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM weekly fixture | 2026-05-02T15:39:17.631Z | 8 | FCM-TEST-weekly-regression | YES | text-token "TEST" in notes/snapshot |
| `dba0d90a-0a40-470a-9e82-ea9fb68694c3` | draft | monthly | Fri May 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Tom | 2026-05-02T15:20:41.643Z | 1 |  | no |  |
| `a82259cf-ac46-417b-9cc7-1ef81177d382` | published | monthly | Sun Apr 26 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Test planner | 2026-05-02T14:52:23.663Z | 569 |  | YES | text-token "TEST" in notes/snapshot |
| `82d638d1-5a96-472c-b828-082465999cd2` | superseded | monthly | Mon Apr 27 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:51:36.015Z | 568 | FC-TEST-T26-published-A | YES | text-token "TEST" in notes/snapshot; status=superseded |
| `0ae068e7-a157-4dff-8391-0c3892939b55` | discarded | monthly | Mon Nov 23 2026 00:00:00 GMT+0200 (שעון ישראל (חורף)) | Test planner | 2026-05-02T14:51:34.922Z | 0 | FC-TEST-T21-opendraft | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `b125ce5a-9b1e-4f73-af26-a46f053c738a` | discarded | monthly | Sun May 17 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Test planner | 2026-05-02T14:51:33.148Z | 0 | FC-TEST-revise | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `c51f3502-59da-4620-aa07-08e21df417fd` | published | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:50:45.429Z | 568 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot |
| `cd6306fe-d52b-4917-b67a-26a25da096a9` | published | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:50:44.729Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot |
| `79ce677e-493e-4c28-b0c7-f39f48768350` | discarded | monthly | Mon Apr 27 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:50:44.324Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `f387c924-f180-4317-8a3f-352320d84786` | discarded | monthly | Mon Apr 27 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:50:43.576Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `9e0fc4c7-7666-4681-8fdd-f42fd6057c78` | discarded | monthly | Mon Apr 27 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:50:43.169Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `f7831868-2a55-4382-90f5-0e7084ad9144` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCSEED seed | 2026-05-02T14:50:43.159Z | 568 | FCSEED-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `3d724977-880d-470f-8906-1f82a7373a60` | discarded | monthly | Mon Jun 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:50:42.355Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `ac696c66-c100-4163-8284-91a5847fdd7e` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:50:41.739Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `3583314b-b3c9-4e12-ba2d-933ef92c489e` | discarded | monthly | Mon Apr 27 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCSEED seed | 2026-05-02T14:50:41.262Z | 568 | FCSEED-TEST-freeze | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `735511db-ed2a-444b-8df3-0510455e783c` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:50:41.126Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `dd62e15d-d4ec-49db-a53f-48bfd68a677f` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:50:40.648Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `5ba28923-c177-457e-b2c0-85e525edfabe` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:50:40.515Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `95322bb2-a55d-49c4-af30-426a526ae19b` | published | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCSEED seed | 2026-05-02T14:50:40.068Z | 0 | FCSEED-TEST-seed | YES | text-token "TEST" in notes/snapshot |
| `81f44e2b-fe16-489c-ba1e-0f0a644013f8` | discarded | monthly | Mon Aug 30 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCR seed | 2026-05-02T14:50:39.887Z | 2 | FCR-R11-B | YES | text-token "SEED" in notes/snapshot; status=discarded |
| `0b932e03-6a69-4c7d-8fe8-adc7239a3221` | discarded | monthly | Mon Aug 30 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCR seed | 2026-05-02T14:50:39.801Z | 2 | FCR-R11-A | YES | text-token "SEED" in notes/snapshot; status=discarded |
| `b6fdb726-352e-4130-9886-ea03a59404d0` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:50:39.414Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `3ecdbc1c-335b-4aac-a9d0-1d97e63018f8` | discarded | monthly | Mon Jun 21 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCR seed | 2026-05-02T14:50:38.788Z | 4 | FCR-R04 | YES | text-token "SEED" in notes/snapshot; status=discarded |
| `174985db-dc96-42c8-bcfa-f47dd6d309ba` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCSEED seed | 2026-05-02T14:50:38.576Z | 568 | FCSEED-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `75a63bd7-26c6-446c-8e54-b25d29c1f907` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:50:38.559Z | 2 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `bae4a977-7016-4944-ac90-76a05334974a` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCSEED seed | 2026-05-02T14:50:38.505Z | 0 | FCSEED-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `c770b846-e98a-4ac5-b67a-f8167759ea4f` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCSEED seed | 2026-05-02T14:50:38.434Z | 0 | FCSEED-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `d93de89e-239f-4c75-8f08-f0f83538d509` | published | monthly | Mon Jun 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | parity-1777733417728 | 2026-05-02T14:50:18.822Z | 1 |  | YES | created_by is non-Tom and unrecognized |
| `ef6db32d-8d2c-48eb-94fd-73c672defe4b` | published | monthly | Sun Nov 01 2026 00:00:00 GMT+0200 (שעון ישראל (חורף)) | FCM-Chunk3-seed | 2026-05-02T14:50:10.402Z | 1 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot |
| `cd54f93d-3c1e-4d59-ad3c-d478381a7e7e` | published | monthly | Thu Oct 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:50:08.769Z | 1 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot |
| `250220d8-d673-4dfa-963f-10d623791810` | published | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:50:06.712Z | 2 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot |
| `92624e9a-fdc3-46bf-8665-7a1ad3dddb75` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:50:05.559Z | 3 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `947f74a2-2e2a-4ac6-87f3-24a91a0df367` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:50:03.915Z | 4 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `9066e154-b768-459f-8bcc-5566265a52a5` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:50:03.097Z | 2 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `8aba19aa-9f06-432d-b505-3b48258b0182` | discarded | monthly | Sat Aug 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM planner | 2026-05-02T14:50:02.758Z | 0 |  | YES | status=discarded |
| `5c81a5e9-21a3-4419-a162-97346916e023` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:50:00.030Z | 10 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `1b53a347-9f44-4f23-8893-de57d976911b` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:49:59.690Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `91664d67-a6a3-4a3a-8262-ea0c46c63c94` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:49:58.488Z | 1 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `03a892ab-8b54-4e03-97df-14a09c594c81` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:49:57.434Z | 2 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `30526c20-8b6d-4456-a44b-75fac7e820b2` | published | weekly | Mon Jun 08 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM weekly fixture | 2026-05-02T14:49:56.524Z | 8 | FCM-TEST-weekly-regression | YES | text-token "TEST" in notes/snapshot |
| `71cf40cc-98af-41a4-98e8-474c3f794747` | published | monthly | Sun Nov 01 2026 00:00:00 GMT+0200 (שעון ישראל (חורף)) | FCM-Chunk3-seed | 2026-05-02T14:48:08.145Z | 1 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot |
| `f19d7a29-bbcf-4ace-830e-4e860ae4881d` | published | monthly | Thu Oct 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:48:06.199Z | 1 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot |
| `82263079-54f4-4839-91b6-1d1f8c9bd6de` | published | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:48:04.733Z | 2 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot |
| `4aaa4f7f-070b-4c73-a1b0-c214a54a68dc` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:48:03.406Z | 3 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `9ab76c2c-989d-421f-9a87-bad4f6dbc731` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:48:01.999Z | 4 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `8e7b7ab0-b2ca-46c4-bf99-28b0b9826061` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:48:01.018Z | 2 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `2b0be719-6fbd-4136-87d6-05a4b9185a09` | discarded | monthly | Sat Aug 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM planner | 2026-05-02T14:48:00.577Z | 0 |  | YES | status=discarded |
| `b719932e-3b2c-4203-b115-47c691e5e646` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:47:57.922Z | 10 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `1b731ac7-1a5d-4455-a73f-93fcc84a08c3` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:47:57.516Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `73ee9202-30a2-4667-9fe6-7fb6d3549b8f` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:47:56.617Z | 1 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `99b3a1ee-fa2f-4174-9839-153bdd693ac9` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:47:55.339Z | 2 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `4074e68a-56ed-4465-8984-c6132a893546` | published | weekly | Mon Jun 08 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM weekly fixture | 2026-05-02T14:47:54.450Z | 8 | FCM-TEST-weekly-regression | YES | text-token "TEST" in notes/snapshot |
| `c9cbb602-91bf-4e63-b5dc-711209b36eaf` | published | monthly | Sun Nov 01 2026 00:00:00 GMT+0200 (שעון ישראל (חורף)) | FCM-Chunk3-seed | 2026-05-02T14:47:46.023Z | 1 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot |
| `cd91bab3-3537-4779-b13b-bdd50ae630db` | published | monthly | Thu Oct 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:47:44.721Z | 1 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot |
| `4902139f-8437-41a2-ba46-d2cb5ea847a3` | published | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:47:43.086Z | 2 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot |
| `9357edcf-37e5-4e6a-8f59-3b88447681dd` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:47:41.924Z | 3 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `8a528eee-1be3-4959-a271-1b67e6d153d7` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:47:40.357Z | 4 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `47d6cdf2-4572-4fd5-80e8-52446e7a4da1` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:47:39.381Z | 2 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `0928b086-fd0d-4c96-9663-df5fa45a2ebc` | discarded | monthly | Sat Aug 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM planner | 2026-05-02T14:47:38.954Z | 0 |  | YES | status=discarded |
| `c3ae231d-aa41-42c0-a884-d1462c1bd8d0` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:47:35.586Z | 10 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `62399eaa-b2c1-45d9-a676-a63ba03d3382` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:47:35.310Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `0eefe792-3d8d-4047-91e6-5a477d0c7eed` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:47:34.421Z | 1 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `47c308f0-c387-4c17-a43d-0ebb1748b9fc` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:47:33.015Z | 2 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `39b8dcb0-b315-4ee1-8fc2-8af180bce37e` | published | weekly | Mon Jun 08 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM weekly fixture | 2026-05-02T14:47:32.382Z | 8 | FCM-TEST-weekly-regression | YES | text-token "TEST" in notes/snapshot |
| `e433a9fc-58c6-4c2d-8558-6e25673b3f04` | published | monthly | Sun Nov 01 2026 00:00:00 GMT+0200 (שעון ישראל (חורף)) | FCM-Chunk3-seed | 2026-05-02T14:47:23.707Z | 1 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot |
| `e1def1d6-1347-4bd1-8796-6d4107709643` | published | monthly | Thu Oct 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:47:22.399Z | 1 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot |
| `db00590d-f916-44bf-ad93-3a8494d6ce56` | published | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:47:20.558Z | 2 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot |
| `3c19abe3-ef04-40fb-a65f-281f582860b1` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:47:18.917Z | 3 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `89326502-acfc-43d8-a580-17a9c0154362` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:47:17.617Z | 4 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `4b47050c-7e73-4086-988a-e1e56bfa3348` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:47:16.405Z | 2 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `dcdaceb1-48a2-4562-a0d5-ad438e244858` | discarded | monthly | Sat Aug 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM planner | 2026-05-02T14:47:15.982Z | 0 |  | YES | status=discarded |
| `40bf6ab4-302a-4ada-ad7e-78b3d5d0d30a` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:47:13.137Z | 10 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `943decaf-edfc-4482-a807-ac739859e13c` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:47:12.861Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `433d6aa0-7ff6-4db1-b09d-468a0e595218` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:47:11.964Z | 1 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `c89ff724-3a19-41bb-8d05-235ab2b1a544` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:47:10.565Z | 2 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `0aee3a9b-71f6-484d-a565-e50dc7c434c3` | published | weekly | Mon Jun 08 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM weekly fixture | 2026-05-02T14:47:09.935Z | 8 | FCM-TEST-weekly-regression | YES | text-token "TEST" in notes/snapshot |
| `afbdbea4-bfe8-445f-b713-b76981d9d0b6` | published | monthly | Sun Nov 01 2026 00:00:00 GMT+0200 (שעון ישראל (חורף)) | FCM-Chunk3-seed | 2026-05-02T14:46:41.778Z | 1 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot |
| `440944cb-322a-4c6e-bf73-358857ad7ee4` | published | monthly | Thu Oct 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:46:40.244Z | 1 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot |
| `a2f64133-5f85-46aa-a975-73533a8c8020` | published | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:46:39.111Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot |
| `f3206f83-a940-489a-9ed1-4820b6770229` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:46:38.573Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `cce9c6b5-3a50-4361-b74e-c0f3a9fc3815` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:46:37.910Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `da534b2b-1c0c-4004-8bf9-509fe71b40e7` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:46:37.145Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `568aef0a-21e8-45b8-b0e0-4be008a865aa` | discarded | monthly | Sat Aug 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM planner | 2026-05-02T14:46:36.808Z | 0 |  | YES | status=discarded |
| `9b312d13-af07-494c-8b2b-5fb2b97692db` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:46:36.189Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `4e42f59a-649e-45c8-8829-8bbb88ba8055` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:46:35.915Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `fdcf562d-038e-425c-acb9-4b5d00fa1f40` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:46:35.026Z | 1 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `106b9638-2578-4ccc-bb71-507f5ded3cc8` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:46:34.475Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `6d6d82f1-1eef-4edd-a737-9545c56e7eb1` | published | weekly | Mon Jun 08 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM weekly fixture | 2026-05-02T14:46:33.520Z | 8 | FCM-TEST-weekly-regression | YES | text-token "TEST" in notes/snapshot |
| `d70cb6b3-5f2f-4ff2-9e32-540a49ce6a4c` | published | monthly | Sun Nov 01 2026 00:00:00 GMT+0200 (שעון ישראל (חורף)) | FCM-Chunk3-seed | 2026-05-02T14:46:24.707Z | 1 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot |
| `37cbcc4d-1c66-42d1-bd42-521b8d2bef14` | published | monthly | Thu Oct 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:46:23.139Z | 1 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot |
| `edbf350b-d2d9-432b-a35d-895414fca1af` | published | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:46:22.047Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot |
| `7b8c6d39-ccc7-416c-9d24-960883020836` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:46:21.415Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `0b383a8f-7dbf-4015-bb2e-36975a807051` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:46:20.756Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `6e95c09b-d225-438d-86d2-3eb3482590f3` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:46:20.216Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `981299e8-1a68-4d60-90a6-1e2a5f8f76e7` | discarded | monthly | Sat Aug 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM planner | 2026-05-02T14:46:19.874Z | 0 |  | YES | status=discarded |
| `1979d5b8-821e-4322-8f11-43b407084293` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:46:19.265Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `bdde77b0-f2f1-4aa8-a3e6-7c3b369cd11a` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:46:18.992Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `3375534d-5dbe-478b-ae78-6a26570a47e8` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:46:18.106Z | 1 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `0f255b7e-b0dd-45de-9a3f-23efd81d6d49` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:46:17.271Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `07daba3c-b4ae-4b3b-bc56-b99351dc8afb` | published | weekly | Mon Jun 08 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM weekly fixture | 2026-05-02T14:46:16.316Z | 8 | FCM-TEST-weekly-regression | YES | text-token "TEST" in notes/snapshot |
| `f07cc43b-aab8-4b35-89a4-f87dca737f2b` | published | monthly | Sun Nov 01 2026 00:00:00 GMT+0200 (שעון ישראל (חורף)) | FCM-Chunk3-seed | 2026-05-02T14:46:06.549Z | 1 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot |
| `b0f71d5c-94af-4cb9-9dd2-02d7228e0c1e` | published | monthly | Thu Oct 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:46:05.027Z | 1 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot |
| `412c42ef-3e79-4611-b579-cfa7bedc68f6` | published | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:46:03.738Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot |
| `8b2a6b97-8d0c-4310-9dce-33bb7b44e60b` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:46:03.264Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `0604aced-f5bd-49a1-988b-0bf8a97eb3df` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:46:02.790Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `031d0e30-f8dc-46ad-93c2-50542c887255` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:46:02.319Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `4089ecf2-8266-42e0-b4b9-865640f16c65` | discarded | monthly | Sat Aug 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM planner | 2026-05-02T14:46:01.977Z | 0 |  | YES | status=discarded |
| `28fe13e0-2491-4281-9c58-a3e077733d9f` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:46:01.158Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `97e06b56-d25b-4b87-9b73-734e6b96c0c8` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:46:00.752Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `c4df879b-c4d5-43b9-a436-533a42289897` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:59.461Z | 1 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `2c027d31-312f-4cb5-b717-00da60e40622` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:58.806Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `ca960ec1-b069-4f43-8a3d-49527c3cb45f` | published | weekly | Mon Jun 08 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM weekly fixture | 2026-05-02T14:45:58.183Z | 8 | FCM-TEST-weekly-regression | YES | text-token "TEST" in notes/snapshot |
| `6e82c327-d42e-4bf4-a4af-7e504303c767` | discarded | monthly | Sun Nov 01 2026 00:00:00 GMT+0200 (שעון ישראל (חורף)) | FCM-Chunk3-seed | 2026-05-02T14:45:33.702Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `600a2753-7a12-46af-95aa-443e56ea3062` | discarded | monthly | Thu Oct 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:33.551Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `965f8fcc-5059-4386-a3c6-c436f8d198ce` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:33.474Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `d2e91023-1b65-49c8-ab39-0706d524fdce` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:33.399Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `d6c2738f-6033-4704-9797-6c173ced539a` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:33.325Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `fceb18d7-e48b-4df7-ba40-a66cb353586d` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:33.255Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `bc0e030c-55a1-4a2d-b4b3-547bd0072399` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:33.110Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `b9a7ab92-9352-404d-838e-dfa6a7859db4` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:33.037Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `18622d9f-26ad-440c-a0e6-ea1e0844b02a` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:32.855Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `251f311c-ee02-4ec1-ba92-f52d5b953a98` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:32.678Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `07d4f6fd-dd2d-429e-b400-4c8bb6b09d52` | published | weekly | Mon Jun 08 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM weekly fixture | 2026-05-02T14:45:31.875Z | 8 | FCM-TEST-weekly-regression | YES | text-token "TEST" in notes/snapshot |
| `b5e71ed1-a5b3-48ff-a308-2b3b85dfb77f` | discarded | monthly | Sun Nov 01 2026 00:00:00 GMT+0200 (שעון ישראל (חורף)) | FCM-Chunk3-seed | 2026-05-02T14:45:24.923Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `e40954b3-2e87-4574-99f7-82e0518e671e` | discarded | monthly | Thu Oct 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:24.784Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `44c6f946-6f2a-4edd-b23f-9d1b4e50878f` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:24.710Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `f782b5a9-8fd4-42f5-95ae-fc3a575df48f` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:24.638Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `1bd4e270-30de-4506-aed9-7d5bb0fe6140` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:24.505Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `05b890da-561e-4d64-8903-86ad5f51ec7e` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:24.432Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `68f6e9c9-e62d-4623-8e93-54e538c52eb3` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:24.230Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `502fce32-b17d-4d43-adf0-cdf88fa3792c` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:24.097Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `72a0dc52-e9a8-4f06-b540-fc9acb4da482` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:24.025Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `1e710569-9771-4496-8919-11e198832553` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:23.934Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `958e2280-d592-4152-84ea-b6e39754938f` | published | weekly | Mon Jun 08 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM weekly fixture | 2026-05-02T14:45:23.077Z | 8 | FCM-TEST-weekly-regression | YES | text-token "TEST" in notes/snapshot |
| `b5fe8e3e-8e41-40da-826e-66f2b9252071` | discarded | monthly | Sun Nov 01 2026 00:00:00 GMT+0200 (שעון ישראל (חורף)) | FCM-Chunk3-seed | 2026-05-02T14:45:16.491Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `30f05e61-7f60-4790-b32d-b12b29e20a02` | discarded | monthly | Thu Oct 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:16.349Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `d268e640-2bdc-4916-b370-46b829e509ba` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:16.270Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `67a93b2b-e2d8-409a-9707-5c43f01b33c1` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:16.196Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `edff5aca-8aca-4fdc-b608-e328a3464084` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:16.122Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `32d14b79-776b-4f04-881a-1ebcdaa8be1f` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:16.047Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `23a55923-019a-468e-81d4-81295c001474` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:15.898Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `6e242a72-f58e-40c6-a8ac-663dc2872886` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:15.822Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `0c90e9cd-5981-4170-8b9c-7c035c37bfbc` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:15.748Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `8908d07e-3539-4966-b9e3-3352e094eb3c` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:15.657Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `3fdba978-64f6-4226-aa95-48536be1fd32` | published | weekly | Mon Jun 08 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM weekly fixture | 2026-05-02T14:45:15.012Z | 8 | FCM-TEST-weekly-regression | YES | text-token "TEST" in notes/snapshot |
| `e49c7729-aa40-431e-bc4c-685986d0bca2` | discarded | monthly | Sun Nov 01 2026 00:00:00 GMT+0200 (שעון ישראל (חורף)) | FCM-Chunk3-seed | 2026-05-02T14:45:07.708Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `8da35773-8734-48c7-a407-6f5ea6fe0ccf` | discarded | monthly | Thu Oct 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:07.498Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `76e80e2e-2509-4445-936a-375729bbb990` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:07.420Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `a828e572-fe3f-4a45-9849-1d38ced462ea` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:07.349Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `3ce37944-e5de-41a6-9f3c-b1d1c884dbfb` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:07.278Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `b8d67871-2a49-4f3f-967c-8133defb69ed` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:07.189Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `d39f85ce-6110-423f-92c6-6a8fad9dacb5` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:06.995Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `7a099afa-5e1c-449d-a718-a02dd8c81540` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:06.914Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `03c2b3e4-812f-43ed-88ea-02c6e9228aaa` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:06.842Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `c6f92b2c-1df3-48b1-894e-79ced89d59eb` | discarded | monthly | Wed Jul 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM-Chunk3-seed | 2026-05-02T14:45:06.685Z | 0 | FCM-TEST-Chunk3 | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `e7f0ff94-cf69-4b26-bfb7-c500807d5ea8` | published | weekly | Mon Jun 08 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCM weekly fixture | 2026-05-02T14:45:05.934Z | 8 | FCM-TEST-weekly-regression | YES | text-token "TEST" in notes/snapshot |
| `8f0f59e4-63e2-4abc-ac4e-d44aa9b2d902` | published | monthly | Mon Jun 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | parity-1777733086512 | 2026-05-02T14:44:47.831Z | 1 |  | YES | created_by is non-Tom and unrecognized |
| `450c0cc0-c9af-4876-9238-dc336c45b531` | published | monthly | Mon Jun 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | parity-1777733047761 | 2026-05-02T14:44:08.840Z | 1 |  | YES | created_by is non-Tom and unrecognized |
| `ab85551b-84fb-42e0-87ad-bef145bc3297` | published | monthly | Mon Jun 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | parity-1777733022613 | 2026-05-02T14:43:43.735Z | 1 |  | YES | created_by is non-Tom and unrecognized |
| `389cfbc4-a221-40b9-89f0-4196609eb66b` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCSEED seed | 2026-05-02T14:41:22.284Z | 552 | FCSEED-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `84f3dd7d-8432-45f8-bb09-520428dd1716` | discarded | monthly | Mon Apr 27 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCSEED seed | 2026-05-02T14:41:20.549Z | 552 | FCSEED-TEST-freeze | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `8a558b6f-936a-4357-85e7-51fac07e2784` | published | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCSEED seed | 2026-05-02T14:41:19.732Z | 0 | FCSEED-TEST-seed | YES | text-token "TEST" in notes/snapshot |
| `04656c9c-cc1c-45b9-9a72-0f00437914b4` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCSEED seed | 2026-05-02T14:41:18.285Z | 552 | FCSEED-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `6932fc76-a1e2-44cd-9526-178b979a4b9c` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCSEED seed | 2026-05-02T14:41:18.213Z | 0 | FCSEED-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `9057dfed-8581-469d-aab1-2e693d838b83` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCSEED seed | 2026-05-02T14:41:18.130Z | 0 | FCSEED-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `9b8cd486-0c49-406d-a0c4-60ece566ec40` | discarded | monthly | Mon Aug 30 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCR seed | 2026-05-02T14:41:07.681Z | 2 | FCR-R11-B | YES | text-token "SEED" in notes/snapshot; status=discarded |
| `e85eeaa2-a022-4f5e-b459-2d048dfeec10` | discarded | monthly | Mon Aug 30 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCR seed | 2026-05-02T14:41:07.612Z | 2 | FCR-R11-A | YES | text-token "SEED" in notes/snapshot; status=discarded |
| `1ca3c5e9-e49f-48c9-9b6a-8dc39e8439e3` | discarded | monthly | Mon Jun 21 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCR seed | 2026-05-02T14:41:06.300Z | 4 | FCR-R04 | YES | text-token "SEED" in notes/snapshot; status=discarded |
| `c5df7116-37c4-4495-b51c-bc24ec923e94` | discarded | monthly | Mon Aug 30 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCR seed | 2026-05-02T14:40:40.490Z | 2 | FCR-R11-B | YES | text-token "SEED" in notes/snapshot; status=discarded |
| `354e24ea-e3d4-4686-8424-38b0906bb2d8` | discarded | monthly | Mon Aug 30 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCR seed | 2026-05-02T14:40:40.421Z | 2 | FCR-R11-A | YES | text-token "SEED" in notes/snapshot; status=discarded |
| `e7932936-41b5-4dc5-93b4-9a9a10f7dbab` | discarded | monthly | Mon Jun 21 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCR seed | 2026-05-02T14:40:39.170Z | 4 | FCR-R04 | YES | text-token "SEED" in notes/snapshot; status=discarded |
| `8b6568d6-2ca4-43a9-b851-d06030f56bff` | discarded | monthly | Mon Aug 30 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCR seed | 2026-05-02T14:40:30.917Z | 2 | FCR-R11-B | YES | text-token "SEED" in notes/snapshot; status=discarded |
| `66fba83c-5e64-4fb0-be3b-ad8ff97cca17` | discarded | monthly | Mon Aug 30 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCR seed | 2026-05-02T14:40:30.850Z | 2 | FCR-R11-A | YES | text-token "SEED" in notes/snapshot; status=discarded |
| `e483c740-7e40-48bb-928b-71d64b2a1410` | discarded | monthly | Mon Jun 21 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCR seed | 2026-05-02T14:40:29.869Z | 4 | FCR-R04 | YES | text-token "SEED" in notes/snapshot; status=discarded |
| `87a2f408-114c-4cae-9ed8-aa60ea117349` | discarded | monthly | Mon Aug 30 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCR seed | 2026-05-02T14:40:18.886Z | 2 | FCR-R11-B | YES | text-token "SEED" in notes/snapshot; status=discarded |
| `5116691c-3030-4962-a0b5-4ef151431f3a` | discarded | monthly | Mon Aug 30 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCR seed | 2026-05-02T14:40:18.817Z | 2 | FCR-R11-A | YES | text-token "SEED" in notes/snapshot; status=discarded |
| `2398d37d-8229-424a-b7f9-94f8c4401a7a` | discarded | monthly | Mon Jun 21 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCR seed | 2026-05-02T14:40:17.827Z | 4 | FCR-R04 | YES | text-token "SEED" in notes/snapshot; status=discarded |
| `d8d076ef-6b1b-40ba-96b5-34bc58186d69` | published | monthly | Sun Apr 26 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Test planner | 2026-05-02T14:39:17.083Z | 553 |  | YES | text-token "TEST" in notes/snapshot |
| `b79dcae3-fca4-4b79-8152-3c6f1335a19c` | superseded | monthly | Mon Apr 27 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:38:31.618Z | 552 | FC-TEST-T26-published-A | YES | text-token "TEST" in notes/snapshot; status=superseded |
| `789a7ac3-fb38-499b-8835-79936b9fae8b` | discarded | monthly | Mon Nov 23 2026 00:00:00 GMT+0200 (שעון ישראל (חורף)) | Test planner | 2026-05-02T14:38:30.524Z | 0 | FC-TEST-T21-opendraft | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `3c00af3f-1589-4533-9f24-81c57db75ddc` | discarded | monthly | Sun May 17 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Test planner | 2026-05-02T14:38:28.814Z | 0 | FC-TEST-revise | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `d82fe5c2-fb6e-4045-9448-cfcbb04cac6d` | published | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:37:42.870Z | 552 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot |
| `f6291347-13f2-4fd9-afb6-b3c30636e441` | published | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:37:42.049Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot |
| `ab0d7df7-7f55-4fca-abe6-09aea8446d86` | discarded | monthly | Mon Apr 27 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:37:41.529Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `88fb5cbe-967d-4f37-835e-5af3e544dfb0` | discarded | monthly | Mon Apr 27 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:37:40.547Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `e79fdb3d-4390-47df-a651-2b8238ab4723` | discarded | monthly | Mon Apr 27 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:37:40.141Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `8bd91f0a-0154-4cd6-a60b-579a2a8566d6` | discarded | monthly | Mon Jun 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:37:39.463Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `c28333b4-3438-48e4-91ee-97ae9c07c96f` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:37:39.053Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `5cd38149-8524-4ee8-81a1-9ae9d5415811` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:37:38.647Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `e9fb07a8-efdd-487a-8b82-11e44a4bc3d3` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:37:38.300Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `f7884f8a-651d-4b88-a9a6-78c519c4af66` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:37:38.164Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `99b1c44e-acb7-487f-96c0-94cd31b2146d` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:37:36.868Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `3fe0f173-e5ab-4e61-9c78-9fa636525796` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:37:35.586Z | 2 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `2d925797-c3fa-486a-9f00-b62e27a8c9c1` | published | monthly | Sun Apr 26 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Test planner | 2026-05-02T14:36:14.180Z | 553 |  | YES | text-token "TEST" in notes/snapshot |
| `83419905-ae7e-4c8b-a360-1dbd94cf35cb` | superseded | monthly | Mon Apr 27 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:35:29.476Z | 552 | FC-TEST-T26-published-A | YES | text-token "TEST" in notes/snapshot; status=superseded |
| `0a2c18c1-0d33-438b-916a-84065184cdb7` | discarded | monthly | Mon Nov 23 2026 00:00:00 GMT+0200 (שעון ישראל (חורף)) | Test planner | 2026-05-02T14:35:28.284Z | 0 | FC-TEST-T21-opendraft | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `58780f80-0e46-4453-98ad-a3ccfe8fba52` | discarded | monthly | Sun May 17 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Test planner | 2026-05-02T14:35:26.611Z | 0 | FC-TEST-revise | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `08698d0b-daa9-40aa-8a8d-71a43902c9ec` | published | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:34:41.144Z | 552 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot |
| `f00ce4de-a54e-46b6-b5bd-a3c27d24de0e` | published | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:34:40.525Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot |
| `82a110b4-bb21-44f6-a322-374ac76e8b66` | discarded | monthly | Mon Apr 27 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:34:40.118Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `7856782a-2f1a-43ad-995b-1f8bce04aaf9` | discarded | monthly | Mon Apr 27 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:34:39.258Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `859f581f-ef28-40a6-ba58-c10144ca4e28` | discarded | monthly | Mon Apr 27 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:34:38.631Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `59a7275c-8171-4e0d-8d75-4ea732162f2b` | discarded | monthly | Mon Jun 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:34:37.954Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `52e648e1-a6bf-40fd-88df-7b52716f3f63` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:34:37.545Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `9dca919f-4940-473f-8b28-f49ab8ecfb63` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:34:37.134Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `ca51643b-bcd9-403a-8963-ff2c22aec1a5` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:34:36.795Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `164700af-dfe2-4423-bd31-19974d105b6c` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:34:36.727Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `03970142-9797-4887-87f9-14badd02b421` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:34:35.658Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `387c35a5-0763-4c23-a91e-e939fd3ad38f` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:34:34.816Z | 2 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `1134ef58-0640-4970-a53f-07590c2cbde1` | published | monthly | Sun Apr 26 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Test planner | 2026-05-02T14:33:38.166Z | 553 |  | YES | text-token "TEST" in notes/snapshot |
| `6ddc788d-02d9-4c3b-a218-d7f8c7635c97` | superseded | monthly | Mon Apr 27 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:32:52.454Z | 552 | FC-TEST-T26-published-A | YES | text-token "TEST" in notes/snapshot; status=superseded |
| `30058330-f0a5-467d-b0c5-da20aa1c9f62` | discarded | monthly | Mon Nov 23 2026 00:00:00 GMT+0200 (שעון ישראל (חורף)) | Test planner | 2026-05-02T14:32:51.523Z | 0 | FC-TEST-T21-opendraft | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `5cf2044b-ed01-4c73-9d35-88b1ad93552a` | discarded | monthly | Sun May 17 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Test planner | 2026-05-02T14:32:49.795Z | 0 | FC-TEST-revise | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `29a17eca-9773-4255-b971-adf08e1ca906` | published | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:32:03.241Z | 552 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot |
| `2bb2308f-91ea-43e4-83d4-37ea0cd2162e` | published | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:32:02.444Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot |
| `fae880ee-e0ac-4c69-b250-cdabcf3ac828` | discarded | monthly | Mon Apr 27 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:32:02.028Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `3d12f9e6-ac2f-4586-ac51-4c6971571f1f` | discarded | monthly | Mon Apr 27 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:32:01.267Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `b90fe2c0-53cf-45a7-9aec-048ca4e5af58` | discarded | monthly | Mon Apr 27 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:32:00.853Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `1733be65-003f-4f1c-9986-dc56a5ac22b9` | discarded | monthly | Mon Jun 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:31:59.972Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `7c7af4fb-2b19-48e6-896c-f7d66886ca62` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:31:59.512Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `00ea09c0-9d5b-46c1-983e-e0d3c255a35d` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:31:59.095Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `06bd1e59-b8a0-4780-8b47-6fddcc995d04` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:31:58.746Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `52c1905c-6d7c-4b30-947a-07603b61dbc0` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:31:58.674Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `3d369306-6a6c-4a2a-927d-e7be3b4b1d81` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:31:57.579Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `d15a993f-8a29-4c92-8072-bbe6f67c43f8` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:31:56.520Z | 2 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `798940a8-9805-4d8a-a085-a7066f12d204` | discarded | monthly | Mon Apr 27 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:29:02.883Z | 552 | FC-TEST-T26-published-A | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `e8fd444d-8564-498c-b3a2-d37bb2ce06d5` | discarded | monthly | Mon Nov 23 2026 00:00:00 GMT+0200 (שעון ישראל (חורף)) | Test planner | 2026-05-02T14:29:01.958Z | 0 | FC-TEST-T21-opendraft | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `0f005947-65c1-49f5-95a4-aa86d0cf4ace` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:28:17.211Z | 552 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `0891e49a-cd2c-4e9b-bc0d-ac14628cfc9d` | published | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:28:16.590Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot |
| `ee71f9e0-3037-4753-978f-d1c5f0d623f6` | discarded | monthly | Mon Apr 27 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:28:16.179Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `52616912-6c62-4312-8690-596a0aec10bc` | discarded | monthly | Mon Apr 27 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:28:15.702Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `0c30c670-d585-4706-9774-4b91da56ee51` | discarded | monthly | Mon Apr 27 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:28:15.089Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `f30c7fb2-9df4-4454-83bc-8a058ca61dac` | discarded | monthly | Mon Jun 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:28:14.065Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `60a7f54e-29a7-4529-9caa-4e487ed8dd06` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:28:13.447Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `11778a6f-003f-415f-95b4-e71e4fce0221` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:28:12.927Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `889128b5-7754-47e1-9717-17f45fd914d1` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:28:12.580Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `77c6c8fa-4e4e-4e7c-8404-851434f075e3` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:28:12.507Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `a14526a1-649f-4b9b-b4df-80fb6b4862ea` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:28:12.088Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `65e6e323-87be-4082-b492-4fca12cc1769` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T14:28:11.648Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `4f34a2a8-b4ea-49e1-8296-1472c4ecf2ce` | draft | monthly | Sat May 02 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Tom | 2026-05-02T13:11:31.789Z | 12 |  | no |  |
| `c597c53f-fa65-4268-a8c2-2ef5f7a04e8a` | published | monthly | Sun Apr 26 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Test planner | 2026-05-02T07:31:15.647Z | 537 |  | YES | text-token "TEST" in notes/snapshot |
| `2f7395b3-dce0-48b5-bc1b-d4f835eeb551` | superseded | monthly | Mon Apr 27 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T07:30:28.953Z | 536 | FC-TEST-T26-published-A | YES | text-token "TEST" in notes/snapshot; status=superseded |
| `4d7a4c2a-c437-4813-8900-71efd6516902` | discarded | monthly | Mon Nov 23 2026 00:00:00 GMT+0200 (שעון ישראל (חורף)) | Test planner | 2026-05-02T07:30:27.723Z | 0 | FC-TEST-T21-opendraft | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `755a05e1-5382-4941-85ef-bbbb94940925` | discarded | monthly | Sun May 17 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Test planner | 2026-05-02T07:30:25.612Z | 0 | FC-TEST-revise | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `964e7881-2803-4e08-a661-db1a6b37fbff` | published | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T07:29:38.766Z | 536 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot |
| `6ef0aa6b-33b8-485b-9ff2-54e14b84872d` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T07:29:38.357Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `25f05736-0397-4edf-8270-183d0a699533` | discarded | monthly | Mon Apr 27 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T07:29:37.951Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `2a7b9a2e-a834-4a5e-b615-d5a55c911573` | discarded | monthly | Mon Apr 27 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T07:29:37.094Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `2131f704-b805-41c7-b949-3eb7a36482a6` | discarded | monthly | Mon Apr 27 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T07:29:36.380Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `ae56205d-2432-4e7c-b8a9-d1d14f15fc36` | discarded | monthly | Mon Jun 01 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T07:29:35.701Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `930b60e9-1b4c-44f4-aa49-13eed7bffcc4` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T07:29:35.292Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `a7692732-75a6-4024-871d-f15c31f4bb97` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T07:29:34.885Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `c6c3fc40-dd52-47cf-aeeb-a815346eaa71` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T07:29:34.544Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `1ac0b5fa-4ed6-45b4-9c5a-d89e96074ab1` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T07:29:34.475Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `978e60cb-d613-4cf2-90c8-b738efc4ab48` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T07:29:33.254Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `0cb3c43f-8894-477c-bf4a-9ede25e2717d` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T07:29:31.999Z | 2 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `dd49f314-3355-4f09-b22f-0c3f218212bb` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCSEED seed | 2026-05-02T07:29:21.235Z | 536 | FCSEED-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `d2578f12-360b-4e4c-98e1-10e658a1e5c5` | discarded | monthly | Mon Apr 27 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCSEED seed | 2026-05-02T07:29:19.389Z | 536 | FCSEED-TEST-freeze | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `153cd6ac-cc64-4319-9a11-f7a899eed4a5` | published | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCSEED seed | 2026-05-02T07:29:18.205Z | 0 | FCSEED-TEST-seed | YES | text-token "TEST" in notes/snapshot |
| `20b012f4-9531-4845-926e-5cf936dd728f` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCSEED seed | 2026-05-02T07:29:16.546Z | 536 | FCSEED-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `496aac56-a070-4d8e-8a32-bd2c3cb3d32b` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCSEED seed | 2026-05-02T07:29:16.475Z | 0 | FCSEED-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `510ace7e-8075-4f92-8ca6-29196a50e8ea` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCSEED seed | 2026-05-02T07:29:16.401Z | 0 | FCSEED-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `d0473acb-4e04-463e-a6bd-7584f8eaab2a` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCSEED seed | 2026-05-02T07:27:36.374Z | 537 | FCSEED-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `b9d049c3-df61-49cf-a5bb-aa2a6f9595d5` | discarded | monthly | Mon Apr 27 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCSEED seed | 2026-05-02T07:27:34.530Z | 536 | FCSEED-TEST-freeze | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `53678e22-bb58-4617-8d64-b7de0353e590` | published | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCSEED seed | 2026-05-02T07:27:33.440Z | 0 | FCSEED-TEST-seed | YES | text-token "TEST" in notes/snapshot |
| `d5448a87-bc7a-4250-8e91-e297aa30da1b` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCSEED seed | 2026-05-02T07:27:31.380Z | 536 | FCSEED-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `adf8230c-09fb-4c50-9ae8-108ba93b7f78` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCSEED seed | 2026-05-02T07:27:31.310Z | 0 | FCSEED-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `c25e597f-584e-4507-9409-44c592271af6` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCSEED seed | 2026-05-02T07:27:31.239Z | 0 | FCSEED-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `730a3306-5142-4f16-bc49-96248b1379b1` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-05-02T06:39:26.484Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `3da24255-3c90-4f84-96b5-0d314edfb09e` | draft | weekly | Mon Apr 27 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | T2 Det fixture | 2026-05-01T21:56:41.411Z | 0 |  | YES | text-token "FIXTURE" in notes/snapshot |
| `b9229f29-edd0-49f3-8103-27082522ae63` | draft | weekly | Mon Apr 27 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | T2 Det fixture | 2026-05-01T21:55:24.965Z | 0 |  | YES | text-token "FIXTURE" in notes/snapshot |
| `91e71d3e-9f53-4ed0-8627-9dd38b119d87` | draft | monthly | Mon Apr 27 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Tom | 2026-04-27T13:35:32.460Z | 0 |  | no |  |
| `65fcf4c7-7af2-443e-9945-ece091ed7a58` | discarded | monthly | Mon Aug 23 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCR seed | 2026-04-26T10:35:44.384Z | 2 | FCR-R11-B | YES | text-token "SEED" in notes/snapshot; status=discarded |
| `7b9a7ff1-0f29-4b00-b8d3-125db387dbe1` | discarded | monthly | Mon Aug 23 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCR seed | 2026-04-26T10:35:44.310Z | 2 | FCR-R11-A | YES | text-token "SEED" in notes/snapshot; status=discarded |
| `e041aca8-1c7d-40a4-8a5e-5cbd2810ba34` | discarded | monthly | Mon Jun 14 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCR seed | 2026-04-26T10:35:43.063Z | 4 | FCR-R04 | YES | text-token "SEED" in notes/snapshot; status=discarded |
| `d54262f6-884d-45f2-928d-e8f9ed326d67` | published | monthly | Sun Apr 19 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Test planner | 2026-04-26T10:35:00.333Z | 473 |  | YES | text-token "TEST" in notes/snapshot |
| `22640889-45b5-4ca4-a770-ded1985a28de` | superseded | monthly | Mon Apr 20 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-26T10:34:22.042Z | 472 | FC-TEST-T26-published-A | YES | text-token "TEST" in notes/snapshot; status=superseded |
| `c09f39df-3a87-46a4-ba59-b938e86c3395` | discarded | monthly | Mon Nov 16 2026 00:00:00 GMT+0200 (שעון ישראל (חורף)) | Test planner | 2026-04-26T10:34:21.179Z | 0 | FC-TEST-T21-opendraft | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `5009ba1e-2734-4b05-8675-2d071d548e98` | discarded | monthly | Sun May 10 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Test planner | 2026-04-26T10:34:19.524Z | 0 | FC-TEST-revise | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `74a14e91-354a-4b0d-a83b-4e00eb3f28e8` | published | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-26T10:33:42.147Z | 472 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot |
| `59e411a4-afe5-4ea1-9f73-e942a5a4b8b3` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-26T10:33:41.715Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `5ef8de1d-f39c-49f6-8827-e8a5d69825a2` | discarded | monthly | Mon Apr 20 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-26T10:33:41.285Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `f0574d9a-59de-4143-afc6-972ec37d85c1` | discarded | monthly | Mon Apr 20 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-26T10:33:40.303Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `c14c3c4b-719f-4768-a334-7d13722e96e9` | discarded | monthly | Mon Apr 20 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-26T10:33:39.780Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `ebe8dba0-52b1-4aaa-9329-30e93b080700` | discarded | monthly | Mon May 25 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-26T10:33:38.925Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `a97ff390-3a5c-4fc4-bec9-2efe65585ab8` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-26T10:33:38.487Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `43d315f5-f926-411b-8509-5f9e7c0c3702` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-26T10:33:38.052Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `f549c6ff-bc5a-4737-9a0f-b8119655b48f` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-26T10:33:37.687Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `3f167e33-fbfa-425e-81ea-25b80c0afebe` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-26T10:33:37.608Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `caf8d910-e67a-4b76-b2d1-559cfbe0f209` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-26T10:33:36.655Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `0fb9a66b-2f69-4726-a88b-ac7b7ff288ab` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-26T10:33:35.768Z | 2 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `8df88ff0-8980-4997-aaff-d80347989657` | discarded | monthly | Mon Aug 23 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCR seed | 2026-04-26T10:32:52.794Z | 2 | FCR-R11-B | YES | text-token "SEED" in notes/snapshot; status=discarded |
| `fb600b51-ae40-47a5-a379-31ac4a807fc1` | discarded | monthly | Mon Aug 23 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCR seed | 2026-04-26T10:32:52.721Z | 2 | FCR-R11-A | YES | text-token "SEED" in notes/snapshot; status=discarded |
| `a483c627-f078-43ed-93a5-d832cf9c1fb9` | discarded | monthly | Mon Jun 14 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCR seed | 2026-04-26T10:32:51.599Z | 4 | FCR-R04 | YES | text-token "SEED" in notes/snapshot; status=discarded |
| `347618e7-c1ce-43fb-ba27-302893c3abac` | discarded | monthly | Mon Apr 20 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-26T10:32:10.487Z | 472 | FC-TEST-T26-published-A | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `765e7b38-6180-4ed5-a152-a7cceebadc3d` | discarded | monthly | Mon Nov 16 2026 00:00:00 GMT+0200 (שעון ישראל (חורף)) | Test planner | 2026-04-26T10:32:09.586Z | 0 | FC-TEST-T21-opendraft | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `7f130027-0763-4210-b80d-9d8fbfde06fd` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-26T10:31:32.085Z | 472 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `a6ed28d6-e6a1-40ab-ad5a-5fb2a7e41dc8` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-26T10:31:31.655Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `14970b7c-4b2c-4860-b891-ac2aa5a72829` | discarded | monthly | Mon Apr 20 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-26T10:31:31.225Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `2b42745c-58e6-4a10-8e56-f91ec218b848` | discarded | monthly | Mon Apr 20 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-26T10:31:30.436Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `d6d6b9b0-fe80-4d4d-ba75-1d18a1a38c9c` | discarded | monthly | Mon Apr 20 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-26T10:31:30.002Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `358832f4-25d0-46ff-bdcb-374f465cf5d6` | discarded | monthly | Mon May 25 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-26T10:31:29.275Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `50efdfad-0ab7-4760-846d-c12d2378b5ae` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-26T10:31:28.845Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `873f545b-1edd-4dce-8f07-ab731326b975` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-26T10:31:28.415Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `8a5ab166-5b7e-45be-9816-329a645b1d5b` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-26T10:31:28.058Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `cb091042-b8f4-4fcc-9651-5d544b09924c` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-26T10:31:27.984Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `39ead761-165c-4993-b4fc-27a442c197f8` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-26T10:31:27.008Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `c404feb4-bc9c-4cc9-9777-69696580671e` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-26T10:31:25.981Z | 2 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `d7dec1ca-ec55-407d-934b-6127994f474c` | draft | monthly | Wed Apr 22 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Tom | 2026-04-22T16:30:21.842Z | 0 |  | no |  |
| `4a9438b3-77ac-4255-b299-fe5595364f87` | published | monthly | Sun Apr 19 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Test planner | 2026-04-21T11:54:00.271Z | 497 |  | YES | text-token "TEST" in notes/snapshot |
| `0cfc875d-bcd8-489e-a183-01e9fdda1974` | superseded | monthly | Mon Apr 20 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:53:17.613Z | 496 | FC-TEST-T26-published-A | YES | text-token "TEST" in notes/snapshot; status=superseded |
| `a75735f1-fd23-40de-97d5-7d3c73aa9b08` | discarded | monthly | Sun May 10 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Test planner | 2026-04-21T11:53:14.554Z | 0 | FC-TEST-revise | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `5fa57b5c-e04b-4b85-91a0-fe4405af70d3` | published | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:52:31.548Z | 496 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot |
| `736da34c-06ee-45e7-987e-7f25484cb8cf` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:52:30.934Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `e2680c01-b48f-451b-a43f-2ecd413470c2` | discarded | monthly | Mon Apr 20 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:52:30.285Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `670413d2-a4e6-4dca-8f57-4754ff2da6ae` | discarded | monthly | Mon Apr 20 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:52:28.848Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `b386590f-0a18-454b-8b4c-1e03cae05543` | discarded | monthly | Mon Apr 20 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:52:28.066Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `7df113a5-e29c-43ee-aa7b-05c4c0b33300` | discarded | monthly | Mon May 25 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:52:27.303Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `7fa92309-5d79-4238-85db-5ba74ffb8367` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:52:26.867Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `620ab531-92e2-4e0a-9f6a-3b6017de44f9` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:52:26.432Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `38386523-6ff1-48d2-bf00-087776bf1f94` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:52:26.062Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `c9bc0c03-bbef-4bee-8e6d-4f38e4dd365f` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:52:25.986Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `a2cb1cb1-ae5c-4cd6-861b-5d231a6e5dae` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:52:24.801Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `953facce-8e98-4bf3-84f4-cf6713714546` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:52:22.711Z | 2 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `87167c14-188b-4c7c-b8f4-7913fafb5890` | draft | monthly | Sun Apr 19 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Test planner | 2026-04-21T11:51:55.706Z | 152 |  | YES | text-token "TEST" in notes/snapshot |
| `feddcf6e-3b6d-43f0-a94c-d2142d184c93` | published | monthly | Mon Apr 20 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:51:11.902Z | 496 | FC-TEST-T26-published-A | YES | text-token "TEST" in notes/snapshot |
| `2c2a0c09-96c1-4b3b-a05a-fcf4140b3d61` | discarded | monthly | Mon Nov 16 2026 00:00:00 GMT+0200 (שעון ישראל (חורף)) | Test planner | 2026-04-21T11:51:10.783Z | 0 | FC-TEST-T21-opendraft | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `843e5e4f-db00-41ca-bee2-67236ad41133` | discarded | monthly | Sun May 10 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Test planner | 2026-04-21T11:51:09.103Z | 0 | FC-TEST-revise | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `d50b7e52-4f03-4df0-a7de-0ff3555d3ede` | published | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:50:19.141Z | 496 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot |
| `f75af9ec-c1d6-48f3-96ab-f03ea46d7c4d` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:50:18.688Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `83f37349-44df-4a79-b6e8-7364c29dd4c4` | discarded | monthly | Mon Apr 20 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:50:18.186Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `3979f76b-012c-4162-b03e-e1c8f4ccbc3e` | discarded | monthly | Mon Apr 20 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:50:17.383Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `16d1b5d9-a3b3-48f5-9247-edbd064954ae` | discarded | monthly | Mon Apr 20 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:50:16.944Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `0b82f137-1ce4-4503-a964-295c6a76cbf8` | discarded | monthly | Mon May 25 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:50:16.141Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `06420d84-1211-4ea8-8bb1-0964f78f6011` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:50:15.592Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `a9458719-5d42-443f-a247-23ddf6132ff8` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:50:14.973Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `70e9d51d-a7ad-4ccf-bf72-f35685611d75` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:50:14.551Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `42225b71-0e06-4241-9efe-3657a768ac10` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:50:14.474Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `3fb85df9-d5ee-4293-8257-1dec304ae6ef` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:50:13.444Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `e3f1df53-b780-4994-acbd-4718188d5dca` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:50:12.530Z | 2 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `8f8ef24f-61c1-4d40-86b5-fcee0e337a2f` | discarded | monthly | Mon Apr 20 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:48:34.621Z | 472 | FC-TEST-T26-published-A | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `1018fc3e-b894-43ec-8110-3f122ee02eb5` | discarded | monthly | Mon Nov 16 2026 00:00:00 GMT+0200 (שעון ישראל (חורף)) | Test planner | 2026-04-21T11:48:33.690Z | 0 | FC-TEST-T21-opendraft | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `63e96f34-7dd7-4b56-94aa-fd0ebc16de5a` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:47:53.908Z | 472 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `df3b1ab1-4a03-463a-996b-b8b1307b8930` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:47:53.294Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `dc11137a-fb50-4128-9033-704e9efc8bae` | discarded | monthly | Mon Apr 20 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:47:52.684Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `e1c80fb7-7b34-416b-84f5-35142d1450dd` | discarded | monthly | Mon Apr 20 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:47:51.419Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `2544e302-a882-4594-95ae-55ec170c84f2` | discarded | monthly | Mon Apr 20 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:47:50.987Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `a67342ba-b606-480d-a640-fd5adf6585a3` | discarded | monthly | Mon May 25 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:47:50.270Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `0c26a902-efb0-443e-a2c4-743aeeec372c` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:47:49.840Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `2d478a0a-53ae-44c6-889b-c36ecec0d7f1` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:47:49.410Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `8d6f218a-d651-4eb0-a3b4-73eaff24a2d5` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:47:49.050Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `ced6e843-8c69-48c6-a662-46375cb6966a` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:47:48.977Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `813e2104-4ac6-48e6-8f8a-b017a12676ce` | discarded | monthly | Mon Aug 23 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCR seed | 2026-04-21T11:47:48.668Z | 2 | FCR-R11-B | YES | text-token "SEED" in notes/snapshot; status=discarded |
| `a7b9a5af-279c-4c22-9859-6d9dbc3fdeaf` | discarded | monthly | Mon Aug 23 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCR seed | 2026-04-21T11:47:48.598Z | 2 | FCR-R11-A | YES | text-token "SEED" in notes/snapshot; status=discarded |
| `35c73215-1a2f-4140-b36d-f7cbd4f4c69e` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:47:48.039Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `ab9d469a-7dee-45d2-91c9-3713ce13d4ce` | discarded | monthly | Mon Jun 14 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCR seed | 2026-04-21T11:47:47.503Z | 4 | FCR-R04 | YES | text-token "SEED" in notes/snapshot; status=discarded |
| `d381a684-4587-4767-9008-569225ee059f` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:47:47.138Z | 2 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `ee61d61f-bf65-4796-b65d-911814f87d7a` | published | monthly | Sun Apr 19 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Test planner | 2026-04-21T11:46:57.108Z | 473 |  | YES | text-token "TEST" in notes/snapshot |
| `f100f7ce-aaca-4490-80aa-018883d03718` | superseded | monthly | Mon Apr 20 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:46:17.807Z | 472 | FC-TEST-T26-published-A | YES | text-token "TEST" in notes/snapshot; status=superseded |
| `c4531ad1-69e1-4681-9794-bc3c4af66c00` | discarded | monthly | Mon Nov 16 2026 00:00:00 GMT+0200 (שעון ישראל (חורף)) | Test planner | 2026-04-21T11:46:16.946Z | 0 | FC-TEST-T21-opendraft | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `e2c6d636-8659-4554-9f7e-39fab615053a` | discarded | monthly | Sun May 10 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Test planner | 2026-04-21T11:46:15.209Z | 0 | FC-TEST-revise | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `71f835af-3d78-4cbf-927d-4fbe3bd3b5d1` | published | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:45:33.512Z | 472 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot |
| `65ee6077-b66f-44fa-b667-ba244bcb0d01` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:45:33.039Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `0dd8b1a1-2498-47be-b3cf-34fd5f0ab63e` | discarded | monthly | Mon Apr 20 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:45:32.603Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `38aa97f9-fe9c-403a-aa48-375039632416` | discarded | monthly | Mon Apr 20 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:45:31.726Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `f4521b99-1552-41ff-98b2-c0d1f0947e70` | discarded | monthly | Mon Apr 20 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:45:31.253Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `cf32d3c5-38ef-441d-8bab-f4a6db7c5dd5` | discarded | monthly | Mon May 25 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:45:30.482Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `ed4a4328-31b9-4146-9cc5-f8169238d025` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:45:30.028Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `692f802d-89f5-495b-89ce-1481f9a686cb` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:45:29.600Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `cc074b6d-264a-4736-bc1c-abf6dee41973` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:45:29.238Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `4623305c-45d0-49f1-8c5c-17579f6cae1a` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:45:29.162Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `520d4899-5518-4dff-97fa-822ff8181da9` | discarded | monthly | Mon Aug 23 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCR seed | 2026-04-21T11:45:28.966Z | 2 | FCR-R11-B | YES | text-token "SEED" in notes/snapshot; status=discarded |
| `6bc7d372-5415-4504-954e-ed2789b74197` | discarded | monthly | Mon Aug 23 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCR seed | 2026-04-21T11:45:28.893Z | 2 | FCR-R11-A | YES | text-token "SEED" in notes/snapshot; status=discarded |
| `9b10806b-f7f2-4bdc-b60a-b2c6d54bbf44` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:45:28.207Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `632ca428-1441-43a0-b686-89c0c48aa20a` | discarded | monthly | Mon Jun 14 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCR seed | 2026-04-21T11:45:27.774Z | 4 | FCR-R04 | YES | text-token "SEED" in notes/snapshot; status=discarded |
| `c3c1a599-f5ad-46dd-9b3e-2ad16e9e37fd` | discarded | monthly | Mon May 11 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-21T11:45:27.295Z | 2 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `5a783133-435d-4368-a7c9-95de4ec7fec0` | discarded | monthly | Mon Apr 13 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T17:06:57.937Z | 464 | FC-TEST-T26-published-A | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `00c2e192-3425-4555-a013-3af53b91e2ca` | discarded | monthly | Mon Nov 09 2026 00:00:00 GMT+0200 (שעון ישראל (חורף)) | Test planner | 2026-04-18T17:06:56.870Z | 0 | FC-TEST-T21-opendraft | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `6dd9568d-033e-42a7-8aa3-75a64e3d4338` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T17:06:22.910Z | 464 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `cf5e7264-56bb-4226-b29f-d6c86adf7e7c` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T17:06:22.511Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `531e8af2-f8ca-4955-bb60-16e6241465d7` | discarded | monthly | Mon Apr 13 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T17:06:22.119Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `edcbea9a-3625-4533-b4ce-881f54f68aec` | discarded | monthly | Mon Apr 13 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T17:06:21.399Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `e3709859-c1d4-4063-84fc-510c99a864db` | discarded | monthly | Mon Apr 13 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T17:06:21.008Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `c90f76c2-120f-4e4b-8dae-e532bcc4cfe9` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T17:06:20.350Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `256b61d0-85da-4406-bc5d-93350108221b` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T17:06:19.946Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `7c627fdb-d980-4c47-b557-e02d438b0634` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T17:06:19.548Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `b99790b1-78f3-47ae-94c5-5ab5789cda77` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T17:06:18.802Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `88516005-6dd6-48fd-90b1-3c77e687dae7` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T17:06:18.620Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `36518ddd-f4df-4b0f-9f98-a01de2e58c3d` | discarded | monthly | Mon Aug 16 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCR seed | 2026-04-18T17:06:18.413Z | 2 | FCR-R11-B | YES | text-token "SEED" in notes/snapshot; status=discarded |
| `1045c6fb-3e95-4e98-8670-ae2678de176b` | discarded | monthly | Mon Aug 16 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCR seed | 2026-04-18T17:06:18.346Z | 2 | FCR-R11-A | YES | text-token "SEED" in notes/snapshot; status=discarded |
| `9d36e6d0-baf7-4f96-9d14-aa0e294a5160` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T17:06:17.748Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `e5db6483-720e-4604-a041-e9f4bacec963` | discarded | monthly | Mon Jun 07 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCR seed | 2026-04-18T17:06:17.332Z | 4 | FCR-R04 | YES | text-token "SEED" in notes/snapshot; status=discarded |
| `4f8a9646-186d-43eb-abf3-05a8c19687a7` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T17:06:16.936Z | 2 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `27cac61c-fc5b-4c8d-a7e3-0aa391ca6b82` | discarded | monthly | Mon Aug 16 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCR seed | 2026-04-18T16:07:42.957Z | 2 | FCR-R11-B | YES | text-token "SEED" in notes/snapshot; status=discarded |
| `873383a3-917e-49c8-ac94-043f5e9a0760` | discarded | monthly | Mon Aug 16 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCR seed | 2026-04-18T16:07:42.891Z | 2 | FCR-R11-A | YES | text-token "SEED" in notes/snapshot; status=discarded |
| `677aaf39-43b1-45ef-abbb-9fe6e6ee9506` | discarded | monthly | Mon Jun 07 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCR seed | 2026-04-18T16:07:41.883Z | 4 | FCR-R04 | YES | text-token "SEED" in notes/snapshot; status=discarded |
| `6e2b2226-3f10-4f9f-999f-fe52876e9b9a` | published | monthly | Sun Apr 12 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Test planner | 2026-04-18T16:06:57.559Z | 465 |  | YES | text-token "TEST" in notes/snapshot |
| `64f9e28a-6840-4a06-8058-f495c085ab10` | superseded | monthly | Mon Apr 13 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T16:06:22.339Z | 464 | FC-TEST-T26-published-A | YES | text-token "TEST" in notes/snapshot; status=superseded |
| `e3321048-9de4-4664-af00-ae97e8fd5e6d` | discarded | monthly | Mon Nov 09 2026 00:00:00 GMT+0200 (שעון ישראל (חורף)) | Test planner | 2026-04-18T16:06:21.554Z | 0 | FC-TEST-T21-opendraft | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `7de0c443-ad83-4011-9100-edd1bf7c52da` | discarded | monthly | Sun May 03 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Test planner | 2026-04-18T16:06:20.034Z | 0 | FC-TEST-revise | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `2e752458-34a0-4662-8ff3-0c16bf80460b` | published | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T16:05:44.223Z | 464 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot |
| `46942e0b-9a5b-49a9-9944-61dc904c8389` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T16:05:43.829Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `4cddd59c-4c0c-499a-a7c8-5311ab04fbf6` | discarded | monthly | Mon Apr 13 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T16:05:43.442Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `754e077b-ca78-4a26-a17f-11f8f60fa2e8` | discarded | monthly | Mon Apr 13 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T16:05:42.734Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `5b1f622e-2b7d-44f8-b8d4-b0a7cc2506c5` | discarded | monthly | Mon Apr 13 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T16:05:42.344Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `c34b8a6d-e048-49da-85c3-f5766465c7e3` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T16:05:41.698Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `33e2b412-4ef3-49ff-b002-73e5e6c4fa9d` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T16:05:41.300Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `8f44c23a-7b53-4f99-90d1-746e68643fac` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T16:05:40.838Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `8221aa71-b52a-444f-8bf0-0470059ff511` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T16:05:40.295Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `ff3dc659-9ea4-468e-bd70-4072d5f9f35b` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T16:05:40.226Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `5aa8d7a4-939c-45b9-8699-97ffdf17e651` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T16:05:38.862Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `9f5c0aad-2850-4ec1-a62d-a5a8aa399278` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T16:05:37.666Z | 2 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `501665c6-1ee8-4aec-8ec9-1be221d97c02` | published | monthly | Sun Apr 12 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Test admin | 2026-04-18T16:04:17.916Z | 465 |  | YES | text-token "TEST" in notes/snapshot |
| `cc5fd06d-1ec0-4471-83fb-61b418133906` | superseded | monthly | Mon Apr 13 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T16:03:42.787Z | 464 | FC-TEST-T26-published-A | YES | text-token "TEST" in notes/snapshot; status=superseded |
| `b0b8c304-2c1d-475d-8376-f95744eb3762` | discarded | monthly | Mon Nov 09 2026 00:00:00 GMT+0200 (שעון ישראל (חורף)) | Test planner | 2026-04-18T16:03:41.997Z | 0 | FC-TEST-T21-opendraft | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `c6a06b77-660b-4886-9259-720328f2c4ee` | discarded | monthly | Sun May 03 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Test planner | 2026-04-18T16:03:40.416Z | 0 | FC-TEST-revise | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `29604242-2ddb-4144-a4f7-930b9b89dc6d` | published | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T16:03:05.528Z | 464 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot |
| `3773462f-9470-400b-a0a8-9d64076af0d3` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T16:03:05.132Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `5a830e85-a3c3-438e-ab4f-7c1fa33fd377` | discarded | monthly | Mon Apr 13 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T16:03:04.732Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `875830da-9bab-445c-a25f-2af1f9b8ee3d` | discarded | monthly | Mon Apr 13 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T16:03:04.006Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `f56331e6-48ff-4806-bbea-eeb6c38ee5ce` | discarded | monthly | Mon Apr 13 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T16:03:03.609Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `e331f25b-3458-4ccd-b06c-8dfc3ee5017e` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T16:03:02.734Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `d484aa88-4367-4861-a42b-d1f9a64f6197` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T16:03:02.118Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `7d1cd00b-56a8-401f-b520-e3e7619c4b95` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T16:03:01.504Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `d3f607e5-210e-4ffb-84bb-b6f92180392a` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T16:03:00.964Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `3c4d5c1f-ae40-434e-badc-b90c5b514cbe` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T16:03:00.894Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `2ffe563b-e2e7-41cd-9e64-967c8fb6301e` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T16:02:59.665Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `b2b584e6-f15c-4c13-b3fd-1b1968f3c726` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T16:02:58.835Z | 2 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `d63b110c-1c6b-41a1-bd05-594d75a28d12` | published | monthly | Sun Apr 12 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Test admin | 2026-04-18T15:58:44.458Z | 465 |  | YES | text-token "TEST" in notes/snapshot |
| `b0dc9838-faa0-4cf6-9809-fabfbab8b6ea` | superseded | monthly | Mon Apr 13 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:58:10.621Z | 464 | FC-TEST-T26-published-A | YES | text-token "TEST" in notes/snapshot; status=superseded |
| `081a02bd-8c07-4f4f-a9cc-785e3eb2b58e` | discarded | monthly | Mon Nov 09 2026 00:00:00 GMT+0200 (שעון ישראל (חורף)) | Test planner | 2026-04-18T15:58:09.741Z | 0 | FC-TEST-T21-opendraft | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `daefe570-eb99-4f10-b720-68d373ded55e` | discarded | monthly | Sun May 03 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Test planner | 2026-04-18T15:58:08.247Z | 0 | FC-TEST-revise | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `7303fabc-085e-47a1-aef8-17dfbfbad2d1` | published | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:57:32.140Z | 464 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot |
| `22582c8a-d6d8-45bb-b611-efd6ead62d3d` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:57:31.741Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `98223d9a-1e58-46b4-98f3-797069848e99` | discarded | monthly | Mon Apr 13 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:57:31.347Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `ecbdfd61-3937-4fcd-b05b-ee0dc5fa381d` | discarded | monthly | Mon Apr 13 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:57:30.621Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `457a928e-1d21-46e8-b2f0-de56775ba2c2` | discarded | monthly | Mon Apr 13 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:57:30.228Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `cc17fde1-7694-4149-862b-40f843ca5347` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:57:29.572Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `0c5f1382-4cd6-4677-94e9-ae9e66dba0f2` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:57:29.182Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `c1076981-e699-4601-9400-6bf0771ceb30` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:57:28.793Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `bfc38af5-bec1-472e-82f3-e541685c84f3` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:57:28.466Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `acffbf1e-862c-4a6d-83fc-656d37db0305` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:57:28.398Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `7199bac0-c496-49a9-b5ab-ec287af1594a` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:57:27.480Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `85262b1f-9d91-42a6-bcdd-f357dca01d2b` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:57:26.108Z | 2 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `62c00520-ccc6-44d0-9feb-ea0a0c6f621c` | discarded | monthly | Mon Aug 16 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCR seed | 2026-04-18T15:57:09.262Z | 2 | FCR-R11-B | YES | text-token "SEED" in notes/snapshot; status=discarded |
| `86c4dddb-04cd-423c-bc7d-5b0ee090bc00` | discarded | monthly | Mon Aug 16 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCR seed | 2026-04-18T15:57:09.195Z | 2 | FCR-R11-A | YES | text-token "SEED" in notes/snapshot; status=discarded |
| `934a91d1-e226-4226-8494-b238f9779ba4` | discarded | monthly | Mon Jun 07 2027 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FCR seed | 2026-04-18T15:57:08.145Z | 4 | FCR-R04 | YES | text-token "SEED" in notes/snapshot; status=discarded |
| `21ed4d4b-1fdc-4b83-93b5-1cf3d4f4ce55` | discarded | monthly | Sun May 03 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Test planner | 2026-04-18T15:05:17.115Z | 0 | FC-TEST-revise | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `13c7650b-8af3-424e-ab65-40a629832361` | published | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:04:40.070Z | 464 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot |
| `624d1d8c-a682-45b9-85ef-a2964700ec1c` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:04:39.681Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `b7a99533-f0ed-4954-95f4-72d0d652b628` | discarded | monthly | Mon Apr 13 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:04:39.287Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `9be34a49-6f43-46f9-babd-4e3499c90de3` | discarded | monthly | Mon Apr 13 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:04:38.568Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `2218421c-b534-46d1-b73f-c434699404e0` | discarded | monthly | Mon Apr 13 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:04:38.028Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `369f34cd-8d4e-4ad9-b7c7-d77a630971be` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:04:37.003Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `fb78f278-e58b-4f18-96f1-0ddd960d2302` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:04:36.387Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `b58b30e7-ca17-457c-b9d3-1810e1dd4e65` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:04:35.776Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `df79be17-5dbe-4161-ac89-0d1721493386` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:04:35.301Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `0c4abd3f-840d-444a-a97f-10cfaade581e` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:04:35.176Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `7fa1251a-1cf9-4d66-a0c2-4e1b934647dc` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:04:34.094Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `db31659e-7d21-4aba-b1e4-8e3865c8b770` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:04:33.275Z | 2 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `69aa2387-bcfc-42e8-b95e-ecaff871dd4b` | discarded | monthly | Sun May 03 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Test planner | 2026-04-18T15:03:46.411Z | 0 | FC-TEST-revise | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `4eb624a7-f3e0-4edc-a957-657b4bff7bc2` | published | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:03:09.876Z | 464 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot |
| `fa9b2a0e-884f-42a4-8256-529a31497a79` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:03:09.481Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `8a1fe606-a008-43d6-b9ef-84f216dcbc2d` | discarded | monthly | Mon Apr 13 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:03:09.094Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `1756468d-8235-4233-8be3-841a60488ef8` | discarded | monthly | Mon Apr 13 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:03:08.374Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `04e7e57d-d87b-4235-ac2f-6cab0b109973` | discarded | monthly | Mon Apr 13 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:03:07.983Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `875916bf-263d-4093-b084-23e5e64650aa` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:03:07.325Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `fed347e3-157c-434a-b09c-2ba2ee945724` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:03:06.937Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `8740e6aa-30b0-4adb-992e-3312fa8a1ab0` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:03:06.543Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `630eb5de-82c1-4fab-915e-aa1559edc34f` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:03:06.216Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `ba8d5119-7830-422c-86e3-f4b182eb8af9` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:03:06.148Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `4bd11008-76d1-495e-9d3b-388417b17d28` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:03:05.293Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `63e5fc59-1159-452b-abe4-71f777cee6a3` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:03:04.367Z | 2 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `c5327a25-def2-4388-beb5-b3d1b6489567` | discarded | monthly | Sun May 03 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Test planner | 2026-04-18T15:02:54.193Z | 0 | FC-TEST-revise | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `0fbc609f-c39e-4b54-ab3c-72fcfb84a902` | published | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:02:17.947Z | 464 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot |
| `40c089fc-8897-4475-8a18-14f0328e845c` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:02:17.555Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `aaa5df61-1e6d-4265-8b67-b299a4bbb2db` | discarded | monthly | Mon Apr 13 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:02:17.160Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `7006bea2-2747-4a6c-a7a6-b7f0accd6c60` | discarded | monthly | Mon Apr 13 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:02:16.443Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `dc62af04-0a3c-40da-b269-c7925873d68f` | discarded | monthly | Mon Apr 13 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:02:15.837Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `5a8f8dba-974e-4b8e-a41c-4c532e218458` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:02:14.804Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `0205b512-db8c-4cb9-8ed5-0c57f341591f` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:02:14.201Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `19cb3f82-f2b1-4a40-bc68-81bb44fda619` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:02:13.644Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `00aeff3b-01a4-4788-8985-8040d645b2ba` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:02:13.246Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `b787e53a-d515-441a-9cbb-3277f2c6f572` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:02:13.179Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `ff0d3704-cee4-4d15-b849-61365e722c7f` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:02:12.337Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `bc8c9be6-c4c7-47f7-9561-1a92c2f02267` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:02:11.521Z | 2 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `2fef81e4-d253-446d-a5b2-d9f77bf1cc92` | discarded | monthly | Sun May 03 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | Test planner | 2026-04-18T15:02:00.480Z | 0 | FC-TEST-revise | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `ee47516d-bd08-4360-9e71-233168a7eee3` | published | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:01:23.350Z | 464 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot |
| `fe7a1a91-4470-4668-90cd-e1898cc73656` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:01:22.954Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `d2212b84-94e7-4953-b3c8-51aa926592ff` | discarded | monthly | Mon Apr 13 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:01:22.559Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `ce5db4d1-ced3-40cb-bf50-431785a4d726` | discarded | monthly | Mon Apr 13 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:01:21.835Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `95959606-0af5-435d-b7c0-956f59104ec4` | discarded | monthly | Mon Apr 13 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:01:21.435Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `dacf75f9-20b2-4f65-ad21-ecc14492c1ee` | discarded | monthly | Mon May 18 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:01:20.773Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `b0d8651e-3375-49f2-bf9a-024b32a4f610` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:01:20.375Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `2a93c15f-52c7-4025-8fc7-19a4dd202c5c` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:01:19.978Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `6d556c39-a352-4cc0-b6a8-953af87984e4` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:01:19.646Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `bf02747e-066e-4016-a9bf-a406c3ccedf7` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:01:19.578Z | 0 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `198557dc-d678-4d06-92b2-cbe71915735a` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:01:18.292Z | 1 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |
| `08b615d1-be36-455c-bcaf-57b95f3a0a18` | discarded | monthly | Mon May 04 2026 00:00:00 GMT+0300 (שעון ישראל (קיץ)) | FC seed | 2026-04-18T15:01:17.043Z | 2 | FC-TEST-seed | YES | text-token "TEST" in notes/snapshot; status=discarded |

## qty pattern (top 20 most-frequent values)

| forecast_quantity | rows |
|---|---|
| 1.00000000 | 23716 |
| 0.00000000 | 6573 |
| 25.00000000 | 96 |
| 50.00000000 | 60 |
| 42.00000000 | 48 |
| 100.00000000 | 45 |
| 10.00000000 | 25 |
| 60.00000000 | 25 |
| 99.00000000 | 24 |
| 200.00000000 | 22 |
| 77.00000000 | 19 |
| 123.00000000 | 19 |
| 999.00000000 | 11 |
| 110.00000000 | 10 |
| 240.00000000 | 10 |
| 90.00000000 | 5 |
| 80.00000000 | 5 |
| 40.00000000 | 5 |
| 42.50000000 | 4 |
| 70.00000000 | 4 |

Round-number stats:
- integer-only qty rows: 30724 / 30728
- multiples of 10:       6790 / 30728
- multiples of 100:      6641 / 30728
- zero qty rows:         6573 / 30728

## created_by breakdown

| user_id | email | role | status | versions | total_lines |
|---|---|---|---|---|---|
| `cccccccc-0000-0000-0000-000000000f01` | fctest-planner@fctest.gt | planner | active | 242 | 14806 |
| `cccccccc-0000-0000-0000-000000000fc1` | fcm-planner@fcm.gt | planner | active | 140 | 235 |
| `cccccccc-0000-0000-0000-000000000f03` | fctest-admin@fctest.gt | admin | active | 58 | 8997 |
| `dddddddd-0000-0000-0000-000000000f01` | fcrtest-planner@fcrtest.gt | planner | active | 36 | 96 |
| `cccccccc-0000-0000-0000-000000000fa2` | fcseed-admin@fcseed.gt | admin | active | 12 | 4385 |
| `cccccccc-0000-0000-0000-000000000fa1` | fcseed-planner@fcseed.gt | planner | active | 12 | 2192 |
| `eeeeeeee-0000-0000-0000-00000000e001` | t1reg@test.gt | planner | active | 4 | 4 |
| `0db008a9-05e3-4521-8b30-42e5d444818d` | tom@gteveryday.com | admin | active | 4 | 13 |
| `ffff0002-0000-0000-0000-000000000e01` | t2det-planner@t2det.gt | planner | active | 2 | 0 |

## Suspect text matches

Tokens scanned: TEST, SEED, SMOKE, FIXTURE, DEMO, PLACEHOLDER, DUMMY, SAMPLE, GOLDEN, CYCLE, W1, W2, W4

| version_id | status | created_by_snapshot | notes |
|---|---|---|---|
| `d3122b1e-8376-470c-b761-1be290353ebc` | published | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `c8b49e39-cd32-44d3-b739-0474e8b6b321` | published | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `3bc3ae80-c72d-4d8f-b6d1-d33285403e3b` | published | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `9421e357-bcf8-4c86-9f33-22e066db5175` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `d2c901dc-195d-45e9-b76b-a9d912e3f2eb` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `5beed049-023c-4b12-a583-1d052b6b6a2c` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `2af43cc4-b4bb-4c6e-a901-eb92dac5cffa` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `eaa99565-1ab8-4d04-bb9f-d8e0c93cb5b0` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `154f6207-2f58-48f2-ac13-62be69927811` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `cc2b44e0-af15-41d7-9aa0-faa76fd62dfb` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `d1414cab-e9df-4469-b664-12ebb94caa5d` | published | FCM weekly fixture | FCM-TEST-weekly-regression |
| `a82259cf-ac46-417b-9cc7-1ef81177d382` | published | Test planner |  |
| `82d638d1-5a96-472c-b828-082465999cd2` | superseded | FC seed | FC-TEST-T26-published-A |
| `0ae068e7-a157-4dff-8391-0c3892939b55` | discarded | Test planner | FC-TEST-T21-opendraft |
| `b125ce5a-9b1e-4f73-af26-a46f053c738a` | discarded | Test planner | FC-TEST-revise |
| `c51f3502-59da-4620-aa07-08e21df417fd` | published | FC seed | FC-TEST-seed |
| `cd6306fe-d52b-4917-b67a-26a25da096a9` | published | FC seed | FC-TEST-seed |
| `79ce677e-493e-4c28-b0c7-f39f48768350` | discarded | FC seed | FC-TEST-seed |
| `f387c924-f180-4317-8a3f-352320d84786` | discarded | FC seed | FC-TEST-seed |
| `9e0fc4c7-7666-4681-8fdd-f42fd6057c78` | discarded | FC seed | FC-TEST-seed |
| `f7831868-2a55-4382-90f5-0e7084ad9144` | discarded | FCSEED seed | FCSEED-TEST-seed |
| `3d724977-880d-470f-8906-1f82a7373a60` | discarded | FC seed | FC-TEST-seed |
| `ac696c66-c100-4163-8284-91a5847fdd7e` | discarded | FC seed | FC-TEST-seed |
| `3583314b-b3c9-4e12-ba2d-933ef92c489e` | discarded | FCSEED seed | FCSEED-TEST-freeze |
| `735511db-ed2a-444b-8df3-0510455e783c` | discarded | FC seed | FC-TEST-seed |
| `dd62e15d-d4ec-49db-a53f-48bfd68a677f` | discarded | FC seed | FC-TEST-seed |
| `5ba28923-c177-457e-b2c0-85e525edfabe` | discarded | FC seed | FC-TEST-seed |
| `95322bb2-a55d-49c4-af30-426a526ae19b` | published | FCSEED seed | FCSEED-TEST-seed |
| `81f44e2b-fe16-489c-ba1e-0f0a644013f8` | discarded | FCR seed | FCR-R11-B |
| `0b932e03-6a69-4c7d-8fe8-adc7239a3221` | discarded | FCR seed | FCR-R11-A |
| `b6fdb726-352e-4130-9886-ea03a59404d0` | discarded | FC seed | FC-TEST-seed |
| `3ecdbc1c-335b-4aac-a9d0-1d97e63018f8` | discarded | FCR seed | FCR-R04 |
| `174985db-dc96-42c8-bcfa-f47dd6d309ba` | discarded | FCSEED seed | FCSEED-TEST-seed |
| `75a63bd7-26c6-446c-8e54-b25d29c1f907` | discarded | FC seed | FC-TEST-seed |
| `bae4a977-7016-4944-ac90-76a05334974a` | discarded | FCSEED seed | FCSEED-TEST-seed |
| `c770b846-e98a-4ac5-b67a-f8167759ea4f` | discarded | FCSEED seed | FCSEED-TEST-seed |
| `ef6db32d-8d2c-48eb-94fd-73c672defe4b` | published | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `cd54f93d-3c1e-4d59-ad3c-d478381a7e7e` | published | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `250220d8-d673-4dfa-963f-10d623791810` | published | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `92624e9a-fdc3-46bf-8665-7a1ad3dddb75` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `947f74a2-2e2a-4ac6-87f3-24a91a0df367` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `9066e154-b768-459f-8bcc-5566265a52a5` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `5c81a5e9-21a3-4419-a162-97346916e023` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `1b53a347-9f44-4f23-8893-de57d976911b` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `91664d67-a6a3-4a3a-8262-ea0c46c63c94` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `03a892ab-8b54-4e03-97df-14a09c594c81` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `30526c20-8b6d-4456-a44b-75fac7e820b2` | published | FCM weekly fixture | FCM-TEST-weekly-regression |
| `71cf40cc-98af-41a4-98e8-474c3f794747` | published | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `f19d7a29-bbcf-4ace-830e-4e860ae4881d` | published | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `82263079-54f4-4839-91b6-1d1f8c9bd6de` | published | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `4aaa4f7f-070b-4c73-a1b0-c214a54a68dc` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `9ab76c2c-989d-421f-9a87-bad4f6dbc731` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `8e7b7ab0-b2ca-46c4-bf99-28b0b9826061` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `b719932e-3b2c-4203-b115-47c691e5e646` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `1b731ac7-1a5d-4455-a73f-93fcc84a08c3` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `73ee9202-30a2-4667-9fe6-7fb6d3549b8f` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `99b3a1ee-fa2f-4174-9839-153bdd693ac9` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `4074e68a-56ed-4465-8984-c6132a893546` | published | FCM weekly fixture | FCM-TEST-weekly-regression |
| `c9cbb602-91bf-4e63-b5dc-711209b36eaf` | published | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `cd91bab3-3537-4779-b13b-bdd50ae630db` | published | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `4902139f-8437-41a2-ba46-d2cb5ea847a3` | published | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `9357edcf-37e5-4e6a-8f59-3b88447681dd` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `8a528eee-1be3-4959-a271-1b67e6d153d7` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `47d6cdf2-4572-4fd5-80e8-52446e7a4da1` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `c3ae231d-aa41-42c0-a884-d1462c1bd8d0` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `62399eaa-b2c1-45d9-a676-a63ba03d3382` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `0eefe792-3d8d-4047-91e6-5a477d0c7eed` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `47c308f0-c387-4c17-a43d-0ebb1748b9fc` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `39b8dcb0-b315-4ee1-8fc2-8af180bce37e` | published | FCM weekly fixture | FCM-TEST-weekly-regression |
| `e433a9fc-58c6-4c2d-8558-6e25673b3f04` | published | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `e1def1d6-1347-4bd1-8796-6d4107709643` | published | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `db00590d-f916-44bf-ad93-3a8494d6ce56` | published | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `3c19abe3-ef04-40fb-a65f-281f582860b1` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `89326502-acfc-43d8-a580-17a9c0154362` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `4b47050c-7e73-4086-988a-e1e56bfa3348` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `40bf6ab4-302a-4ada-ad7e-78b3d5d0d30a` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `943decaf-edfc-4482-a807-ac739859e13c` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `433d6aa0-7ff6-4db1-b09d-468a0e595218` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `c89ff724-3a19-41bb-8d05-235ab2b1a544` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `0aee3a9b-71f6-484d-a565-e50dc7c434c3` | published | FCM weekly fixture | FCM-TEST-weekly-regression |
| `afbdbea4-bfe8-445f-b713-b76981d9d0b6` | published | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `440944cb-322a-4c6e-bf73-358857ad7ee4` | published | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `a2f64133-5f85-46aa-a975-73533a8c8020` | published | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `f3206f83-a940-489a-9ed1-4820b6770229` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `cce9c6b5-3a50-4361-b74e-c0f3a9fc3815` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `da534b2b-1c0c-4004-8bf9-509fe71b40e7` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `9b312d13-af07-494c-8b2b-5fb2b97692db` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `4e42f59a-649e-45c8-8829-8bbb88ba8055` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `fdcf562d-038e-425c-acb9-4b5d00fa1f40` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `106b9638-2578-4ccc-bb71-507f5ded3cc8` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `6d6d82f1-1eef-4edd-a737-9545c56e7eb1` | published | FCM weekly fixture | FCM-TEST-weekly-regression |
| `d70cb6b3-5f2f-4ff2-9e32-540a49ce6a4c` | published | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `37cbcc4d-1c66-42d1-bd42-521b8d2bef14` | published | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `edbf350b-d2d9-432b-a35d-895414fca1af` | published | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `7b8c6d39-ccc7-416c-9d24-960883020836` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `0b383a8f-7dbf-4015-bb2e-36975a807051` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `6e95c09b-d225-438d-86d2-3eb3482590f3` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `1979d5b8-821e-4322-8f11-43b407084293` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `bdde77b0-f2f1-4aa8-a3e6-7c3b369cd11a` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `3375534d-5dbe-478b-ae78-6a26570a47e8` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `0f255b7e-b0dd-45de-9a3f-23efd81d6d49` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `07daba3c-b4ae-4b3b-bc56-b99351dc8afb` | published | FCM weekly fixture | FCM-TEST-weekly-regression |
| `f07cc43b-aab8-4b35-89a4-f87dca737f2b` | published | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `b0f71d5c-94af-4cb9-9dd2-02d7228e0c1e` | published | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `412c42ef-3e79-4611-b579-cfa7bedc68f6` | published | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `8b2a6b97-8d0c-4310-9dce-33bb7b44e60b` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `0604aced-f5bd-49a1-988b-0bf8a97eb3df` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `031d0e30-f8dc-46ad-93c2-50542c887255` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `28fe13e0-2491-4281-9c58-a3e077733d9f` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `97e06b56-d25b-4b87-9b73-734e6b96c0c8` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `c4df879b-c4d5-43b9-a436-533a42289897` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `2c027d31-312f-4cb5-b717-00da60e40622` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `ca960ec1-b069-4f43-8a3d-49527c3cb45f` | published | FCM weekly fixture | FCM-TEST-weekly-regression |
| `6e82c327-d42e-4bf4-a4af-7e504303c767` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `600a2753-7a12-46af-95aa-443e56ea3062` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `965f8fcc-5059-4386-a3c6-c436f8d198ce` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `d2e91023-1b65-49c8-ab39-0706d524fdce` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `d6c2738f-6033-4704-9797-6c173ced539a` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `fceb18d7-e48b-4df7-ba40-a66cb353586d` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `bc0e030c-55a1-4a2d-b4b3-547bd0072399` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `b9a7ab92-9352-404d-838e-dfa6a7859db4` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `18622d9f-26ad-440c-a0e6-ea1e0844b02a` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `251f311c-ee02-4ec1-ba92-f52d5b953a98` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `07d4f6fd-dd2d-429e-b400-4c8bb6b09d52` | published | FCM weekly fixture | FCM-TEST-weekly-regression |
| `b5e71ed1-a5b3-48ff-a308-2b3b85dfb77f` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `e40954b3-2e87-4574-99f7-82e0518e671e` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `44c6f946-6f2a-4edd-b23f-9d1b4e50878f` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `f782b5a9-8fd4-42f5-95ae-fc3a575df48f` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `1bd4e270-30de-4506-aed9-7d5bb0fe6140` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `05b890da-561e-4d64-8903-86ad5f51ec7e` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `68f6e9c9-e62d-4623-8e93-54e538c52eb3` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `502fce32-b17d-4d43-adf0-cdf88fa3792c` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `72a0dc52-e9a8-4f06-b540-fc9acb4da482` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `1e710569-9771-4496-8919-11e198832553` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `958e2280-d592-4152-84ea-b6e39754938f` | published | FCM weekly fixture | FCM-TEST-weekly-regression |
| `b5fe8e3e-8e41-40da-826e-66f2b9252071` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `30f05e61-7f60-4790-b32d-b12b29e20a02` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `d268e640-2bdc-4916-b370-46b829e509ba` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `67a93b2b-e2d8-409a-9707-5c43f01b33c1` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `edff5aca-8aca-4fdc-b608-e328a3464084` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `32d14b79-776b-4f04-881a-1ebcdaa8be1f` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `23a55923-019a-468e-81d4-81295c001474` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `6e242a72-f58e-40c6-a8ac-663dc2872886` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `0c90e9cd-5981-4170-8b9c-7c035c37bfbc` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `8908d07e-3539-4966-b9e3-3352e094eb3c` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `3fdba978-64f6-4226-aa95-48536be1fd32` | published | FCM weekly fixture | FCM-TEST-weekly-regression |
| `e49c7729-aa40-431e-bc4c-685986d0bca2` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `8da35773-8734-48c7-a407-6f5ea6fe0ccf` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `76e80e2e-2509-4445-936a-375729bbb990` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `a828e572-fe3f-4a45-9849-1d38ced462ea` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `3ce37944-e5de-41a6-9f3c-b1d1c884dbfb` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `b8d67871-2a49-4f3f-967c-8133defb69ed` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `d39f85ce-6110-423f-92c6-6a8fad9dacb5` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `7a099afa-5e1c-449d-a718-a02dd8c81540` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `03c2b3e4-812f-43ed-88ea-02c6e9228aaa` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `c6f92b2c-1df3-48b1-894e-79ced89d59eb` | discarded | FCM-Chunk3-seed | FCM-TEST-Chunk3 |
| `e7f0ff94-cf69-4b26-bfb7-c500807d5ea8` | published | FCM weekly fixture | FCM-TEST-weekly-regression |
| `389cfbc4-a221-40b9-89f0-4196609eb66b` | discarded | FCSEED seed | FCSEED-TEST-seed |
| `84f3dd7d-8432-45f8-bb09-520428dd1716` | discarded | FCSEED seed | FCSEED-TEST-freeze |
| `8a558b6f-936a-4357-85e7-51fac07e2784` | published | FCSEED seed | FCSEED-TEST-seed |
| `04656c9c-cc1c-45b9-9a72-0f00437914b4` | discarded | FCSEED seed | FCSEED-TEST-seed |
| `6932fc76-a1e2-44cd-9526-178b979a4b9c` | discarded | FCSEED seed | FCSEED-TEST-seed |
| `9057dfed-8581-469d-aab1-2e693d838b83` | discarded | FCSEED seed | FCSEED-TEST-seed |
| `9b8cd486-0c49-406d-a0c4-60ece566ec40` | discarded | FCR seed | FCR-R11-B |
| `e85eeaa2-a022-4f5e-b459-2d048dfeec10` | discarded | FCR seed | FCR-R11-A |
| `1ca3c5e9-e49f-48c9-9b6a-8dc39e8439e3` | discarded | FCR seed | FCR-R04 |
| `c5df7116-37c4-4495-b51c-bc24ec923e94` | discarded | FCR seed | FCR-R11-B |
| `354e24ea-e3d4-4686-8424-38b0906bb2d8` | discarded | FCR seed | FCR-R11-A |
| `e7932936-41b5-4dc5-93b4-9a9a10f7dbab` | discarded | FCR seed | FCR-R04 |
| `8b6568d6-2ca4-43a9-b851-d06030f56bff` | discarded | FCR seed | FCR-R11-B |
| `66fba83c-5e64-4fb0-be3b-ad8ff97cca17` | discarded | FCR seed | FCR-R11-A |
| `e483c740-7e40-48bb-928b-71d64b2a1410` | discarded | FCR seed | FCR-R04 |
| `87a2f408-114c-4cae-9ed8-aa60ea117349` | discarded | FCR seed | FCR-R11-B |
| `5116691c-3030-4962-a0b5-4ef151431f3a` | discarded | FCR seed | FCR-R11-A |
| `2398d37d-8229-424a-b7f9-94f8c4401a7a` | discarded | FCR seed | FCR-R04 |
| `d8d076ef-6b1b-40ba-96b5-34bc58186d69` | published | Test planner |  |
| `b79dcae3-fca4-4b79-8152-3c6f1335a19c` | superseded | FC seed | FC-TEST-T26-published-A |
| `789a7ac3-fb38-499b-8835-79936b9fae8b` | discarded | Test planner | FC-TEST-T21-opendraft |
| `3c00af3f-1589-4533-9f24-81c57db75ddc` | discarded | Test planner | FC-TEST-revise |
| `d82fe5c2-fb6e-4045-9448-cfcbb04cac6d` | published | FC seed | FC-TEST-seed |
| `f6291347-13f2-4fd9-afb6-b3c30636e441` | published | FC seed | FC-TEST-seed |
| `ab0d7df7-7f55-4fca-abe6-09aea8446d86` | discarded | FC seed | FC-TEST-seed |
| `88fb5cbe-967d-4f37-835e-5af3e544dfb0` | discarded | FC seed | FC-TEST-seed |
| `e79fdb3d-4390-47df-a651-2b8238ab4723` | discarded | FC seed | FC-TEST-seed |
| `8bd91f0a-0154-4cd6-a60b-579a2a8566d6` | discarded | FC seed | FC-TEST-seed |
| `c28333b4-3438-48e4-91ee-97ae9c07c96f` | discarded | FC seed | FC-TEST-seed |
| `5cd38149-8524-4ee8-81a1-9ae9d5415811` | discarded | FC seed | FC-TEST-seed |
| `e9fb07a8-efdd-487a-8b82-11e44a4bc3d3` | discarded | FC seed | FC-TEST-seed |
| `f7884f8a-651d-4b88-a9a6-78c519c4af66` | discarded | FC seed | FC-TEST-seed |
| `99b1c44e-acb7-487f-96c0-94cd31b2146d` | discarded | FC seed | FC-TEST-seed |
| `3fe0f173-e5ab-4e61-9c78-9fa636525796` | discarded | FC seed | FC-TEST-seed |
| `2d925797-c3fa-486a-9f00-b62e27a8c9c1` | published | Test planner |  |
| `83419905-ae7e-4c8b-a360-1dbd94cf35cb` | superseded | FC seed | FC-TEST-T26-published-A |
| `0a2c18c1-0d33-438b-916a-84065184cdb7` | discarded | Test planner | FC-TEST-T21-opendraft |
| `58780f80-0e46-4453-98ad-a3ccfe8fba52` | discarded | Test planner | FC-TEST-revise |
| `08698d0b-daa9-40aa-8a8d-71a43902c9ec` | published | FC seed | FC-TEST-seed |
| `f00ce4de-a54e-46b6-b5bd-a3c27d24de0e` | published | FC seed | FC-TEST-seed |
| `82a110b4-bb21-44f6-a322-374ac76e8b66` | discarded | FC seed | FC-TEST-seed |
| `7856782a-2f1a-43ad-995b-1f8bce04aaf9` | discarded | FC seed | FC-TEST-seed |
| `859f581f-ef28-40a6-ba58-c10144ca4e28` | discarded | FC seed | FC-TEST-seed |
| `59a7275c-8171-4e0d-8d75-4ea732162f2b` | discarded | FC seed | FC-TEST-seed |
| `52e648e1-a6bf-40fd-88df-7b52716f3f63` | discarded | FC seed | FC-TEST-seed |
| `9dca919f-4940-473f-8b28-f49ab8ecfb63` | discarded | FC seed | FC-TEST-seed |
| `ca51643b-bcd9-403a-8963-ff2c22aec1a5` | discarded | FC seed | FC-TEST-seed |
| `164700af-dfe2-4423-bd31-19974d105b6c` | discarded | FC seed | FC-TEST-seed |
| `03970142-9797-4887-87f9-14badd02b421` | discarded | FC seed | FC-TEST-seed |
| `387c35a5-0763-4c23-a91e-e939fd3ad38f` | discarded | FC seed | FC-TEST-seed |
| `1134ef58-0640-4970-a53f-07590c2cbde1` | published | Test planner |  |
| `6ddc788d-02d9-4c3b-a218-d7f8c7635c97` | superseded | FC seed | FC-TEST-T26-published-A |
| `30058330-f0a5-467d-b0c5-da20aa1c9f62` | discarded | Test planner | FC-TEST-T21-opendraft |
| `5cf2044b-ed01-4c73-9d35-88b1ad93552a` | discarded | Test planner | FC-TEST-revise |
| `29a17eca-9773-4255-b971-adf08e1ca906` | published | FC seed | FC-TEST-seed |
| `2bb2308f-91ea-43e4-83d4-37ea0cd2162e` | published | FC seed | FC-TEST-seed |
| `fae880ee-e0ac-4c69-b250-cdabcf3ac828` | discarded | FC seed | FC-TEST-seed |
| `3d12f9e6-ac2f-4586-ac51-4c6971571f1f` | discarded | FC seed | FC-TEST-seed |
| `b90fe2c0-53cf-45a7-9aec-048ca4e5af58` | discarded | FC seed | FC-TEST-seed |
| `1733be65-003f-4f1c-9986-dc56a5ac22b9` | discarded | FC seed | FC-TEST-seed |
| `7c7af4fb-2b19-48e6-896c-f7d66886ca62` | discarded | FC seed | FC-TEST-seed |
| `00ea09c0-9d5b-46c1-983e-e0d3c255a35d` | discarded | FC seed | FC-TEST-seed |
| `06bd1e59-b8a0-4780-8b47-6fddcc995d04` | discarded | FC seed | FC-TEST-seed |
| `52c1905c-6d7c-4b30-947a-07603b61dbc0` | discarded | FC seed | FC-TEST-seed |
| `3d369306-6a6c-4a2a-927d-e7be3b4b1d81` | discarded | FC seed | FC-TEST-seed |
| `d15a993f-8a29-4c92-8072-bbe6f67c43f8` | discarded | FC seed | FC-TEST-seed |
| `798940a8-9805-4d8a-a085-a7066f12d204` | discarded | FC seed | FC-TEST-T26-published-A |
| `e8fd444d-8564-498c-b3a2-d37bb2ce06d5` | discarded | Test planner | FC-TEST-T21-opendraft |
| `0f005947-65c1-49f5-95a4-aa86d0cf4ace` | discarded | FC seed | FC-TEST-seed |
| `0891e49a-cd2c-4e9b-bc0d-ac14628cfc9d` | published | FC seed | FC-TEST-seed |
| `ee71f9e0-3037-4753-978f-d1c5f0d623f6` | discarded | FC seed | FC-TEST-seed |
| `52616912-6c62-4312-8690-596a0aec10bc` | discarded | FC seed | FC-TEST-seed |
| `0c30c670-d585-4706-9774-4b91da56ee51` | discarded | FC seed | FC-TEST-seed |
| `f30c7fb2-9df4-4454-83bc-8a058ca61dac` | discarded | FC seed | FC-TEST-seed |
| `60a7f54e-29a7-4529-9caa-4e487ed8dd06` | discarded | FC seed | FC-TEST-seed |
| `11778a6f-003f-415f-95b4-e71e4fce0221` | discarded | FC seed | FC-TEST-seed |
| `889128b5-7754-47e1-9717-17f45fd914d1` | discarded | FC seed | FC-TEST-seed |
| `77c6c8fa-4e4e-4e7c-8404-851434f075e3` | discarded | FC seed | FC-TEST-seed |
| `a14526a1-649f-4b9b-b4df-80fb6b4862ea` | discarded | FC seed | FC-TEST-seed |
| `65e6e323-87be-4082-b492-4fca12cc1769` | discarded | FC seed | FC-TEST-seed |
| `c597c53f-fa65-4268-a8c2-2ef5f7a04e8a` | published | Test planner |  |
| `2f7395b3-dce0-48b5-bc1b-d4f835eeb551` | superseded | FC seed | FC-TEST-T26-published-A |
| `4d7a4c2a-c437-4813-8900-71efd6516902` | discarded | Test planner | FC-TEST-T21-opendraft |
| `755a05e1-5382-4941-85ef-bbbb94940925` | discarded | Test planner | FC-TEST-revise |
| `964e7881-2803-4e08-a661-db1a6b37fbff` | published | FC seed | FC-TEST-seed |
| `6ef0aa6b-33b8-485b-9ff2-54e14b84872d` | discarded | FC seed | FC-TEST-seed |
| `25f05736-0397-4edf-8270-183d0a699533` | discarded | FC seed | FC-TEST-seed |
| `2a7b9a2e-a834-4a5e-b615-d5a55c911573` | discarded | FC seed | FC-TEST-seed |
| `2131f704-b805-41c7-b949-3eb7a36482a6` | discarded | FC seed | FC-TEST-seed |
| `ae56205d-2432-4e7c-b8a9-d1d14f15fc36` | discarded | FC seed | FC-TEST-seed |
| `930b60e9-1b4c-44f4-aa49-13eed7bffcc4` | discarded | FC seed | FC-TEST-seed |
| `a7692732-75a6-4024-871d-f15c31f4bb97` | discarded | FC seed | FC-TEST-seed |
| `c6c3fc40-dd52-47cf-aeeb-a815346eaa71` | discarded | FC seed | FC-TEST-seed |
| `1ac0b5fa-4ed6-45b4-9c5a-d89e96074ab1` | discarded | FC seed | FC-TEST-seed |
| `978e60cb-d613-4cf2-90c8-b738efc4ab48` | discarded | FC seed | FC-TEST-seed |
| `0cb3c43f-8894-477c-bf4a-9ede25e2717d` | discarded | FC seed | FC-TEST-seed |
| `dd49f314-3355-4f09-b22f-0c3f218212bb` | discarded | FCSEED seed | FCSEED-TEST-seed |
| `d2578f12-360b-4e4c-98e1-10e658a1e5c5` | discarded | FCSEED seed | FCSEED-TEST-freeze |
| `153cd6ac-cc64-4319-9a11-f7a899eed4a5` | published | FCSEED seed | FCSEED-TEST-seed |
| `20b012f4-9531-4845-926e-5cf936dd728f` | discarded | FCSEED seed | FCSEED-TEST-seed |
| `496aac56-a070-4d8e-8a32-bd2c3cb3d32b` | discarded | FCSEED seed | FCSEED-TEST-seed |
| `510ace7e-8075-4f92-8ca6-29196a50e8ea` | discarded | FCSEED seed | FCSEED-TEST-seed |
| `d0473acb-4e04-463e-a6bd-7584f8eaab2a` | discarded | FCSEED seed | FCSEED-TEST-seed |
| `b9d049c3-df61-49cf-a5bb-aa2a6f9595d5` | discarded | FCSEED seed | FCSEED-TEST-freeze |
| `53678e22-bb58-4617-8d64-b7de0353e590` | published | FCSEED seed | FCSEED-TEST-seed |
| `d5448a87-bc7a-4250-8e91-e297aa30da1b` | discarded | FCSEED seed | FCSEED-TEST-seed |
| `adf8230c-09fb-4c50-9ae8-108ba93b7f78` | discarded | FCSEED seed | FCSEED-TEST-seed |
| `c25e597f-584e-4507-9409-44c592271af6` | discarded | FCSEED seed | FCSEED-TEST-seed |
| `730a3306-5142-4f16-bc49-96248b1379b1` | discarded | FC seed | FC-TEST-seed |
| `3da24255-3c90-4f84-96b5-0d314edfb09e` | draft | T2 Det fixture |  |
| `b9229f29-edd0-49f3-8103-27082522ae63` | draft | T2 Det fixture |  |
| `65fcf4c7-7af2-443e-9945-ece091ed7a58` | discarded | FCR seed | FCR-R11-B |
| `7b9a7ff1-0f29-4b00-b8d3-125db387dbe1` | discarded | FCR seed | FCR-R11-A |
| `e041aca8-1c7d-40a4-8a5e-5cbd2810ba34` | discarded | FCR seed | FCR-R04 |
| `d54262f6-884d-45f2-928d-e8f9ed326d67` | published | Test planner |  |
| `22640889-45b5-4ca4-a770-ded1985a28de` | superseded | FC seed | FC-TEST-T26-published-A |
| `c09f39df-3a87-46a4-ba59-b938e86c3395` | discarded | Test planner | FC-TEST-T21-opendraft |
| `5009ba1e-2734-4b05-8675-2d071d548e98` | discarded | Test planner | FC-TEST-revise |
| `74a14e91-354a-4b0d-a83b-4e00eb3f28e8` | published | FC seed | FC-TEST-seed |
| `59e411a4-afe5-4ea1-9f73-e942a5a4b8b3` | discarded | FC seed | FC-TEST-seed |
| `5ef8de1d-f39c-49f6-8827-e8a5d69825a2` | discarded | FC seed | FC-TEST-seed |
| `f0574d9a-59de-4143-afc6-972ec37d85c1` | discarded | FC seed | FC-TEST-seed |
| `c14c3c4b-719f-4768-a334-7d13722e96e9` | discarded | FC seed | FC-TEST-seed |
| `ebe8dba0-52b1-4aaa-9329-30e93b080700` | discarded | FC seed | FC-TEST-seed |
| `a97ff390-3a5c-4fc4-bec9-2efe65585ab8` | discarded | FC seed | FC-TEST-seed |
| `43d315f5-f926-411b-8509-5f9e7c0c3702` | discarded | FC seed | FC-TEST-seed |
| `f549c6ff-bc5a-4737-9a0f-b8119655b48f` | discarded | FC seed | FC-TEST-seed |
| `3f167e33-fbfa-425e-81ea-25b80c0afebe` | discarded | FC seed | FC-TEST-seed |
| `caf8d910-e67a-4b76-b2d1-559cfbe0f209` | discarded | FC seed | FC-TEST-seed |
| `0fb9a66b-2f69-4726-a88b-ac7b7ff288ab` | discarded | FC seed | FC-TEST-seed |
| `8df88ff0-8980-4997-aaff-d80347989657` | discarded | FCR seed | FCR-R11-B |
| `fb600b51-ae40-47a5-a379-31ac4a807fc1` | discarded | FCR seed | FCR-R11-A |
| `a483c627-f078-43ed-93a5-d832cf9c1fb9` | discarded | FCR seed | FCR-R04 |
| `347618e7-c1ce-43fb-ba27-302893c3abac` | discarded | FC seed | FC-TEST-T26-published-A |
| `765e7b38-6180-4ed5-a152-a7cceebadc3d` | discarded | Test planner | FC-TEST-T21-opendraft |
| `7f130027-0763-4210-b80d-9d8fbfde06fd` | discarded | FC seed | FC-TEST-seed |
| `a6ed28d6-e6a1-40ab-ad5a-5fb2a7e41dc8` | discarded | FC seed | FC-TEST-seed |
| `14970b7c-4b2c-4860-b891-ac2aa5a72829` | discarded | FC seed | FC-TEST-seed |
| `2b42745c-58e6-4a10-8e56-f91ec218b848` | discarded | FC seed | FC-TEST-seed |
| `d6d6b9b0-fe80-4d4d-ba75-1d18a1a38c9c` | discarded | FC seed | FC-TEST-seed |
| `358832f4-25d0-46ff-bdcb-374f465cf5d6` | discarded | FC seed | FC-TEST-seed |
| `50efdfad-0ab7-4760-846d-c12d2378b5ae` | discarded | FC seed | FC-TEST-seed |
| `873f545b-1edd-4dce-8f07-ab731326b975` | discarded | FC seed | FC-TEST-seed |
| `8a5ab166-5b7e-45be-9816-329a645b1d5b` | discarded | FC seed | FC-TEST-seed |
| `cb091042-b8f4-4fcc-9651-5d544b09924c` | discarded | FC seed | FC-TEST-seed |
| `39ead761-165c-4993-b4fc-27a442c197f8` | discarded | FC seed | FC-TEST-seed |
| `c404feb4-bc9c-4cc9-9777-69696580671e` | discarded | FC seed | FC-TEST-seed |
| `4a9438b3-77ac-4255-b299-fe5595364f87` | published | Test planner |  |
| `0cfc875d-bcd8-489e-a183-01e9fdda1974` | superseded | FC seed | FC-TEST-T26-published-A |
| `a75735f1-fd23-40de-97d5-7d3c73aa9b08` | discarded | Test planner | FC-TEST-revise |
| `5fa57b5c-e04b-4b85-91a0-fe4405af70d3` | published | FC seed | FC-TEST-seed |
| `736da34c-06ee-45e7-987e-7f25484cb8cf` | discarded | FC seed | FC-TEST-seed |
| `e2680c01-b48f-451b-a43f-2ecd413470c2` | discarded | FC seed | FC-TEST-seed |
| `670413d2-a4e6-4dca-8f57-4754ff2da6ae` | discarded | FC seed | FC-TEST-seed |
| `b386590f-0a18-454b-8b4c-1e03cae05543` | discarded | FC seed | FC-TEST-seed |
| `7df113a5-e29c-43ee-aa7b-05c4c0b33300` | discarded | FC seed | FC-TEST-seed |
| `7fa92309-5d79-4238-85db-5ba74ffb8367` | discarded | FC seed | FC-TEST-seed |
| `620ab531-92e2-4e0a-9f6a-3b6017de44f9` | discarded | FC seed | FC-TEST-seed |
| `38386523-6ff1-48d2-bf00-087776bf1f94` | discarded | FC seed | FC-TEST-seed |
| `c9bc0c03-bbef-4bee-8e6d-4f38e4dd365f` | discarded | FC seed | FC-TEST-seed |
| `a2cb1cb1-ae5c-4cd6-861b-5d231a6e5dae` | discarded | FC seed | FC-TEST-seed |
| `953facce-8e98-4bf3-84f4-cf6713714546` | discarded | FC seed | FC-TEST-seed |
| `87167c14-188b-4c7c-b8f4-7913fafb5890` | draft | Test planner |  |
| `feddcf6e-3b6d-43f0-a94c-d2142d184c93` | published | FC seed | FC-TEST-T26-published-A |
| `2c2a0c09-96c1-4b3b-a05a-fcf4140b3d61` | discarded | Test planner | FC-TEST-T21-opendraft |
| `843e5e4f-db00-41ca-bee2-67236ad41133` | discarded | Test planner | FC-TEST-revise |
| `d50b7e52-4f03-4df0-a7de-0ff3555d3ede` | published | FC seed | FC-TEST-seed |
| `f75af9ec-c1d6-48f3-96ab-f03ea46d7c4d` | discarded | FC seed | FC-TEST-seed |
| `83f37349-44df-4a79-b6e8-7364c29dd4c4` | discarded | FC seed | FC-TEST-seed |
| `3979f76b-012c-4162-b03e-e1c8f4ccbc3e` | discarded | FC seed | FC-TEST-seed |
| `16d1b5d9-a3b3-48f5-9247-edbd064954ae` | discarded | FC seed | FC-TEST-seed |
| `0b82f137-1ce4-4503-a964-295c6a76cbf8` | discarded | FC seed | FC-TEST-seed |
| `06420d84-1211-4ea8-8bb1-0964f78f6011` | discarded | FC seed | FC-TEST-seed |
| `a9458719-5d42-443f-a247-23ddf6132ff8` | discarded | FC seed | FC-TEST-seed |
| `70e9d51d-a7ad-4ccf-bf72-f35685611d75` | discarded | FC seed | FC-TEST-seed |
| `42225b71-0e06-4241-9efe-3657a768ac10` | discarded | FC seed | FC-TEST-seed |
| `3fb85df9-d5ee-4293-8257-1dec304ae6ef` | discarded | FC seed | FC-TEST-seed |
| `e3f1df53-b780-4994-acbd-4718188d5dca` | discarded | FC seed | FC-TEST-seed |
| `8f8ef24f-61c1-4d40-86b5-fcee0e337a2f` | discarded | FC seed | FC-TEST-T26-published-A |
| `1018fc3e-b894-43ec-8110-3f122ee02eb5` | discarded | Test planner | FC-TEST-T21-opendraft |
| `63e96f34-7dd7-4b56-94aa-fd0ebc16de5a` | discarded | FC seed | FC-TEST-seed |
| `df3b1ab1-4a03-463a-996b-b8b1307b8930` | discarded | FC seed | FC-TEST-seed |
| `dc11137a-fb50-4128-9033-704e9efc8bae` | discarded | FC seed | FC-TEST-seed |
| `e1c80fb7-7b34-416b-84f5-35142d1450dd` | discarded | FC seed | FC-TEST-seed |
| `2544e302-a882-4594-95ae-55ec170c84f2` | discarded | FC seed | FC-TEST-seed |
| `a67342ba-b606-480d-a640-fd5adf6585a3` | discarded | FC seed | FC-TEST-seed |
| `0c26a902-efb0-443e-a2c4-743aeeec372c` | discarded | FC seed | FC-TEST-seed |
| `2d478a0a-53ae-44c6-889b-c36ecec0d7f1` | discarded | FC seed | FC-TEST-seed |
| `8d6f218a-d651-4eb0-a3b4-73eaff24a2d5` | discarded | FC seed | FC-TEST-seed |
| `ced6e843-8c69-48c6-a662-46375cb6966a` | discarded | FC seed | FC-TEST-seed |
| `813e2104-4ac6-48e6-8f8a-b017a12676ce` | discarded | FCR seed | FCR-R11-B |
| `a7b9a5af-279c-4c22-9859-6d9dbc3fdeaf` | discarded | FCR seed | FCR-R11-A |
| `35c73215-1a2f-4140-b36d-f7cbd4f4c69e` | discarded | FC seed | FC-TEST-seed |
| `ab9d469a-7dee-45d2-91c9-3713ce13d4ce` | discarded | FCR seed | FCR-R04 |
| `d381a684-4587-4767-9008-569225ee059f` | discarded | FC seed | FC-TEST-seed |
| `ee61d61f-bf65-4796-b65d-911814f87d7a` | published | Test planner |  |
| `f100f7ce-aaca-4490-80aa-018883d03718` | superseded | FC seed | FC-TEST-T26-published-A |
| `c4531ad1-69e1-4681-9794-bc3c4af66c00` | discarded | Test planner | FC-TEST-T21-opendraft |
| `e2c6d636-8659-4554-9f7e-39fab615053a` | discarded | Test planner | FC-TEST-revise |
| `71f835af-3d78-4cbf-927d-4fbe3bd3b5d1` | published | FC seed | FC-TEST-seed |
| `65ee6077-b66f-44fa-b667-ba244bcb0d01` | discarded | FC seed | FC-TEST-seed |
| `0dd8b1a1-2498-47be-b3cf-34fd5f0ab63e` | discarded | FC seed | FC-TEST-seed |
| `38aa97f9-fe9c-403a-aa48-375039632416` | discarded | FC seed | FC-TEST-seed |
| `f4521b99-1552-41ff-98b2-c0d1f0947e70` | discarded | FC seed | FC-TEST-seed |
| `cf32d3c5-38ef-441d-8bab-f4a6db7c5dd5` | discarded | FC seed | FC-TEST-seed |
| `ed4a4328-31b9-4146-9cc5-f8169238d025` | discarded | FC seed | FC-TEST-seed |
| `692f802d-89f5-495b-89ce-1481f9a686cb` | discarded | FC seed | FC-TEST-seed |
| `cc074b6d-264a-4736-bc1c-abf6dee41973` | discarded | FC seed | FC-TEST-seed |
| `4623305c-45d0-49f1-8c5c-17579f6cae1a` | discarded | FC seed | FC-TEST-seed |
| `520d4899-5518-4dff-97fa-822ff8181da9` | discarded | FCR seed | FCR-R11-B |
| `6bc7d372-5415-4504-954e-ed2789b74197` | discarded | FCR seed | FCR-R11-A |
| `9b10806b-f7f2-4bdc-b60a-b2c6d54bbf44` | discarded | FC seed | FC-TEST-seed |
| `632ca428-1441-43a0-b686-89c0c48aa20a` | discarded | FCR seed | FCR-R04 |
| `c3c1a599-f5ad-46dd-9b3e-2ad16e9e37fd` | discarded | FC seed | FC-TEST-seed |
| `5a783133-435d-4368-a7c9-95de4ec7fec0` | discarded | FC seed | FC-TEST-T26-published-A |
| `00c2e192-3425-4555-a013-3af53b91e2ca` | discarded | Test planner | FC-TEST-T21-opendraft |
| `6dd9568d-033e-42a7-8aa3-75a64e3d4338` | discarded | FC seed | FC-TEST-seed |
| `cf5e7264-56bb-4226-b29f-d6c86adf7e7c` | discarded | FC seed | FC-TEST-seed |
| `531e8af2-f8ca-4955-bb60-16e6241465d7` | discarded | FC seed | FC-TEST-seed |
| `edcbea9a-3625-4533-b4ce-881f54f68aec` | discarded | FC seed | FC-TEST-seed |
| `e3709859-c1d4-4063-84fc-510c99a864db` | discarded | FC seed | FC-TEST-seed |
| `c90f76c2-120f-4e4b-8dae-e532bcc4cfe9` | discarded | FC seed | FC-TEST-seed |
| `256b61d0-85da-4406-bc5d-93350108221b` | discarded | FC seed | FC-TEST-seed |
| `7c627fdb-d980-4c47-b557-e02d438b0634` | discarded | FC seed | FC-TEST-seed |
| `b99790b1-78f3-47ae-94c5-5ab5789cda77` | discarded | FC seed | FC-TEST-seed |
| `88516005-6dd6-48fd-90b1-3c77e687dae7` | discarded | FC seed | FC-TEST-seed |
| `36518ddd-f4df-4b0f-9f98-a01de2e58c3d` | discarded | FCR seed | FCR-R11-B |
| `1045c6fb-3e95-4e98-8670-ae2678de176b` | discarded | FCR seed | FCR-R11-A |
| `9d36e6d0-baf7-4f96-9d14-aa0e294a5160` | discarded | FC seed | FC-TEST-seed |
| `e5db6483-720e-4604-a041-e9f4bacec963` | discarded | FCR seed | FCR-R04 |
| `4f8a9646-186d-43eb-abf3-05a8c19687a7` | discarded | FC seed | FC-TEST-seed |
| `27cac61c-fc5b-4c8d-a7e3-0aa391ca6b82` | discarded | FCR seed | FCR-R11-B |
| `873383a3-917e-49c8-ac94-043f5e9a0760` | discarded | FCR seed | FCR-R11-A |
| `677aaf39-43b1-45ef-abbb-9fe6e6ee9506` | discarded | FCR seed | FCR-R04 |
| `6e2b2226-3f10-4f9f-999f-fe52876e9b9a` | published | Test planner |  |
| `64f9e28a-6840-4a06-8058-f495c085ab10` | superseded | FC seed | FC-TEST-T26-published-A |
| `e3321048-9de4-4664-af00-ae97e8fd5e6d` | discarded | Test planner | FC-TEST-T21-opendraft |
| `7de0c443-ad83-4011-9100-edd1bf7c52da` | discarded | Test planner | FC-TEST-revise |
| `2e752458-34a0-4662-8ff3-0c16bf80460b` | published | FC seed | FC-TEST-seed |
| `46942e0b-9a5b-49a9-9944-61dc904c8389` | discarded | FC seed | FC-TEST-seed |
| `4cddd59c-4c0c-499a-a7c8-5311ab04fbf6` | discarded | FC seed | FC-TEST-seed |
| `754e077b-ca78-4a26-a17f-11f8f60fa2e8` | discarded | FC seed | FC-TEST-seed |
| `5b1f622e-2b7d-44f8-b8d4-b0a7cc2506c5` | discarded | FC seed | FC-TEST-seed |
| `c34b8a6d-e048-49da-85c3-f5766465c7e3` | discarded | FC seed | FC-TEST-seed |
| `33e2b412-4ef3-49ff-b002-73e5e6c4fa9d` | discarded | FC seed | FC-TEST-seed |
| `8f44c23a-7b53-4f99-90d1-746e68643fac` | discarded | FC seed | FC-TEST-seed |
| `8221aa71-b52a-444f-8bf0-0470059ff511` | discarded | FC seed | FC-TEST-seed |
| `ff3dc659-9ea4-468e-bd70-4072d5f9f35b` | discarded | FC seed | FC-TEST-seed |
| `5aa8d7a4-939c-45b9-8699-97ffdf17e651` | discarded | FC seed | FC-TEST-seed |
| `9f5c0aad-2850-4ec1-a62d-a5a8aa399278` | discarded | FC seed | FC-TEST-seed |
| `501665c6-1ee8-4aec-8ec9-1be221d97c02` | published | Test admin |  |
| `cc5fd06d-1ec0-4471-83fb-61b418133906` | superseded | FC seed | FC-TEST-T26-published-A |
| `b0b8c304-2c1d-475d-8376-f95744eb3762` | discarded | Test planner | FC-TEST-T21-opendraft |
| `c6a06b77-660b-4886-9259-720328f2c4ee` | discarded | Test planner | FC-TEST-revise |
| `29604242-2ddb-4144-a4f7-930b9b89dc6d` | published | FC seed | FC-TEST-seed |
| `3773462f-9470-400b-a0a8-9d64076af0d3` | discarded | FC seed | FC-TEST-seed |
| `5a830e85-a3c3-438e-ab4f-7c1fa33fd377` | discarded | FC seed | FC-TEST-seed |
| `875830da-9bab-445c-a25f-2af1f9b8ee3d` | discarded | FC seed | FC-TEST-seed |
| `f56331e6-48ff-4806-bbea-eeb6c38ee5ce` | discarded | FC seed | FC-TEST-seed |
| `e331f25b-3458-4ccd-b06c-8dfc3ee5017e` | discarded | FC seed | FC-TEST-seed |
| `d484aa88-4367-4861-a42b-d1f9a64f6197` | discarded | FC seed | FC-TEST-seed |
| `7d1cd00b-56a8-401f-b520-e3e7619c4b95` | discarded | FC seed | FC-TEST-seed |
| `d3f607e5-210e-4ffb-84bb-b6f92180392a` | discarded | FC seed | FC-TEST-seed |
| `3c4d5c1f-ae40-434e-badc-b90c5b514cbe` | discarded | FC seed | FC-TEST-seed |
| `2ffe563b-e2e7-41cd-9e64-967c8fb6301e` | discarded | FC seed | FC-TEST-seed |
| `b2b584e6-f15c-4c13-b3fd-1b1968f3c726` | discarded | FC seed | FC-TEST-seed |
| `d63b110c-1c6b-41a1-bd05-594d75a28d12` | published | Test admin |  |
| `b0dc9838-faa0-4cf6-9809-fabfbab8b6ea` | superseded | FC seed | FC-TEST-T26-published-A |
| `081a02bd-8c07-4f4f-a9cc-785e3eb2b58e` | discarded | Test planner | FC-TEST-T21-opendraft |
| `daefe570-eb99-4f10-b720-68d373ded55e` | discarded | Test planner | FC-TEST-revise |
| `7303fabc-085e-47a1-aef8-17dfbfbad2d1` | published | FC seed | FC-TEST-seed |
| `22582c8a-d6d8-45bb-b611-efd6ead62d3d` | discarded | FC seed | FC-TEST-seed |
| `98223d9a-1e58-46b4-98f3-797069848e99` | discarded | FC seed | FC-TEST-seed |
| `ecbdfd61-3937-4fcd-b05b-ee0dc5fa381d` | discarded | FC seed | FC-TEST-seed |
| `457a928e-1d21-46e8-b2f0-de56775ba2c2` | discarded | FC seed | FC-TEST-seed |
| `cc17fde1-7694-4149-862b-40f843ca5347` | discarded | FC seed | FC-TEST-seed |
| `0c5f1382-4cd6-4677-94e9-ae9e66dba0f2` | discarded | FC seed | FC-TEST-seed |
| `c1076981-e699-4601-9400-6bf0771ceb30` | discarded | FC seed | FC-TEST-seed |
| `bfc38af5-bec1-472e-82f3-e541685c84f3` | discarded | FC seed | FC-TEST-seed |
| `acffbf1e-862c-4a6d-83fc-656d37db0305` | discarded | FC seed | FC-TEST-seed |
| `7199bac0-c496-49a9-b5ab-ec287af1594a` | discarded | FC seed | FC-TEST-seed |
| `85262b1f-9d91-42a6-bcdd-f357dca01d2b` | discarded | FC seed | FC-TEST-seed |
| `62c00520-ccc6-44d0-9feb-ea0a0c6f621c` | discarded | FCR seed | FCR-R11-B |
| `86c4dddb-04cd-423c-bc7d-5b0ee090bc00` | discarded | FCR seed | FCR-R11-A |
| `934a91d1-e226-4226-8494-b238f9779ba4` | discarded | FCR seed | FCR-R04 |
| `21ed4d4b-1fdc-4b83-93b5-1cf3d4f4ce55` | discarded | Test planner | FC-TEST-revise |
| `13c7650b-8af3-424e-ab65-40a629832361` | published | FC seed | FC-TEST-seed |
| `624d1d8c-a682-45b9-85ef-a2964700ec1c` | discarded | FC seed | FC-TEST-seed |
| `b7a99533-f0ed-4954-95f4-72d0d652b628` | discarded | FC seed | FC-TEST-seed |
| `9be34a49-6f43-46f9-babd-4e3499c90de3` | discarded | FC seed | FC-TEST-seed |
| `2218421c-b534-46d1-b73f-c434699404e0` | discarded | FC seed | FC-TEST-seed |
| `369f34cd-8d4e-4ad9-b7c7-d77a630971be` | discarded | FC seed | FC-TEST-seed |
| `fb78f278-e58b-4f18-96f1-0ddd960d2302` | discarded | FC seed | FC-TEST-seed |
| `b58b30e7-ca17-457c-b9d3-1810e1dd4e65` | discarded | FC seed | FC-TEST-seed |
| `df79be17-5dbe-4161-ac89-0d1721493386` | discarded | FC seed | FC-TEST-seed |
| `0c4abd3f-840d-444a-a97f-10cfaade581e` | discarded | FC seed | FC-TEST-seed |
| `7fa1251a-1cf9-4d66-a0c2-4e1b934647dc` | discarded | FC seed | FC-TEST-seed |
| `db31659e-7d21-4aba-b1e4-8e3865c8b770` | discarded | FC seed | FC-TEST-seed |
| `69aa2387-bcfc-42e8-b95e-ecaff871dd4b` | discarded | Test planner | FC-TEST-revise |
| `4eb624a7-f3e0-4edc-a957-657b4bff7bc2` | published | FC seed | FC-TEST-seed |
| `fa9b2a0e-884f-42a4-8256-529a31497a79` | discarded | FC seed | FC-TEST-seed |
| `8a1fe606-a008-43d6-b9ef-84f216dcbc2d` | discarded | FC seed | FC-TEST-seed |
| `1756468d-8235-4233-8be3-841a60488ef8` | discarded | FC seed | FC-TEST-seed |
| `04e7e57d-d87b-4235-ac2f-6cab0b109973` | discarded | FC seed | FC-TEST-seed |
| `875916bf-263d-4093-b084-23e5e64650aa` | discarded | FC seed | FC-TEST-seed |
| `fed347e3-157c-434a-b09c-2ba2ee945724` | discarded | FC seed | FC-TEST-seed |
| `8740e6aa-30b0-4adb-992e-3312fa8a1ab0` | discarded | FC seed | FC-TEST-seed |
| `630eb5de-82c1-4fab-915e-aa1559edc34f` | discarded | FC seed | FC-TEST-seed |
| `ba8d5119-7830-422c-86e3-f4b182eb8af9` | discarded | FC seed | FC-TEST-seed |
| `4bd11008-76d1-495e-9d3b-388417b17d28` | discarded | FC seed | FC-TEST-seed |
| `63e5fc59-1159-452b-abe4-71f777cee6a3` | discarded | FC seed | FC-TEST-seed |
| `c5327a25-def2-4388-beb5-b3d1b6489567` | discarded | Test planner | FC-TEST-revise |
| `0fbc609f-c39e-4b54-ab3c-72fcfb84a902` | published | FC seed | FC-TEST-seed |
| `40c089fc-8897-4475-8a18-14f0328e845c` | discarded | FC seed | FC-TEST-seed |
| `aaa5df61-1e6d-4265-8b67-b299a4bbb2db` | discarded | FC seed | FC-TEST-seed |
| `7006bea2-2747-4a6c-a7a6-b7f0accd6c60` | discarded | FC seed | FC-TEST-seed |
| `dc62af04-0a3c-40da-b269-c7925873d68f` | discarded | FC seed | FC-TEST-seed |
| `5a8f8dba-974e-4b8e-a41c-4c532e218458` | discarded | FC seed | FC-TEST-seed |
| `0205b512-db8c-4cb9-8ed5-0c57f341591f` | discarded | FC seed | FC-TEST-seed |
| `19cb3f82-f2b1-4a40-bc68-81bb44fda619` | discarded | FC seed | FC-TEST-seed |
| `00aeff3b-01a4-4788-8985-8040d645b2ba` | discarded | FC seed | FC-TEST-seed |
| `b787e53a-d515-441a-9cbb-3277f2c6f572` | discarded | FC seed | FC-TEST-seed |
| `ff0d3704-cee4-4d15-b849-61365e722c7f` | discarded | FC seed | FC-TEST-seed |
| `bc8c9be6-c4c7-47f7-9561-1a92c2f02267` | discarded | FC seed | FC-TEST-seed |
| `2fef81e4-d253-446d-a5b2-d9f77bf1cc92` | discarded | Test planner | FC-TEST-revise |
| `ee47516d-bd08-4360-9e71-233168a7eee3` | published | FC seed | FC-TEST-seed |
| `fe7a1a91-4470-4668-90cd-e1898cc73656` | discarded | FC seed | FC-TEST-seed |
| `d2212b84-94e7-4953-b3c8-51aa926592ff` | discarded | FC seed | FC-TEST-seed |
| `ce5db4d1-ced3-40cb-bf50-431785a4d726` | discarded | FC seed | FC-TEST-seed |
| `95959606-0af5-435d-b7c0-956f59104ec4` | discarded | FC seed | FC-TEST-seed |
| `dacf75f9-20b2-4f65-ad21-ecc14492c1ee` | discarded | FC seed | FC-TEST-seed |
| `b0d8651e-3375-49f2-bf9a-024b32a4f610` | discarded | FC seed | FC-TEST-seed |
| `2a93c15f-52c7-4025-8fc7-19a4dd202c5c` | discarded | FC seed | FC-TEST-seed |
| `6d556c39-a352-4cc0-b6a8-953af87984e4` | discarded | FC seed | FC-TEST-seed |
| `bf02747e-066e-4016-a9bf-a406c3ccedf7` | discarded | FC seed | FC-TEST-seed |
| `198557dc-d678-4d06-92b2-cbe71915735a` | discarded | FC seed | FC-TEST-seed |
| `08b615d1-be36-455c-bcaf-57b95f3a0a18` | discarded | FC seed | FC-TEST-seed |

## Recommendation

All versions classified `suspect=YES` should be candidates for cleanup.
Classification rule used here: a version is **suspect** if ANY of the following holds:
- created by a known fixture user (planner.fixture / operator.fixture / viewer.fixture from migration 0059)
- created by any user other than Tom (admin `0db008a9-05e3-4521-8b30-42e5d444818d`)
- notes or `created_by_snapshot` contains TEST/SEED/SMOKE/FIXTURE/DEMO/PLACEHOLDER/DUMMY/SAMPLE/GOLDEN/CYCLE/W1/W2/W4
- status is `discarded` or `superseded`

Cleanup must respect the contract: `forecast_versions` deletion is forbidden by §A.3.
Operationally that means a separate documented purge migration with explicit Tom approval, not in scope here.

Raw query dump: `cleanup_audit_forecasts_raw.txt`