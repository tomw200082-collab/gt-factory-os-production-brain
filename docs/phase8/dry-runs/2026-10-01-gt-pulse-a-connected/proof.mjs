// Connected staging proof: GoTrue magic link -> portal -> API -> committed DB.
import { chromium } from '/home/user/wt/portal/node_modules/playwright/index.mjs';
import pg from '/home/user/wt/backend/api/node_modules/pg/lib/index.js';
const OUT = '/home/user/wt/brain/docs/phase8/dry-runs/2026-10-01-gt-pulse-a-connected';
const BASE = 'http://localhost:3000';
const db = new pg.Client({ connectionString: 'postgresql://supabase_admin:stagepw@localhost:55433/postgres' });
await db.connect();
// Fresh synthetic leads per run, so every run proves the same thing from the same start.
const seedRun = Date.now().toString(36);
async function seedLead(tag, assignee, phone, ageDays) {
  const id = (await db.query(`insert into sales_core.lead(org_id,source,external_id,contact_name,phone_raw,assignee,status,next_touch_at,created_at)
    values('5a000000-0000-4000-8000-000000000001','test',$1,$2,$3,$4,'new',now()+interval '1 day',now()-make_interval(days=>$5)) returning id::text`,
    [`stage-${tag}-${seedRun}`, `סינתטי ${tag}`, phone, assignee, ageDays])).rows[0].id;
  await db.query(`insert into sales_core.lead_event(lead_id,event_type,payload,actor) values($1,'created','{}','staging-seed')`, [id]);
  return id;
}
await db.query(`update sales_core.lead set status='lost', lost_reason='staging run reset' where external_id like 'stage-%' and status in ('new','working')`);
const n = () => `05000${String(Math.floor(Math.random() * 1e5)).padStart(5, '0')}`;
const REP_LEAD = await seedLead('rep', 'rep@staging.invalid', n(), 0);
const MGR_LEAD = await seedLead('mgr', 'manager@staging.invalid', n(), 0);
const UNOWNED = await seedLead('unowned', null, n(), 4);
const results = [];
const check = (name, ok, detail = '') => { results.push({ name, ok, detail }); console.log(`${ok ? 'PASS' : 'FAIL'} ${name} ${detail}`); };
const RUN = Date.now().toString(36);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function magicLink(email, since) {
  for (let i = 0; i < 30; i++) {
    const list = await (await fetch('http://localhost:58025/api/v1/messages?limit=20')).json();
    const m = list.messages.find((x) => x.To.some((t) => t.Address === email) && new Date(x.Created) >= since);
    if (m) {
      const full = await (await fetch(`http://localhost:58025/api/v1/message/${m.ID}`)).json();
      const url = (full.Text.match(/http:\/\/localhost:54321\/auth\/v1\/verify\S+/) || [])[0];
      if (url) return url.replace(/&amp;/g, '&');
    }
    await sleep(500);
  }
  throw new Error(`no magic link for ${email}`);
}

async function login(browser, email, deepLink, viewport) {
  const ctx = await browser.newContext({ viewport, locale: 'he-IL' });
  await ctx.addInitScript(() => {
    window.__GT_SALES_OUTCOME_DELAY_MS__ = 0;
    // Harness only: the phone's dialer takes over a tel: link. Headless Chromium has no
    // dialer and stalls input after the external-protocol navigation, so the navigation
    // (not the app's click handler, which runs first at the React root) is cancelled.
    window.addEventListener('click', (e) => { if (e.target?.closest?.('a[href^="tel:"]')) e.preventDefault(); });
  });
  const page = await ctx.newPage();
  page.on('pageerror', (e) => console.log('PAGEERROR', String(e).slice(0, 300)));
  page.on('console', (m) => { if (m.type() === 'error') console.log('CONSOLE', m.text().slice(0, 200)); });
  await page.goto(BASE + deepLink);
  check(`${email}: signed-out deep link goes to login with destination kept`,
    page.url().includes('/login') && decodeURIComponent(page.url()).includes(deepLink), page.url().replace(BASE, ''));
  const since = new Date(Date.now() - 1000);
  await page.getByTestId('login-email-input').fill(email);
  await page.getByTestId('login-submit').click();
  await page.getByTestId('login-sent-state').waitFor();
  const link = await magicLink(email, since);
  await page.goto(link);
  await page.waitForURL((u) => u.pathname.startsWith('/sales/leads'), { timeout: 20000 });
  check(`${email}: magic link lands on the deep link`, page.url().endsWith(deepLink), page.url().replace(BASE, ''));
  return { ctx, page };
}

async function leaveAndReturn(page) {
  await page.evaluate(() => {
    Object.defineProperty(document, 'visibilityState', { value: 'hidden', configurable: true });
    document.dispatchEvent(new Event('visibilitychange'));
    Object.defineProperty(document, 'visibilityState', { value: 'visible', configurable: true });
    document.dispatchEvent(new Event('visibilitychange'));
  });
}

async function answer(page, note, trigger = page.getByTestId('drawer-call')) {
  await trigger.click();
  await leaveAndReturn(page);
  await page.getByTestId('outcome-answered_progressing').click();
  await page.getByTestId('activity-note').fill(note);
  await page.getByLabel('מה הפעולה הבאה?').selectOption('call');
  const d = new Date(Date.now() + 2 * 86400000).toISOString().slice(0, 10);
  await page.getByLabel('מתי לבצע?').fill(d);
}

const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
try {
  // ---- Rep: email link -> lead -> atomic activity -> committed rows
  const rep = await login(browser, 'rep@staging.invalid', `/sales/leads?lead=${REP_LEAD}`, { width: Number(process.env.W || 390), height: 844 });
  await rep.page.getByTestId('lead-drawer').waitFor();
  await rep.page.screenshot({ path: `${OUT}/01-rep-deeplink-390.png` });
  await answer(rep.page, `שיחה סינתטית ראשונה ${RUN}`);
  const [resp] = await Promise.all([
    rep.page.waitForResponse((r) => r.url().includes(`/api/sales/leads/${REP_LEAD}/activity`) && r.request().method() === 'POST'),
    rep.page.getByTestId('activity-save').click(),
  ]);
  const body = await resp.json();
  const reqId = resp.request().postDataJSON().request_id;
  check('rep activity saved over HTTP', resp.status() === 200, `status=${resp.status()} request_id=${reqId}`);
  const ev = await db.query(`select count(*)::int n from sales_core.lead_event where id = any($1::uuid[]) and lead_id=$2`,
    [[body.outcome_event_id, body.note_event_id].filter(Boolean), REP_LEAD]);
  const tk = await db.query(`select owner_email, kind, status from sales_core.task where id = any($1::uuid[])`, [body.task_ids]);
  check('request correlates to committed lead_event rows', ev.rows[0].n === [body.outcome_event_id, body.note_event_id].filter(Boolean).length, `events=${ev.rows[0].n}`);
  check('request correlates to a committed open task owned by the rep',
    tk.rows.length === 1 && tk.rows[0].owner_email === 'rep@staging.invalid' && tk.rows[0].status === 'open', JSON.stringify(tk.rows));
  await rep.page.screenshot({ path: `${OUT}/02-rep-after-save-390.png` });

  // ---- Lost response: server commits, client times out, reload keeps the draft, retry does not duplicate
  await rep.page.goto(`${BASE}/sales/leads?lead=${REP_LEAD}`);
  await rep.page.getByTestId('lead-drawer').waitFor();
  await answer(rep.page, `שיחה סינתטית שנייה ${RUN}`);
  let firstId = null;
  await rep.page.route(`**/api/sales/leads/${REP_LEAD}/activity`, async (route) => {
    firstId = route.request().postDataJSON().request_id;
    await route.fetch();            // reaches the server and commits
    await route.abort('timedout');  // the client never sees the answer
  }, { times: 1 });
  await rep.page.getByTestId('activity-save').click();
  await rep.page.getByTestId('outcome-error').waitFor();
  await rep.page.reload();
  await rep.page.getByTestId('lead-drawer').waitFor();
  await leaveAndReturn(rep.page);
  await rep.page.getByTestId('outcome-answered_progressing').click();
  const kept = await rep.page.getByTestId('activity-note').inputValue();
  check('draft survives a timeout and a reload', kept === `שיחה סינתטית שנייה ${RUN}`, kept);
  const [retry] = await Promise.all([
    rep.page.waitForResponse((r) => r.url().includes(`/api/sales/leads/${REP_LEAD}/activity`) && r.request().method() === 'POST'),
    rep.page.getByTestId('activity-save').click(),
  ]);
  const retryId = retry.request().postDataJSON().request_id;
  const dup = await db.query(`select count(*)::int n from sales_core.lead_event where lead_id=$1 and event_type='note' and payload->>'text' = $2`, [REP_LEAD, `שיחה סינתטית שנייה ${RUN}`]);
  const dupAny = await db.query(`select count(*)::int n from sales_core.lead_event where lead_id=$1 and payload::text like $2`, [REP_LEAD, `%שיחה סינתטית שנייה ${RUN}%`]);
  check('retry reuses the request id', retryId === firstId, `${firstId} / ${retryId}`);
  check('retry after a committed-but-lost response writes one fact', retry.status() === 200 && dupAny.rows[0].n === 1, `status=${retry.status()} rows=${dupAny.rows[0].n} note_rows=${dup.rows[0].n}`);

  // ---- Cross-owner denial
  const denied = await rep.page.request.get(`${BASE}/api/sales/leads/${MGR_LEAD}/events`);
  check("rep is denied the manager's lead timeline", denied.status() === 403, `status=${denied.status()}`);
  const list = await (await rep.page.request.get(`${BASE}/api/sales/leads`)).json();
  const ids = (list.rows ?? []).map((r) => r.id);
  const owners = await db.query(`select count(*)::int n from sales_core.lead where id = any($1::uuid[]) and assignee is distinct from 'rep@staging.invalid'`, [ids]);
  check("rep lead list holds only the rep's leads", ids.includes(REP_LEAD) && !ids.includes(MGR_LEAD) && !ids.includes(UNOWNED) && owners.rows[0].n === 0, `rows=${ids.length} foreign=${owners.rows[0].n}`);
  await rep.page.goto(`${BASE}/sales/leads?lead=${MGR_LEAD}`);
  await rep.page.getByTestId('lead-not-found').waitFor();
  check('rep deep link to a foreign lead shows the approved unavailable state', true);
  await rep.page.screenshot({ path: `${OUT}/03-rep-foreign-lead-390.png` });
  check('rep has no factory link (D11)', (await rep.page.getByTestId('sales-switch-factory').count()) === 0);
  // ---- D5 on staging: an order-line reply (same SQL as order_line_reply.ts) routes a reply task due now
  await db.query(`insert into sales_core.lead_event(lead_id,event_type,payload,actor)
    values($1,'note',jsonb_build_object('kind','repeat_contact','source','whatsapp_order_line','external_id',$2::text),'system:order-line')`,
    [REP_LEAD, `wamid.staging.${RUN}`]);
  const reply = await db.query(`select owner_email from sales_core.task where lead_id=$1 and kind='reply' and status='open'`, [REP_LEAD]);
  check('order-line reply routes one open reply task to the owner', reply.rows.length === 1 && reply.rows[0].owner_email === 'rep@staging.invalid', JSON.stringify(reply.rows));
  // ---- Today entry point: the rep's own task card
  await rep.page.goto(`${BASE}/sales/today`);
  const card = rep.page.getByTestId('task-card').first();
  await card.waitFor({ timeout: 10000 }).catch(async (e) => { await rep.page.screenshot({ path: '/tmp/claude-0/stage/debug-today.png', fullPage: true }); throw e; });
  await answer(rep.page, `שיחה סינתטית מהיום ${RUN}`, card.getByRole('link', { name: 'התקשר' }));
  const [today] = await Promise.all([
    rep.page.waitForResponse((r) => r.url().includes('/activity') && r.request().method() === 'POST'),
    rep.page.getByTestId('activity-save').click(),
  ]);
  const todayBody = today.request().postDataJSON();
  check('Today task card saves an activity with its source task', today.status() === 200 && Boolean(todayBody.source_task_id), `status=${today.status()}`);
  await rep.page.screenshot({ path: `${OUT}/05-rep-today-after-save.png` });
  await rep.ctx.close();

  // ---- Manager
  const mgr = await login(browser, 'manager@staging.invalid', `/sales/leads?lead=${REP_LEAD}`, { width: 1280, height: 900 });
  await mgr.page.getByTestId('lead-drawer').waitFor();
  const mgrEvents = await mgr.page.request.get(`${BASE}/api/sales/leads/${REP_LEAD}/events`);
  check("manager reads the rep's lead", mgrEvents.status() === 200);
  const unassigned = await (await mgr.page.request.get(`${BASE}/api/sales/tasks?scope=unassigned`)).json();
  check('manager queue holds the unowned lead task', (unassigned.rows ?? []).some((t) => t.lead_id === UNOWNED));
  // ---- Attention entry point: manager works the unowned lead
  await mgr.page.goto(`${BASE}/sales/attention`);
  const call = mgr.page.locator(`[data-testid^="attention-call-${UNOWNED}-"]`).first();
  await call.waitFor();
  await answer(mgr.page, `שיחה סינתטית מתשומת לב ${RUN}`, call);
  const [att] = await Promise.all([
    mgr.page.waitForResponse((r) => r.url().includes(`/api/sales/leads/${UNOWNED}/activity`) && r.request().method() === 'POST'),
    mgr.page.getByTestId('activity-save').click(),
  ]);
  const attRows = await db.query(`select count(*)::int n from sales_core.lead_event where lead_id=$1 and payload::text like $2`, [UNOWNED, `%שיחה סינתטית מתשומת לב ${RUN}%`]);
  check('Attention saves an activity that commits one fact', att.status() === 200 && attRows.rows[0].n === 1, `status=${att.status()} rows=${attRows.rows[0].n}`);
  await mgr.page.goto(`${BASE}/sales/today`);
  await mgr.page.waitForLoadState('networkidle');
  await mgr.page.screenshot({ path: `${OUT}/04-manager-today-1280.png` });
  check('manager keeps the factory link', (await mgr.page.getByTestId('sales-switch-factory').count()) === 1);
  await mgr.ctx.close();
} catch (e) {
  check('script completed', false, String(e).slice(0, 300));
} finally {
  await browser.close(); await db.end();
  const failed = results.filter((r) => !r.ok).length;
  console.log(`\nSUMMARY ${results.length - failed}/${results.length}`);
  process.exit(failed ? 1 : 0);
}
