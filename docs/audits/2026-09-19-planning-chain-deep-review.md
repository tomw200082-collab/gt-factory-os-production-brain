# ביקורת עומק — שרשרת התכנון: תחזית → ייצור → רכש → הזמנות → קבלת סחורה

> **תאריך:** 2026-09-19 (שבת) · **מבקש:** טום · **סוג:** ביקורת + הצעת שינוי (proposal). **לא מסמך סמכות.**
> **מקורות ראיה:** קוד חי בשלושת הריפוזיטוריים (`gt-factory-os`, `gt-factory-os-portal`, `gt-factory-os-production-brain`), שאילתות קריאה-בלבד על `gt-ops-prod` (`rvadsozabmxkkrktwgnv`) ב-19.9, ארבעה סוכני ביקורת קוד מקבילים (ציטוטי `קובץ:שורה` בגוף המסמך), ו-UX release gate נפרד: `docs/phase8/dry-runs/2026-09-19-ux-release-gate-planning-chain.md`.
> **מוסכמות:** `be/` = `gt-factory-os`, `po/` = `gt-factory-os-portal`, `M0239` = `be/db/migrations/0239_*.sql`. חומרה P0/P1/P2 × מאמץ S/M/L.

---

## 0. שורה תחתונה

1. **הכיוון שלך נכון, והנתונים החיים מוכיחים אותו.** הטקס של תכנון-קדימה (14 יום → firm → סשן רכש → תור ביצוע) הפסיק לעבוד בפועל בסוף אוגוסט: סשן רכש אחרון 23.8 (נוצר מחדש 7 פעמים באותו יום), טיוטות מנוע בוטלו כל שבוע באוגוסט, 23 שורות תוכנית פתוחות ומאחרות (24.8 → 17.9), 0 הזמנות רכש בוצעו בספטמבר, 6 מתוך 7 קבלות הסחורה בספטמבר ללא PO. **דיווח הייצור נפל לגמרי: פלט ייצור אחרון בספר 7.9.** התוצאה: 15 פריטי FG אמיתיים במלאי שלילי (סה"כ −543 יחידות; בנוסף ה-sentinel `EXCLUDED-NONSTOCK` −617 שאינו מלאי), כולם ממופים ל-Shopify → ה-reconciler מציב להם `available = 0` בחנות מאז → **מכירות אבודות בפועל**, לא רק "תכנון עיוור".
2. **"דיווח קודם, מעקב רטרואקטיבי" כבר קיים ב-80% בקוד.** מאז 27.7 דוח סוף-ריצה מחשב צריכה תקנית מה-BOM גם בלי ליקוט (`be/api/src/production-runs/report-handler.ts:488-495`, `net-picks.ts:221-239`). מה שחסר: דיווח ברמת טנק, ריצה בלי תוכנית כברירת מחדל (ולא כ"חריגה מסומנת"), תאריך אירוע אחורה, השלמה אוטומטית של טנקים, וערוץ AI. **זה תיקון M, לא בנייה מחדש.**
3. **"רכש נטו מהתחזית" = שינוי SQL אחד** ב-`fn_generate_purchase_session` (Part A.3, ~40 שורות) מאחורי מפתח policy, אחרי dry-run צד-לצד. **אבל חובה קודם לתקן P0:** תצוגת הביקוש `v_planning_demand_v2` סופרת **כל הזמנת LionWheel שאי פעם נראתה** (גם COMPLETED/CANCELED) כביקוש של השבוע — 49,313 יחידות "פתוחות" מול 1,313 באמת. רכש מהתחזית שיירש את זה יקנה על ביקוש פאנטום.
4. **תכנון ייצור קדימה — לבטל את הטקס, לא את הידע.** מה שהתוכנית נותנת באמת (סדר טנקים לפי תאריך אזילה, ≤1 טנק/יום, כלל מוזה-200) חי רק במתזמן. ההצעה: "המלצה להיום" = שאילתה (לא מצב שמור), מוצגת ב-`/production`; `production_plan` מוקפא לקריאה בלבד. אין firm/lock/cancel, אין שורות מאחרות, אין "ריצה לא מתוכננת".

**שלוש החלטות שרק אתה יכול לקבל** (§8): (א) לאשר תיקון P0 של תצוגת הביקוש עכשיו; (ב) בסיס ביקוש לרכש — תחזית בלבד או `GREATEST(תחזית, הזמנות פתוחות)` בשבוע הנוכחי; (ג) הקפאת `production_plan` + ביטול פגישת רביעי כטקס.

---

## 1. מה קורה בפועל — ראיות חיות (19.9.2026)

| מדד | ערך חי | משמעות |
|---|---|---|
| `rebuild_verifier` (cron לילי) | 19.9 succeeded, drift 0 (וגם 18.9, 17.9) | אמת המלאי מחזיקה — הבעיה היא **מה לא נכנס** לספר, לא מה שנכנס |
| פלט ייצור אחרון (`PRODUCTION_OUTPUT`) | **2026-09-07** (שורה אחת, דרך הטופס הישן `PA:`) | 12 ימים בלי דיווח ייצור. מכירות נמשכו: 1,040 יח' בשבוע 14.9, 1,750 בשבוע 7.9 |
| FG במלאי שלילי | **15 פריטים אמיתיים, −543 יח'** (+ sentinel `EXCLUDED-NONSTOCK` −617, לא מלאי): FG-NAM-1L −260 (ייצור אחרון 26.8), FG-FRE-500ML −45, FG-DET-500ML −29, FG-DET-500ML-NS −26, FG-CON-1L −11, FG-REV-500ML −9 … | כולם `shopify=y` → `available=0` בחנות (הקלמפ לאפס נעול, בצדק). זו עלות ישירה של אי-דיווח |
| RM/PKG שליליים | 11 מתוך 164 (PKG-CAP-GOLD-METAL −42, תוויות סנגריה/UBE/HOJ, RAW-APPLE-DRY −7) | קבלות סחורה לא נרשמות בזמן / צריכה תקנית גבוהה מהמציאות |
| דיווחי ייצור לפי חודש (`form_submissions`) | run_report: יולי 23, אוג' 28, **ספט' 6** · legacy `production_actual_submit`: יולי 45, אוג' 0, **ספט' 2** | הטופס הישן חזר לשימוש בספטמבר. שני מסלולים חיים במקביל |
| ריצות (`production_run`) | PLANNED 39 · IN_PRODUCTION 8 · PICKING 2 · REPORTED 59 · CANCELLED 8 | 49 ריצות תקועות באמצע. **אף ריצת TANK לא מדווחת אף פעם** (הקוד אוסר, ראו §3 F6) |
| תוכנית ייצור (`production_plan`) | 23 שורות `planned` מאחרות (24.8→17.9). אוגוסט: טיוטות מנוע (TEAEDD) בוטלו 5–6/שבוע; שורות שהושלמו = ידניות (proposal_id null) | הטקס generate → firm לא מחזיק; מה שמיוצר לא עובר דרכו |
| סשן רכש אחרון | **2026-08-23** (open; 7 superseded באותו יום; 18 POs: approved 1, skipped 9, proposed 8) | 4 שבועות בלי סשן. `planning_runs` אחרון 23.7 |
| הזמנות רכש 90 יום | כולן `source=manual`: CANCELLED 39, RECEIVED 12, OPEN 2, PARTIAL 2 · `purchase_order_place`: יולי 11, אוג' 5, **ספט' 0** | יחס ביטול 3:1. תור הביצוע של דורין ריק בספטמבר |
| PO פתוחות עכשיו | 5 (PO-00308 OPEN eta=NULL, 00307 PARTIAL NULL, 00310 PARTIAL NULL, 00216 PARTIAL eta 5.9 (עבר), 00287 OPEN eta 20.8 (עבר)) · 7/10 שורות פתוחות בלי ETA | "מלכודת הזמנה כפולה" חיה אצל 70% מהשורות |
| קבלות סחורה | יוני 26, יולי 28, אוג' 22, **ספט' 7 (1 בלבד מקושרת ל-PO)** | קבלה ממשיכה, אבל מחוץ לשרשרת הרכש |
| ספירות | 135–187/חודש; אחרונות 23.8 לכל הסוגים | סופרים הרבה — הספירה היא הדיווח שכן עובד. אבל 27 יום מאז האחרונה |
| תחזית | monthly, 13 שבועות, start 1.8, published 6.9 (3 גרסאות published במקביל) | טרייה. **נכתבה ב-SQL, לא דרך הפורטל** (הפורטל מוגבל ל-2 חודשים) |
| ביקוש "הזמנות פתוחות" השבוע (`v_planning_demand_v2`) | **49,313 יח' / 70 שורות** מול תחזית 2,885. באמת פתוח במראה: **1,313 יח'** | P0 §3 F1 |
| הזמנות LionWheel פתוחות | 36, **36 בלי `pickup_at`** | ההקרנה (`fn_compute_daily_fg_projection`) רואה 0 ביקוש מחויב; ה-brain מפצה ידנית |
| `orders_mirror` | 2,009 הזמנות, **0 עם `retired_at`**: COMPLETED 1,788, CANCELED 105, ROUNDTRIP_DELIVERED 80, UNASSIGNED 31, ASSIGNED 5 | שורש F1 |
| תיבת חריגים פתוחה | lionwheel_capped_window_gap 2,006 · lw_pick_data_missing 866 · lionwheel_order_note 270 · lw_pick_count_pause_skipped 240 · … · `po_line_over_receipt` 9 · `shopify_oversell` 15 · `count_large_variance` 2 | רעש אינטגרציה קובר את החריגים האמיתיים. אף אחד לא עובר על זה |
| `planning_policy` | `session_day_of_week=0` (ראשון) מאז 16.5 — הפגישה עברה לרביעי/חמישי ב-30.7 · `max_batches_per_day=2` (23.8) · `consolidation_window_days=26` · `component_cover_days_default=7` (שטוח לכולם) | גדר השחרור של הסשן מכוונת ליום הלא נכון |

**קריאה:** המערכת בנויה כשרשרת "תכנן → נעל → לקט → דווח → קנה". בפועל המפעל עובד "ייצר → (לפעמים) דווח → קנה כשחסר → קלוט". כל שלב-ביניים שהמערכת דורשת לפני הדיווח (שורת תוכנית, ריצה, ליקוט, סגירת טנק) הוא מקום שבו הדיווח נופל — והוא נפל.

---

## 2. איך זה בנוי היום (מפה קצרה)

```
תחזית חודשית (forecast_lines, SKU×חודש)
  └─ fn_forecast_daily_demand (M0239) — חלוקה לימי עבודה
       ├─ fn_compute_daily_fg_projection — GREATEST(LW מתוארך, תחזית), clamp 0   → /planning/inventory-flow, מתזמן טנקים, guardian
       ├─ v_planning_demand (v1, sum)  → fn_compute_fg_net_requirements → planning run (מנוע A — רדום מ-23.7)
       └─ v_planning_demand_v2 (GREATEST שבוע נוכחי) → purchase session Part B (פריטים BOUGHT_FINISHED בלבד)

production_plan (draft→planned→in_production→completed / cancelled)
  ├─ נכתב ע"י fn_plan_tea_production / fn_plan_matcha_repack / ידני (proposal_id null)
  ├─ ← purchase session Part A.1/A.2 (M0286:284-320): הביקוש היחיד ל-RM/PKG של פריטים מיוצרים
  ├─ ← fn_compute_daily_fg_projection_with_production (M0238): draft+planned = אספקה עתידית
  ├─ ← production_run "today" (materialize מהתוכנית) → ליקוט (production_run_pick, ללא ledger) → דוח (PICK_CONSUMPTION + PRODUCTION_OUTPUT)
  └─ ← v_production_plan_vs_actual (M0315), guardian Stage 0.5, Today board

purchase_session_po (proposed→approved→placed) → fn_create_manual_po → APPROVED_TO_ORDER → תור ביצוע (דורין) → fn_place_purchase_order (ETA חובה) → OPEN → goods receipt (GR_POSTED + related_po_line_id) → PARTIAL/RECEIVED
```

שני מסכי דיווח ייצור חיים: `/production` (ריצות, בניווט) ו-`/stock/production-actual` (הטופס הישן, 5,046 שורות, מחוץ לניווט אבל חי ב-URL ובשימוש בספטמבר). שני מנועי רכש: מנוע A (planning run, מבוסס תחזית, לא מורץ) ומנוע B (purchase session, מבוסס תוכנית, מזין את `/planning/procurement`).

---

## 3. ממצאים מדורגים (Top-25, חומרה ואז מאמץ עולה)

| # | חומרה | מאמץ | מקטע | ממצא | ראיה | תיקון |
|---|---|---|---|---|---|---|
| F1 | **P0** | S | ביקוש | **ביקוש פאנטום.** ענף ההזמנות הפתוחות ב-`v_planning_demand`/`_v2` מסנן רק `retired_at is null ∧ resolved ∧ qty>0`, בלי `lw_status`; ה-poller אף פעם לא כותב `retired_at` → 1,973 הזמנות שהושלמו/בוטלו נספרות כביקוש של השבוע הנוכחי (49,313 מול 1,313) | `M0239:1063-1068, 1138-1144`; `be/api/src/integrations/lionwheel/poller.ts:24-25, 349`; שאילתה חיה 19.9 | להוסיף `om.lw_status in ('UNASSIGNED','ASSIGNED','ACTIVE')` (אותו פרדיקט כמו ההקרנה `M0239:272`) לשתי התצוגות + pgTAP. A3 לא משתנה |
| F2 | **P0** | M | דיווח | **ייצור לא מדווח → FG שלילי → Shopify מציג 0.** 15 פריטים, −543 יח'; פלט אחרון 7.9. השורש: הדיווח דורש שורת תוכנית → ריצה → (ליקוט) → דוח פר-SKU; TANK לא ניתן לדיווח; טנק לא נסגר לבד; הטופס הישן חזר לשימוש | `report-handler.ts:101-105` (409 RUN_NOT_REPORTABLE ל-TANK), `:294-299` (רק תוכנית מקושרת-פריט נסגרת); `po/src/app/(production)/production/_lib/runs.ts:49-54`; DB חי | §4.1 "דיווח קודם": מסך "דווח יום" אחד + ערוץ AI; ריצה נוצרת מהדיווח; טנק = שדה ליטרים אופציונלי. **מיידי:** להשלים דיווחים אחורה ל-8–18.9 (הערוץ החדש עושה בדיוק את זה) |
| F3 | **P0** | M | רכש | **מסלול הרכש מת בלי תוכנית.** Part A.1/A.2 של הסשן = 100% שורות `production_plan`; Part B = BOUGHT_FINISHED בלבד. בלי תוכנית firmed → רשימת קנייה ריקה (חוץ ממלאי שלילי). ראיה: אין סשן מ-23.8, 0 PO בספטמבר | `M0286:284-333, 554-558, 616, 640` | Part A.3 מבוסס תחזית (§4.2), אחרי F1 |
| F4 | P1 | S | תכנון | 23 שורות תוכנית מאחרות. שורה מתוכננת שלא יוצרה = אספקה פנטום בהקרנה (אין `plan_date ≥ today`, קבלה = יום עסקים הבא) ובמקביל ביקוש בסשן. שום דבר לא סוגר אותן | `M0238:111-124`; `M0279:210`; `handler.overdue.ts:434`; `CURRENT_STATE.md:53` | להיום: לסגור/לבטל את ה-23 איתך. מבנית: הקפאת `production_plan` (§4.3) או תיחום CTE + ביטול אוטומטי בחצות |
| F5 | P1 | S | דיווח | טנקים לעולם לא מושלמים מהזרימה (השורש של תקרית 29.7). `close-batch` = planner/admin בלבד, בלי כפתור ב-`/production` | `report-handler.ts:276-278, 294-309`; `handler.close_batch.ts:63` | השלמה אוטומטית כשכל חברי ה-manifest דווחו; או — בהקפאת התוכנית — הבעיה נעלמת |
| F6 | P1 | M | דיווח | צריכה כפולה של RM בסיס כשטנק לוקט ויש >1 ריצת PACK: הדוח הראשון "שואב" את ליקוטי הטנק במלואם; ריצה שנייה מפוצצת מחדש מהמתכון. **מאושר בקוד; ב-26.8 (1,281 ל' פלט מול 1,299 ל' מים) לא נצפה פיצוץ** | `report-handler.ts:443-459, 409-413`; `net-picks.ts:242-262`; ledger 26.8 | הפשוט ביותר: לגזור בסיס תמיד לפי בקבוקים, ליקוטי טנק = אות שונות בלבד |
| F7 | P1 | M | ביקוש | **שני מודלים של ביקוש מחויב.** ההקרנה דורשת `pickup_at IS NOT NULL` → 36/36 הזמנות פתוחות בלתי נראות למנוע; התצוגות רואות הכל (F1). 0099 בוטל בשקט ע"י 0128 | `M0239:271-276`; `M0128:110-118`; `plan-production-14d/SKILL.md:27, 62-93` | פרדיקט "פתוח" משותף אחד (סטטוס פתוח, כמות לא-מלוקטת); ללא-תאריך = השבוע הנוכחי גם בהקרנה (כלל A3) |
| F8 | P1 | S | ביקוש | כמה גרסאות תחזית `published` חוקיות במקביל (אין unique); התצוגות סוכמות (כפול), ההקרנה מבצעת dedup | `handler.ts:199-214`; `M0239:1022-1046` מול `:296-303` | `DISTINCT ON (item, day)` לפי `published_at` בתוך `fn_forecast_daily_demand` |
| F9 | P1 | S | רכש | "אין בסיס ביקוש = עצור" (נעול 24.7) חי רק בסקיל. המנוע קונה על מלאי שלילי, עם LT `global_default`, cover שטוח | `M0286:616, 640, 746-749, 569` | `blocking_issue 'no_demand_basis'` ו-`lt_source='global_default'` בשלב 5 (~8 שורות) |
| F10 | P1 | S | רכש | `session_day_of_week=0` (ראשון) חי מול קדנציה רביעי/חמישי → גדר שחרור שגויה, תת-הזמנה | DB חי; `M0286:160-165, 907-914` | ערך policy, בלי קוד |
| F11 | P1 | S | רכש | `missing_price` → `unit_cost=0` → סה"כ ₪ של הסשן מוקטן; MOQ/order_multiple NULL על כל הקטלוג → עיגול no-op; `tier` קורס (~97% urgent) בעוד `tier_v2` קיים | `M0286:755-776`; `M0291:40-59`; `system_map.md:222-224, 287-294` | להחריג מה-₪ + סימון "≥"; המנוע יקרא `v_component_effective_moq`; לכתוב `tier_v2` |
| F12 | P1 | S | רכש | פריטים עם LT > 56 יום אף פעם לא נראים בזמן (אופק 56 חוסם את `need_date`) → תמיד "דחוף באיחור" | `M0286:142-144, 614-618, 780` | אופק ≥ max(LT)+consolidation (~150 יום), או `forecast_uncovered` חוסם פר-שורה |
| F13 | P1 | M | רכש | buffer שטוח 7 ימים לכל 187 הרכיבים; ההצעות ב-0292 מניחות "אין היסטוריית צריכה" — לא נכון מאז 27.7 | `M0286:151-153, 571`; `M0292:11-12` | 0292 יקרא צריכה אמיתית; overrides פר-פריט במפתח הקיים |
| F14 | P1 | S | תכנון | אסימטריה: `draft` נספר כאספקת FG בהקרנה אבל לא בסשן → תא "ירוק" בזרימת מלאי בזמן שהקנייה לא מכוסה | `M0238:128, 151` מול `M0286:296, 317` | אותה קבוצת סטטוסים בשני המקומות |
| F15 | P1 | XS | דיווח | דוח ריצה מתוארך אחורה מקבל `event_at=now` למרות בורר יום | `po/…/production/_components/ReportForm.tsx:173`; `RunList.tsx:113-132` | להעביר `?date=` ל-`event_at` |
| F16 | P1 | S | דיווח | קיצור-למלאי (cap-to-on-hand) מסתיר חוסרים: אין שורת `exceptions`, הפורטל מציג שורה אחת ונעלם | `report-handler.ts:523-532`; `ReportForm.tsx:310-317` | חריג פר-חוסר, או ברירת מחדל `confirm_negative=true` (המלאי השלילי הוא האות) |
| F17 | P1 | S | דיווח | דוחות ריצה בלתי הפיכים ובלתי נראים ל-API הניהולי של actuals (`PICK_CONSUMPTION` לא במפת ההיפוך) | `reverse-handler.ts:57-61, 208-212`; `detail-handler.ts:66-69` | להרחיב את המפה + פילטר `form_type` |
| F18 | P1 | S | חריגים | תיבת החריגים מוצפת ברעש LionWheel (>3,600 פתוחים) → `po_line_over_receipt`, `count_large_variance`, `shopify_oversell` קבורים | DB חי | סגירה/השתקה אוטומטית של קטגוריות רעש; תיבה = רק מה שדורש יד אדם |
| F19 | P1 | S | קבלה | סקיל הקבלה מ-AI כותב SQL ישיר ועוקף את ה-handler (בלי בדיקת סטטוס PO, התאמת פריט, Price Truth, `final_delivery`); אין API להיפוך קבלה; קבלת-יתר בלי תקרה (GAP-026: 15,005,002 יח') | `goods-receipt-from-invoice/SKILL.md:53-70`; `goods-receipts/schemas.ts:7`; `M0055:112-136` | הסקיל יקרא ל-`POST /goods-receipts` (צריך bearer של בוט, §4.4); `POST /goods-receipts/:id/reverse`; 409 מעל `ordered×(1+x)` בלי אישור |
| F20 | P1 | S | PO | `PATCH purchase-orders/:id` מקבל `expected_receive_date: null` על OPEN/PARTIAL → השורה נופלת מקבלות הסשן → סיכון הזמנה כפולה (הגנה קיימת רק בביצוע) | `update_handler.ts:19-24, 35, 116-118`; `M0298:120` | לדחות null בסטטוסים אלה |
| F21 | P2 | XS | PO | דף PO: `POStatusBadge` בלי APPROVED_TO_ORDER, `LineStatusBadge` בלי CLOSED_SHORT, ביטול מותר ב-API ל-APPROVED_TO_ORDER אבל לא בפורטל | `po/src/app/(po)/purchase-orders/[po_id]/page.tsx:238-254, 382-391, 592` | 4 מחרוזות |
| F22 | P2 | S | מעקב | Stage 0.5 של ה-guardian ו-Today board "אתמול" מפתחים על `status='planned'` / `completed_submission_id` → טנקים תמיד "לא דווח"; `v_production_plan_vs_actual` ללא צרכן בפורטל | `daily-ops-guardian/references/sql_library.md:44-56`; `po/src/features/home/today-board.ts:151-153, 187` | "האם היה דיווח אתמול" מהספר (`PRODUCTION_OUTPUT`), לא מהתוכנית |
| F23 | P2 | — | רכש | שני מנועי רכש סוטים זה מזה (ביקוש additive מול GREATEST, בטיחות, בחירת ספק, ETA) | `M0288:150-176` מול `M0286:571`; `M0103:102-197` מול `M0286:655-748` | החלטה: מנוע אחד (§4.2) |
| F24 | P2 | S | כללי | אזורי זמן: `current_date` של ה-DB (UTC) מכריע "מאחר"/"לא דווח" מול תאריך IL; ריצות מקבלות תאריך UTC | `M0315:206`; `handler.overdue.ts:434`; `production-runs/handler.ts:375` | `(now() at time zone 'Asia/Jerusalem')::date` במקום אחד |
| F25 | P2 | XS | מסמכים | `LOCKED_DECISIONS.md:236-238, 292-294` אומרים "דוח בלי ליקוט לא צורך כלום" / "צריכה בליקוט" — **לא נכון מאז 27.7** (וגם `report-handler.ts:18-19`, `0295:9`, tranche 147:29) | `report-handler.ts:365-367, 488-495` | תיקון מסמך (docs lane, אישור טום) |

ממצאים נוספים (P2, ברשימת המחיקות §6): גרסאות מתות של `fn_propose_weekly_production_plan` v1–v3, `v_forecast_export_*`, `/planning/weekly-outlook`, `/planning/production-simulation` (902 שורות `material_requirements.ts`), `v_planned_inflow_by_day` + שכבת PlannedChip, `revalidate-after-count` ללא צרכן, 17 מפתחות `planning.demand.mto.*` ללא קורא, `planning.forecast.freeze_horizon_weeks` (לא נקרא), ענפי קדנציה weekly/daily בתחזית (הכל monthly בפועל).

---

## 4. הערכת הכיוון שלך — מה מחזיק, מה נשבר, הדרך הקצרה

### 4.1 "קודם מדווחים ייצור, המעקב רטרואקטיבי"

**כבר קיים:** `POST /api/v1/mutations/production-runs/:run_id/report` גוזר צריכה תקנית מה-BOM המוצמד לכל רכיב שאין לו שורת ליקוט (`report-handler.ts:374-424, 488-495`; `net-picks.ts:221-239`), מפרסם `PICK_CONSUMPTION` + `PRODUCTION_OUTPUT` בטרנזקציה אחת, אידמפוטנטי, קיצור-למלאי. הליקוט כבר אופציונלי. אין הנחת "500 ליטר מלא" — הצריכה = מתכון × בקבוקים שדווחו.

**מה חסר כדי שזה יהיה מסלול ברירת המחדל (M):**
1. **ריצה נוצרת מהדיווח.** היום ריצה קיימת רק אם יש שורת תוכנית לאותו יום או "+ Extra job" (מסומן כחריג ל-טום). לשנות: `unplanned` = מצב נורמלי, בלי חריג, בלי `change_log` מיוחד (`production-runs/handler.ts:764-780`). הסכמה כבר מאפשרת (`production_run.plan_id` nullable).
2. **מסך "דווח יום" אחד** (במקום כרטיס פר-ריצה): רשימת FG שיוצרו היום + כמות + פחת, שדה אופציונלי "ליטרים בטנק" פר-בסיס, תאריך (ברירת מחדל היום, ניתן אחורה — F15). לחיצה אחת → תצוגת צריכה מקדימה (הקיימת: `consumption-preview`) → אישור → N דוחות בטרנזקציה. זה מסך פורטל אחד + endpoint אחד `POST /mutations/production-reports/day` שעוטף את הלוגיקה הקיימת (או, בגרסה העצלה, הסקיל מתזמר את ה-endpoints הקיימים ואין backend חדש).
3. **טנק:** ליטרים שבושלו = שדה אופציונלי ב-actual (חדש, לא בספר); חריג "תפוקה" כש-Σ בקבוקים×מילוי < ליטרים×(1−x). ריצות TANK הופכות לרשומת-ליקוט בלבד; אף פעם לא חוסמות דיווח.
4. **תיקון F6** (בסיס תמיד לפי בקבוקים) לפני שמאפשרים ליקוט + דיווח-קודם באותו טנק.
5. **מעקב רטרואקטיבי** — שלוש שאילתות, לא מצב שמור: (א) "ייצור אתמול" מהספר (Stage 0.5 של ה-guardian → F22); (ב) תחזית מול מכירות (`Stage 1b` הקיים, כבר בלתי תלוי בתוכנית); (ג) יוצר-מול-צורך: `PRODUCTION_OUTPUT` פר-פריט/יום מול חוסר ההקרנה של אותו יום (`fn_compute_daily_fg_projection`). `v_production_plan_vs_actual` נשאר להיסטוריה בלבד.

**מה מפסידים:** אישור-מראש של הליקוט כ"מדידה" (הליקוט נשאר אפשרי כאופציה). **לא מפסידים** שום דבר באמת המלאי: הספר נשאר append-only, המפתחות הקיימים, `related_bom_version_id` נכון-מקור.

### 4.2 "רכש נטו לפי התחזית"

**מצב:** מנוע A (`fn_execute_planning_run` → `fn_compute_fg_net_requirements` → `fn_explode_bom_to_components` → `fn_compute_component_net_purchase` → recs) **כבר מבוסס תחזית מקצה לקצה** (`M0288:109` → `M0126` → `M0107` → `M0103`) — אבל רדום (ריצה אחרונה 23.7, אין cron, מגיע לתור רק דרך convert). מנוע B (הסשן החי) מבוסס תוכנית לפריטים מיוצרים.

**השינוי המינימלי (M, ~40 שורות SQL, בלי טבלאות חדשות):** ב-`fn_generate_purchase_session` STEP 1 להוסיף Part A.3 לפריטי MANUFACTURED/REPACK: ביקוש יומי מ-`fn_forecast_daily_demand` (אחרי dedup F8, פריטים ACTIVE), הליכה על מלאי FG (`current_balances`) − ביקוש מצטבר, ופיצוץ תוספת החוסר של כל יום דרך `fn_explode_bom_to_components(item_id, qty)` (overload פר-פריט, `M0191`) לתוך `_ps_demand`. כל מה שאחרי (avg_daily, safety, need_date, lot, MOQ, tier) לא משתנה כי הוא קורא רק מ-`_ps_demand`. **גידור:** מפתח `planning.purchase.demand_basis ∈ {firmed_plan, forecast}` (ברירת מחדל `firmed_plan`), שני סשנים dry-run צד-לצד (ה-brain דורש dry-run לפני שינוי התנהגות), ואז מחיקת A.1/A.2 והמפתח.

**תנאים מוקדמים:** F1 (אחרת קונים על ביקוש פאנטום), F8, אופק תחזית ≥ אופק רכש + LT (הגרסה החיה 13 שבועות — מספיק לרוב; F12 לפריטי LT ארוך), F9 (עצירה על "אין בסיס").

**מה נשבר / דורש החלטה:** הכלל הנעול של 24.7 ("תוכנית firmed = הבסיס החזק, תחזית = fallback") מתהפך — צריך שורת lock חדשה; `NOT EXISTS v_firmed_production_fg_demand` הופך ל-no-op; טסטים `0235` ו-`planning_firmed_week_demand_api.test.ts` לכתיבה מחדש; **מנוע אחד** — ההמלצה: להשאיר את הסשן (B) כמנוע היחיד כי הוא מזין את `/planning/procurement` ואת תור דורין, ולהקפיא את מנוע A (planning runs, recommendations, `/planning/runs`).

### 4.3 "בלי תכנון ייצור קדימה"

**מה התוכנית נותנת באמת** (מקרה-נגד הוגן): סדר טנקים על 10 בסיסים עם 1–2 טנקים/יום לפי ימי כיסוי (`M0279:259-270`); ≤1 טנק/יום + כלל מוזה-200 (`M0279:215-236` — קיימים רק במתזמן, אפס אכיפה בזמן ריצה); פיצול אריזה פר-טנק לפי חוסר פר-FG (`M0279:280-307`); לוח חגים/ימי עבודה; שרשרת ביקורת תוכנית→ריצה→בפועל. **קניית RM קדימה לא תלויה בתוכנית** אם 4.2 נוחת (LT 14 יום ברירת מחדל מכוסה ע"י netting מהתחזית).

**ההמלצה (הכי עצלה שעובדת):** לבטל את הטקס (drafts → פורטל → firm → Lock Gate → relay) ואת פגישת רביעי כ"נעילה". במקומו: **"המלצה להיום" = שאילתה** על `/production` — אותה לוגיקת EDD + backlog מחויב + כללי מוזה/קיבולת, מחושבת בבוקר, מוצגת כרשימה מדורגת עם "למה" (תאריך אזילה, ₪ בסיכון). דניס לוחץ "התחל" (ריצה) או פשוט מדווח בסוף היום. **אין מצב שמור → אין שורות מאחרות, אין firm/cancel, אין "לא מתוכנן".** `production_plan` מוקפא לקריאה בלבד (היסטוריה; ⊥ DROP TABLE). אם תרצה בכל זאת תוכנית ממומשת (למשל ל-Today board), הווריאנט: `fn_plan_tea_production` עם `p_emit_days=1..2`, נכתב ע"י ה-guardian 06:30, מבוטל אוטומטית בחצות — בלי פגישה ובלי UI נעילה.

**מה הופך למת** (רשימה מלאה §6): דף `/planning/meeting`, handlers firm/cancel/generate-drafts/draft-week/firmed-week-demand, `v_firmed_production_fg_demand`, `v_production_plan_slippage`, PlannedChip overlay, `material_requirements.ts`/production-simulation, סקיל `plan-production-14d` (שלבים 2–5), אריחי "slipped plans" בדשבורד.

### 4.4 "כל הדיווחים עם AI"

**התבנית כבר קיימת** ב-`goods-receipt-from-invoice`: חילוץ → אימות חי → הצגה → אישור טום → פרסום → אימות. **הערוץ כבר קיים:** `supabase/functions/wa-order-bot` (מקלט WhatsApp, HMAC, ACK) → worker ב-`api/src/order-intake` (מנוע פרסור נבדק). **האימות כבר קיים:** מסלול bearer `JOB_RUNNER_TOKEN` בלי סשן Supabase (`server.ts:231-281`).

**ההצעה — "ערוץ דיווח אחד" לארבעת סוגי הדיווח:**

| דיווח | קלט טבעי | מה ה-AI בונה | לאן זה נכנס (קיים) | פער |
|---|---|---|---|---|
| ייצור (עדיפות) | "בישלתי 500 ל' דטוקס, מילאתי 400 ליטר ו-180 חצי, פחת 5" (טקסט/קול/תמונת דף ייצור) | `{date, lines:[{item, qty, scrap}], tank?:{base, liters}}` → מיפוי שמות→`items` (+aliases) | `GET production-runs/today?date` → `POST production-runs` (ריצה ללא תוכנית) → `GET consumption-preview` → `POST …/report` עם `idempotency_key='AIPR:<date>:<item>:<hash>'` | bearer לבוט (actor = app_user של דניס); endpoint "יום" אחד (או תזמור בסקיל); שדה ליטרים; F6/F5/F15 |
| קבלת סחורה | תמונת חשבונית/תעודה (קיים) | קיים | `POST /goods-receipts` **במקום SQL ישיר** (F19) | bearer; API להיפוך |
| ספירה | "ספרתי: סוכר 12 שקים, מים 40 ג'ריקן…" / תמונת דף ספירה | שורות ספירה | `POST /physical-counts` (open → submit; blind count נשמר כי הצילום לא רואה snapshot) | bearer |
| פחת | "זרקתי 2 ק"ג מחית לימון, פג תוקף" | שורה + סיבה + תמונה | `POST /waste-adjustments` (ספי אישור קיימים) | bearer |

**עקרונות:** (1) אישור אנושי אחד תמיד (דניס בטלפון או טום בצ'אט — החלטה §8), (2) הפרסום דרך ה-API ולא SQL — כל בדיקות ה-handler והאידמפוטנטיות נשמרות, (3) הצעה ≠ אמת: ה-AI מכין, האדם מאשר, המערכת רושמת — בדיוק כפי שנעול ב-CLAUDE.md ("טפסים ואינטגרציות יוצרים אירועים"), (4) חוק הברזל של דניס "שום יציאה בלי דיווח" נאכף ע"י ה-guardian ב-06:30 מהספר (F22), לא מהתוכנית.

---

## 5. תוכנית מוצעת (שלושה שלבים, כל אחד ניתן לאישור לבד)

### שלב A — תיקונים שלא תלויים בשום החלטה (השבוע, לאנה `backend-db` + `portal`, ~2 ימי עבודה)

| # | מה | ממצא | בדיקה |
|---|---|---|---|
| A1 | פילטר `lw_status` בשתי תצוגות הביקוש | F1 | pgTAP: הזמנה COMPLETED לא נספרת; סשן dry-run מציג −2,167 יח' BF פאנטום |
| A2 | להשלים דיווחי ייצור 8–18.9 אחורה (עם דניס, דרך המסלול הקיים + `event_at` נכון) | F2 | FG לא שלילי; `rebuild_verifier()=0`; Shopify `available` > 0 לפריטים המדווחים |
| A3 | לסגור/לבטל 23 שורות תוכנית מאחרות (איתך, שורה-שורה) | F4 | שאילתת G3 = 0 |
| A4 | `session_day_of_week` → ערך התואם את יום הביצוע של דורין (חמישי = 4) | F10 | סשן dry-run: גדר השחרור זזה |
| A5 | דוח ריצה: `event_at` מהיום שנבחר; טנק נסגר אוטומטית כשכל ה-manifest דווח; `PICK_CONSUMPTION` במפת ההיפוך | F15, F5, F17 | טסט handler: דוח אחורה, טנק+2 PACK, היפוך |
| A6 | חוסר → שורת `exceptions` (או `confirm_negative` כברירת מחדל) | F16 | חריג נפתח בדוח עם חוסר |
| A7 | `PATCH PO` דוחה ETA null ב-OPEN/PARTIAL; 4 מחרוזות בדף PO | F20, F21 | טסט 409; snapshot |
| A8 | השתקה/סגירה אוטומטית של קטגוריות רעש LionWheel בתיבה | F18 | תיבה פתוחה < 50 |
| A9 | dedup גרסאות תחזית ב-`fn_forecast_daily_demand` | F8 | pgTAP: שתי גרסאות חופפות → סכום אחד |

### שלב B — הכיוון (2–3 שבועות, אחרי ההחלטות ב-§8)

| # | מה | תלוי ב | לאנה |
|---|---|---|---|
| B1 | דיווח-קודם: ריצה ללא תוכנית = נורמלי; מסך "דווח יום"; שדה ליטרים; בסיס לפי בקבוקים (F6) | החלטה (ג) | backend-db + portal (UX handoff) |
| B2 | ערוץ דיווח AI: bearer לבוט (actor = דניס) + סקיל `production-report-from-message` (תבנית הקבלה) + הסבת סקיל הקבלה ל-API | B1 | integration + docs |
| B3 | רכש מהתחזית: Part A.3 מאחורי `planning.purchase.demand_basis`; 2 סשנים dry-run; החלפה; מחיקת A.1/A.2 + seam | A1, A9, החלטה (ב) | backend-db |
| B4 | "המלצה להיום" על `/production` (שאילתה: EDD + backlog + כללים כאזהרות) | B1 | backend-db (view) + portal |
| B5 | הקפאת `production_plan` + הסרת meeting/firm/cancel/generate מהניווט; guardian Stage 0.5 מהספר; Today board "אתמול" מהספר | B4, החלטה (ג) | portal + docs |
| B6 | עדכוני lock (טום, כותב יחיד): §Forecast (8 שבועות → מתגלגל 13 שבועות חודשי), §Production v2 (ריצה ללא תוכנית = נורמלי; צריכה נגזרת בדיווח; ליקוט אופציונלי), procurement-planning כלל 2 (תחזית = בסיס ראשי), `plan-production-14d` → ארכיון, F25 | — | טום |

### שלב C — מחיקות (אחרי B, כל אחת עם ראיית "אין קורא")

ראו §6. ⊥ `DROP TABLE`/`DROP COLUMN` בפרוד; פונקציות ותצוגות ללא קורא — כן.

---

## 6. רשימת מחיקה (מועמדים, כל אחד עם ראיה)

**מיד (אין קורא היום):** `fn_propose_weekly_production_plan` v1–v3 (`M0135/0140/0143`; לא קיימת בפרוד); `api_read.v_daily_inventory_projection` (`M0136/0141`); `v_forecast_export_headline/lines` (`M0019:482-529`); `v_forecast_status` + `handleForecastActive`; routes תחזית ללא צרכן (validation-summary, diff, discard); `/planning/weekly-outlook` + `/queries/inventory/weekly-outlook`; `revalidate-after-count`; מפתחות policy יתומים (`planning.demand.mto.*` ×17, `planning.forecast.freeze_horizon_weeks`); ענפי weekly/daily בתחזית; `toLedgerItemType` ו-`requirementForRun` כפול.

**אחרי B5:** `/planning/meeting`, handlers firm/cancel/draft-week/generate-drafts/firmed-week-demand, `v_firmed_production_fg_demand` (`M0221`), `v_production_plan_slippage` (`M0118`) + slipped-plans, `v_planned_inflow_by_day` + PlannedChip/PlannedOverlayToggle/PlannedTooltip/PlannedItemSection, `material_requirements.ts` + `/planning/production-simulation`, `fn_plan_tea_production`/`fn_plan_matcha_repack` (או שמירה כ"המלצה להיום"), `plan-production-14d`, `/planning/purchase-session` ו-`/planning/purchase-calendar` (stubs להפניה).

**אחרי B3:** מנוע A כולו (`M0104/0288/0126/0107/0103/0110/0289`, `planning_runs*`, `planning/route.ts` run/recs/convert, `po_bridge.ts`, `/planning/runs`, כרטיס RecommendationsToConvert) — או ההפך; אחד חייב ללכת (F23).

**אחרי B1:** הטופס הישן `/stock/production-actual` (5,046 שורות) + `production-actuals/handler.ts` נתיב submit (1,588 שורות; להשאיר list/detail/reverse), `tests/e2e/production-actual-real.spec.ts` (URL-ים מתים), ואם הליקוט מבוטל: `pick-confirm-handler.ts`, `material-delta-handler.ts`, PickList/PickRow/DoneBar/EditQtySheet/AddMaterialControl, סוגי תנועה `MATERIAL_DELTA(_REVERSAL)` (מעולם לא נכתבו).

---

## 7. מה נשמר קדוש (לא משתנה בשום תרחיש)

`stock_ledger` append-only, תיקונים בהיפוך בלבד; `balance_anchors` + הקרנה מחושבת; `rebuild_verifier()=0` כשער; דגלים קפואים; הכיוון מערכת→Shopify והקלמפ לאפס; A3/A4 (הבאקטינג לשבוע נוכחי ו-inbound=0 ב-FG netting — הופכים ל-moot רק אם מנוע A מוקפא בכתב); אין סוג תנועה חדש בלי אישור בכתב (ההצעה לא מוסיפה אף אחד).

---

## 8. שאלות פתוחות לטום (7, כל אחת עם ברירת מחדל שאפשר פשוט לאשר)

1. **F1 עכשיו?** ברירת מחדל: כן. משנה את מספרי ה-BF בסשן הבא (−2,167 יח' פאנטום).
2. **בסיס ביקוש לרכש:** תחזית בלבד, או `GREATEST(תחזית, הזמנות פתוחות)` בשבוע הנוכחי (A3)? ברירת מחדל: GREATEST בשבוע הנוכחי, תחזית בלבד אחריו.
3. **תכנון קדימה:** להקפיא `production_plan` ולהחליף ב"המלצה להיום" (שאילתה)? או וריאנט 1–2 ימים ממומש? ברירת מחדל: שאילתה.
4. **פריטים עם LT מעבר לכיסוי התחזית:** להמשיך בקצב ממוצע, או לחסום ולשאול פר-פריט? ברירת מחדל: לחסום (`forecast_uncovered`) — זה הכלל הישר.
5. **חוסרים בדיווח:** לפרסם מלאי שלילי כאמת (`confirm_negative` ברירת מחדל) או קיצור ל-0 + חריג? ברירת מחדל: שלילי = אות; ספירה מתקנת.
6. **ערוץ AI:** מי מאשר (דניס בטלפון / טום בצ'אט) ואיזה חשבון מפרסם (app_user של דניס דרך bearer בוט)? ברירת מחדל: דניס מאשר, actor = דניס, טום מקבל סיכום ב-06:30.
7. **ליטרים בטנק:** לתעד כ-actual (תפוקה נראית) או בקבוקים בלבד? ברירת מחדל: שדה אופציונלי, חריג תפוקה >10%.

---

## 9. נספחים

### 9.1 שאילתות שהריצו את הראיות (קריאה בלבד, 19.9)

```sql
-- ביקוש פאנטום (F1)
select source_type, round(sum(demand_qty)), count(*) from api_read.v_planning_demand_v2
where period_bucket_key = date_trunc('week', current_date)::date group by 1;
-- open_order: 49313 / 70 rows ; forecast: 2885 / 38 rows
select lw_status, count(*), count(*) filter (where retired_at is not null) from private_core.orders_mirror group by 1;
-- COMPLETED 1788 (0 retired), CANCELED 105, ROUNDTRIP_DELIVERED 80, UNASSIGNED 31, ASSIGNED 5

-- FG שלילי (F2)
select item_id, round(calculated_on_hand) from private_core.current_balances where item_type='FG' and calculated_on_hand<0;
-- 16 rows incl. sentinel EXCLUDED-NONSTOCK (-617); real items 15, sum -543; last PRODUCTION_OUTPUT 2026-09-07

-- תוכנית מאחרת (F4)
select count(*) from private_core.production_plan where plan_type='production' and status in ('planned','in_production')
 and completed_submission_id is null and closed_at is null and cancelled_at is null and plan_date < current_date;  -- 23

-- ליקוט + דיווח באותו יום (F6, 26.8): RAW-WATER 6 rows -1299 L; output ≈ 1281 L → לא נצפה כפל
```

### 9.2 דוחות הסוכנים

ארבעת דוחות הביקורת המלאים (מקטע 1 תחזית/ביקוש, 2 תכנון, 3 דיווח, 4 רכש/PO/קבלה) נמצאים בתמליל הסשן; הממצאים שלהם מוזגו ל-§3 עם ציטוטי `קובץ:שורה`. ה-UX gate (5 ממדים, צילומי מסך) — `docs/phase8/dry-runs/2026-09-19-ux-release-gate-planning-chain.md`.

### 9.3 מה לא נבדק

- LionWheel / Green Invoice API חיים (לא נדרש לביקורת זו; כל ממצא אינטגרציה כאן הוא מהמראה ב-DB).
- ערך ₪ מדויק של המכירות האבודות מ-`available=0` (אפשרי מ-`v_fg_economics` × ימי אפס; לא חושב).
- ריצת pgTAP/`npm test` — הביקורת קריאה-בלבד; שום קוד לא שונה.
