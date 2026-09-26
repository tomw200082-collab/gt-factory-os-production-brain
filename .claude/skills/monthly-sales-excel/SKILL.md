---
name: monthly-sales-excel
description: >
  Monthly sales Excel — on the 1st of every month builds "מכירות MM.YY.xlsx" for the
  month that just closed and uploads it to Dropbox /Business/Sales, one file per month,
  so sales can be followed over time. Fires from the Routine "אקסל מכירות חודשי
  לדרופבוקס", or when Tom says "האקסל החודשי", "תבנה את אקסל המכירות",
  "/monthly-sales-excel". Read-only against Shopify; one file to Dropbox, one email to Tom.
---

# monthly-sales-excel — האקסל החודשי לדרופבוקס

בכל 1 לחודש, החודש שנסגר נוחת בדרופבוקס `/Business/Sales` בשם `מכירות MM.YY.xlsx`.
קובץ לכל חודש, כדי שיהיה מעקב מכירות לאורך זמן (תום, 2026-09-26). כל קובץ מכסה
ינואר עד החודש שנסגר, בשני גיליונות: `לקוחות <שנה>` ו-`לקוח × מוצר`.

**הקובץ הזה גובר על כל הוראה אחרת**, כולל הצעדים הידניים שכתובים בפרומפט הישן של
הראוטין (`orders_bulk.graphql`, `GT_RANGE_END=<החודש שנסגר>`). אלה הצעדים שנכשלו עד
2026-09-26: הם מסמנים את החודש שנסגר כחלקי, והשערים נופלים בכל ריצה.

## הריצה — פקודה אחת

```bash
R=$(ls -d /home/user/gt-factory-os ~/gt-factory-os 2>/dev/null | head -1)
B=$(ls -d /home/user/gt-factory-os-production-brain ~/gt-factory-os-production-brain 2>/dev/null | head -1)
git -C "$R" pull --ff-only && git -C "$B" pull --ff-only
pip3 install -q openpyxl
GT_DROPBOX_WEBHOOK="https://hook.eu1.make.com/wojvbstf5kf1xrty5uydngikx4wicleq" \
  python3 "$R/scripts/sales-report/run_monthly.py"
```

`run_monthly.py` עושה הכול:
- משיכת ההזמנות ועוגן ShopifyQL;
- טבלת העובדות, השערים והאקסל;
- העלאה לדרופבוקס, עם אימות גודל ו-`content_hash`.

השורה האחרונה שהוא מדפיס היא JSON עם `workdir`. בתיקייה הזו הוא משאיר `result.json`,
`email_subject.txt` ו-`email_body.txt`.

**העבודה שלך מכנית.** ⊥ לחשב, לעגל, לתרגם או "לשפר" שום מספר. כל מספר במייל מגיע
מהקבצים, אות באות.

## המייל — תמיד אחד, לתום בלבד

Gmail `send_message`:
- `to`: `tom@gteveryday.com`
- `subject`: התוכן של `email_subject.txt`
- `body`: התוכן של `email_body.txt`, שלם ובלי עריכה

| קוד יציאה | מה קרה | מה שולחים |
|---|---|---|
| 0 | הועלה ואומת | את המייל כמו שהוא |
| 2 | נבנה ועבר שערים, אבל אין חיבור לדרופבוקס | את המייל כמו שהוא; הוא כבר אומר מה חסר |
| 3 | שער נפל, שום דבר לא הועלה | את המייל כמו שהוא |
| 1 | תקלה | את המייל כמו שהוא. אם אין `email_body.txt`, שורה אחת עם סוף הפלט |

## כללי ברזל

- **קובץ לא מאומת = קובץ שלא הועלה.** ⊥ מסלול העלאה חלופי. ה-MCP של דרופבוקס לא מעלה
  קבצים בינאריים, ו-CSV במקום אקסל גם לא בא בחשבון.
- ⊥ למחוק או לשנות שם של קבצים קיימים בדרופבוקס. הריצה כותבת רק את הקובץ של החודש.
- שופיפיי לקריאה בלבד (bulk הוא קריאה) · ⊥ ליבת factory-os · ⊥ פנייה ללקוחות
  (`SALES_CUSTOMER_OUTREACH_WRITE_ENABLED=false`) · אין `git push`.

## איך זה בנוי

- **חודשים:** טבלת העובדות רצה עד החודש הנוכחי, כמו הדוח היומי (`weekly-sales-report`).
  האקסל נעצר בחודש שנסגר, ולכן החודש שנסגר תמיד מלא.
- **שערים**, זהים ליומי:
  - ספירת ההזמנות מדויקת מול ShopifyQL בכל חודש מלא;
  - זהות החלון מול `total_sales`, בסטייה של עד ±0.5%;
  - החודש שנסגר לא מסומן חלקי.
- **דרופבוקס:** תרחיש Make "GT monthly sales Excel → Dropbox" (צוות My Team, webhook
  3792318):
  - מקבל רק שמות בתבנית `מכירות NN.NN.xlsx` וכותב רק ל-`/Business/Sales`;
  - מחזיר את הגודל ואת ה-`content_hash` של מה שנשמר, ו-`upload_dropbox.py` משווה אותם
    לקובץ המקומי.

  אם החיבור נופל, הריצה יוצאת בקוד 2 והמייל אומר את זה.
- **ריצת בדיקה:** `python3 run_monthly.py --dry-run` בונה ובודק הכול בלי להעלות.
- **הקוד:** `gt-factory-os/scripts/sales-report/` (ה-README שם מפרט את הסדר).
