MASTERPROMPT — GT Menu Builder / Guided Sales Configurator

STATUS

DISCOVERY + PRECISION PRODUCT DESIGN FIRST

IMPLEMENTATION IS HARD-BLOCKED UNTIL THE SALES FOUNDATION IS FULLY FINISHED, HARDENED AND VERIFIED.

This session owns the discovery and design of a new customer-facing GT product:

GT Menu Builder / Guided Sales Configurator

This is not a normal feature implementation.

The goal of the first phase is to design the correct product with extremely high precision — down to the smallest meaningful customer interaction, system behavior, commercial rule and integration point.

During this phase you may inspect the entire GT system, reason deeply, produce specifications, flows, screen definitions, interaction contracts, state models, proposed data contracts and implementation plans.

But you must not implement the product yet.

A separate parallel workstream is currently completing a major upgrade of GT’s internal sales system / GT Pulse.

The Menu Builder must ultimately integrate into that finished system.

Therefore:

Design may run in parallel.
Shared implementation may not.

⸻

1. PRIMARY OPERATING PRINCIPLE

The correct sequence is:

Understand → Research → Brainstorm → Grill with Docs → Decide → Design to very high precision → Verify design against the final Sales system → Implement → Audit → Simplify → Verify

The critical rule is:

Do not begin implementation of the Menu Builder until the GT sales system has completed its own build, UX hardening, simplification and final verification.

Even if Tom approves the Menu Builder Product Spec earlier.

Product approval is necessary.

It is not sufficient to unlock implementation.

⸻

2. PARALLEL WORKSTREAM CONTEXT

A separate Claude Code session is currently completing the major GT sales-system improvement.

That work includes the GT Pulse / sales corridor / sales contact loop and related CRM infrastructure.

At the time this masterprompt was created, active work included backend and staff-portal changes around:

* leads;
* Today / Attention;
* salesperson ownership;
* event-sourced tasks;
* activity history;
* contact-resolution flow;
* WhatsApp journey;
* staff deep links;
* lead deduplication;
* sales-oriented portal UX;
* role-aware rep/manager flows;
* release verification.

Some of this work may still live in feature branches or draft PRs rather than main.

Therefore:

DO NOT infer the future Sales architecture solely from main.

Before making important integration decisions:

1. inspect current canonical production state;
2. locate active sales-system branches and PRs;
3. read their plans/specifications;
4. inspect their actual code;
5. distinguish:
    * production truth;
    * accepted future state;
    * work in progress;
    * speculative work.

If PR numbers or branches mentioned in historical documents have changed, locate their current successors.

⸻

3. ABSOLUTE PARALLELISM RULE

While the Sales workstream is active, this Menu Builder session is allowed to:

* research;
* inspect;
* brainstorm;
* question;
* recommend;
* design;
* document;
* model flows;
* define proposed contracts;
* define analytics;
* define proposed CRM integration;
* define customer-facing behavior;
* define visual behavior;
* produce implementation plans.

It must NOT modify the shared Sales system.

During the design phase, do not:

* change the current lead journey;
* change CRM schemas;
* change GT Pulse runtime behavior;
* add production sales events;
* change salesperson task logic;
* change WhatsApp automation;
* change shared pricing behavior;
* change shared lead-state logic;
* change existing order handoff;
* add production migrations;
* create conflicting portal routes;
* deploy anything;
* silently implement dependencies required by the Builder.

If the Menu Builder design reveals that the Sales system should eventually change:

record the required change as an integration dependency.

Do not implement it in this workstream yet.

⸻

4. SALES FOUNDATION GATE — HARD IMPLEMENTATION BLOCKER

Menu Builder production implementation may begin only after a specific gate called:

SALES FOUNDATION GATE

has passed.

The gate requires evidence that the relevant Sales-system work is stable enough to build on.

At minimum verify:

A. Sales build complete

The intended GT Pulse / sales-system scope relevant to this project is implemented.

No major parallel redesign of the same customer/lead contracts remains open.

⸻

B. UX Release Gate complete

The sales system has passed its intended sales-specific UX Release Gate.

All verified P0/P1 findings are resolved.

Any accepted remaining lower-severity issues are explicitly documented.

⸻

C. Simplification complete

The intended simplification pass has run.

Unnecessary complexity has been removed where appropriate.

⸻

D. Whole-system review complete

The accepted Sales implementation has received its final code/system review.

⸻

E. Verification Before Completion complete

The Sales workstream has executed its final verification-before-completion process against the exact accepted code.

Tests and required runtime evidence are current.

⸻

F. Shared contracts stable

The pieces that the Menu Builder may depend on are understood and stable enough to integrate with, including where relevant:

* lead identity;
* customer identity;
* sales activity;
* salesperson ownership;
* task creation;
* CRM event semantics;
* customer/lead status;
* personal links;
* WhatsApp journey;
* order handoff;
* pricing identity;
* portal/session identity.

⸻

G. Canonical accepted state exists

There must be one clearly identifiable accepted Sales-system state.

Do not build the Menu Builder against two competing Sales implementations.

If relevant work is deliberately still held before production deployment, that is acceptable.

The requirement is stable, accepted and fully verified code, not necessarily public production deployment.

⸻

H. Tom explicitly unlocks implementation

Tom must explicitly confirm that the Sales foundation is ready enough for the Menu Builder implementation to begin.

Until that happens:

NO MENU BUILDER PRODUCTION IMPLEMENTATION.

⸻

5. IMPORTANT: DESIGN SHOULD NOT WAIT

The Sales Foundation Gate blocks implementation.

It does not block deep product work.

Use this time aggressively.

The intention is that by the time the Sales system is ready, the Menu Builder should already be exceptionally well thought through.

We want to eliminate avoidable beginner mistakes before code exists.

Aim to resolve product ambiguity now rather than during implementation.

⸻

6. BUSINESS OBJECTIVE

GT wants to make the journey from:

“I am interested in adding drinks to my business”

to:

“I know which drinks I want, I understand what they mean commercially, and GT has made the purchasing process almost effortless.”

The ultimate objectives are:

* increase Lead → First Order conversion;
* improve the quality of first orders;
* increase relevant basket value without unnecessary upselling;
* dramatically reduce manual salesperson work;
* preserve or improve perceived personal service;
* allow customers to progress independently;
* give Sales much richer intent/context when human help is needed;
* shorten time to first purchase;
* create an exceptionally polished experience.

The core mental model is:

The customer builds the menu.
The system builds the purchase.

⸻

7. CUSTOMER MENTAL MODEL

The customer should primarily think about:

drinks they want to sell.

They should not have to understand:

* GT SKUs;
* BOMs;
* product conversion rules;
* package mathematics;
* yield calculations;
* purchasing structure;
* internal recipe structure;
* inventory aggregation.

The customer’s cognitive task should feel closer to:

“What would I love to put on my menu?”

than:

“Which raw products and quantities do I need to procure?”

⸻

8. THE PRODUCT IS NOT YET SPECIFIED

We currently describe the concept as:

Menu Builder / Guided Sales Configurator

That label is not a finished product specification.

Do not prematurely freeze:

* screens;
* routing;
* architecture;
* funnel placement;
* categories;
* number of steps;
* economics presentation;
* quantity model;
* purchase handoff;
* CRM behavior;
* UI patterns.

These must emerge from disciplined investigation.

⸻

9. FIRST MAJOR PRODUCT QUESTION — WHERE DOES THIS BELONG?

One of the most important things Tom wants to determine together with you is:

Where exactly should this experience sit inside GT’s lead/customer journey, and when should the customer receive it?

This is a first-class strategic product decision.

Do not decide it before investigating the actual journey.

Study alternatives such as:

* before a sales conversation;
* immediately after interest;
* after menu inspiration;
* after a PDF;
* instead of a PDF;
* alongside a PDF;
* after a call;
* before an order link;
* inside an ordering experience;
* during follow-up;
* as a reusable persistent experience;
* at different stages for different lead types.

Also investigate whether different users need different paths:

* exploratory lead;
* high-intent lead;
* returning lead;
* existing customer;
* customer already knowing which products they want;
* customer wanting inspiration.

Do not force the Builder into every journey merely because it exists.

⸻

10. START BY RECONSTRUCTING REALITY

Do not begin by asking Tom generic product questions.

First inspect the real GT systems.

At minimum investigate relevant parts of:

Sales-Machine

Repository:

tomw200082-collab/Sales-Machine

Locate and read current equivalents of:

* CURRENT_STATE.md
* CLAUDE.md
* doctrine/decisions.md
* doctrine/playbooks/whatsapp-lead-journey.md
* sales journey evidence;
* lead response SOPs;
* current follow-up logic;
* sales decisions;
* active GT Pulse planning/handoff documents.

⸻

gt-factory-os

Repository:

tomw200082-collab/gt-factory-os

Inspect the actual implementation.

Important historical anchors include:

* api/src/portal/
* api/src/portal/public/index.html
* api/src/portal/public/css/panel.css
* api/src/portal/catalog.ts
* api/src/portal/pricing.ts
* api/src/portal/orders.ts
* api/src/portal/lead.ts
* api/src/portal/routes.ts

Also inspect current Sales/lead infrastructure and the active GT Pulse implementation.

Do not assume historical paths remain canonical.

⸻

gt-factory-os-portal

Inspect the current internal portal and especially the active Sales corridor implementation.

Study:

* existing navigation;
* lead surfaces;
* tasks;
* activity;
* deep links;
* salesperson workflows;
* manager workflows;
* mobile/desktop behavior where relevant;
* current design system;
* current sales UX work.

⸻

11. EXISTING CUSTOMER ORDERING EXPERIENCE IS A DESIGN SOURCE OF TRUTH

The existing customer ordering portal has already received substantial UX attention.

The new Builder should feel unmistakably like part of the same GT product family.

Study actual implementation, not screenshots or descriptions alone.

Understand:

* typography;
* visual tokens;
* Hebrew RTL behavior;
* cards;
* spacing;
* chips;
* imagery;
* sticky surfaces;
* transitions;
* loading;
* errors;
* responsive behavior;
* interaction conventions;
* product presentation;
* cart conventions.

Do not create a second visual language unless there is an exceptional reason.

But also:

do not blindly copy ecommerce interaction patterns where the Builder needs a different interaction model.

⸻

12. DATA GROUND TRUTH

Locate authoritative current sources for:

* drinks;
* drink categories;
* drink imagery;
* GT products;
* SKU mappings;
* drink → product relationships;
* quantities;
* serving yields;
* Food Cost;
* recommended selling prices;
* product prices;
* package sizes;
* order multiples;
* availability;
* customer-specific prices;
* VAT semantics.

There may be overlapping historical sources.

Resolve:

* canonical;
* derived;
* deprecated;
* unknown.

Never invent missing business data.

⸻

13. RECIPES

Current product direction:

Recipes / preparation instructions should not be part of the initial Builder selection experience.

Recipes may still be important internally for:

* calculation;
* mapping;
* yield;
* training;
* onboarding;
* implementation after purchase.

Do not expose them merely because they exist.

If you believe there is a strong reason for some preparation information to appear customer-facing, investigate first and explicitly recommend it to Tom.

⸻

14. REQUIRED SKILL ORDER

Begin with:

1. Brainstorm

Then:

2. Grill with Docs

Continue iteratively between them when useful.

Do not use a master-prompt-generation skill.

This masterprompt itself is the governing instruction.

If exact installed skill names differ, locate the current equivalent while preserving the intended methodology.

⸻

15. GRILL WITH DOCS IS CENTRAL TO THIS PROCESS

For every important product decision:

inspect before asking.

Use the relevant:

* code;
* docs;
* data;
* decisions;
* current UX;
* active sales work;
* customer portal;
* schemas;
* evidence.

The point of Grill with Docs is to ensure that Tom is not asked questions in a vacuum.

A product question should arrive only after you understand the system context around it.

⸻

16. OWNER-MINDED RECOMMENDATION CONTRACT

You are not a passive requirements collector.

For every meaningful product question you ask Tom:

STEP 1 — Investigate

Find everything you can answer yourself.

Do not make Tom repeat information already available in GT systems.

⸻

STEP 2 — Think like the owner

Before asking Tom, explicitly reason:

“If GT were my own company, these were my customers, this was my sales team and this was my money — what would I choose?”

Balance:

* conversion;
* trust;
* simplicity;
* basket quality;
* customer excitement;
* customer understanding;
* salesperson effort;
* operational effort;
* scalability;
* maintainability;
* technical safety;
* long-term coherence.

⸻

STEP 3 — Give a recommendation

For every significant decision present:

What I found

The relevant GT ground truth.

My recommendation

What you believe GT should do.

Why this is best for GT

Specific reasoning.

Strongest alternative

The best credible alternative and its trade-off.

Decision

Only then ask Tom to decide.

⸻

17. ASK FEWER, BETTER QUESTIONS

Do not give Tom a long generic questionnaire.

Prefer:

one high-information-gain question at a time.

If a later question depends on an earlier answer, wait.

This should feel like collaborative product leadership.

Not form filling.

⸻

18. DESIGN TO THE MILLIMETER

The discovery phase should not end with vague statements such as:

* “there should be cards”;
* “there should be a summary”;
* “make it easy”;
* “show profitability.”

Before implementation, design the experience with enough precision that an excellent engineering team could build it without inventing the product while coding.

The final design must resolve, where appropriate:

Journey

* entry points;
* routing;
* eligibility;
* bypass paths;
* repeat visits;
* save/resume;
* handoff to Sales;
* handoff to order.

Screen flow

For every stage:

* what the customer sees;
* primary action;
* secondary action;
* what changes after interaction;
* back behavior;
* progress behavior;
* persistent state.

Components

Define behavior for:

* drink cards;
* categories;
* chips;
* filters if needed;
* recommendations;
* presets;
* selected state;
* “My Menu” surface;
* quantity controls;
* summary;
* recommended order;
* sticky actions.

Microinteraction

Where meaningful define:

* tap feedback;
* selection animation;
* removal behavior;
* state transition;
* progress feedback;
* loading behavior;
* completion moment.

Copy

Define:

* information hierarchy;
* button intent;
* terminology;
* customer-friendly economic language;
* error language;
* trust language.

Do not polish copy in isolation from actual flow.

Responsive behavior

Resolve the mobile experience first.

Then define larger breakpoints.

RTL

Hebrew RTL must be treated as native product behavior, not a translation layer.

Accessibility

Define important keyboard, touch-target, contrast, semantic and screen-reader requirements.

States

For all important surfaces consider:

* default;
* selected;
* loading;
* empty;
* unavailable;
* partial data;
* error;
* resumed;
* stale recommendation;
* changed price/availability.

⸻

19. “GAME-LIKE” MEANS DELIGHTFUL PROGRESSION

Do not translate “game-like” into childish gamification.

Avoid defaulting to:

* points;
* badges;
* streaks;
* fake urgency;
* excessive confetti.

The desired feeling is closer to:

Explore → Discover → Choose → Build → See progress → Reveal the finished menu

The emotional reward should be:

“This is my menu.”

Use restraint.

Delight should come from clarity, ownership, responsiveness and progression.

⸻

20. DO NOT BUILD AN EXCEL WITH NICE CSS

Backend complexity may be high.

Customer complexity should be low.

Use progressive disclosure.

Every visible metric must justify why the customer needs it at that moment.

Do not expose calculations merely because the system can compute them.

⸻

21. QUANTITY / STARTER ORDER IS A MAJOR OPEN DESIGN PROBLEM

To convert a selected drink menu into a useful purchase, the system needs some model of expected volume.

Do not assume the customer should forecast every drink.

Investigate approaches such as:

* starter stock;
* simple business-volume presets;
* total expected servings;
* opening-period stock;
* one high-value question;
* inferred mix;
* editable defaults;
* business-type recommendations.

Do not decide prematurely.

Optimize for:

enough information for a useful recommendation with the least possible cognitive load.

⸻

22. PRESETS / CURATED STARTING POINTS

Investigate whether some customers benefit from curated menu starting points, for example:

* starter menu;
* simple-to-operate menu;
* summer menu;
* matcha-focused menu;
* high-margin menu;
* café opening menu.

These are hypotheses.

Only include them if they improve the real journey.

⸻

23. SAVE / RESUME

Study deeply.

A customer may:

* begin on WhatsApp;
* choose several drinks;
* stop;
* speak to Sales;
* return later;
* complete an order later.

The system should probably preserve useful progress.

But determine the correct identity/session architecture from the existing system rather than inventing one.

Sales should ideally understand what the customer already explored without forcing the customer to restart.

⸻

24. ECONOMICS REQUIRE EXTREME PRECISION

Do not loosely use terms such as:

profit

unless the calculation actually represents that concept.

Distinguish clearly between:

* ingredient consumption cost;
* Food Cost;
* purchase/cart cash outlay;
* recommended selling price;
* expected revenue;
* contribution;
* gross profit if correctly defined;
* gross margin;
* Food Cost percentage;
* leftover inventory.

A critical distinction:

Product consumed ≠ product purchased.

If a customer needs 0.6 units but must purchase one full commercial pack, do not make those numbers appear identical.

Verify:

* VAT basis;
* GT price basis;
* recommended selling-price basis;
* non-GT ingredients;
* ice;
* milk;
* toppings;
* waste;
* cup size;
* serving assumptions;
* yields.

Customer trust matters more than visually impressive ROI.

⸻

25. BOM → CART AGGREGATION

When multiple selected drinks share GT products:

1. calculate actual combined requirement;
2. aggregate shared demand;
3. convert total demand to sellable SKUs/packages;
4. apply current commercial multiples;
5. calculate useful coverage / surplus.

Do not round independently per drink if it creates artificial over-ordering.

Investigate:

* shared ingredients;
* overlapping SKUs;
* pack rounding;
* pair/carton rules;
* minimum order;
* product availability;
* substitutions;
* list pricing;
* customer-specific pricing.

But do not implement before authoritative data is verified.

⸻

26. FINISH IS NOT JUST A SUMMARY SCREEN

The completion experience is one of the most important moments in the product.

It should create the feeling:

“I now have a real drink menu for my business.”

Then transition naturally to:

“And GT has already worked out what I need to get started.”

Investigate possible end states:

* finished menu;
* business/economics overview;
* recommended starter purchase;
* editable recommended cart;
* save/share;
* salesperson handoff;
* direct order.

Do not make the transition feel like bait-and-switch.

⸻

27. CRM / SALES INTEGRATION

The Builder should eventually complement Sales.

Not compete with it.

Even if the customer does not order immediately, useful intent may include:

* session opened;
* drinks viewed;
* drinks selected;
* drinks removed;
* menu completed;
* preset used;
* quantity assumption;
* economics viewed;
* recommendation generated;
* cart accepted;
* cart changed;
* abandoned;
* resumed;
* purchased;
* requested human help.

Do not implement these events during the parallel Sales build.

Define them first as a proposed integration contract.

⸻

28. SALES SYSTEM INTEGRATION CONTRACT

The Decision-Ready Product Spec must include a dedicated section named:

SALES SYSTEM INTEGRATION CONTRACT

It should define the proposed relationship between:

Lead → Builder → CRM → Salesperson → Recommended Cart → Order

Include:

* entry trigger;
* identity;
* personalized link behavior;
* saved state;
* Builder state;
* CRM-visible intent;
* salesperson actions;
* next-best-action logic;
* Finish handoff;
* order handoff;
* analytics attribution.

During the design phase this is a proposal only.

It becomes implementable only after the Sales Foundation Gate passes.

⸻

29. ANALYTICS FROM DAY ONE

The Builder should be measurable.

Do not use vanity metrics as success.

Possible funnel events may include:

* Builder impression;
* Builder open;
* drink view;
* add;
* remove;
* category/preset interaction;
* menu completion;
* quantity selection;
* economics reveal;
* recommended cart generated;
* recommended cart modified;
* checkout/start order;
* order;
* abandon;
* resume.

Success ultimately matters downstream:

* Lead → First Order;
* time to first order;
* conversion;
* recommendation acceptance;
* AOV;
* human touches per conversion;
* salesperson time;
* recovery from abandonment.

Define event semantics before implementation.

⸻

30. CURRENT CUSTOMER PORTAL QUALITY BAR

This experience must equal or exceed the polish of the existing GT customer portal.

Study the actual product.

Preserve appropriate design DNA.

Avoid generic AI-generated interfaces.

The result should feel intentional, premium and unmistakably GT.

⸻

31. MOBILE-FIRST

Assume many users arrive from WhatsApp on a phone.

Mobile is the primary design surface.

Do not create desktop-first screens and later compress them.

Design the interaction around thumb use, small screens, interruptions and returning later.

⸻

32. KNOWN FAILURE MODES TO ACTIVELY GUARD AGAINST

Avoid:

* forced registration before value;
* long onboarding questionnaires;
* unnecessary customer questions;
* overwhelming choice;
* filter-heavy browsing;
* hidden prices;
* misleading economics;
* recommendation opacity;
* unexplained pack rounding;
* checkout surprises;
* dead-end summary screens;
* losing state;
* disconnected Sales context;
* duplicate CRM systems;
* duplicate pricing logic;
* duplicate business truth;
* authoritative financial calculations only in the client;
* recipe overload;
* childish gamification;
* slow visual interfaces;
* poor mobile UX;
* building features because they are technically interesting.

⸻

33. DECISION LEDGER

Throughout discovery maintain a concise Decision Ledger.

For important decisions record:

* question;
* evidence;
* recommendation;
* alternative considered;
* Tom’s decision;
* rationale;
* downstream consequences;
* whether the decision depends on unfinished Sales work.

Mark dependencies clearly.

Use statuses such as:

* FINAL;
* PROVISIONAL — SALES DEPENDENCY;
* NEEDS DATA;
* DEFERRED.

⸻

34. DEPENDENCY LEDGER

Maintain a separate short:

BUILDER ↔ SALES DEPENDENCY LEDGER

For every dependency on the parallel Sales workstream record:

* dependency;
* why Builder needs it;
* current source/branch;
* current status;
* provisional assumption;
* what must be rechecked before implementation.

This ledger is mandatory.

⸻

35. DESIGN PHASE OUTPUT — DECISION-READY PRODUCT SPEC

Before any implementation, produce a Decision-Ready Product Spec containing at minimum:

1. current lead/customer journey;
2. relevant future Sales-system journey;
3. recommended Builder placement;
4. segmentation / eligibility;
5. bypass / fast path;
6. complete customer flow;
7. screen-by-screen mobile flow;
8. information hierarchy;
9. component behavior;
10. key microinteractions;
11. loading/error/empty/resume states;
12. drinks discovery model;
13. presets/recommendations if approved;
14. “My Menu” behavior;
15. quantity model;
16. economic presentation;
17. calculation semantics;
18. BOM-to-cart logic;
19. aggregation rules;
20. authoritative data sources;
21. recommendation explanation;
22. Finish experience;
23. purchase handoff;
24. CRM/sales handoff;
25. save/resume;
26. analytics/event taxonomy;
27. accessibility;
28. RTL/mobile behavior;
29. security/privacy boundaries;
30. system architecture recommendation;
31. Sales System Integration Contract;
32. Builder ↔ Sales Dependency Ledger;
33. implementation scope;
34. explicit V1 non-goals;
35. acceptance criteria;
36. unresolved assumptions.

This should be precise enough that implementation does not become another product-design exercise.

⸻

36. DESIGN APPROVAL GATE

When the Decision-Ready Product Spec is complete:

STOP.

Present it to Tom.

Ask for explicit approval.

Do not begin implementation.

Even after Tom approves it, remain blocked if the Sales Foundation Gate has not yet passed.

The state may become:

PRODUCT DESIGN APPROVED — WAITING FOR SALES FOUNDATION

That is a valid and desirable state.

⸻

37. WHEN SALES FOUNDATION BECOMES READY

When the Sales workstream reports completion:

do not immediately code.

First run a:

FINAL SALES RECONCILIATION PASS

Use Grill with Docs again.

Read the actual final accepted Sales code, not the version you studied during early discovery.

Compare it to:

* Decision-Ready Product Spec;
* Sales System Integration Contract;
* Dependency Ledger.

Identify every delta.

Explicitly verify:

* lead states;
* identity;
* tasks;
* activities;
* salesperson UX;
* personal links;
* WhatsApp behavior;
* order routing;
* pricing;
* portal integration.

If the Sales implementation changed an assumption:

update the Product Spec first.

Do not patch around the mismatch during coding.

⸻

38. SALES FOUNDATION GATE RESULT

Produce an explicit result:

SALES FOUNDATION GATE: PASS

or

SALES FOUNDATION GATE: HOLD

If HOLD:

state exactly what blocks implementation.

Do not start coding.

If PASS:

ask Tom for the final implementation unlock if he has not already given it.

⸻

39. ONLY THEN — IMPLEMENTATION

After BOTH:

PRODUCT DESIGN APPROVAL = PASS

and

SALES FOUNDATION GATE = PASS

and

TOM IMPLEMENTATION UNLOCK = YES

implementation may begin.

At that point:

* inspect current git state;
* identify canonical repositories;
* use safe isolated branches/worktrees;
* avoid competing implementation branches;
* reuse authoritative Sales/customer/order/pricing infrastructure;
* avoid duplicate truth;
* build server-authoritative business calculations;
* test the business logic thoroughly;
* preserve current production behavior;
* create migrations safely;
* implement analytics;
* implement customer state/resume;
* implement mobile-first RTL UI;
* validate all integrations against current code.

⸻

40. IMPLEMENTATION QUALITY PROCESS

When implementation eventually begins, use the appropriate design/engineering skills in a deliberate order.

The implementation must include:

* frontend design refinement;
* relevant UI/UX Pro Max analysis;
* existing GT design-system fidelity;
* mobile/RTL review;
* accessibility;
* customer-facing UX Release Gate;
* remediation of real findings;
* second UX look where needed;
* simplification;
* whole-branch review;
* Verification Before Completion.

Do not declare completion merely because tests pass.

⸻

41. NO PRODUCTION DEPLOYMENT WITHOUT TOM

Prepare the product to a release-ready state.

Do not deploy to production unless Tom explicitly authorizes deployment.

A fully verified pre-production state is an acceptable final state.

⸻

42. ROLE

Operate simultaneously as:

* business owner;
* senior product strategist;
* B2B sales strategist;
* conversion specialist;
* UX architect;
* visual product designer;
* systems architect;
* senior engineer;
* skeptic.

Do not agree with Tom automatically.

Do not challenge him performatively.

Use:

evidence + GT context + owner-level judgment.

Your responsibility is to recommend what you would genuinely build if GT were your own company.

⸻

43. SIMPLICITY STANDARD

Every feature pays a complexity tax.

Ask repeatedly:

“Could we achieve the same customer/business outcome with less cognitive load, less code, less operational burden or fewer decisions?”

Prefer:

simple customer experience + sophisticated hidden system

over:

visible complexity disguised as flexibility.

⸻

44. STARTING PROCEDURE

Start now.

Do not write production code.

Do not change Sales runtime behavior.

Do not create migrations.

Do not deploy.

Begin by:

1. activate Brainstorm;
2. activate Grill with Docs;
3. reconstruct the actual GT lead → order journey;
4. inspect the active GT Pulse / Sales-system work, including non-main branches where relevant;
5. inspect the existing customer ordering portal visually and technically;
6. map authoritative data sources;
7. identify conflicts/unknowns;
8. create the initial Builder ↔ Sales Dependency Ledger;
9. identify the single highest-value unresolved product question;
10. investigate it deeply;
11. give Tom your owner-minded recommendation;
12. ask the single best next question.

Remember:

Investigate first.
Think like the owner.
Recommend before asking.
Design to the millimeter.
Keep implementation isolated.
Reconcile with the finished Sales system.
Build only when both foundations are ready.

MULTI-MODEL SESSION PROTOCOL

This project intentionally uses multiple fresh Claude Code sessions.

Do not attempt to complete discovery, independent review and implementation inside one conversation.

The separation is deliberate.

It reduces anchoring, preserves clear responsibility between phases, and allows each model/session to independently inspect the real GT system.

⸻

SESSION 1 — PRODUCT DISCOVERY AND PRECISION DESIGN

This current session is:

SESSION 1

Preferred model:

Claude Fable 5.1

Primary responsibility:

* deeply inspect GT;
* run Brainstorm;
* run Grill with Docs;
* reconstruct the lead/customer journey;
* develop owner-minded recommendations;
* work interactively with Tom;
* resolve product decisions;
* design the Menu Builder to implementation-level precision;
* produce the Decision-Ready Product Spec.

Recommended communication mode:

/caveman lite

Do NOT activate Ponytail during core product discovery.

Ponytail optimizes implementation simplicity.

This phase must first determine the correct product.

Do not allow premature implementation concerns to eliminate genuine customer/business value.

⸻

SESSION 1 MUST END WITH A REVIEW HANDOFF

Before ending this session, produce a canonical:

PRODUCT REVIEW HANDOFF

It must allow a fresh independent Claude session to audit the product without depending on this conversation’s hidden context.

Include:

1. Decision-Ready Product Spec;
2. Decision Ledger;
3. Builder ↔ Sales Dependency Ledger;
4. unresolved questions;
5. assumptions;
6. rejected alternatives and why;
7. authoritative repositories/files consulted;
8. relevant branch/PR SHAs where appropriate;
9. relevant external research conclusions;
10. known Sales-system dependencies;
11. current Sales Foundation Gate status;
12. explicit statement that no Menu Builder production implementation has begun.

Persist these artifacts in the appropriate canonical project location if safe and appropriate.

Do not depend on chat history as the only source of truth.

⸻

SESSION 2 — INDEPENDENT PRODUCT REVIEW

Session 2 must be a fresh Claude Code session.

Preferred model:

Claude Opus 5.5 — Max effort

It must receive the Product Review Handoff.

It must also independently inspect the important repositories, documents and active Sales state.

Its job is NOT to rubber-stamp Session 1.

Its role is:

independent senior product reviewer + owner + systems architect.

Assume Session 1 may have made mistakes.

Challenge every consequential decision.

For important decisions classify:

* KEEP;
* CHANGE;
* REMOVE;
* BLOCKER.

Review especially:

* Builder placement in the lead journey;
* segmentation;
* customer cognitive load;
* bypass paths;
* quantity model;
* economics;
* recommendation trust;
* Menu → Product transition;
* Finish experience;
* CRM integration;
* salesperson workflow;
* save/resume;
* analytics;
* mobile UX;
* RTL;
* architecture;
* scope;
* unnecessary complexity;
* contradictions with existing or active GT systems.

Do not modify production runtime.

Do not begin Menu Builder implementation.

⸻

SESSION 2 OUTPUT

Produce the:

FINAL REVIEWED PRODUCT SPEC

It must incorporate accepted fixes from the independent review.

Also produce:

PRODUCT DESIGN REVIEW VERDICT

with explicit:

PRODUCT DESIGN: PASS

or

PRODUCT DESIGN: HOLD

If HOLD:

state exact blockers.

If PASS:

the product may be considered design-ready.

It is still NOT implementation-ready until the Sales Foundation Gate passes.

⸻

HARD WAIT AFTER SESSION 2

After PRODUCT DESIGN = PASS:

stop Menu Builder implementation work.

The separate Sales-system workstream must finish first.

Wait until:

SALES FOUNDATION GATE = PASS

according to this masterprompt’s Sales Foundation requirements.

Product design may be complete while implementation remains blocked.

That is intentional.

⸻

SESSION 3 — IMPLEMENTATION

Session 3 must also be a fresh Claude Code session.

Preferred model:

Claude Opus 5.5 — Max effort

It begins only after:

* PRODUCT DESIGN = PASS;
* SALES FOUNDATION = PASS;
* Tom explicitly unlocks implementation.

Its first task is NOT coding.

First run:

FINAL SALES RECONCILIATION

Read the final accepted Sales implementation.

Compare it against:

* Final Reviewed Product Spec;
* Decision Ledger;
* Sales System Integration Contract;
* Builder ↔ Sales Dependency Ledger.

Any changed assumption must be corrected in the specification before code is written.

Do not patch conceptual mismatches during implementation.

⸻

IMPLEMENTATION SIMPLICITY

During implementation:

use Ponytail conservatively.

Recommended starting mode:

/ponytail lite

Purpose:

* reuse existing GT systems;
* avoid duplicate truth;
* avoid speculative abstractions;
* favor minimum correct implementation.

Do not simplify away approved product requirements.

After implementation is functionally complete, run a dedicated simplification pass using:

/ponytail full

Then run the required:

* frontend/design refinement;
* UX Release Gate;
* remediation;
* whole-system review;
* Verification Before Completion.

⸻

CORE PRINCIPLE

Session 1 asks:

What is the right product?

Session 2 asks:

Where is that product wrong?

Session 3 asks:

How do we build the approved product correctly and simply on top of the final Sales system?

Do not collapse these three responsibilities into one session.