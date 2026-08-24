# Hebrew copy — written, not translated

Contents: the core move · translationese tells · word swaps · gendered address ·
RTL punctuation and typography · rhythm · headlines · CTA verbs · HoReCa vocabulary ·
WhatsApp register · checklist.

## The core move

Do not draft in English and translate. Decide the idea, then compose in Hebrew from the
first word. Translated copy carries English sentence architecture — long subordinate
clauses, a subject in front of every verb, ceremonial openings — and Israeli readers hear
it instantly as *foreign* or, worse, as *institutional*.

Israeli business Hebrew is direct, short, and low-ceremony. Warmth comes from being useful
and specific, not from politeness formulas.

## Translationese tells

| Tell | Why it reads foreign | Fix |
|---|---|---|
| "אנחנו גאים להציג" | corporate press-release voice, says nothing | open on the reader's situation |
| "פתרון מוביל / חדשני / איכותי" | adjectives a competitor can copy verbatim | a number, a mechanism, a moment |
| "ניתן להזמין" | passive, bureaucratic | "אפשר להזמין" / "תזמינו" |
| "על מנת" (and the incorrect "בכדי") | formal register drag | "כדי" |
| "הינו" / "מהווה" | false copula, officialese | drop it, or "הוא" |
| "אנו" / "אשר" | written-register formality | "אנחנו" / "ש" |
| "לבצע הזמנה", "מתן שירות" | nominalization — verbs turned into nouns | "להזמין", "לשרת" |
| "חוויה" for everything | emptied by overuse | name what actually happens |
| "בין אם… ובין אם…" | direct calque of "whether… or…" | split into two short sentences |
| Three-noun smichut chains ("תהליך שיפור איכות השירות") | unparsable at a glance | break into two sentences |

## Word swaps that lift register instantly

לבצע רכישה → לקנות · לבצע הזמנה → להזמין · להוות → להיות · בעל אופי → כמו ·
בטרם → לפני · כמו כן → וגם · לאור העובדה ש → כי · בהמשך לכך → אז ·
מוצר פרימיום → what makes it better, concretely · פתרון → the thing itself.

## Gendered address

Hebrew forces a gender choice in second person. Ranked options for marketing copy:

1. **Impersonal / infinitive** — the cleanest escape: "לתיאום טעימה — הודעה אחת",
   "כדי להזמין: השיבו במילה אחת". No gender, no clunk.
2. **Plural (אתם)** — the default for business audiences, reads natural in B2B.
3. **Masculine singular** — common in Israeli advertising, still excludes half the market;
   use only when the audience is genuinely known and singular.
4. **Slash forms (את/ה)** — acceptable in forms and terms, poison in a headline; they break
   rhythm and signal that nobody chose an audience.

Whichever you pick, hold it consistently across the whole piece. Mixed address is the single
most common amateur tell in Hebrew campaigns.

## RTL punctuation and typography — the mechanics

The bidi algorithm gets this right *only* when the container's direction is right. Most
"the period jumped to the wrong side" bugs are a missing direction, not a typing mistake.

- **Set the direction explicitly.** HTML: `dir="rtl"` on the block (plus `text-align: right`
  where the framework doesn't inherit it). Email: `dir="rtl"` on the wrapping `<table>`/`<div>`,
  because many clients strip `<html dir>`. Plain-text fields that default to LTR will mirror
  parentheses and quotes wrongly no matter how you type them.
- **A line ending in Latin text or a number** ("…מ־GT" · "…65 ₪") can pull the final period
  to the visually wrong end. Insert RLM (U+200F, `&rlm;`) after the Latin/number token, or
  wrap the token in `<bdi>`.
- **Ranges and hyphenated numbers** ("10-20", "052-1234567") render reversed in RTL contexts.
  Write ranges in words in prose — "בין 10 ל-20" — and place phone numbers and SKUs on their
  own line or inside `<bdi>`.
- **Currency.** Both "₪65" and "65 ₪" appear in Israeli usage; pick one per document and never
  mix. State the VAT basis whenever a price appears in customer-facing copy
  ("לפני מע״מ" / "כולל מע״מ") — omitting it is the most common source of a price argument.
- **Geresh and gershayim** are ׳ (U+05F3) and ״ (U+05F4), not the ASCII apostrophe and quote:
  מע״מ, ד״ר, ג׳ינג׳ר. ASCII substitutes are tolerated in chat, not in print or a catalog.
- **Quotation marks:** straight ASCII double quotes are safest in RTL — smart quotes inherited
  from an LTR editor mirror unpredictably across clients.
- **Dates:** dd.mm.yyyy. Emails and URLs go on their own line; inline they visually shatter
  the sentence.
- **Never hand-break lines** to "fix" alignment. It breaks on every other screen width.

## Rhythm

Hebrew is denser than English — a faithful translation of an English draft is typically
20–30% too long. Cut it. Then read aloud: Hebrew punishes long sentences harder than English
does, because there are fewer function words to signal structure.

## Headline patterns that work in Hebrew

- Diagnosis: "למה תפריט המשקאות שלכם לא מוכר בקיץ"
- Arithmetic: "3 דקות הכנה. 40 שניות הגשה."
- Pattern interrupt: "תפסיקו לסחוט לימונים בשש בבוקר"
- Self-selection: "אם יש לכם יותר משני סניפים — כדאי לקרוא"
- Insider: "מה שברמנים יודעים על עלות מנה ובעלי מקום לא"

Verb-forward and short. Hebrew headlines built on nominalizations die on arrival.

## CTA verbs that actually get pressed

תזמינו · קבלו · שלחו הודעה · ענו במילה אחת · בואו נבדוק ביחד · לתיאום טעימה ·
תגידו לי מתי נוח. Avoid "לחצו כאן" — it names the mechanic, not the payoff.

## HoReCa vocabulary (the reader's own words)

Places: בית קפה · מסעדה · בר · מאפייה · מלון · קייטרינג · חנות נוחות.
Roles: בעל/ת מקום · מנהל רכש · שף · ברמן · מנהל משמרת.
Operations: תפריט · מנה · מנת הגשה · עלות מנה (פוד קוסט) · ספק · מק״ט · הזמנה · משלוח ·
חשבונית · שוטף+30 · מלאי · שעת עומס · רווח למנה.
Using their operational vocabulary is the fastest credibility signal there is — far faster
than any claim about yourself.

## WhatsApp register

No "שלום רב". Open with their name and one line establishing why you are writing to *them*
specifically. Three to five short lines. One question at the end, answerable in a word.
A cold first message with a link in it reads as a broadcast; earn the link with the reply.

## Before you ship

- One consistent form of address throughout?
- Any sentence that only makes sense if you know the English original?
- Nominalizations replaced by verbs?
- Prices carry a VAT basis; numbers, phones, and SKUs render correctly in RTL?
- Read aloud — does it sound like an Israeli talking to a colleague, or like a brochure?
