# מחקר: איך מפעילים רציניים מנהלים הזמנות והודעות ללקוח B2B, ומה זה אומר ל-GT

> סטטוס: מחקר לפני עיצוב סופי (Tom 2026-09-09: "לוודא שלא פספסנו כלום"). ⊥ authority.
> מקורות בסוף. הגרד: `doc_confirmed` לכל ממצא עם קישור; `inferred` מסומן.
> קשור: PR gt-factory-os#272 (הבוט החדש: עגלות קטלוג + הודעות קבועות, חי מ-2026-09-08).

## 1. מי נבדק

- **Choco** (EU/US, הזמנות מסעדה→ספק בצ'אט): "Place orders in just three taps", "Orders on autopilot" (OrderAgent), אישור הזמנה עם Product IDs + יחידות + אישור אספקה במקום אחד, "check order accuracy and report missing items" אחרי המסירה. ההזמנות מומרות לפורמט שהספק רוצה (email/WhatsApp/ERP).
- **REKKI** (UK): צ'אט + רשימת מוצרים אישית ללקוח, הספק "can confirm your delivery with the click of a button", דיווח בעיות בצ'אט, חשבוניות במקום אחד, תשלום לפי חשבונית או **בתנאים עם דף ריכוז שבועי/חודשי**, התראות שינוי מחיר.
- **Ordermentum** (AU, ספקי מזון סיטונאי): **standing orders**, מועדפים, **cut-off לפי מסלול**, "remind customers when orders are due via text, email or push", תמחור ותנאי סחר לפי סוג לקוח, גבייה בכרטיס.
- **Sysco Shop / US Foods MOXē** (US): Quick Order, עריכת הזמנה עד ה-cut-off, **התראות תחליפים בזמן אמת**, התראת "המשאית 30 דקות מכם", 14 חודשי היסטוריה.
- **Backbar**: תזכורת cut-off "כשעתיים לפני הדדליין אם עדיין לא הוזמן השבוע".
- **Cut+Dry / Food Logistics**: נראות מלאי בחנות מונעת הזמנה של מה שאין.
- **WhatsApp Business Platform (Meta)**: הודעות קטלוג, מוצר יחיד, **רב-מוצרים (עד 30 מוצרים במקטעים)**, קרוסלה; עגלה עד 99 יחידות לפריט; העגלה מגיעה כ-webhook עם `product_retailer_id` + כמות. תבניות Utility פטורות ממגבלת התדירות; תבניות Marketing מוגבלות ל-**~2 ליום למשתמש מכל העסקים יחד** (שגיאה 131049), ודורשות opt-in ויציאה קלה. חיוב לפי הודעת תבנית שנמסרה, לפי קטגוריה ומדינה; הודעות שירות בתוך חלון 24 השעות חינם.
- **קטלוג מסונכרן משופיפיי**: פריט שנגמר בשופיפיי **נעלם אוטומטית מקטלוג הוואטסאפ** (אלא אם "המשך למכור כשאזל"); ה-Content ID בקטלוג = **Variant ID** של שופיפיי.
- **גבייה B2B**: תזכורת עדינה לפני המועד, ואז קצב קבוע אחרי (3/7/14/30 ימים), הסלמה לאדם, ריבוד לפי סיכון.

## 2. פערים מול העיצוב הנוכחי של GT, לפי ערך

| # | מה עושים הרציניים | מה יש לנו | פער | המלצה |
|---|---|---|---|---|
| A | **מלאי בתוך ממשק ההזמנה**: אי אפשר להזמין מה שאין | קטלוג ידני; המלאי האמיתי נכתב לשופיפיי כל 5 דקות | הלקוח יכול להזמין פריט חסר, ואז 14:00 "חסר" | **הכרעה נדרשת** (§3): קטלוג מסונכרן משופיפיי (מלאי+item codes אוטומטיים, מחיר מוצג) מול קטלוג ידני (בלי מחיר, בלי מלאי) |
| B | **"ההזמנה הרגילה שלך" בלחיצה** (Choco 3 taps, Sysco Quick Order, REKKI רשימה אישית) | קישור לקטלוג המלא | הלקוח מחפש ב-57 פריטים | תשובה לטקסט חופשי = **הודעת רב-מוצרים אישית** (עד 30) מההיסטוריה של הלקוח, במקום קישור. בתוך חלון 24 השעות, חינם. v1 |
| C | **standing orders** (Ordermentum, Choco autopilot) | אין | לקוחות קבועים מקלידים כל שבוע | תבנית שבועית ביום ההזמנה הרגיל: "ההזמנה הקבועה: [פריטים]. [אשר] [שנה]" → אישור = דראפט. v2, אחרי שיש נתוני עגלות |
| D | **תזכורת cut-off** (Backbar 2h לפני, Ordermentum) | אין | לקוח שמפספס 14:00 מקבל אספקה יום מאוחר | תזכורת ביום ההזמנה הרגיל של הלקוח ב-11:00 אם עדיין לא הזמין: "היום עד 14:00 לאספקה מחר". v2, מתמזג עם 9 |
| E | **עריכה עד ה-cut-off** (Sysco) | עגלה שנייה = דראפט שני | כפילויות | כלל: עגלה נוספת לפני 14:00 מאותו לקוח = "עדכון להזמנה של היום", דראפט אחד. הקבלה אומרת "לשינוי עד 14:00 שלחו עגלה מעודכנת". v1 |
| F | **תחליפים/חוסרים בזמן אמת** (US Foods, Sysco) | ידני, טלפון | | כפתור בפורטל בהצלבה 14:00: "הודע ללקוח" → תבנית עם [להסיר] [להחליף ב-Y] [להמתין]. v2 |
| G | **אספקה: "בדרך" / 30 דקות** | LionWheel יש לו התראות משלו | | ⊥ לבנות. לבדוק שהתראת הלקוח של LionWheel דולקת. אפס קוד |
| H | **נמסר + הוכחת מסירה + "משהו חסר?"** (Choco/REKKI) | תחנה 7 מתוכננת | | להוסיף ל-7: תמונת POD מ-LionWheel כשיש, ושורה "משהו חסר או לא תקין? השיבו כאן". תשובה = חלון 24 שעות פתוח, אבי מטפל, זיכוי. v1 |
| I | **דף ריכוז חודשי** (REKKI statements) | חשבונית לכל הזמנה במייל | | הודעת מסמך (PDF) פעם בחודש לפני סבב הגבייה. v2 |
| J | **גבייה בקצב מדורג** | 3 לפני, 7 אחרי | | להוסיף: לא בשבת/חג, מקסימום 2 אוטומטיות ואז דורין, ניסוח מסלים בעדינות. v1 (הגדרות בלבד) |
| K | **opt-in ותדירות שיווקית** | לא מוגדר | תבנית "מזמן לא הזמנתם" = Marketing | לרשום opt-in (הלקוח פנה אלינו = קשר קיים, לתעד תאריך), לכבד "הסר" תמיד, ⊥ יותר מהודעה שיווקית אחת ב-30 יום ללקוח. v1 (כללים) |
| L | **חלון עריכה לאדם** | | | כשעגלה מגיעה, אבי רואה אותה גם באפליקציה. אין פער |

## 3. ההכרעה שהמחקר מכריח: מי מנהל את הקטלוג

**אפשרות 1: קטלוג מסונכרן משופיפיי** (ערוץ Facebook & Instagram של שופיפיי → Commerce Manager → WhatsApp).
- מלאי אמיתי: פריט שאזל נעלם מהקטלוג לבד. זה ה"אילוץ מלאי" של GT, נפתר במקור.
- Item codes אוטומטיים (Variant ID), שמות ותמונות משופיפיי. אבי ⊥ מקליד 57 קודים.
- **מחיר מוצג** (מחיר הקטלוג, 65). סותר את ההחלטה "בלי מחיר". אפשר לרכך: הקבלה אומרת "המחירים לפי ההסכם שלכם".
- הבוט: הפענוח מ-Variant ID ישיר, אפילו פשוט יותר מ-SKU.

**אפשרות 2: קטלוג ידני באפליקציה** (מה שהוחלט אתמול).
- בלי מחיר. Item code = SKU ידני.
- בלי מלאי: הלקוח יכול להזמין פריט חסר; נופל ל-14:00 ולתחנה F.
- אפשר להוסיף בהמשך עדכון זמינות אוטומטי דרך Catalog API, אם ל-Dualhook יש הרשאת קטלוג. ⊥ ידוע (`inferred`).

המלצה: **אפשרות 1**, כי מלאי-במקור שווה יותר מהסתרת מחיר, וכי היא מבטלת עבודה ידנית שנשברת. אם המחיר המוצג לא מקובל, אפשרות 2 + F.

## 4. מה נשאר כמו שהיה

תחנות 1, 2, 4, 7, 8, 9 מהעיצוב של 2026-09-08 עומדות. LionWheel webhooks (ASSIGNED/COMPLETED) הם הטריגר ל-4 ול-7 (מסמך ה-API: URL + סטטוסים בהגדרות הארגון, payload = אובייקט המשימה עם `pickup_at`, `original_order_id`).

## 5. מקורות

- Choco: https://choco.com/us/restaurants · https://customers.twilio.com/en-us/choco · https://help.choco.com/en/articles/6572341-get-in-touch-with-your-suppliers
- REKKI: https://rekki.com/app · https://rekki.com/suppliers/connect
- Ordermentum: https://www.ordermentum.com/supplier/features/order-management/automation · https://www.ordermentum.com/how-it-works
- Sysco Shop / US Foods MOXē: https://www.sysco.com/shopmobile · https://www.usfoods.com/our-services/easy-ordering.html
- Backbar cut-off notifications: https://www.getbackbar.com/support/managing-order-cutoff-notifications
- Cut+Dry / Food Logistics: https://www.foodlogistics.com/software-technology/e-commerce-solutions/article/22919540/cutdry-ecommerce-every-food-distributors-secret-weapon
- Meta, catalogs: https://developers.facebook.com/documentation/business-messaging/whatsapp/catalogs/catalogs-overview/ · pricing: https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing
- Meta frequency cap: https://m.aisensy.com/blog/meta-frequency-capping-for-whatsapp-marketing-messages/ · https://chatarmin.com/en/blog/whats-app-messaging-limits
- Shopify→WhatsApp catalog sync: https://www.zoko.io/post/whatsapp-business-catalog-bulk-upload-shopify · Content ID = Variant ID: https://docs.analyzify.com/find-content-id-format-facebook-catalog
- AR cadence: https://www.versapay.com/resources/tips-to-create-and-distribute-payment-reminders · https://blog.alguna.com/b2b-collections-best-practices/
- LionWheel API: https://github.com/lionwheel/api
