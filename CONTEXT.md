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
_Avoid_: Ice Dream, אייס דרינק, calling LionWheel a distributor

**Held stock**:
GT's finished goods sitting in the Distributor's warehouse. They stay GT's until they are delivered to the customer.
_Avoid_: consignment, Icedream's stock

**Factory stock**:
GT's finished goods at the factory.
_Avoid_: our stock (Held stock is ours too), GT-MAIN

**Stock reset**:
A full physical count of every item, finished goods, raw materials and packaging, entered so the system matches the shelf. Each count replaces the item's starting point; no history is deleted.
_Avoid_: zeroing the stock, deleting the ledger

**Direct account**:
A customer GT keeps serving itself instead of through the Distributor: Eli Avrahami, Unimarket and Elita.
_Avoid_: key account, big three

**Order email**:
The email GT's system sends the Distributor the moment an order enters Shopify, carrying everything needed to key the order in by hand.
_Avoid_: order file, handoff

**Delivery report**:
The Distributor's morning report on the previous day: what it delivered, what it did not deliver and why, what it took back, and what it received from GT.
_Avoid_: daily report, POD

**Truck transfer**:
A truck of GT's finished goods from the factory to the Distributor's warehouse. It moves goods from Factory stock to Held stock; ownership does not change.
_Avoid_: shipment, sale

**Distributor fee**:
Icedream's charge for its service: a percentage of GT's revenue on the orders it handles.
_Avoid_: commission, margin

**Consolidated invoice**:
The invoice GT issues the Distributor for its orders: totals only, with no product lines. The product lines live in GT's Shopify.
_Avoid_: summary invoice, monthly invoice

### Planning

**Open order**:
An order taken and not yet delivered or cancelled. Today its LionWheel task tells: open while unassigned, assigned, active or in transfer. After the switch, an order sent to the Distributor stays open until the Delivery report closes it.
_Avoid_: order (alone), pending order

**Sales forecast**:
GT's expected sales per product per month, six months ahead, updated every two weeks. A run publishes itself unless a line moves past its limit; such a line reaches Tom as a Decision. It drives purchasing whenever there is no Production plan.
_Avoid_: forecast (alone, it is ambiguous next to the revenue forecast in the daily sales brief), demand plan

**Production plan**:
A plan to make specific products on a specific day. When one exists, purchasing follows it for that day instead of the Sales forecast. Usually there is none.
_Avoid_: schedule, production forecast

**Production report**:
The record of what was actually made, entered after the fact and within two working days.
_Avoid_: production plan, actuals

**Safety buffer**:
The extra raw material purchasing adds on top of the need, so a rushed or emergency production run never stalls for materials.
_Avoid_: safety stock (finished goods), padding

**Purchase recommendation**:
What the system proposes to buy, from whom, how much and by when. It is driven by the Production plan when one exists and by the Sales forecast otherwise, and it must be right to the unit.
_Avoid_: purchase draft, purchase suggestion

### Tom's attention

**Decision**:
An item that needs Tom's yes, no or number today, put to him with a proposed answer.
_Avoid_: exception (already used for stock and Shopify exceptions), alert, task

**Open end**:
Anything a session leaves for a person to finish later: an unposted receipt, an unanswered question, an unchecked result. An operational skill ends its session with none.
_Avoid_: follow-up, pending, TODO

**Morning message**:
The one message Tom gets each workday at 07:30, carrying only that day's Decisions.
_Avoid_: morning brief, daily report
