---
name: weekly-sales-report
description: >
  Daily refresh of the GT sales-report artifact + a short Hebrew email to Tom with the
  link and the exact data-freshness time. Fires from the scheduled routine
  "דוח מכירות" every Sunday-Thursday 09:00 IL, or when Tom says "רענן את דוח המכירות",
  "תעדכן את הדוח לפגישה", "/weekly-sales-report". Sunday carries the full weekly block
  for the Wednesday meeting; Monday-Thursday is the short daily pulse. Read-only against
  Shopify; republishes the SAME artifact URL; never emails anyone but Tom.
---

# weekly-sales-report — רענון יומי + מייל

שפת עבודה: **עברית**. המטרה: **ראשון–חמישי 09:00** (תום 2026-08-31) הדוח מעודכן
והלינק אצל תום במייל, עם שעה מדויקת של טריות הנתונים. הדוח ⊥ מסמך שבועי שמתיישן —
הוא נכון כל בוקר. הפגישה (רביעי) רצה סביב אותו קובץ.

**שני מצבי מייל, אותה ריצה בדיוק:**
- **ראשון** — הבלוק השבועי המלא (צעד 7א).
- **שני–חמישי** — הדופק היומי הקצר (צעד 7ב). מייל יומי שחוזר על אותם מספרי-שנה
  הופך לרעש שמפסיקים לקרוא.

שישי–שבת ⊥ ריצה: אין חלוקה, והמספר היחיד שהיה משתנה הוא הזמנות אונליין בודדות.

## עוגנים קבועים

- **Artifact URL (לעולם לא משתנה):** `https://claude.ai/code/artifact/ad0dd380-d95e-4a21-94e3-af9ee386fc88`
  — מפרסמים עם `url=<זה>` כדי לעדכן את אותו קישור. פרסום בלי `url` = באג.
- Scripts: `gt-factory-os/scripts/sales-report/` (README שם = סדר ההרצה; השאילתה = `orders_bulk.graphql`).
- שיטה מלאה: `Sales-Machine/recipes/sales-report.md` · מספרי ייחוס: `Sales-Machine/evidence/2026-08-24-sales-report.md`.
- בסיס נעול: כל ₪ ללא מע״מ (המחיר השמור) · discountedTotalSet · חודש לפי שעון ישראל ·
  מבוטלות מוחרגות · עמודות המס/net של שופיפיי אסורות · amountSpent אסור.
- מייל: `tom@gteveryday.com` בלבד. אין שום פנייה ללקוח.

## צעדים

0. **קודם כל — `git pull` בשני הריפו** (`gt-factory-os`, `gt-factory-os-production-brain`).
   הריצה בונה מ-`main`. ב-02/09/2026 ריצה מתוזמנת רצה על checkout ישן, בנתה דוח בלי
   גליון הרשתות ובלי הגליון היומי, ופרסמה אותו **על אותו URL** — שבועיים של עבודה נמחקו
   בשקט. הפרסום הוא החלק ההרסני של הריצה הזו; checkout ישן ⊥ מתגלה בשום שער מספרי.
1. **חלון:** `END` = החודש הנוכחי (שעון ישראל). משיכה מ-1 לחודש של `END−24` פחות יום.
2. **משיכה:** `bulkOperationRunQuery` עם `scripts/sales-report/orders_bulk.graphql`
   **כמות שהוא** (`<START>` = התאריך מסעיף 1). השאילתה נעולה שם כי היא נשברת בשקט:
   בלי `id` על `lineItems` כל השורות נופלות ו-`fact_rows=0` (נמדד 2026-08-25). Poll עד
   `COMPLETED`, הורדת ה-JSONL אל `<workdir>/raw/orders.jsonl`. לרשום את **שעת ה-completedAt
   בשעון ישראל** — זו חותמת הטריות.
3. **עוגן בלתי-תלוי:** `python3 fetch_shopifyql.py <START> shopifyql_month.json`
   (`FROM sales SHOW orders, gross_sales, discounts, sales_reversals, net_sales, shipping_charges, taxes, total_sales TIMESERIES month`).
   הסקריפט עובד בלי MCP ועוטף את המלכודות: ה-Admin API קורא לעמודה `returns`, לא
   `sales_reversals` — והבקשה השגויה חוזרת HTTP 200 עם השגיאה קבורה ב-`parseErrors`;
   צורת `rows` משתנה בין גרסאות API; והתאים חוזרים כמחרוזות. אומת זהה ל-MCP ב-25/25 חודשים.
   ה-MCP (`run-analytics-query`) עדיין עובד כשיש connectors — אבל ⊥ לבנות עליו.
4. **בנייה:** להעתיק את הסקריפטים מהריפו ל-workdir, ואז
   `GT_RANGE_END=<END> python3 build_facts.py` →
   `GT_RANGE_END=<END> GT_PULLED_AT=<ISO שעת המשיכה> python3 build_report.py`.
5. **שערי חובה לפני פרסום** (מ-`out/gates.json` + recon):
   - התאמת הזמנות מול ShopifyQL (כולל מבוטלות): **מדויק בכל החודשים המלאים**.
   - זהות חלון-מלא מול `total_sales`: **|Δ| ≤ 0.5%**.
   - SKU חדשים שאינם במיפוי נופלים אוטומטית לדלי ההיסטורי הגלוי — אם ההכנסה שלהם
     בחודש האחרון > ₪20K, לציין במייל שנדרש עדכון מיפוי מול תום (לא חוסם).
5.5 **שער נסיגה — חובה, לפני הפרסום.** השערים שלמעלה בודקים מספרים; הם ⊥ מבחינים
   בין דוח מלא לדוח שחסר לו חצי. על `report.html` שנבנה עכשיו:

   ```bash
   grep -c 'data-s="daily"' report.html   # 1 — הגליון היומי
   grep -c 'data-s="chain"' report.html   # 1 — גליון הרשתות
   grep -c 'chainMeta'      report.html   # ≥1 — מפת הרשתות נטענה
   python3 -c "import json;print(len(json.load(open('out/chain_conflicts.json'))))"   # 0
   python3 -c "import json;d=json.load(open('out/dim_customers.json'));print(sum(1 for c in d if c['chain']))"   # ≥250
   ```

   מספר נמוך או `0` = בנית דוח נסוג. **⊥ לפרסם.** לעצור, לחזור לצעד 0, ואם זה חוזר —
   מייל כשל (צעד 8) ולא פרסום. פרסום גורע הוא הנזק היחיד כאן שאי אפשר לבטל: הגרסה
   הקודמת ⊥ חוזרת מעצמה.
5.9 **מייל אישור — מיד לפני הפרסום, רק כשהדף משותף** (תום 2026-09-24).
   `Artifact action:"read"` על ה-URL הקבוע. הכותרת מכילה `shared with` → הפרסום בצעד 6
   ייעצר עד שתום יאשר (routines.md: דף משותף = Claude שואל; ⊥ הגדרה שעוקפת את זה).
   אז, לפני צעד 6, מייל אחד אל `tom@gteveryday.com` (Gmail `send_message`):
   - קישור: `mcp__Claude_Code_Remote__get_session` **בלי** `session_id` → `ccr.id`
     (`session_…`) → `https://claude.ai/code/<ccr.id>`. הכלי חסר → `https://claude.ai/code`.
   - נושא: `לאשר את דוח המכירות · <DD/MM> · לחיצה אחת` (התאריך של הבוקר הזה)
   - `htmlBody` (להחליף רק את LINK):
     `<div dir="rtl" style="font-family:Arial,sans-serif;font-size:16px"><p>דוח המכירות מוכן וממתין לאישור שלך.</p><p><a href="LINK" style="display:inline-block;background:#2F5D3F;color:#ffffff;padding:16px 32px;border-radius:10px;text-decoration:none;font-weight:bold;font-size:18px">לאשר פרסום</a></p><p style="color:#666666;font-size:13px">הכפתור פותח את הריצה — שם לאשר.</p></div>`
   - `body`: `לאשר פרסום: LINK`
   הכותרת ⊥ מכילה `shared with` (דף פרטי) → ⊥ מייל; הפרסום עובר בלי אישור.
   נושא אחר ממייל צעד 7 — ⊥ נספר ב-D6.
6. **פרסום:** Artifact publish של `report.html` עם `url` הקבוע. הדף כבר מציג
   ״עודכן <תאריך+שעה>״ בשורת הטאבים.
   הפרסום נדחה כי לדף יש גרסה חדשה מזו שנקראה בצעד 5.9 (ריצה מאוחרת יותר, שאושרה
   קודם, כבר פרסמה) → **⊥ לפרסם שוב, ⊥ `force`, ⊥ מייל צעד 7.** לעצור. דוח ישן ⊥ דורס חדש.
7. **מייל לתום** (Gmail MCP, `send_message`), עברית, קצר וללא קישוט.
   נושא בשני המצבים: `דוח המכירות מעודכן · הנתונים עד <DD/MM HH:MM>`
   פתיח בשני המצבים: (א) הקישור. (ב) ״הדוח עודכן אוטומטית; הנתונים נכונים בדיוק עד
   <DD/MM/YYYY HH:MM> (שעון ישראל), ללא מע״מ, ללא מבוטלות; החודש הנוכחי חלקי ומסומן.״

   **7א · ראשון — הבלוק השבועי.** אחרי הפתיח:
   3 מספרים לפתיחת הפגישה: 12ח׳ אחרונים ₪X (±% מול הקודמים) · החודש המלא האחרון
   ₪Y (±% YoY) · לקוחות פעילים N. ואז שורת ״מה לבדוק השבוע״: הלקוח עם הירידה
   הגדולה ביותר **ב-12 החודשים האחרונים מול 12 שלפניהם** (מספר אחד, לא רשימה).
   תום 2026-08-30: החלון החודשי נבדק ונפסל — הוא מייצר רעש (הירידה הגדולה ביותר
   ב-07/2026 היתה ₪8,400), בעוד חלון 12 החודשים מייצר ממצא בר-החלטה (₪108,136).

   **7ב · שני–חמישי — הדופק היומי.** אחרי הפתיח, שלוש שורות בלבד, כולן מגליון ״יומי״:
   יום העסקים האחרון ₪X (±% מול חציון ארבעת אותם ימים בשבוע שקדמו) ·
   החודש עד היום ₪Y (±% מול אותם ימים בחודש שעבר) · ממוצע 7 ימים סגורים ₪Z.
   שורה רביעית **רק אם** יש חריגה אמיתית: יום עסקים שירד מעל 40% מול החציון שלו,
   או הזמנה בודדת מעל ₪50K. אין חריגה → ⊥ שורה רביעית, ⊥ מילוי מקום.

   ״יום העסקים האחרון״ = היום המלא האחרון שאינו שישי/שבת. ב-09:00 היום הנוכחי בן שעה
   ולכן ⊥ כותרת; הוא מופיע בדוח כ״היום עד עכשיו״ ומסומן חלקי.
8. **כשל שער = אין פרסום.** לא מפרסמים דוח שגוי; שולחים מייל קצר:
   ״הדוח לא עודכן הבוקר — <הסטייה במספרים>. הקישור מציג את הגרסה הקודמת (עדכנית
   ל-<תאריך קודם>).״ כלל הברזל של תום: עדיף פחות — אסור לשקר.

## גבולות

האח החודשי — `monthly-sales-excel` (האקסל לדרופבוקס, 1 לחודש). שופיפיי לקריאה בלבד (bulk = קריאה) · ⊥ ליבת factory-os · ⊥ פנייה ללקוחות
(`SALES_CUSTOMER_OUTREACH_WRITE_ENABLED=false`) · שינוי טקסונומיה/רשתות — רק דרך שער
תום (עמוד האימות: `https://claude.ai/code/artifact/9d94c4ff-7ea2-4ddc-a148-0a1781ad1c3e`) ·
אין ⁠`git push` נדרש — הריצה לא נוגעת בריפו.
