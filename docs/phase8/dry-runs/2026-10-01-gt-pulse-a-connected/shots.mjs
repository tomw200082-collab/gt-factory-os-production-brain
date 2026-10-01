// Connected screenshot matrix for the five-lens audit (real GoTrue session, real API, staging DB).
import { chromium } from '/home/user/wt/portal/node_modules/playwright/index.mjs';
import pg from '/home/user/wt/backend/api/node_modules/pg/lib/index.js';
const OUT = '/home/user/wt/brain/docs/phase8/dry-runs/2026-10-01-gt-pulse-a-connected/shots';
const BASE = 'http://localhost:3000';
const db = new pg.Client({ connectionString: 'postgresql://supabase_admin:stagepw@localhost:55433/postgres' }); await db.connect();
const lead = async (email) => (await db.query(`select id::text from sales_core.lead where assignee=$1 and status in ('new','working') order by created_at desc limit 1`, [email])).rows[0].id;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function link(email, since) {
  for (let i = 0; i < 30; i++) {
    const l = await (await fetch('http://localhost:58025/api/v1/messages?limit=20')).json();
    const m = l.messages.find((x) => x.To.some((t) => t.Address === email) && new Date(x.Created) >= since);
    if (m) { const f = await (await fetch(`http://localhost:58025/api/v1/message/${m.ID}`)).json();
      const u = (f.Text.match(/http:\/\/localhost:54321\/auth\/v1\/verify\S+/) || [])[0]; if (u) return u; }
    await sleep(500);
  }
  throw new Error('no link');
}
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const notes = [];
async function session(email) {
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const p = await ctx.newPage();
  await p.goto(`${BASE}/login`);
  await p.screenshot({ path: `${OUT}/login-signedout-1280.png` });
  const since = new Date(Date.now() - 1000);
  await p.getByTestId('login-email-input').fill(email); await p.getByTestId('login-submit').click();
  await p.getByTestId('login-sent-state').waitFor();
  await p.screenshot({ path: `${OUT}/login-sent-1280.png` });
  await p.goto(await link(email, since)); await p.waitForURL((u) => !u.pathname.startsWith('/auth') && !u.pathname.startsWith('/login'));
  const state = await ctx.storageState(); await ctx.close(); return state;
}
for (const [role, email] of [['rep', 'rep@staging.invalid'], ['manager', 'manager@staging.invalid']]) {
  const state = await session(email);
  const id = await lead(email);
  const routes = { today: '/sales/today', leads: '/sales/leads', drawer: `/sales/leads?lead=${id}`, attention: '/sales/attention', orgs: '/sales/orgs', settings: '/sales/settings' };
  const variants = [
    ...[320, 390, 430, 1280].map((w) => ({ tag: `${w}`, viewport: { width: w, height: w < 1000 ? 844 : 900 } })),
    { tag: '390-dark', viewport: { width: 390, height: 844 }, colorScheme: 'dark' },
    { tag: '320-dark', viewport: { width: 320, height: 700 }, colorScheme: 'dark' },
    { tag: '390-reduced', viewport: { width: 390, height: 844 }, reducedMotion: 'reduce' },
  ];
  for (const v of variants) {
    await db.query(`update private_core.app_users set theme_preference=$1 where email=$2`, [v.colorScheme === 'dark' ? 'dark' : 'light', email]);
    const ctx = await browser.newContext({ storageState: state, viewport: v.viewport, colorScheme: v.colorScheme ?? 'light', reducedMotion: v.reducedMotion ?? 'no-preference', locale: 'he-IL' });
    await ctx.addInitScript(() => { window.__GT_SALES_OUTCOME_DELAY_MS__ = 0;
      window.addEventListener('click', (e) => { if (e.target?.closest?.('a[href^="tel:"]')) e.preventDefault(); }); });
    const p = await ctx.newPage();
    for (const [name, path] of Object.entries(routes)) {
      await p.goto(BASE + path); await p.waitForLoadState('networkidle'); await sleep(300);
      const overflow = await p.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
      if (overflow > 0) notes.push(`${role} ${name} ${v.tag}: horizontal overflow ${overflow}px`);
      await p.screenshot({ path: `${OUT}/${role}-${name}-${v.tag}.png`, fullPage: true });
      if (name === 'today' || name === 'attention') {
        // FAB clearance at the end of the scroll, measured, not read off a full-page shot.
        const hit = await p.evaluate(() => {
          window.scrollTo(0, document.documentElement.scrollHeight);
          const fixed = [...document.querySelectorAll('body *')].filter((e) => getComputedStyle(e).position === 'fixed' && e.getBoundingClientRect().height > 0 && e.getBoundingClientRect().top > innerHeight / 2);
          const btns = [...document.querySelectorAll('main button, main a')].filter((b) => b.getBoundingClientRect().height > 0);
          const last = btns.sort((a, b) => b.getBoundingClientRect().bottom - a.getBoundingClientRect().bottom)[0];
          if (!last) return 'no-controls';
          const r = last.getBoundingClientRect();
          return fixed.some((f) => { const q = f.getBoundingClientRect(); return r.bottom > q.top && r.top < q.bottom && r.right > q.left && r.left < q.right; }) ? 'OVERLAP' : 'clear';
        });
        if (hit !== 'clear') notes.push(`${role} ${name} ${v.tag}: last control vs fixed bars at scroll end = ${hit}`);
      }
    }
    // The result sheet, activity step, on the lead drawer.
    await p.goto(`${BASE}/sales/leads?lead=${id}`); await p.getByTestId('lead-drawer').waitFor();
    await p.getByTestId('drawer-call').click();
    await p.evaluate(() => { Object.defineProperty(document, 'visibilityState', { value: 'hidden', configurable: true }); document.dispatchEvent(new Event('visibilitychange'));
      Object.defineProperty(document, 'visibilityState', { value: 'visible', configurable: true }); document.dispatchEvent(new Event('visibilitychange')); });
    await p.getByTestId('outcome-sheet').waitFor();
    await p.screenshot({ path: `${OUT}/${role}-sheet-root-${v.tag}.png` });
    await p.getByTestId('outcome-answered_progressing').click();
    await p.getByTestId('activity-note').fill('בדיקת תצוגה סינתטית');
    await p.screenshot({ path: `${OUT}/${role}-sheet-activity-${v.tag}.png` });
    const save = await p.getByTestId('activity-save').boundingBox();
    const vh = v.viewport.height;
    if (v.colorScheme === 'dark') notes.push(`${role} ${v.tag}: html.dark=${await p.evaluate(() => document.documentElement.classList.contains('dark'))} bg=${await p.evaluate(() => getComputedStyle(document.querySelector('[data-app="sales"]')).backgroundColor)}`);
    if (!save || save.y + save.height > vh) notes.push(`${role} sheet ${v.tag}: save button outside viewport (${JSON.stringify(save)})`);
    await ctx.close();
  }
  // Keyboard: Tab order on Today at 1280, focus must be visible.
  const ctx = await browser.newContext({ storageState: state, viewport: { width: 1280, height: 900 } });
  const p = await ctx.newPage(); await p.goto(`${BASE}/sales/today`); await p.waitForLoadState('networkidle');
  const order = [];
  for (let i = 0; i < 40; i++) {
    await p.keyboard.press('Tab');
    order.push(await p.evaluate(() => { const a = document.activeElement; const s = getComputedStyle(a);
      return `${a.tagName.toLowerCase()}:${(a.getAttribute('aria-label') || a.textContent || '').trim().slice(0, 18)}|outline=${s.outlineStyle}/${s.outlineWidth}|shadow=${s.boxShadow !== 'none'}`; }));
    if (i === 3) await p.screenshot({ path: `${OUT}/${role}-today-keyboard-focus-1280.png` });
  }
  notes.push(`${role} Today tab order (40 stops): ${order.join(' > ')}`);
  notes.push(`${role} Today keyboard reaches task actions: ${order.some((o) => o.includes('התקשר')) && order.some((o) => o.includes('השלם משימה'))}`);
  await ctx.close();
}
await db.query(`update private_core.app_users set theme_preference='light' where email like '%@staging.invalid'`);
await browser.close(); await db.end();
console.log(notes.join('\n'));
