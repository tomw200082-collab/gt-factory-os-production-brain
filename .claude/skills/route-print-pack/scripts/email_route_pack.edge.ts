// Supabase Edge Function: email_route_pack  (deployed to project rvadsozabmxkkrktwgnv)
// Relay that emails the route-print-pack PDF via Resend. The build sandbox cannot
// reach api.resend.com (Cloudflare 1010); Supabase's network can. Invoked by
// scripts/send_email.py with the service-role bearer.
//
// Deploy: Supabase MCP deploy_edge_function (verify_jwt=true).
// production@ delivery needs gteveryday.com verified in Resend + ALERT_EMAIL_FROM
// set to a @gteveryday.com sender.
import "jsr:@supabase/functions-js/edge-runtime.d.ts";

function json(o: unknown, s: number) {
  return new Response(JSON.stringify(o), { status: s, headers: { "content-type": "application/json" } });
}

Deno.serve(async (req: Request) => {
  if (req.method !== "POST") return json({ error: "method_not_allowed" }, 405);
  const body = await req.json().catch(() => null) as any;
  if (!body || !body.pdf_base64) return json({ error: "pdf_base64 required" }, 400);
  const key = Deno.env.get("RESEND_API_KEY");
  if (!key) return json({ error: "RESEND_API_KEY unset" }, 500);
  const from = body.from ?? Deno.env.get("ALERT_EMAIL_FROM") ?? "onboarding@resend.dev";
  const to = body.to ?? "production@gteveryday.com";
  const resp = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      from: `GT Factory OS <${from}>`,
      to: [to],
      subject: body.subject ?? "מסלול הפצה",
      text: body.text ?? "",
      attachments: [{ filename: body.filename ?? "route.pdf", content: body.pdf_base64 }],
    }),
  });
  const rb = await resp.json().catch(() => null);
  return json({ ok: resp.status >= 200 && resp.status < 300, http_status: resp.status, resend: rb }, 200);
});
