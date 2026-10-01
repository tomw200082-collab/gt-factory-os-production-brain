-- Forecast Sep-Oct 2026 publish. Run ONCE, as one transaction (psql -1 -f publish.sql).
-- New version supersedes c7e9db2a (Aug-Sep-Oct, published 2026-07-23). Aug lines copied unchanged.
-- Method + per-item table: gt-factory-os-production-brain/docs/planning/2026-09-06-forecast-sep-oct-2026.md
begin;
select set_config('audit.actor_user_id','0db008a9-05e3-4521-8b30-42e5d444818d',true),
       set_config('audit.actor_snapshot','Tom',true),
       set_config('audit.session_id','claude-2026-09-06-forecast',true);

insert into private_core.forecast_versions
  (version_id, site_id, cadence, horizon_start_at, horizon_weeks, status, created_by_user_id, created_by_snapshot, supersedes_version_id, notes)
values
  ('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','GT-MAIN','monthly','2026-08-01',13,'draft',
   '0db008a9-05e3-4521-8b30-42e5d444818d','Tom','c7e9db2a-f81f-4903-94de-613d8da571e4',
   $n$Sep-Oct 2026 rebuild (Tom-directed, session 2026-09-06). Aug copied unchanged from c7e9db2a. Basis = Shopify net units Jun-Aug 2026 (weighted 0.2/0.4/0.4, per working day), not censored FG_OUT_PICK. Sep = actual Sep 1-6 + holiday-week shape (pre-RH 1.5, RH-YK 0.74, YK 0.74, Sukkot 0.59; from 2024+2025 weekly ratios). Oct = 20.6 wd-eq x family autumn index (2025 Oct/Nov vs Jul/Aug, shrunk 50% to 1). MTO/private-label still excluded. New: FG-DES-500ML, ADD-ROSE-200G. Sep bucket frozen-window override: admin Tom, reason = holiday shutdown 17.09-04.10 planning. Doc: gt-factory-os-production-brain docs/planning/2026-09-06-forecast-sep-oct-2026.md$n$);

insert into private_core.form_submissions
  (form_type, idempotency_key, submitted_by, submitted_at, event_at, status, posted_at, posted_by, site_id, raw_payload)
values ('forecast_open_draft','fc-sepoct2026-opendraft-01','0db008a9-05e3-4521-8b30-42e5d444818d',now(),now(),'posted',now(),
        '0db008a9-05e3-4521-8b30-42e5d444818d','GT-MAIN',
        '{"cadence":"monthly","horizon_weeks":13,"horizon_start_at":"2026-08-01","supersedes_version_id":"c7e9db2a-f81f-4903-94de-613d8da571e4","version_id":"9a1c6f2e-5b3d-4e8a-9f70-2026090601aa"}'::jsonb);

-- Aug: copied unchanged from the superseded version
insert into private_core.forecast_lines (version_id, item_id, period_bucket_key, forecast_quantity)
select '9a1c6f2e-5b3d-4e8a-9f70-2026090601aa', item_id, period_bucket_key, forecast_quantity
from private_core.forecast_lines
where version_id='c7e9db2a-f81f-4903-94de-613d8da571e4' and period_bucket_key='2026-08-01';

-- Sep / Oct: new
insert into private_core.forecast_lines (version_id, item_id, period_bucket_key, forecast_quantity) values
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-DET-1L','2026-09-01',1294),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-DET-1L','2026-10-01',1229),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-DET-1L-NS','2026-09-01',729),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-DET-1L-NS','2026-10-01',581),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-DET-500ML','2026-09-01',388),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-DET-500ML','2026-10-01',475),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-DET-500ML-NS','2026-09-01',254),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-DET-500ML-NS','2026-10-01',300),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-FRE-1L','2026-09-01',840),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-FRE-1L','2026-10-01',778),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-FRE-1L-NS','2026-09-01',333),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-FRE-1L-NS','2026-10-01',234),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-FRE-500ML','2026-09-01',379),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-FRE-500ML','2026-10-01',372),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-FRE-500ML-NS','2026-09-01',155),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-FRE-500ML-NS','2026-10-01',153),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-NAM-1L','2026-09-01',1010),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-NAM-1L','2026-10-01',1418),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-NAM-500ML','2026-09-01',283),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-NAM-500ML','2026-10-01',426),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-REV-1L','2026-09-01',448),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-REV-1L','2026-10-01',495),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-REV-500ML','2026-09-01',235),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-REV-500ML','2026-10-01',240),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-CAL-1L','2026-09-01',315),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-CAL-1L','2026-10-01',311),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-CAL-500ML','2026-09-01',135),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-CAL-500ML','2026-10-01',160),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-CON-1L','2026-09-01',241),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-CON-1L','2026-10-01',227),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-CON-500ML','2026-09-01',125),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-CON-500ML','2026-10-01',135),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-ENE-1L','2026-09-01',263),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-ENE-1L','2026-10-01',258),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-ENE-500ML','2026-09-01',209),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-ENE-500ML','2026-10-01',208),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-DES-1L','2026-09-01',160),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-DES-1L','2026-10-01',144),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-DES-500ML','2026-09-01',49),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-DES-500ML','2026-10-01',20),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-MAT-18G','2026-09-01',2766),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-MAT-18G','2026-10-01',3200),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-MAT-500G','2026-09-01',127),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-MAT-500G','2026-10-01',149),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','GT-MAT-KIT','2026-09-01',7),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','GT-MAT-KIT','2026-10-01',11),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-NM-1L','2026-09-01',129),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-NM-1L','2026-10-01',178),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-NM-3850ML','2026-09-01',22),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-NM-3850ML','2026-10-01',34),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-SAN-PIN-1L','2026-09-01',16),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-SAN-PIN-1L','2026-10-01',19),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-SAN-WHI-1L','2026-09-01',27),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-SAN-WHI-1L','2026-10-01',31),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-SAN-RED-3850ML','2026-09-01',4),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-SAN-RED-3850ML','2026-10-01',4),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-SAN-WHI-3850ML','2026-09-01',17),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','FG-SAN-WHI-3850ML','2026-10-01',9),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','ADD-ODK-MAN-1L','2026-09-01',204),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','ADD-ODK-MAN-1L','2026-10-01',221),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','ADD-ODK-PEA-1L','2026-09-01',20),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','ADD-ODK-PEA-1L','2026-10-01',26),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','ADD-ODK-STR-1L','2026-09-01',262),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','ADD-ODK-STR-1L','2026-10-01',269),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','ADD-UBE-1KG','2026-09-01',21),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','ADD-UBE-1KG','2026-10-01',20),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','ADD-UBE-500G','2026-09-01',30),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','ADD-UBE-500G','2026-10-01',33),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','ADD-GAR-ORA-DRY','2026-09-01',32),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','ADD-GAR-ORA-DRY','2026-10-01',38),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','ADD-ROSE-200G','2026-09-01',5),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','ADD-ROSE-200G','2026-10-01',7),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','AP-CUP-MAT-600','2026-09-01',1),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','AP-CUP-MAT-600','2026-10-01',2),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','AP-FRO-MAT','2026-09-01',6),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','AP-FRO-MAT','2026-10-01',6),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','ADD-GAR-ROSE-DRY','2026-09-01',0),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','ADD-GAR-ROSE-DRY','2026-10-01',0),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','ADD-MUZ-BZSM-1L','2026-09-01',0),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','ADD-MUZ-BZSM-1L','2026-10-01',0),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','ADD-MUZ-HER-1L','2026-09-01',0),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','ADD-MUZ-HER-1L','2026-10-01',0),
('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','ADD-MUZ-MRCL-1L','2026-09-01',0),('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','ADD-MUZ-MRCL-1L','2026-10-01',0);

insert into private_core.form_submissions
  (form_type, idempotency_key, submitted_by, submitted_at, event_at, status, posted_at, posted_by, site_id, raw_payload)
values ('forecast_save','fc-sepoct2026-save-01','0db008a9-05e3-4521-8b30-42e5d444818d',now(),now(),'posted',now(),
        '0db008a9-05e3-4521-8b30-42e5d444818d','GT-MAIN',
        '{"version_id":"9a1c6f2e-5b3d-4e8a-9f70-2026090601aa","n_items":42,"buckets":["2026-08-01(copied)","2026-09-01","2026-10-01"],"freeze_override_reason":"Tom-directed Sep/Oct rebuild for holiday shutdown 17.09-04.10 planning (admin override, session 2026-09-06)","actor_role":"admin"}'::jsonb);

update private_core.forecast_versions
   set status='published', published_by_user_id='0db008a9-05e3-4521-8b30-42e5d444818d', published_by_snapshot='Tom', published_at=now()
 where version_id='9a1c6f2e-5b3d-4e8a-9f70-2026090601aa';

update private_core.forecast_versions
   set status='superseded', superseded_at=now()
 where version_id='c7e9db2a-f81f-4903-94de-613d8da571e4' and status='published';

insert into private_core.form_submissions
  (form_type, idempotency_key, submitted_by, submitted_at, event_at, status, posted_at, posted_by, site_id, raw_payload)
values ('forecast_publish','fc-sepoct2026-publish-01','0db008a9-05e3-4521-8b30-42e5d444818d',now(),now(),'posted',now(),
        '0db008a9-05e3-4521-8b30-42e5d444818d','GT-MAIN',
        '{"version_id":"9a1c6f2e-5b3d-4e8a-9f70-2026090601aa","superseded_version_id":"c7e9db2a-f81f-4903-94de-613d8da571e4"}'::jsonb);

-- Advisory correction factors were calibrated against the superseded pick-based forecast; they would double-count now.
delete from private_core.planning_policy where key like 'planning.demand.correction_factor.%';
commit;
