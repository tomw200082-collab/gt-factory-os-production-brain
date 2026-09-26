# Recruitment — גיוס: new candidates and personal outreach

Moved here on 2026-09-26 from the claude.ai account skill `gt-recruitment-outreach`, when account skills left the account (workspace ledger, Layer 1). Hiring is rare, so this is a reference doc, not a skill: read it when Tom asks to check new candidates or write outreach messages ("בדוק מועמדים חדשים", "מי שלח קורות חיים", "תכין הודעות פנייה").

The goal is to find genuinely new applicants in Tom's Gmail, read their CVs, judge fit for the open role, and draft a warm, personal Hebrew message for each relevant one. Never blast everyone: the value is the filtering plus one real line per candidate.

People and the office address are in `people_rhythm.md`. Alex screens driver candidates.

## 1. Find the new applicants

Search each channel. The default window is `newer_than:3d`; widen it if the last check was longer ago. Compare against candidates already contacted (the conversation and existing Drafts), so only new people surface.

- **Drushim** is the best source, because the CV is readable in the email body: `from:drushim.co.il newer_than:3d`. Real applications have the subject `קו"ח: <role> | <name> | <city>`. Ignore the Drushim mail that is not a candidate:
  - job-posting confirmations from `Yaniv@drushim.co.il` ("בנוגע למשרה");
  - sales and contact-person mail from `yafa@drushim.co.il` ("אשת קשר");
  - invoices from `system@sent-via.netsuite.com`.
- **Mploy:** `from:mploy.co.il subject:"התקבלה מועמדות" newer_than:3d`. Only **"התקבלה מועמדות חדשה"** is a real application. **"נמצא פרופיל חדש"** is automated AI-match noise. The body holds only name, phone and email; the CV is an attachment that can't be read here.
- **Other channels** (direct email, AllJobs): `("קורות חיים" OR "מועמדות" OR resume OR CV OR alljobs) newer_than:3d -from:mploy.co.il`.

## 2. Read each CV

Open the thread with full content.
- Drushim emails carry a structured summary (name, email, phone, area, last role, years of experience) plus the full CV in the body. Read both.
- Hebrew in the body is sometimes Windows-1255 mojibake: Latin gibberish such as `ãðéàì`, which is דניאל. Decode it; the content is recoverable.
- If the CV part of the body is empty, the CV is only in the attachment. Use the summary and say the details are limited.

## 3. Judge relevance before writing

- **Delivery driver (נהג חלוקה ייצוגי).**
  - Relevant: hands-on driving, delivery, courier or route work; logistics or warehouse; a valid licence; food handling; a presentable, client-facing manner, since the driver meets café and bakery clients.
  - Location: central Israel near Holon is a plus. Far north is a commute note, not a disqualifier.
- **Bookkeeping and office manager.** Look for bookkeeping, back office, office management and the relevant software. Verify a bookkeeping certificate; don't assume one.
- **Exclude, with a one-line reason each:** candidates with no relevant background who want other work, candidates abroad or needing a visa, and clearly off-role profiles.
- Drushim's auto-tag **"נסיון רלוונטי: ללא ניסיון" is sometimes wrong.** Judge from the CV itself.

## 4. Draft the messages

The style Tom approved is warm, human, personal and respectful, not stiff. Hebrew, **no emojis**, signed "תום, גרינטי". Every message carries one line tied to that candidate's real CV; never generic flattery. Show each message with the candidate's phone number, so Tom can send it by WhatsApp or SMS in one tap.

```
היי <שם>, שמי תום מגרינטי. עברתי על קורות החיים שלך למשרת <תפקיד>, ו<שורה אישית מותאמת מה-CV>. אשמח להכיר אותך.
מתי נוח לך השבוע לראיון? נתאם בקלות.
מחכה לפגוש אותך,
תום, גרינטי
```

An example of the personal line for a driver: "הניסיון שלך בניהול קו חלוקה ובעבודה מול לקוחות ממש רלוונטי למה שאנחנו מחפשים". If an interview time is already set for that candidate, replace the availability question with it.

## 5. Output

Give one list. For each relevant candidate, show **name — phone**, the ready-to-send message, and one line on why they fit, with any location note. List the excluded candidates separately, one line each.

Then offer the next steps:
- **Interviews:** schedule them and create Google Calendar events of about 45 minutes, inviting the candidate and Alex, at the office.
- **CV email to Alex:** one private email per candidate, with the full CV in the body. Alex has no access to the job sites, so the CV must be in the body, not linked. The candidate is never a recipient.

## Gotchas

- The email address in the Drushim application field sometimes differs from the one in the CV. Flag it when later emails depend on it.
- Some candidates ask for WhatsApp when a call goes unanswered. Mention it when the CV says so.
- Create drafts only; Tom sends them himself. If a write needs Tom's approval on his device and is blocked, say so and give a manual fallback rather than failing silently.
