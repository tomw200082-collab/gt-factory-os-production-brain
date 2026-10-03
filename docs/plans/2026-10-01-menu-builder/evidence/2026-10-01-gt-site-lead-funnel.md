# Evidence — gt-site: the top of the lead funnel as built (read 2026-10-01)

> Read-only reconstruction by a Session 1 exploration agent, verbatim. True as of gt-site `main` `5d3e69c` (#34) on 2026-10-01.
> Authority: `system_verified` for every line that cites a file:line; re-read the files before relying on a number.
> Live-theme caveat: `PUBLISH.md:12` says the live theme `166730072305` carries `73c302e` (#30); #32 and #34 are merged but not recorded as pushed live.

## 1. Lead dialog (#27, #29, #33, #34)

- Every `a[href="#contact"]` (19 links) opens a native `<dialog id="ldlg">`; one form (`#pform`) moves into the dialog and back. Generator `tools/patch_lead_dialog.py`; served markup `theme/sections/gt-home.liquid:286-328`; served JS `theme/assets/gt-site.js:591-742`.
- Phone: bottom sheet. ≥640px: centred 480px card. ≥880px: 820px two-column card with the drink photo it was opened from. Rim colour `--ld-tint`. History entry pushed, so back closes it.
- Steps and copy:
  1. Heading `בואו נעבוד יחד`, sub-line `עונים תוך יום עסקים אחד`.
  2. Business question `יש לכם עסק?` / `אנחנו עובדים רק עם עסקים, בסיטונאות.` Buttons `כן, יש לי עסק` · `לא, לשימוש פרטי`. "No" → `אנחנו עובדים רק עם עסקים.` / `ללקוחות פרטיים, המוצרים שלנו נמכרים באתר של אליטה אופק.` + link to elitaofek.co.il; nothing is sent.
  3. Form: four required fields `שם מלא` · `שם העסק` · `עיר` · `טלפון`; disclosure `עוד פרטים (לא חובה)`: `תפקיד` (בעלים / מנהל/ת / אחראי/ת בר / בריסטה / אחר), `אימייל`, `מה מעניין אתכם` (תמציות תה / מאצ׳ה ואבקות / מחיות פרי / כלי בר ואביזרים / כל תפריט הקיץ), `משהו שכדאי שנדע?`; honeypot `gt_hp`; required consent `אפשר לפנות אליי בנושא אספקה סיטונאית.` (browser-only). Send `שליחה ←` → `שולח…` → `נשלח ✓`. Under it `או כתבו לנו בוואטסאפ · 054-398-2444`. **Business type (venue type, branches) is NOT collected.**
  4. Thanks: `תודה רבה!` / `קיבלנו את הפרטים ונחזור אליכם תוך יום עסקים אחד. אם דחוף — 054-398-2444.`
  5. Lead line: `מה הכי מעניין אתכם?` / `נשלח לכם את התפריט בוואטסאפ.` Five pills → `wa.me/972547588132` with prefilled text: מאצ׳ה `היי, אני מעוניין במאצ׳ה` · אובה `…באובה` · צ׳אי מסאלה `…בצ׳אי מסאלה` · תמציות תה `…בתמציות תה` · full-width `בניית תפריט משקאות עשיר ורווחי לעסק` → `היי, אני מעוניין בבניית תפריט משקאות עשיר ורווחי לעסק` (Tom's words, #29, copy row U-26). No close timer; closes on `visibilitychange` when the visitor returns from WhatsApp.
- Validation: browser — blank required → `חסרים פרטי חובה. בדקו שם מלא, שם העסק, עיר וטלפון.`; <9 digits → `מספר הטלפון לא נראה תקין. בדקו אותו ונסו שוב.` Server (`supabase/functions/website_lead_intake/index.ts:118-122`, `phoneOk()`): mobile/07x needs 9 digits after the 0, landline 8, `+972` normalised, foreign `+` and 8–15 digits; `bad_phone` / `bad_email` (`כתובת המייל לא נראית תקינה. בדקו אותה ונסו שוב.`). Other failure: `לא הצלחנו לשלוח את הפנייה. נסו שוב, או דברו איתנו ישירות: וואטסאפ · 054-398-2444.` Sends held until 3.05 s after navigation start; success requires `res.ok && j.ok && 'was_new' in j`; 15 s abort.
- Posts to `POST …/functions/v1/website_lead_intake` with `contact_name, venue, city, role, phone, email, interest, message, company_website, elapsed_ms, page, referrer`. CORS: gteveryday.com, www, greenteaeveryday.myshopify.com. Accepted `form_name`s: `partner_enquiry`, `landing-site-{chai,matcha,iced-tea,ube}`; anything else stored as `partner_enquiry`. Forwards to `sales-leads-poll/ingest` with `source:"website_form"`, `external_id: web-<date>-<last9digits>` (one lead per phone per day), `display_name: venue`, `platform:"website"`, `is_organic:true`; `campaign_name` deliberately absent. Then inserts a `sales_core.lead_event` `note` (actor `system:website_form`) with `טופס האתר / עיר / תפקיד / מתעניין ב / הודעה / עמוד / הגיע מ`. Returns `{ok:true, was_new}`. Contract frozen (site gate GOVERNOR C6).

## 2. Campaign links `?c=` (#34)

- `gteveryday.com/?c=matcha|tea|ube|chai|menu`; defined only in code (`gt-site.js:711-723`). Dialog opens on load; business question still first; after send only the matching pill shows, relabelled `לקבלת <menu label> בוואטסאפ`; `interest` falls back to the campaign label; `lead_cta = campaign-<key>`.
- `menu` → button `לקבלת תפריט הפתיחה בוואטסאפ`, WhatsApp text `היי, אני מעוניין בבניית תפריט משקאות עשיר ורווחי לעסק`, interest `בניית תפריט משקאות`.
- "That campaign's menu" = a hosted PDF sent by the lead line (`gt-factory-os/api/src/order-intake/sales/lead_texts.ts:11-21`, keys `matcha, ube, chai, tea, opening`, recognised by exact match on the prefilled text, masc./fem.). Not a Shopify collection, not a drink list on the site.
- Separate: `?view=chai|matcha|iced-tea|ube` category landing pages (`tools/landing-pages/gen.py`), own forms (`form_name: landing-site-<slug>`), `/pages/<slug>` unpublished.

## 3. Menus and drinks on the site

- Data in `theme/assets/gt-site.js`: `COLS` (10 collections, 48 drinks; drink fields `he, en, d, st, ing, m`), `FLMAP` (product → [collection, drink], 51 rows), `PUREES` (purée → 4 drinks), `DPHOTO` (one photo per drink). Figures (`fc, p, pr`) only in `src/index.html:1955` and `data/drinks_final_figures.json` (48 pages, VAT 0.18, cost ex-VAT, price incl. VAT, margin = (price/1.18 − cost)/(price/1.18), cup 350 ml; synced from brain skill `drinks-pricelist`).
- Collections: 01 חליטות קרות (7) · 02 לימונדות (3) · 03 משקאות הדגל (4) · 04 גזוז (3) · 05 אייס מאצ׳ה (6) · 06 מאצ׳ה ספיישל (5) · 07 מאצ׳ה קוקוס (5) · 08 צ׳אי מסאלה (6) · 09 קולד פואם (4) · 10 אובה (5).
- Doses exist only inside the Hebrew `ing`/`st` strings; no structured bill of materials: tea concentrate drinks and lemonades 50 ml; signature/gazoz 40 ml concentrate + 40 ml purée or juice; chai and cold foam 50 ml masala; matcha 50 ml prepared = 1.8 g powder (+40 ml purée or masala); ube 50 ml prepared = 2 g powder (+40 ml purée, 50 ml masala or 1.8 g matcha). Non-GT inputs: milk, coconut water/cream, lychee water, apple juice, agave, banana purée, tonic, espresso.
- Recipe card `#cmodal`: name, English kicker, description, steps, ingredients, photo, `על בסיס <product>` links; only `רווחיות X%` survives of the figures; `הוסיפו לתפריט` button. Deep link `#recipe-<ci>-<di>`.
- Served yield/margin claims: `מתמצית אחת יוצאים עד 13 משקאות בתפריט, ומכל בקבוק 20–25 כוסות. רווחיות של עד 87%…`; stat cards `87%` · `20–25` · `48` · `12`; product window `בקבוק אחד = 20–25 כוסות`. Landing pages: chai `20 כוסות מבקבוק של ליטר`, iced-tea `20–25`, matcha `277 כוסות מ־500 גרם` (`50 גרם ≈ 27`), ube `500 כוסות מקילו` (`500 גרם ≈ 250`). Open P0 "COPY-01, cups per bottle" waits for Tom's words (commit `73c302e`); Sales-Machine CL-2 lists `20–25 כוסות` as a catalogue defect. Product-card badges (Detox 3, Revive 3, Energy 2, American 2) do not match `FLMAP` counts (2, 2, 1, 0).

## 4. Products, portal, FAQ, where to start

- 11 concentrates (500 ml / 1 L), matcha 50 g / 500 g, hojicha 500 g, ube 500 g / 1 kg, ODK purées (mango, strawberry, peach) 1 L 50% fruit, eight bar tools. Served page shows sizes only: `data/site_flags.json` `show_prices:false` (Tom 2026-09-24); `#pricing` section removed; tools read `מחירון אביזרים מלא לפי בקשה`. `src/index.html` only: ₪33 / ₪65 a bottle, `כל המחירים בשקלים, לפני מע״מ`; per cup `עלות חומר גלם · ללא מע״מ` and `מחיר מומלץ · כולל מע״מ`.
- Portal entry `https://gt-factory-os-api-production.up.railway.app/portal/` labelled `כניסה לעסקים` (phone pill `לעסקים`), behind theme switch `show_portal_entry` (true in `templates/index.json:7`). No links to Shopify `/products` or `/collections`.
- FAQ: 22 questions in three groups (`gt-home.liquid:243-271`, JSON-LD at `:412`). Notable answers: איך מתחילים? → `משאירים פרטים כאן למטה, ואנחנו בונים לכם תפריט פתיחה למקום, כולל מתכונים, תמחור והדרכת צוות.` · איך מזמינים? → `בקישור אישי להזמנה שנשלח אליכם בוואטסאפ: בוחרים מוצרים וכמויות, ושולחים…` · איפה רואים את המחירים? → `את המחירון המלא, עם תמחיר לכל משקה, אנחנו שולחים ישירות אליכם…` · יש חוזה או התחייבות? → `…יש רק מינימום להזמנה…` (no amount) · אתם מספקים לכל הארץ? → centre Sun/Mon/Thu, north Tue, south + Jerusalem Wed, cutoff 14:00 · יש הדרכה לצוות? → `…סרטון הדרכה… חוברת משקאות עם הוראות הכנה ותמחור לכל משקה.` · כמה משקאות יוצאים מבקבוק אחד? → `בקבוק תמצית אחד נותן 20–25 כוסות…`.
- "Where to start" exists as copy only: the first FAQ answer; contact `השאירו פרטים — נחזור אליכם ונבנה יחד את תפריט המשקאות שלכם.`; closing banner `אפשר להפסיק עם התפריט המשעמם?` / `נבנה יחד תפריט משקאות שהאורחים שלכם יצלמו.`; the fifth pill.

## 5. Design rules a sibling product must respect

- Tokens (`theme/assets/gt-site.css:6-12`): `--ink #20241F`, `--ink-soft #4B5148`, `--paper #FBF8F2`, `--card #F3EFE6`, `--white #FFF`, `--gt #3E6E34`, `--gt-d #2B4F24`, `--terra #C4744B`, `--line #E7E1D3`. Flavours: detox `#4E8C4A`, energy `#F0A63A`, revive `#E2634B`, consc `#C4327E`, amer `#C81F2E`, nama `#D96B3F`, fresh `#E63950`, desert `#C9922F`, calm `#8B7FBF`, matcha `#5FA34C`, ube `#7B5CC6`. Theme colour `#3E6E34`. Error box `#FBEAE7` / `#E5B4AB` / `#7A2E1E`.
- Type: Heebo 400–900 (Roca One named first, unlicensed → falls back). Body 17.5px. Display `clamp(44px,5vw,80px)`; italic `em` at 700. Eyebrow 12px, `.28em`, uppercase, 800, `#9C5C3C`, 34px rule. Landing pages: Assistant / Bellefair / Playfair Display, `g-` prefixed classes.
- Layout `.wrap` 1240px, 28px padding; sections 100px vertical. Radii: inputs 14px; cards/stats/tables 20–22px; product cards/forms/modals/dialog 26px; hero/economics 30–32px; buttons/pills 999px. Buttons: ink pill, uppercase, `.06em`, 800, hover `--gt-d`, arrow `←`; `.btn.light` paper. Pills min 52px; touch targets ≥44px; focus ring 3px (2px on fields) `--gt`; reduced motion honoured. Shadows: card hover `0 30px 60px -18px rgba(32,36,31,.22)`; form `0 30px 60px -30px rgba(32,36,31,.18)`; modals `0 40px 90px -20px rgba(0,0,0,.4)`.
- Soft floor rule (#23, Tom 2026-09-26): never `filter:drop-shadow` on product images (iOS Safari clips it); use `background:radial-gradient(closest-side,rgba(32,36,31,.28),transparent) 50% 100%/72% 8% no-repeat`. Partner logos no shadow.
- RTL: `<html lang="he" dir="rtl">`; sliding tracks pinned LTR; close buttons on the left; arrows `←`; number ranges in `<bdi dir="ltr">`; never push off-screen with large negative offsets (CI guard). Imagery: flavour-colour grounds, cut-out bottle/pouch duo shots, one photo per drink on a 925×1052 canvas; content-addressed `gt-<sha1[:10]>.webp`; CI fails on wsrv.nl/cloudfront URLs.
- Process: change the generator never the outputs; Liquid section <256 KB; no new dependency without strong reason; every figure from the record (`verify_figures.py` = 0 disagreements); Hebrew copy needs Tom; ship only through `tools/theme_ship.py` (`PUBLISH.md`). Harness `tools/site_shots.mjs` (p360, p390, d1366, d1920, landing pages, axe, slow-4G; stubs the intake). Gate brief `docs/SITE_GATE_BRIEF.md`. Two WhatsApp numbers never merged (GOVERNOR C7): 054-398-2444 contact; 054-758-8132 lead line.

## 6. Analytics and attribution

- GTM `GTM-TFH9M99` → GA4 `G-YFDQ5P8EM3`; GA4 `G-QCNXYQR1TR` and Google Ads `AW-331942645` via Shopify's Google channel; Taboola `1547330` and Retention Rocket `ym6nRgm7` behind `third_party_pixels`; `analytics_id` must stay empty. No Meta pixel, no Klaviyo, no capture of UTM / fbclid / gclid (`docs/2026-09-02_analytics.md`).
- Events: only `generate_lead` after a confirmed store: `{form:'partner_enquiry', lead_interest, lead_role, lead_cta}` (+ `gtag` if present); landing pages `{form:'landing-site-<slug>', lead_cta:'lp'}`. `lead_cta` ∈ `nav, hero, slide-1..10, catalogue, economics, closing, product, recipe, puree, faq, link, contact, campaign-<key>, lp`. As of 2026-09-03 GTM had no trigger on `generate_lead`.
- What reaches the CRM: `source='website_form'`, `form_name`, `platform='website'`, `is_organic:true` hard-coded even for paid traffic; `campaign_name` not set; the campaign survives only in the note (`מתעניין ב:`, `עמוד:` with `?c=`, `הגיע מ:`). Per-landing-page attribution via `form_name` + `sales_core.campaign_map` (migration 0344).

## 7. The journey as the site defines it

Landing (`עידן חדש של משקאות / בבית העסק שלכם.`, `בואו נעבוד יחד ←`, `לצפייה במשקאות`) → any of 19 CTAs opens the dialog (`?c=` opens on arrival) → business question → form → send (held ≥3 s) → thanks → lead line pills → WhatsApp to 054-758-8132 with prefilled text → off-site: the lead line answers with the menu PDF and three buttons. The site promises a reply within one business day and the menu on WhatsApp. Portal is only for existing businesses (`כניסה לעסקים`). FAQ says ordering happens through "a personal order link sent on WhatsApp".

## 8. What this means for the Menu Builder (agent's reading)

- Reusable today: `COLS` + `FLMAP` + `PUREES` (drink → GT product), `ing` strings (doses), yields for powders (1.8 g matcha, 2 g ube), implied for concentrates (1 L ÷ 40–50 ml).
- Missing: a structured bill of materials, SKUs or Shopify handles, any venue-type field, campaign/UTM attribution.
- Prices: showing ₪ to visitors contradicts `show_prices:false`; margins are allowed.
- Intake: a new lead source needs a new `FORM_NAMES` entry (`index.ts:81-87`) and a `campaign_map` key; the intake contract is frozen.
- Precedent: `docs/2026-09-03_benchmark.md:44-48` — sales sends "three recipes from the category that brought the lead, never the 48"; ideas #6 (route by venue type) and #9 (per-venue starters).
