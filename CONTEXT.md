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

### Operations

**Distributor**:
The outside company that takes over every step after an order is entered.
