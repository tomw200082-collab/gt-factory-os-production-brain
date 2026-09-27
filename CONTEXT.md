# GT Everyday workspace

The repos, skills and scheduled runs Claude uses to operate GT Everyday, a small beverage factory in Israel.

## Language

### Workspace

**Brain**:
The one repo that holds everything Claude uses to run GT: governance, skills with their scripts, agents, knowledge and Routine prompts. Nothing deploys from it.
_Avoid_: AI brain, sales brain, Box 1, PRODUCTION

**Runtime repo**:
A repo whose code deploys and serves people: the backend, the portal and the brand site.
_Avoid_: canonical runtime, Box 2

**Account skill**:
A skill stored in the claude.ai account rather than in git.
_Avoid_: synced skill

**Sunset**:
A part of the system that stays running unchanged, with no fixes and no deletion, until the Distributor takes over its job; then it is deleted.
_Avoid_: frozen (reserved for feature flags held until Tom approves a flip)

### Operations

**Distributor**:
Icedream: the outside company that holds GT's finished goods in its warehouse, picks and delivers each order, invoices the customer and collects the money. GT still takes the orders.
_Avoid_: using "distributor" for Aviv or for LionWheel

**Direct account**:
A customer GT keeps serving itself instead of through the Distributor: Eli Avrahami, Unimarket and Elita.
_Avoid_: key account, big three

**Consolidated invoice**:
The invoice GT issues the Distributor for its orders: totals only, with no product lines. The product lines live in GT's Shopify.
_Avoid_: summary invoice, monthly invoice
