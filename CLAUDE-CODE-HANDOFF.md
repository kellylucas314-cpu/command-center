# 🎯 Kelly's Command Center — Claude Code Handoff

> **For:** Claude Code / Coding Agent  
> **Created by:** Kelly Lucas + Kip 🦉  
> **Date:** February 11, 2026  
> **Goal:** A personal fundraising command center with CRM, To-Dos, Investor Finder, and Knowledge Vault

---

## THE VISION

One place for everything Kelly needs to raise money and run HelioFlux:
- **CRM** — Track contacts, investors, pipeline
- **To-Dos** — ADHD-friendly daily priorities (max 3)
- **Investor Finder** — Search, filter, match investors to needs
- **Vault** — Store key docs, research, specs, templates

---

## DESIGN DIRECTION

**Vibe:** Dark mode, cinematic, professional — NOT generic SaaS
**Inspiration:** The HelioFlux patient journey aesthetic
**Feel:** Premium, focused, calm

**Colors (from Patient Journey):**
```css
--bg-primary: #0A2540;      /* Deep navy */
--accent-teal: #00B4D8;     /* Interactive elements */
--accent-glow: #7DF9FF;     /* Highlights */
--text-primary: #F8F9FA;    /* Main text */
--text-muted: #6C757D;      /* Secondary text */
--success: #28A745;
--warning: #FFC107;
--danger: #DC3545;
```

**Typography:**
- Headers: Space Grotesk
- Body: Inter

---

## FEATURE 1: CRM

### What It Does
- View all contacts in searchable list
- Filter by status, category, priority
- Quick actions (email, update status, add note)
- Pipeline visualization

### Data Model (Existing SQLite)
```
Contact:
- id, name, email, phone
- company, title, linkedin
- category (VC/Fund, Angel, Family Office, Advisor, etc.)
- status (Committed, In Conversation, Warm Lead, Cold Outreach, Cold)
- priority (A, B, C)
- notes, last_contact, next_action
```

### Views
1. **List view** — All contacts, sortable
2. **Pipeline view** — Kanban by status
3. **Detail view** — Single contact with history

### Quick Stats (Dashboard)
- Total contacts: 35
- Committed: 5
- Warm leads: 11
- Need follow-up: X (overdue next_action)

---

## FEATURE 2: TO-DO LIST

### Philosophy
Kelly has ADHD. The to-do list should:
- Show MAX 3 priorities per day
- Make it easy to defer/reschedule
- Celebrate completion
- Not overwhelm

### Data Model
```
Task:
- id, title, description
- due_date (nullable)
- priority (1, 2, 3)
- status (pending, done, deferred)
- category (HelioFlux, Job Search, Personal, Bull Stories)
- created_at, completed_at
```

### Views
1. **Today's 3** — The main view, just 3 items
2. **Backlog** — Everything else, organized
3. **Completed** — Celebration/history

### UX Details
- Drag to reorder priorities
- Check to complete (satisfying animation)
- "Defer to tomorrow" button
- Weekly review prompt

---

## FEATURE 3: INVESTOR FINDER

### What It Does
Help Kelly find the RIGHT investors for HelioFlux

### Data Sources
- 8 research reports from tonight
- CRM contacts (who she already knows)
- Curated investor database

### Investor Database Schema
```
Investor:
- id, name, firm
- type (VC, Angel, Family Office, Corporate, Foundation)
- stage_focus (Pre-seed, Seed, Series A+)
- sector_focus (Oncology, Diagnostics, Biotech, General)
- check_size_min, check_size_max
- location
- warm_intro_available (boolean)
- contact_info
- notes
- fit_score (calculated)
```

### Fit Scoring Algorithm
Score investors 1-100 based on:
- Sector match (oncology = high score)
- Stage match (seed/early = high score)
- Check size match (bridge round = $50K-500K)
- Warm intro available (+20 points)
- Location proximity (+5 points)

### Views
1. **Search/Filter** — Find investors by criteria
2. **Best Matches** — Sorted by fit score
3. **Outreach Tracker** — Who contacted, status

### Pre-loaded Investors (From Tonight's Research)
- Aglaia Oncology (perfect fit)
- IndieBio (accelerator + funding)
- Codon Capital
- 5AM Ventures
- ARCH Venture Partners
- Boehringer Ingelheim Venture Fund
- Mark Foundation (grants)
- Prevent Cancer Foundation (grants)
- (+ 40 more from the research)

---

## FEATURE 4: VAULT (Knowledge Base)

### What It Does
Store and organize everything important

### Categories
1. **Research Reports** — The 8 reports from tonight
2. **Specs & Handoffs** — Claude Code docs
3. **Pitch Materials** — Deck, one-pagers
4. **Templates** — Email templates, outreach scripts
5. **Key Documents** — iScience paper, patents, etc.
6. **Meeting Notes** — Investor meetings, partner calls
7. **Links** — Important URLs, resources

### Data Model
```
Document:
- id, title
- category
- file_path (if file) OR content (if text) OR url (if link)
- tags (array)
- created_at, updated_at
- pinned (boolean)
```

### Views
1. **Browse by category**
2. **Search** (full-text)
3. **Recent** (last 10 accessed)
4. **Pinned** (favorites)

### Pre-loaded Content
- 8 research reports
- Patient journey spec
- Jeopardy game spec
- Maya's story copy
- Email templates (from previous sessions)

---

## PAGE STRUCTURE

```
/                     → Dashboard (Today's 3 + Pipeline snapshot + Recent docs)
/crm                  → CRM list view
/crm/:id              → Contact detail
/crm/pipeline         → Kanban view
/todos                → Full to-do list
/investors            → Investor finder
/investors/:id        → Investor detail
/vault                → Knowledge base
/vault/:category      → Category view
/vault/doc/:id        → Document view
/settings             → Preferences
```

---

## DASHBOARD (Home)

The main view Kelly sees every day:

```
┌─────────────────────────────────────────────────────────────┐
│  KELLY'S COMMAND CENTER                    Feb 12, 2026    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  TODAY'S PRIORITIES                                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 1. □ Sign Mike's patent engagement ($2,500)         │   │
│  │ 2. □ Apply to Aglaia Oncology                       │   │
│  │ 3. □ Sign up for Outlier.ai                         │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  PIPELINE                           NEED FOLLOW-UP          │
│  ├── Committed: 5                   • Jim Armstrong (3d)    │
│  ├── In Conversation: 1             • Andy Lehman (5d)      │
│  ├── Warm Lead: 11                  • Emily Atkinson (7d)   │
│  └── Cold Outreach: 12                                      │
│                                                             │
│  RECENT DOCS                        QUICK ACTIONS           │
│  • Competitor Landscape             [+ Add Contact]         │
│  • Grant Opportunities              [+ Add Task]            │
│  • AI Training Jobs                 [+ Add Doc]             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## TECHNICAL SPEC

### Option A: Pure HTML/CSS/JS (Simplest)
```
- Single HTML file or few files
- LocalStorage for data (or connect to SQLite)
- No build step
- Deploy to GitHub Pages
```

### Option B: React + SQLite (More Powerful)
```
- React frontend
- SQLite database (existing CRM)
- TailwindCSS
- Optional: Electron for desktop app
```

### Option C: Next.js + Database (Full Stack)
```
- Next.js app
- PostgreSQL or SQLite
- Deploy to Vercel
- API routes for data
```

### Recommended: Start with Option A
- Get something working fast
- Iterate based on use
- Upgrade later if needed

---

## FILE STRUCTURE (Option A)

```
command-center/
├── index.html          # Dashboard
├── crm.html            # CRM view
├── todos.html          # To-do list
├── investors.html      # Investor finder
├── vault.html          # Knowledge base
├── styles.css          # Shared styles
├── app.js              # Shared logic
├── data/
│   ├── contacts.json   # CRM data (export from SQLite)
│   ├── investors.json  # Investor database
│   ├── tasks.json      # To-do items
│   └── documents.json  # Vault index
└── docs/               # Actual document files
    ├── research/
    ├── specs/
    └── templates/
```

---

## DATA MIGRATION

### From Existing SQLite CRM
```bash
# Export contacts to JSON
sqlite3 ~/.openclaw/crm/helioflux_crm.sqlite \
  "SELECT * FROM contacts" \
  -json > data/contacts.json
```

### From Research Reports
Copy the 8 reports into `docs/research/`

---

## MVP SCOPE (Build First)

### Phase 1 (Day 1)
- [ ] Dashboard with Today's 3
- [ ] Pipeline snapshot
- [ ] Basic styling

### Phase 2 (Day 2)
- [ ] CRM list view
- [ ] Contact detail page
- [ ] Search/filter

### Phase 3 (Day 3)
- [ ] Investor finder with fit scoring
- [ ] Vault with categories
- [ ] Recent docs

### Phase 4 (Polish)
- [ ] Animations
- [ ] Mobile responsive
- [ ] LocalStorage persistence

---

## HOW TO START IN CLAUDE CODE

Paste this prompt:

> "Read CLAUDE-CODE-HANDOFF.md in the command-center folder. Build the dashboard (index.html) first with:
> 1. Dark theme matching HelioFlux patient journey
> 2. Today's 3 priorities section
> 3. Pipeline snapshot
> 4. Recent docs
> 5. Use the color palette and fonts specified in the doc."

---

## SUCCESS CRITERIA

The Command Center is successful when:
- [ ] Kelly checks it every morning
- [ ] She can find any investor in <10 seconds
- [ ] To-dos don't overwhelm (max 3 visible)
- [ ] Documents are findable
- [ ] It looks as good as the patient journey

---

*Built with 🦉 by Kip for Kelly — February 2026*

*"One place for everything. Everything in its place."*
