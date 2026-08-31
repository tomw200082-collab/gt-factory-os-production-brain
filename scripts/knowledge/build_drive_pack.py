#!/usr/bin/env python3
"""Render the knowledge cards into the Markdown an agent reads from Drive.

A WhatsApp agent running over an API cannot see the repo. So the Drive folder
`GT · מוח ה-AI` has to stand on its own — which means the cards are rendered out,
not linked. Rendered, never authored: every file says so at the top, and a change
made in Drive is lost on the next build.

Output order matters and is not alphabetical. The refusal layer is file 01 because
an agent that reads the answers first will answer an allergen question correctly
and still be wrong.

    python3 scripts/knowledge/build_drive_pack.py [-o outdir]
"""
import argparse
import datetime as dt
import os
import subprocess

import yaml

BRAIN = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SALES = os.path.join(os.path.dirname(BRAIN), "Sales-Machine")
K = os.path.join(SALES, "knowledge")
IDENTITY_CARD = "https://docs.google.com/document/d/14DsBautlpXWVkMzdXVoCADIKXiBvWMfmvXwwhtJ76-I/edit"


def card(rel):
    with open(os.path.join(K, rel), encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def sha(repo):
    try:
        return subprocess.check_output(["git", "-C", repo, "rev-parse", "--short", "HEAD"],
                                       text=True).strip()
    except Exception:
        return "unknown"


def stamp(what):
    return (f"> **נוצר אוטומטית — ⊥ לערוך כאן.** {what}\n"
            f"> מקור: `Sales-Machine/knowledge/` · נבנה {dt.date.today().isoformat()} · "
            f"קומיט `{sha(SALES)}`\n"
            f"> עריכה בדרייב תימחק בבנייה הבאה. שינוי נכנס בריפו.\n")


# ------------------------------------------------------------------ 01 boundaries
def boundaries():
    d = card("boundaries/refusals.yaml")
    out = ["# הגבולות — מה אסור להגיד\n", stamp("שכבת הבטיחות. נקראת **לפני** בנק התשובות."), ""]
    out += [
        "## הכלל שגובר על הכל", "",
        "שאלה נבדקת **קודם** מול הכללים כאן. אם נדלק כלל — הוא גובר על כל תשובה,",
        "גם על תשובה מאושרת. שאלה שלא נתפסה ואין לה שורה מאושרת בבנק התשובות ⇒",
        "**מעבירים לאלכסנדר**. ⊥ מאמץ-הכי-טוב, ⊥ הסקה, ⊥ \"נראה לי\".", "",
        "> למה זה ראשון ולא אחרון: סוכן שקורא קודם את התשובות יענה נכון על שאלת",
        "> אלרגנים — ועדיין יהיה שגוי.", "",
    ]
    order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    rules = sorted([r for r in d["rules"] if r["id"] != "unmatched_default"],
                   key=lambda r: order[r["severity"]])
    for r in rules:
        out += [f"## {r['id']} · {r['severity']}", ""]
        out += [f"**מתי נדלק:** {'، '.join(str(p) for p in r['patterns'])}", ""]
        out += [f"**למה:** {' '.join(r['reason'].split())}", ""]
        out += [f"**אומרים בדיוק:**", "", f"> {' '.join(r['say_he'].split())}", ""]
        if r.get("never"):
            out += [f"**⊥ אומרים לעולם:** {' · '.join(r['never'])}", ""]
        if r.get("vat_rule"):
            out += [f"**מע״מ:** {' '.join(r['vat_rule'].split())}", ""]
        out += [f"מעבירים ל: `{r.get('escalate_to') or '— סוגרים, ⊥ מעבירים'}`", ""]
    dflt = next(r for r in d["rules"] if r["id"] == "unmatched_default")
    out += ["## ברירת המחדל — כל השאר", "",
            f"> {' '.join(dflt['say_he'].split())}", "",
            "כל שאלה שלא נתפסה למעלה ואין לה שורה מאושרת בבנק — זו התשובה.", ""]
    return "\n".join(out)


def claims():
    d = card("claims/public-claims.yaml")
    out = ["# הטענות — מה מותר לטעון, ומה הראיה\n",
           stamp("לפני שאומרים טענה על GT, בודקים אותה כאן."), "",
           "`authority` אומר על מי הטענה נשענת:",
           "`system_verified` מדידה · `user_confirmed` טום · `doc_confirmed` מסמך ·",
           "**`unsourced` ⇒ ⊥ נאמרת ללקוח.**", ""]
    for c in d["claims"]:
        flag = "" if c["status"] == "approved" else "  ⛔"
        out += [f"## {c['id']}{flag}", "",
                f"> {' '.join(c['text_he'].split())}", "",
                f"- **סטטוס:** {c['status']} · **דרגה:** {c['authority']} · **תאריך:** {c['date']}",
                f"- **הראיה:** {' '.join(c['evidence'].split())}"]
        if c.get("replacement_he"):
            out += [f"- **אומרים במקום:** {' '.join(c['replacement_he'].split())}"]
        if c.get("caution"):
            out += [f"- ⚠ {' '.join(c['caution'].split())}"]
        out += [""]
    return "\n".join(out)


# ------------------------------------------------------------------ 02 answers
def answers():
    d = card("answers/answer-bank.yaml")
    a = d["answers"]
    n = {k: sum(1 for x in a if x["סטטוס"] == k) for k in ("מאושר", "טיוטה", "העברה")}
    out = ["# בנק התשובות\n",
           stamp(f"{len(a)} שורות · {n['מאושר']} מאושרות · {n['טיוטה']} טיוטה · {n['העברה']} העברה."), "",
           "**סדר הפעולה:** הגבולות (01) נבדקים ראשונים. רק אם לא נדלק כלל —", "מחפשים כאן.", "",
           "| סטטוס | מה עושים |", "|---|---|",
           "| `מאושר` | אומרים כלשונו |",
           "| `טיוטה` | **⊥ נאמר ללקוח.** ממתין לאישור. מעבירים לאלכסנדר |",
           "| `העברה` | אין תשובה. מעבירים — וזו תשובה תקינה, ⊥ חור |", ""]
    for status in ("מאושר", "טיוטה", "העברה"):
        out += [f"---\n\n# {status}\n"]
        for x in [r for r in a if r["סטטוס"] == status]:
            out += [f"## {x['שאלה']}", "",
                    f"**מילות מפתח:** {'، '.join(str(k) for k in x['מילות מפתח'])}", ""]
            body = x.get("תשובה") or x.get("say_he") or ""
            out += [f"> {' '.join(str(body).split())}", ""]
            if x.get("caution"):
                out += [f"⚠ **שים לב:** {' '.join(x['caution'].split())}", ""]
            if x.get("escalate_to"):
                out += [f"מעבירים ל: `{x['escalate_to']}`", ""]
            out += [f"`{x['id']}` · מקור: {' '.join(x['source'].split())}", ""]
    return "\n".join(out)


# ------------------------------------------------------------------ 03 products & drinks
def products():
    d = card("products/catalog.yaml")
    live = [p for p in d["products"] if p.get("customer_facing")]
    held = [p for p in d["products"] if not p.get("customer_facing")]
    out = ["# מחירון — מה מוכרים ובכמה\n",
           stamp(f"{len(live)} מוצרים ללקוח · {len(held)} מוחזקים."), "",
           "**כל המחירים כאן ללא מע״מ.** זה מה שאומרים לבעל עסק — תמיד.",
           "מחיר כולל מע״מ נאמר רק כשמדובר במה שהעסק מוכר ללקוח הקצה שלו",
           "(המחיר המומלץ למשקה, בקובץ 48 המשקאות).", "",
           "**תמיד להוביל במספר למנה.** פחית מאצ'ה ב-₪590 נשמעת יקרה — היא ₪2.13",
           "למנה. לקוח שרואה ₪590 קודם נושר לפני שהבין.", ""]
    fams = [("tea_concentrate", "תמציות תה"), ("powder", "אבקות"), ("kit", "ערכות"),
            ("puree", "מחיות פרי"), ("accessory", "עזרי הכנה")]
    for key, title in fams:
        rows = [p for p in live if p["family"] == key]
        if not rows:
            continue
        out += [f"## {title}", "", "| מוצר | אריזה | SKU | ₪ ללא מע״מ | מנות | עלות למנה |", "|---|---|---|---|---|---|"]
        for p in sorted(rows, key=lambda r: (-float(r["price_exvat"]), r["name_he"])):
            out.append(f"| {p['name_he']} | {p.get('pack','—')} | `{p['sku']}` | "
                       f"{p['price_exvat']:g} | {p.get('servings_per_unit','—')} | "
                       f"{p.get('cost_per_serving','—')} |")
        out += [""]
        extras = [p for p in rows if p.get("ingredients_he")]
        if extras:
            out += ["**רכיבים ונטול קפאין:**", ""]
            seen = set()
            for p in extras:
                if p["name_he"] in seen:
                    continue
                seen.add(p["name_he"])
                caf = " · **נטול קפאין**" if p.get("caffeine_free") else ""
                out.append(f"- **{p['name_he']}** — {p['ingredients_he']}{caf}")
            out += [""]
    out += ["---", "", "## ⊥ מציעים · ⊥ מתמחרים", "",
            "המוצרים האלה קיימים בחנות אבל **אינם במחירון הלקוחות**. שאלה עליהם", "עוברת לאלכסנדר.", "",
            "| מוצר | SKU | למה |", "|---|---|---|"]
    for p in held:
        why = " ".join(p.get("why_not_customer_facing", "").split())
        out.append(f"| {p['name_he']} | `{p.get('sku','—')}` | {why} |")
    out += [""]
    for p in live:
        if p.get("caution"):
            out += [f"> ⚠ **{p['name_he']}** — {' '.join(p['caution'].split())}", ""]
    return "\n".join(out)


def drinks():
    d = card("drinks/catalog.yaml")
    rows = d["drinks"]
    out = ["# 48 המשקאות\n",
           stamp("עלות רכיבים ללא מע״מ · מחיר מומלץ כולל מע״מ 18% · רווח על ההכנסה נטו."), "",
           "עלות = רכיבי המשקה בלבד. **⊥ כולל** גרניש, קרח, מים, סודה, אריזה ועבודה.",
           "רווח נגזר: `round((מחיר/1.18 − עלות) / (מחיר/1.18) × 100)`.", "",
           "שתי מנות בסיס חוזרות: מאצ'ה — 1.8 גרם ב-50 מ״ל מים · אובה — 2 גרם ב-50 מ״ל.", ""]
    for cat in ("תה", "צ'אי", "אבקות"):
        g = [r for r in rows if r["category"] == cat]
        out += [f"## {cat} · {len(g)} משקאות", "",
                f"עלות {min(r['cost'] for r in g):g}–{max(r['cost'] for r in g):g} ₪ · "
                f"מחיר {min(r['price'] for r in g):g}–{max(r['price'] for r in g):g} ₪ · "
                f"רווח {min(r['margin_pct'] for r in g)}–{max(r['margin_pct'] for r in g)}%", "",
                "| משקה | משפחה | עלות | מחיר | רווח לכוס | רווח |", "|---|---|---|---|---|---|"]
        for r in g:
            out.append(f"| {r['name']} | {r['family']} | {r['cost']:g} | {r['price']:g} | "
                       f"{r['profit_per_cup']:g} | {r['margin_pct']}% |")
        out += [""]
    return "\n".join(out)


# ------------------------------------------------------------------ 04 buyer & motion
def buyers():
    d = card("segments/buyers.yaml")
    out = ["# מי הלקוח\n", stamp("המיון קודם לכל השאר."), "",
           f"**{' '.join(d['card']['rule'].split())}**", "", "---", "", "# שלושה סוגי ליד", ""]
    for b in d["buyer_types"]:
        out += [f"## {b['name_he']}", ""]
        if b.get("cares_about"):
            out += [f"- **אכפת לו מ:** {'، '.join(b['cares_about'])}"]
        if b.get("does_not_care_about"):
            out += [f"- **⊥ אכפת לו מ:** {'، '.join(b['does_not_care_about'])}"]
        if b.get("authority_he"):
            out += [f"- **סמכות:** {b['authority_he']}"]
        out += [f"- **מה עובד:** {' '.join(b['what_works_he'].split())}"]
        if b.get("signs"):
            out += [f"- **איך מזהים:** {'، '.join(b['signs'])}"]
        out += [""]
    out += ["---", "", "# סוגי עסק", ""]
    for v in d["venue_types"]:
        if v.get("status") == "unresolved":
            out += [f"## {v['name_he']} — ⛔ אין תסריט", "",
                    f"{' '.join(v['why_he'].split())}", ""]
            continue
        out += [f"## {v['name_he']}", "",
                f"- **נכנסים עם:** {v['entry_product']}",
                f"- **למה:** {' '.join(v['why_he'].split())}"]
        if v.get("entry_offer"):
            out += [f"- **הצעת כניסה:** {v['entry_offer']}"]
        if v.get("expand_to"):
            out += [f"- **מרחיבים ל:** {'، '.join(v['expand_to'])}"]
        if v.get("caution"):
            out += [f"- ⚠ {' '.join(v['caution'].split())}"]
        out += [""]
    return "\n".join(out)


def motion():
    d = card("segments/sales-motion.yaml")
    out = ["# רצף השיחה\n", stamp("ששה שלבים, שלוש נגיעות, שישה מסלולי הרחבה."), "",
           "## שלושה עקרונות", ""]
    out += [f"{i}. {p}" for i, p in enumerate(d["card"]["principles"], 1)]
    out += ["", "---", "", "# השלבים", ""]
    for i, s in enumerate(d["stages"], 1):
        out += [f"## {i:02d} · {s['name_he']}  ({s['when']})", ""]
        for k in ("do_he", "why_he", "shape_he", "also_he"):
            if s.get(k):
                out += [f"{' '.join(s[k].split())}", ""]
        if s.get("script_he"):
            out += ["**הנוסח:**", "", f"> {' '.join(s['script_he'].split())}", ""]
        if s.get("blocked_note"):
            out += [f"⛔ **חסום ({s.get('blocked_by')}):** {' '.join(s['blocked_note'].split())}", ""]
        if s.get("changed_from_book"):
            out += [f"ℹ {' '.join(s['changed_from_book'].split())}", ""]
    out += ["---", "", "# כשאין תשובה — שלוש נגיעות, ואז עוצרים", ""]
    for f in d["follow_ups"]:
        head = f"יום {f['day']}" if isinstance(f["day"], int) else "אחרי כן"
        out += [f"## {head} · {f['name_he']}", ""]
        for k in ("rule_he", "why_he"):
            if f.get(k):
                out += [f"{' '.join(f[k].split())}", ""]
        if f.get("script_he"):
            out += [f"> {' '.join(f['script_he'].split())}", ""]
    out += ["---", "", "# לאן מרחיבים אחרי ההזמנה הראשונה", "",
            "| מ־ | אל | מה זה עולה ללקוח |", "|---|---|---|"]
    for x in d["expansion_map"]:
        t = " ".join((x.get("cost_to_customer_he") or x.get("what_he", "")).split())
        if x.get("caution"):
            t += f" ⚠ {' '.join(x['caution'].split())}"
        out.append(f"| {x['from']} | {x['to']} | {t} |")
    out += [""]
    return "\n".join(out)



# ------------------------------------------------------------------ 00 the map
def readme():
    ans = card("answers/answer-bank.yaml")["answers"]
    rules = card("boundaries/refusals.yaml")["rules"]
    cl = card("claims/public-claims.yaml")["claims"]
    prods = card("products/catalog.yaml")["products"]
    drk = card("drinks/catalog.yaml")["drinks"]
    live = sum(1 for p in prods if p.get("customer_facing"))
    ok = sum(1 for a in ans if a["סטטוס"] == "מאושר")
    draft = sum(1 for a in ans if a["סטטוס"] == "טיוטה")
    move = sum(1 for a in ans if a["סטטוס"] == "העברה")
    withheld = [c["id"] for c in cl if c["authority"] == "unsourced"]
    return "\n".join([
        "# קרא אותי קודם", "",
        stamp("המפה. כל סוכן — אנושי או AI — מתחיל כאן."), "",
        "## מה זה", "",
        "התיקייה הזאת היא **מה שסוכן צריך כדי ללוות ליד של GT מהרגע שנכנס ועד",
        "ההזמנה הראשונה** — בלי לשאול אף אחד ובלי להמציא.",
        "היא עומדת בפני עצמה: סוכן ווטסאפ ב-API ⊥ רואה שום מאגר קוד, ולכן הכל כאן.", "",
        "## סדר הקריאה — ⊥ אלפביתי, יש לו סיבה", "",
        "| # | תיקייה | למה בסדר הזה |",
        "|---|---|---|",
        "| 01 | גבולות וטענות | **ראשון.** סוכן שקורא קודם את התשובות יענה נכון על שאלת אלרגנים ועדיין יהיה שגוי |",
        "| 02 | בנק התשובות | רק מה שלא נחסם ב-01 |",
        "| 03 | מוצרים ומחירים | המספרים |",
        "| 04 | הלקוח והשיחה | מי הוא, באיזה שלב, ומה שולחים |",
        "| 05 | מה שולחים ללקוח | הקבצים עצמם — קטלוג, תמונות, סרטונים |",
        "| 06 | העלאות — גולמי | הכניסה. שם מניחים קבצים חדשים |", "",
        "## מה יש כאן, במספרים", "",
        f"- **{len(rules)}** כללי סירוב · ברירת מחדל = העברה לאלכסנדר",
        f"- **{len(ans)}** תשובות — {ok} מאושרות · {draft} טיוטה (**⊥ נאמרות**) · {move} העברה",
        f"- **{len(cl)}** טענות פומביות · {len(withheld)} בדרגה `unsourced` ⇒ ⊥ נאמרות: "
        + "، ".join(f"`{w}`" for w in withheld),
        f"- **{live}** מוצרים במחירון · **{len(drk)}** משקאות עם עלות, מחיר ורווח", "",
        "## איזו אמת יושבת איפה", "",
        "| נושא | האמת | מי מעדכן |",
        "|---|---|---|",
        "| מוצר, מחיר, משקה, תשובה, גבול | `Sales-Machine/knowledge/` בגיט | Claude, מהריפו |",
        "| שם משפטי, ח.פ, כתובת, טלפון, מייל, צבעים, לוגו | "
        f"[כרטיס זהות v2]({IDENTITY_CARD}) | טום, ידנית |",
        "| מלאי, הזמנות, מי לקוח ומה הזמין | המערכת (Shopify / factory-os) | חי, ⊥ קובץ |",
        "| התיקייה הזאת | **תצוגה בלבד** | נבנית — עריכה כאן תימחק |", "",
        "> שינוי בקובץ כאן ⊥ שורד. הוא נכנס בריפו ונבנה החוצה.", "",
        "## מה הקבצים האלה ⊥ יכולים לתת לך", "",
        "שלוש שאלות שסוכן ייתקל בהן ו**אין להן תשובה בשום קובץ** — הן חיות במערכת:", "",
        "1. **האם הפונה כבר לקוח שלנו, ומה הזמין לאחרונה** — צריך גישה לנתוני הלקוחות.",
        "2. **האם המוצר במלאי** — משתנה בכל שעה. ⊥ מאשרים מלאי מקובץ.",
        "3. **מתי בדיוק ההזמנה שלו תגיע** — ימי החלוקה ידועים (04), התאריך ⊥.", "",
        "בשלושתן: מעבירים לאלכסנדר, ⊥ מנחשים.", "",
        "## חמישה דברים שלעולם ⊥ עושים", "",
        "1. ⊥ עונים על **אלרגנים**. גם ⊥ \"נראה לי שאין\". מסעדה מסתמכת על זה מול סועד.",
        "2. ⊥ נוקבים ב**מחיר שאינו במחירון** (03).",
        "3. ⊥ מבטיחים **תאריך אספקה** להזמנה ספציפית.",
        "4. ⊥ נותנים **הנחה או תנאי תשלום**.",
        "5. ⊥ טוענים **טענת בריאות**. DETOX הוא שם מותג — זה בסדר. "
        "\"מנקה רעלים\" הוא חשיפה רגולטורית.", "",
        "## מע״מ — הכלל שקל לטעות בו", "",
        "מחיר שנאמר ל**בעל עסק** — תמיד **ללא מע״מ**.",
        "מחיר שנוגע למה שהוא מוכר **ללקוח הקצה שלו** — **כולל מע״מ**.",
        "לכן: המחירון (03 · מחירון) ללא מע״מ; המחיר המומלץ ב-48 המשקאות כולל מע״מ 18%.", "",
        "## פרטי GT", "",
        "GT Everyday · גרינטי · גרינטי אוירי דיי בע\"מ",
        "הלהב 15, חולון · 054-398-2444 · info@gteveryday.com · gteveryday.com",
        "מענה טלפוני: א׳–ה׳ 9:00–18:00",
        f"המקור המלא: [כרטיס זהות v2]({IDENTITY_CARD}) — ⊥ להעתיק פרטים לכאן, להצביע עליו.", "",
        "## העברה לאלכסנדר", "",
        "רוב הכללים ב-01 מסתיימים ב\"מעבירים לאלכסנדר\". כשמעבירים, מוסרים לו:",
        "שם העסק · העיר · השאלה **כלשונה** · מה כבר נאמר ללקוח · מאיזה מקור הגיע הליד.", "",
        "> ⚠ **פרטי הקשר של אלכסנדר ⊥ רשומים בשום מקום.** להשלים לפני שסוכן",
        "> אוטומטי עולה לאוויר — אחרת \"מעביר לאלכסנדר\" הוא מבוי סתום.", "",
        "## איך מוסיפים חומר", "",
        "מניחים את הקובץ הגולמי ב-**06 · העלאות — גולמי** ואומרים ל-Claude.",
        "הוא ממיר אותו לפורמט שסוכן קורא, מתייק בתיקייה הנכונה, ומעדכן את המפה הזאת.",
        "⊥ מתייקים ידנית ל-01–05 — מה שיושב שם נבנה מהריפו ויידרס.", "",
    ])


def assets_readme():
    return "\n".join([
        "# מה שולחים ללקוח", "",
        stamp("התיקייה היחידה כאן שאינה נבנית מהריפו — כאן יושבים הקבצים עצמם."), "",
        "## מה אמור להיות כאן", "",
        "| מה | למה זה נחוץ | מצב |",
        "|---|---|---|",
        "| **קטלוג משקאות סופי 26** (PDF) | מה ששולחים בשלב 03. יש ארבעה קטלוגים בקנבה ו**רק זה בתוקף** | ⊥ הועלה |",
        "| **מחירון ללקוח** (PDF) | מה שנשלח אחרי \"כן\" | ⊥ הועלה |",
        "| **תמונות מוצר**, לפי SKU | ליד שואל \"איך זה נראה\" | קיימות ב`נכסי מותג / 02` — לקשר |",
        "| **סרטוני הדרכה**, לפי מוצר ומשקה | הספר מבטיח שיש לכל מוצר ומשקה. **אין קישור לאף אחד בשום קובץ** | ⊥ הועלה |",
        "| **מתכונים** לכל אחד מ-48 המשקאות | הכרטיסים מחזיקים עלות/מחיר/רווח — ⊥ את המתכון | ⊥ הועלה |",
        "| **תעודת כשרות** בד\"ץ בית יוסף | לקוח מבקש לראות. טום אישר את הטענה כעובדה, מסמך אין | ⊥ קיים |",
        "| **דף חבילות ההתחלה** | השלב שכל השיחה מכוונת אליו | ממתין להחלטת טום |", "",
        "> **הפער הגדול ביותר של הסוכן.** הוא יודע מה להגיד, ואין לו מה לשלוח.",
        "> שלושת הראשונים ברשימה שווים יותר מכל שיפור בנוסחים.", "",
        "## הכלל", "",
        "קובץ שנשלח ללקוח ⊥ סותר את 01–03. אם קטלוג מראה מחיר אחר מהמחירון —",
        "**המחירון גובר, והקטלוג צריך תיקון.**", "",
    ])


def inbox_readme():
    return "\n".join([
        "# העלאות — גולמי", "",
        "## מה עושים כאן", "",
        "מניחים כאן כל קובץ שהסוכן צריך לדעת עליו או לשלוח, **בפורמט שיש לכם**:",
        "PDF, תמונה, מסמך וורד, ייצוא מקנבה, צילום מסך, אקסל, קישור לסרטון.", "",
        "אחר כך אומרים ל-Claude \"יש חדש בתיקיית ההעלאות\". הוא:", "",
        "1. קורא את הקובץ",
        "2. ממיר אותו ל-Markdown שסוכן קורא, או משאיר כקובץ לשליחה",
        "3. מתייק ב-01–05 לפי מה שזה",
        "4. מצליב מול הריפו — ואם יש סתירה, **עוצר ושואל** במקום לתקן לבד",
        "5. מעדכן את `00 · קרא אותי קודם`", "",
        "## מה ⊥ עושים", "",
        "- ⊥ מתייקים ידנית ל-01–05. מה שיושב שם נבנה מהריפו ויידרס בבנייה הבאה.",
        "- ⊥ עורכים קובץ שכתוב עליו \"נוצר אוטומטית\". השינוי יימחק.",
        "- ⊥ מוחקים מכאן אחרי המרה — הגולמי נשאר כראיה.", "",
    ])

FILES = [
    ("00", "קרא אותי קודם.md", readme),
    ("05", "מה שולחים ללקוח.md", assets_readme),
    ("06", "איך מוסיפים חומר.md", inbox_readme),
    ("01", "גבולות — מה אסור להגיד.md", boundaries),
    ("01", "טענות — מה מותר לטעון.md", claims),
    ("02", "בנק התשובות.md", answers),
    ("03", "מחירון.md", products),
    ("03", "48 משקאות.md", drinks),
    ("04", "מי הלקוח.md", buyers),
    ("04", "רצף השיחה.md", motion),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default=os.path.join(SALES, "docs/drive-pack"))
    a = ap.parse_args()
    for folder, name, fn in FILES:
        d = os.path.join(a.out, folder)
        os.makedirs(d, exist_ok=True)
        body = fn()
        with open(os.path.join(d, name), "w", encoding="utf-8") as fh:
            fh.write(body + "\n")
        print(f"{folder}/{name}  —  {len(body):,} chars")


if __name__ == "__main__":
    main()
