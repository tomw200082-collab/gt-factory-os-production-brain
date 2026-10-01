# מאסטרפרומפט — צינור לידים מלא: קליטה → Postgres → התראה → פורטל

> **הוראת שימוש (Tom):** הדבק את כל הקובץ הזה כהודעה ראשונה בסשן Claude Code חדש.
> הסשן בונה את הכל בשלבים, עם ראיות בכל שלב. אל תדביק חלקים — הקובץ שלם בכוונה.
>
> **מקור:** נכתב 2026-08-07 בסשן `claude/auto-email-leads-updates-1ojqwa` אחרי אבחון מלא
> של תשתית הלידים הקיימת (Make + Google Sheets). האבחון המלא:
> `docs/integrations/leads-email-alert-2026-08-07.md` בריפו production-brain.

---

## פתיחה — מי אתה ומה המטרה

אתה בונה את **צינור הלידים של GT Everyday** מקצה לקצה, כך שתום יוכל לשכוח לגמרי
מהתשתית שאליה לידים נכנסים. הגדרת הצלחה אחת: **ליד ממלא טופס בפייסבוק → תוך דקות
תום מקבל מייל, והליד מופיע במסך הלידים בפורטל עם סטטוס, אחראי וטיימר SLA — בלי
Google Sheets ובלי Make בנתיב הקליטה.**

עבוד לפי `CLAUDE.md` של production-brain (סדר סמכויות, ראיות, stop conditions).
זה מודול `sales` — **בידוד מודולים חל: אסור לגעת בסכמת הליבה של factory-os.**

## רקע — מה קיים ומה שבור (אומת 2026-08-07, אל תאמת מחדש אלא אם נתקעת)

1. היום לידים מ-Facebook Lead Ads נכתבים "ישירות" לגיליון Google Sheets
   `לידים GT` (`1G2HpMpGIQDfkokQ11WVTw2OzWUYlbFOR8kT3EHA_4PI`) — אינטגרציה שתום לא
   בנה ב-Make. הליד האחרון: **07/06/2026**. הצינור מת ואיש לא ידע.
2. ב-Make (team `1240098`): כל חיבורי Facebook פגי תוקף, **כל חיבורי Google
   Sheets מבוטלים (`invalid_grant`)**. חיבור Gmail `new leads` (id `6308857`) —
   **חי, תקף עד 2027-02**, מוכח בשליחה (Guardian daily).
3. תרחיש Make `5195363` ("GT — התראת ליד חדש") תוקן ברמת התבנית (מיפוי שדות
   נכון, HTML מעוצב RTL מוכן) אבל תלוי בחיבורי Sheets מתים. **אל תנסה להחיות
   אותו — הוא נשאר legacy.** קח ממנו רק את תבנית ה-HTML של המייל.
4. לקח מרכזי מהאבחון: OAuth refresh-tokens של אינטגרציות צד-שלישי מתים בשקט.
   לכן הארכיטקטורה החדשה מחזיקה **מינימום OAuth**: קליטה ב-webhook לשרת שלנו,
   שליחת מייל דרך webhook יחיד ל-Make (בלי OAuth בצד שלנו).

## סמכות ואישורים

- הצהרת מודול `sales` אושרה בכתב (Tom, 2026-08-04). **Amendment A** (טבלאות
  `lead`, `lead_event`, `assignment`, `task` + הסרת דחיית ממשקי UX) ממתין ב-PR #98
  של production-brain. **הדבקת המאסטרפרומפט הזה על-ידי תום היא אישורו בכתב של
  Amendment A.** פעולה ראשונה שלך: עדכן את
  `docs/decisions/modules/sales-declaration.md` — סמן Amendment A כ-APPROVED עם
  תאריך היום והפניה לקובץ הזה, ורשום ב-PR #98 שהאישור ניתן.
- `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` נשאר `false`. **שום שליחה ללקוח/ליד.**
  מייל התראה לתום (`tom@gteveryday.com`) הוא פנימי — מותר.
- דגלים קפואים, `stock_ledger`, `balance_anchors` — לא נוגעים. בכלל.

## ריפואים לצרף לסשן (add_repo)

| ריפו | תפקיד |
|---|---|
| `tomw200082-collab/gt-factory-os-production-brain` | ממשל, החלטות, תיעוד |
| `tomw200082-collab/gt-factory-os` | backend: Fastify, Postgres, migrations, Edge Functions |
| `tomw200082-collab/gt-factory-os-portal` | פורטל Next.js 15 |
| `tomw200082-collab/Sales-Machine` | דוקטרינת מכירות, מסע לקוח, מצב מודול `sales` |

## ארכיטקטורה — החלטות נעולות לבנייה הזו

```
Facebook Lead Ads ──webhook──► Supabase Edge Function (meta-leads-webhook)
                                    │  Graph API fetch (page token)
                                    ▼
                          Postgres: sales_core.lead + lead_event (append-only)
                                    │                    │
                        POST webhook│                    │ read models
                                    ▼                    ▼
                     Make "GT — Lead Alert" (Gmail)   פורטל /sales/leads
                            → tom@gteveryday.com
```

1. **מקור אמת ללידים: Postgres, סכמה `sales_core`.** לא Sheets. Sheets הופך
   ל-legacy לקריאה בלבד אחרי ייבוא היסטורי.
2. **קליטה: Meta Lead Ads webhook → Supabase Edge Function.** בלי Make ובלי
   Sheets בנתיב. בנוסף endpoint קליטה גנרי (`POST /ingest/lead` + bearer token)
   כדי שכל מקור עתידי (טופס אתר, WhatsApp, הזנה ידנית) ייכנס לאותו צינור.
3. **התראה: trigger בצד ה-backend על ליד חדש → POST ל-webhook חדש ב-Make
   ("GT — Lead Alert": CustomWebHook → Gmail `sendAnEmail`, חיבור `6308857`).**
   אותו דפוס מוכח כמו Guardian daily (HTTP 200 evidence בריפו). תבנית המייל:
   ה-HTML המתוקן מתרחיש `5195363` (RTL, שם עסק, איש קשר, טלפון ללא קידומת `p:`,
   קישורי tel:/mailto:, כפתור לפתיחת הליד — עדכן לקשר לפורטל במקום לגיליון).
4. **פורטל: route group חדש `/sales`** תחת gt-factory-os-portal. מודול מבודד.
5. **דדופ:** unique על `(source, external_id)`. התאמת טלפון/אימייל לליד קיים —
   דגל `possible_duplicate`, לא חסימה.
6. **SLA ברירת מחדל: 24 שעות** לנגיעה ראשונה (U-010 פתוח — פרמטר, לא קבוע בקוד).

## שלבי ביצוע — עצור בסוף כל שלב עם ראיות לפני המעבר הלאה

### שלב 0 — ממשל
קרא boot docs. עדכן sales-declaration (אישור Amendment A, ראה למעלה). ודא lane.

### שלב 1 — סכמה
Migration חדש ב-gt-factory-os: סכמה `sales_core` נפרדת.

- `lead`: `id uuid pk`, `source text` (`facebook` / `manual` / `import_sheets` / …),
  `external_id text`, `business_name`, `contact_name`, `phone`, `email`, `city`,
  `campaign_name`, `ad_name`, `is_owner boolean`, `status text`
  (`new` / `contacted` / `in_progress` / `won` / `lost`), `assignee text`,
  `possible_duplicate_of uuid null`, `created_at`, `first_touch_at timestamptz null`.
  `unique (source, external_id)`.
- `lead_event`: append-only, כמו דוקטרינת ledger — `id`, `lead_id fk`,
  `event_type` (`created` / `status_change` / `note` / `assignment` / `alert_sent`),
  `payload jsonb`, `actor text`, `created_at`. **אין UPDATE/DELETE — תיקון = אירוע
  הפוך.** טריגר DB שחוסם UPDATE/DELETE.
- שינוי סטטוס/אחראי על lead תמיד כותב גם lead_event (בטרנזקציה אחת).
- pgTAP: קליטה, דדופ, חסימת UPDATE על lead_event, מעבר סטטוס. דווח N/N.

### שלב 2 — קליטה
שתי Edge Functions ב-gt-factory-os:

- `meta-leads-webhook`: GET לאימות challenge של Meta (`META_VERIFY_TOKEN`);
  POST מקבל אירוע `leadgen`, מושך שדות מלאים מ-Graph API
  (`META_PAGE_ACCESS_TOKEN` — long-lived, secret), ממפה, מכניס ל-`sales_core.lead`
  + `lead_event(created)`. אידמפוטנטי על `leadgen_id`. שדות הטופס הקיימים:
  שם עסק ("מה_שם_המסעדה/בית_הקפה/בר_שלך?"), בעלים/מנהל
  ("האם_את.ה_מנהל.ת_או_בעלים_בתחום_המסעדנות?"), full_name, email, phone_number
  (מגיע עם קידומת `p:` — הסר), city. **אל תנחש שמות שדות מעבר לאלה — משוך lead
  אמיתי אחד ובדוק.**
- `sales-lead-ingest`: POST גנרי, bearer `LEAD_INGEST_TOKEN`, אותו נתיב כתיבה.

Secrets שתום מגדיר (עצור ובקש כשמגיעים לכאן): `META_VERIFY_TOKEN`,
`META_PAGE_ACCESS_TOKEN`, `LEAD_INGEST_TOKEN`, `MAKE_LEAD_ALERT_WEBHOOK_URL`.

### שלב 3 — התראה
- בנה ב-Make (MCP זמין) תרחיש חדש "GT — Lead Alert": CustomWebHook → Gmail
  (חיבור `6308857`, נמען `tom@gteveryday.com`, `{{1.subject}}` + `{{1.html}}` raw).
  הפעל אותו. שמור את ה-URL של ה-hook כ-secret.
- בצד הקליטה: אחרי insert מוצלח של ליד חדש (לא ייבוא, לא כפילות) — POST ל-hook,
  רשום `lead_event(alert_sent)`. אידמפוטנטי: לא יותר מהתראה אחת לליד.
- נושא: `🟢 ליד חדש: {business_name} | {contact_name}`.

### שלב 4 — ייבוא היסטורי
~248 לידים מהגיליון (הלשונית המטופלת: `סטטוס | תאריך | שם העסק | שם מלא | טלפון |
אימייל | עיר | בעלים? | מודעה | הערות`). קרא דרך Drive MCP (עובד — OAuth של Make
הוא ששבור, לא של MCP) או בקש מתום CSV. `source='import_sheets'`,
`external_id` = hash של (טלפון+תאריך). **ייבוא לא שולח מיילים.** דדופ מול עצמו.
דווח: נקלטו X, כפילויות Y, נדחו Z + סיבה.

### שלב 5 — פורטל
**לפני קוד: פתח tranche doc עם מניפסט קבצים מלא (hook אוכף), ועמוד בשער ה-UX
של הפורטל (handoff packet).** היקף מינימלי ושמיש:

- `/sales/leads` — אינבוקס: טאבים לפי סטטוס, שורת ליד = עסק, איש קשר, עיר,
  קמפיין, גיל הליד + באדג' SLA (ירוק <24h, אדום מעבר), אחראי. מיון: חדשים למעלה.
- `/sales/leads/[id]` — פרטי ליד: כל השדות, ציר זמן מ-`lead_event`, פעולות:
  שינוי סטטוס, שיוך אחראי, הוספת הערה, קישורי `tel:` / `wa.me` / `mailto:`.
  כל פעולה = mutation שכותבת lead_event.
- עברית, RTL, לפי `portal_ux_standard.md`. **אין עריכת** `tailwind.config.ts`,
  `globals.css`, או קבצי UX standard.
- Role-gating לפי מנגנון `app_users` הקיים.

### שלב 6 — חיבור לייצור וראיות קצה-לקצה
1. תום מחבר את ה-webhook ב-Meta (App → Webhooks → leadgen, subscribe לעמוד
   `1939072889681856`). תן לו הוראות מדויקות צעד-צעד כשמגיעים לכאן.
2. ליד בדיקה אמיתי דרך Meta Lead Ads Testing Tool.
3. הוכחה מלאה (6 שכבות לפי CLAUDE.md): שורה ב-`lead` → `lead_event(created)` →
   מייל התקבל בפועל אצל תום → הליד נראה בפורטל → שינוי סטטוס בפורטל נכתב
   כאירוע → נתיב חריגה (payload כפול = אין ליד כפול ואין מייל כפול; payload
   שבור = נדחה + לוג). **200 OK לבדו אינו ראיה.**
4. אחרי PASS: עדכן `Sales-Machine/CURRENT_STATE.md` + תיעוד ב-production-brain;
   הגיליון מוכרז legacy לקריאה בלבד.

## אסור

- לגעת בסכמת ליבה של factory-os, ב-`stock_ledger`, בדגלים קפואים.
- לשלוח שום דבר לליד או ללקוח. נמען יחיד: tom@gteveryday.com.
- לנחש שמות שדות של Meta Graph API בלי בדיקה מול ליד אמיתי.
- להחיות את תרחישי Make הישנים של לידים (`5174396`, `5195363`, `5176271`).
- `git add -A`. עבוד לפי כללי ה-git של הריפו, PR-ים כטיוטה.

## פתוח לתום (החלטות, לא חוסמים לבנייה)

- U-010: שעות SLA (ברירת מחדל 24h). U-011: תפקיד Erik בשיוך לידים —
  בינתיים הכל לתום. שמות סטטוסים בעברית במסך (מיפוי תצוגה, לא סכמה).
