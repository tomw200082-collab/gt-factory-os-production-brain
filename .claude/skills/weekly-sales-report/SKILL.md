---
name: weekly-sales-report
description: >
  Weekly refresh of the GT sales-report artifact + a simple Hebrew email to Tom with the
  link and the exact data-freshness time, ahead of the weekly meeting. Fires from the
  scheduled routine "דוח מכירות שבועי" (Wednesday 07:30 IL), or when Tom says
  "רענן את דוח המכירות", "תעדכן את הדוח לפגישה", "/weekly-sales-report". Read-only
  against Shopify; republishes the SAME artifact URL; never emails anyone but Tom.
---

# weekly-sales-report — רענון שבועי + מייל לפגישה

שפת עבודה: **עברית**. המטרה: בכל רביעי בבוקר הדוח מעודכן והלינק אצל תום במייל,
עם שעה מדויקת של טריות הנתונים — הפגישה השבועית רצה סביב הקובץ הזה.

## עוגנים קבועים

- **Artifact URL (לעולם לא משתנה):** `https://claude.ai/code/artifact/ad0dd380-d95e-4a21-94e3-af9ee386fc88`
  — מפרסמים עם `url=<זה>` כדי לעדכן את אותו קישור. פרסום בלי `url` = באג.
- Scripts: `gt-factory-os/scripts/sales-report/` (README שם = סדר ההרצה).
- שיטה מלאה: `Sales-Machine/recipes/sales-report.md` · מספרי ייחוס: `Sales-Machine/evidence/2026-08-24-sales-report.md`.
- בסיס נעול: כל ₪ ללא מע״מ (המחיר השמור) · discountedTotalSet · חודש לפי שעון ישראל ·
  מבוטלות מוחרגות · עמודות המס/net של שופיפיי אסורות · amountSpent אסור.
- מייל: `tom@gteveryday.com` בלבד. אין שום פנייה ללקוח.

## צעדים

1. **חלון:** `END` = החודש הנוכחי (שעון ישראל). משיכה מ-1 לחודש של `END−24` פחות יום.
2. **משיכה:** Shopify MCP → `bulkOperationRunQuery` על `orders(query:"created_at:>=<תאריך>")`
   עם השדות המדויקים שבתחילת `build_facts.py` (הזמנה+לקוח+שורות+refunds). Poll עד
   `COMPLETED`, הורדת ה-JSONL אל `<workdir>/raw/orders.jsonl`. לרשום את **שעת ה-completedAt
   בשעון ישראל** — זו חותמת הטריות.
3. **עוגן בלתי-תלוי:** ShopifyQL
   `FROM sales SHOW orders, gross_sales, discounts, sales_reversals, net_sales, shipping_charges, taxes, total_sales TIMESERIES month SINCE <START>-01 UNTIL today`
   → לשמור כ-`shopifyql_month.json` באותו מבנה קיים (rows של מערכים).
4. **בנייה:** להעתיק את הסקריפטים מהריפו ל-workdir, ואז
   `GT_RANGE_END=<END> python3 build_facts.py` →
   `GT_RANGE_END=<END> GT_PULLED_AT=<ISO שעת המשיכה> python3 build_report.py`.
5. **שערי חובה לפני פרסום** (מ-`out/gates.json` + recon):
   - התאמת הזמנות מול ShopifyQL (כולל מבוטלות): **מדויק בכל החודשים המלאים**.
   - זהות חלון-מלא מול `total_sales`: **|Δ| ≤ 0.5%**.
   - SKU חדשים שאינם במיפוי נופלים אוטומטית לדלי ההיסטורי הגלוי — אם ההכנסה שלהם
     בחודש האחרון > ₪20K, לציין במייל שנדרש עדכון מיפוי מול תום (לא חוסם).
6. **פרסום:** Artifact publish של `report.html` עם `url` הקבוע. הדף כבר מציג
   ״עודכן <תאריך+שעה>״ בשורת הטאבים.
7. **מייל לתום** (Gmail MCP, `send_message`), עברית, קצר וללא קישוט:
   - נושא: `דוח המכירות מעודכן · הנתונים עד <DD/MM HH:MM>`
   - גוף: (א) הקישור. (ב) ״הדוח עודכן אוטומטית; הנתונים נכונים בדיוק עד
     <DD/MM/YYYY HH:MM> (שעון ישראל), ללא מע״מ, ללא מבוטלות; החודש הנוכחי חלקי ומסומן.״
     (ג) 3 מספרים לפתיחת הפגישה: 12ח׳ אחרונים ₪X (±% מול הקודמים) · החודש המלא האחרון
     ₪Y (±% YoY) · לקוחות פעילים N. (ד) שורת ״מה לבדוק השבוע״: הלקוח עם הירידה
     הגדולה ביותר YoY בחודש המלא האחרון (מספר אחד, לא רשימה).
8. **כשל שער = אין פרסום.** לא מפרסמים דוח שגוי; שולחים מייל קצר:
   ״הדוח לא עודכן הבוקר — <הסטייה במספרים>. הקישור מציג את הגרסה הקודמת (עדכנית
   ל-<תאריך קודם>).״ כלל הברזל של תום: עדיף פחות — אסור לשקר.

## גבולות

שופיפיי לקריאה בלבד (bulk = קריאה) · ⊥ ליבת factory-os · ⊥ פנייה ללקוחות
(`SALES_CUSTOMER_OUTREACH_WRITE_ENABLED=false`) · שינוי טקסונומיה/רשתות — רק דרך שער
תום (עמוד האימות: `https://claude.ai/code/artifact/9d94c4ff-7ea2-4ddc-a148-0a1781ad1c3e`) ·
אין ⁠`git push` נדרש — הריצה לא נוגעת בריפו.
