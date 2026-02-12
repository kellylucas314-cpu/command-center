# Kelly's Command Center

A personal fundraising dashboard with CRM, To-Dos, Investor Finder, and Document Vault.

## Quick Start (Local Mode)

```bash
# Install Flask
pip install flask

# Run the app
python app.py

# Open in browser
open http://localhost:5000
```

## Features

- **Dashboard** - Today's priorities, pipeline overview, top investor matches
- **CRM** - Connected to your SQLite database at `~/.openclaw/crm/helioflux_crm.sqlite`
- **To-Dos** - ADHD-friendly (max 3 daily priorities)
- **Investor Finder** - Search/filter by type, sector, fit score
- **Vault** - Browse research reports and documents

## API Endpoints

When running locally:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/contacts` | GET | List all CRM contacts |
| `/api/contacts` | POST | Add new contact |
| `/api/contacts/:id` | PUT | Update contact |
| `/api/pipeline` | GET | Pipeline stats |
| `/api/tasks` | GET | List tasks |
| `/api/tasks` | POST | Add task |
| `/api/tasks/:id` | PUT | Update task |
| `/api/investors` | GET | List investors |
| `/api/investors/search` | GET | Search/filter investors |
| `/api/documents` | GET | List vault documents |

## File Structure

```
command-center/
├── index.html          # Dashboard
├── app.py              # Flask backend
├── requirements.txt    # Python dependencies
├── data/
│   ├── investors.json  # Investor database
│   └── tasks.json      # To-do items
└── docs/
    └── research/       # Research reports
```

## Modes

- **Local mode** (`python app.py`): Full functionality, connected to SQLite CRM
- **Static mode** (GitHub Pages): Read-only demo with sample data

## Live Demo

https://kellylucas314-cpu.github.io/command-center/

---

Built with 🦉 by Kip for Kelly
