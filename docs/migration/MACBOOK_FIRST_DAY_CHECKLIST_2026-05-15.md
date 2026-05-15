# MacBook First Day — GT Factory OS Setup Checklist

> **For Tom.** Plain-language steps to get GT Factory OS running on the new MacBook.
> Companion technical reference: `MAC_REBUILD_READINESS_2026-05-15.md`.
> Take it one step at a time. Nothing here is dangerous. If a step fails, stop and ask Claude Code — don't guess.

---

## Before you start — on the OLD Windows machine

Do this first, while Windows still works:

- [ ] Copy these three secret files somewhere safe (password manager, or a USB stick / encrypted drive). GitHub does **not** have them, so this is the one thing you must move yourself:
  - `C:/Users/tomw2/Projects/gt-factory-os/.env`
  - `C:/Users/tomw2/Projects/window2-portal-sandbox/.env.local`
  - `C:/Users/tomw2/Projects/gt-lionwheel-daily-route-agent/.env` *(this one may not exist — that's fine, skip it if so)*
- [ ] (Optional) If you want the exact 122 supplier-invoice PDFs, copy the folder `C:/Users/tomw2/Projects/gt-factory-os/scripts/gi_pdfs/`. If you skip this, they can be re-downloaded later — no real loss.

That's it for Windows. Everything else is safely on GitHub.

---

## Step 1 — Install the basic tools

Open the **Terminal** app on the Mac. Paste each line, press Enter, wait for it to finish.

- [ ] Install Homebrew (the Mac software installer):
  ```
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  ```
- [ ] Install the development tools:
  ```
  brew install git node python postgresql@16 gh
  ```
- [ ] Install VS Code (the editor):
  ```
  brew install --cask visual-studio-code
  ```
- [ ] Install **Claude Code** — follow Anthropic's install instructions for Claude Code.
- [ ] Connect Git to GitHub:
  ```
  gh auth login
  ```
  Choose GitHub.com, HTTPS, and log in with your browser when asked.

---

## Step 2 — Make a projects folder and download the four repositories

- [ ] Create a home for the projects:
  ```
  mkdir -p ~/Projects && cd ~/Projects
  ```
- [ ] Download each repository (run all four):
  ```
  git clone https://github.com/tomw200082-collab/gt-factory-os-production-brain.git
  git clone https://github.com/tomw200082-collab/gt-factory-os.git
  git clone https://github.com/tomw200082-collab/gt-factory-os-portal.git
  git clone https://github.com/tomw200082-collab/gt-lionwheel-daily-route-agent.git
  ```
- [ ] Set the brain repo to its working branch (this one matters — the default branch is **not** the right one):
  ```
  cd ~/Projects/gt-factory-os-production-brain
  git checkout planning-masterplan-2026-05-08
  cd ~/Projects
  ```
  The other three repos are fine on their default branch — leave them.

---

## Step 3 — Put the secret files back

Copy the three `.env` files you saved from Windows into their new homes:

- [ ] `gt-factory-os/.env`  → into `~/Projects/gt-factory-os/`
- [ ] `gt-factory-os-portal/.env.local` → into `~/Projects/gt-factory-os-portal/`
- [ ] `gt-lionwheel-daily-route-agent/.env` → into `~/Projects/gt-lionwheel-daily-route-agent/` *(only if it existed)*

If you ever need the exact list of what each file should contain, it is in §6 of `MAC_REBUILD_READINESS_2026-05-15.md`.

---

## Step 4 — Install each project's dependencies

- [ ] Backend:
  ```
  cd ~/Projects/gt-factory-os && npm install
  cd ~/Projects/gt-factory-os/api && npm install
  ```
- [ ] Portal:
  ```
  cd ~/Projects/gt-factory-os-portal && npm install
  ```
- [ ] LionWheel agent:
  ```
  cd ~/Projects/gt-lionwheel-daily-route-agent
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -e ".[dev]"
  ```

---

## Step 5 — Check that everything works

Run these and look for a clean result:

- [ ] Portal — should finish with no errors:
  ```
  cd ~/Projects/gt-factory-os-portal && npm run typecheck && npm run build
  ```
- [ ] LionWheel agent — should say "117 passed":
  ```
  cd ~/Projects/gt-lionwheel-daily-route-agent && source .venv/bin/activate && python -m pytest
  ```
- [ ] Backend — typecheck (a few harmless pre-existing warnings are expected, see "Don't panic" below):
  ```
  cd ~/Projects/gt-factory-os && npm run typecheck
  ```
- [ ] Open each of the four folders in VS Code / Claude Code and confirm Claude Code loads them.

---

## Step 6 — Before you wipe the old Windows machine

Do **not** erase Windows until ALL of these are true:

- [ ] All four repos downloaded without error.
- [ ] The three `.env` files are restored on the Mac.
- [ ] Portal `npm run build` finished cleanly.
- [ ] LionWheel `pytest` shows 117 passed.
- [ ] Claude Code opens all four projects correctly.
- [ ] You completed **one real work session** on the Mac — e.g. a daily inventory update, or a LionWheel route run — and it worked end to end.

When every box is ticked, the Windows machine is safe to retire.

---

## Don't panic about these — they are normal

- **Backend typecheck shows a few errors.** Expected. There is 1 error in an old archived script and 6 in one test file. They existed before the migration and do not affect the running system.
- **Portal `npm run test` shows ~35 failures.** Expected and known — that is the long-standing test baseline. The build still passes; the portal works.
- **`LF will be replaced by CRLF` messages.** Just Git noticing Windows-vs-Mac line endings. Harmless.
- **Git worktrees from Windows are gone.** Intentional — they don't transfer. Every branch is safely on GitHub; Claude Code can recreate a worktree if a task needs one.
- **One open Pull Request (#21) on the portal.** That is a normal product change waiting for review — not a migration problem. Review and merge it whenever you like.
- **The `redesign/production-simulation` branch on the portal.** Just a saved snapshot of work; the normal branch is `main`.

---

## If something goes wrong

Open Claude Code in the affected repo and describe what failed. Every repository is fully backed up on GitHub, so nothing you do locally can lose work — at worst you delete the folder and clone it again.
