#!/usr/bin/env python3
"""
Export all data sources to JSON for Command Center
Run this to sync real data to the static dashboard
"""

import sqlite3
import json
import os
import re
from datetime import datetime
from pathlib import Path

# Paths
WORKSPACE = Path.home() / ".openclaw/workspace"
CRM_DB = Path.home() / ".openclaw/crm/helioflux_crm.sqlite"
KB_DB = WORKSPACE / "knowledge-base/knowledge.db"
EMAIL_DB = WORKSPACE / "crm/email_outreach.db"
MEMORY_DIR = WORKSPACE / "memory"
OUTPUT_DIR = WORKSPACE / "command-center/data"

def export_crm():
    """Export CRM data to JSON."""
    if not CRM_DB.exists():
        return {"contacts": [], "stats": {}}
    
    conn = sqlite3.connect(CRM_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all contacts
    cursor.execute("""
        SELECT id, name, email, phone, company, title, status, category, priority, 
               check_size, intro_source, linkedin_url, twitter_handle, notes, 
               meeting_notes_link, next_step, last_contact, created_at, updated_at
        FROM contacts
        ORDER BY 
            CASE priority 
                WHEN 'A' THEN 1 
                WHEN 'B' THEN 2 
                WHEN 'C' THEN 3 
                ELSE 4 
            END,
            updated_at DESC
    """)
    contacts = [dict(row) for row in cursor.fetchall()]
    
    # Get stats
    cursor.execute("SELECT COUNT(*) FROM contacts")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT status, COUNT(*) FROM contacts GROUP BY status")
    by_status = {row[0]: row[1] for row in cursor.fetchall()}
    
    cursor.execute("SELECT category, COUNT(*) FROM contacts GROUP BY category")
    by_category = {row[0]: row[1] for row in cursor.fetchall()}
    
    cursor.execute("SELECT priority, COUNT(*) FROM contacts WHERE priority IS NOT NULL GROUP BY priority")
    by_priority = {row[0]: row[1] for row in cursor.fetchall()}
    
    conn.close()
    
    data = {
        "contacts": contacts,
        "stats": {
            "total": total,
            "by_status": by_status,
            "by_category": by_category,
            "by_priority": by_priority
        },
        "exported_at": datetime.now().isoformat()
    }
    
    with open(OUTPUT_DIR / "crm.json", "w") as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"✅ Exported {len(contacts)} contacts to crm.json")
    return data

def export_knowledge_base():
    """Export Knowledge Base to JSON."""
    if not KB_DB.exists():
        return {"entries": []}
    
    conn = sqlite3.connect(KB_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, source_type as type, title, url, full_text as content, summary, tags, created_at
        FROM entries
        ORDER BY created_at DESC
    """)
    entries = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    data = {
        "entries": entries,
        "exported_at": datetime.now().isoformat()
    }
    
    with open(OUTPUT_DIR / "knowledge.json", "w") as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"✅ Exported {len(entries)} KB entries to knowledge.json")
    return data

def export_email_outreach():
    """Export email outreach tracking to JSON."""
    if not EMAIL_DB.exists():
        return {"emails": [], "stats": {}}
    
    conn = sqlite3.connect(EMAIL_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, email_id, sent_at, to_email, to_name, subject, status, 
               response_at, bounce_reason, thread_id
        FROM outreach
        ORDER BY sent_at DESC
        LIMIT 500
    """)
    emails = [dict(row) for row in cursor.fetchall()]
    
    # Stats
    cursor.execute("SELECT COUNT(*) FROM outreach")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT status, COUNT(*) FROM outreach GROUP BY status")
    by_status = {row[0]: row[1] for row in cursor.fetchall()}
    
    conn.close()
    
    data = {
        "emails": emails,
        "stats": {
            "total": total,
            "by_status": by_status
        },
        "exported_at": datetime.now().isoformat()
    }
    
    with open(OUTPUT_DIR / "outreach.json", "w") as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"✅ Exported {len(emails)} emails to outreach.json")
    return data

def export_memory():
    """Export memory files to JSON."""
    if not MEMORY_DIR.exists():
        return {"entries": []}
    
    entries = []
    for md_file in sorted(MEMORY_DIR.glob("*.md"), reverse=True):
        try:
            content = md_file.read_text()
            # Extract date from filename
            date_match = re.match(r"(\d{4}-\d{2}-\d{2})", md_file.name)
            date = date_match.group(1) if date_match else md_file.name.replace(".md", "")
            
            # Extract key highlights (lines starting with ##)
            highlights = []
            for line in content.split("\n"):
                if line.startswith("## "):
                    highlights.append(line[3:].strip())
            
            entries.append({
                "filename": md_file.name,
                "date": date,
                "highlights": highlights[:5],  # Top 5 highlights
                "preview": content[:500] + "..." if len(content) > 500 else content,
                "full_content": content
            })
        except Exception as e:
            print(f"Warning: Could not read {md_file}: {e}")
    
    data = {
        "entries": entries,
        "exported_at": datetime.now().isoformat()
    }
    
    with open(OUTPUT_DIR / "memory.json", "w") as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"✅ Exported {len(entries)} memory files to memory.json")
    return data

def export_tasks():
    """Export tasks from various sources."""
    tasks = []
    
    # Read from MEMORY.md for active tasks/blockers
    memory_file = WORKSPACE / "MEMORY.md"
    if memory_file.exists():
        content = memory_file.read_text()
        
        # Extract In Progress items
        in_progress = re.search(r"### In Progress\n(.*?)(?=\n###|\n## |$)", content, re.DOTALL)
        if in_progress:
            for line in in_progress.group(1).split("\n"):
                if line.strip().startswith("- ["):
                    done = "[x]" in line.lower()
                    text = re.sub(r"- \[.\] ", "", line.strip())
                    if text:
                        tasks.append({
                            "text": text,
                            "done": done,
                            "priority": "high" if "URGENT" in text.upper() else "medium",
                            "source": "MEMORY.md"
                        })
        
        # Extract Blocked items
        blocked = re.search(r"### Blocked\n(.*?)(?=\n###|\n## |$)", content, re.DOTALL)
        if blocked:
            for line in blocked.group(1).split("\n"):
                if line.strip().startswith("- "):
                    text = line.strip()[2:]
                    if text:
                        tasks.append({
                            "text": f"🚫 {text}",
                            "done": False,
                            "priority": "high",
                            "source": "MEMORY.md (Blocked)"
                        })
    
    # Read today's memory for recent tasks
    today = datetime.now().strftime("%Y-%m-%d")
    today_file = MEMORY_DIR / f"{today}.md"
    if today_file.exists():
        content = today_file.read_text()
        # Look for action items
        for line in content.split("\n"):
            if "TODO" in line.upper() or "ACTION" in line.upper():
                text = re.sub(r"^[-*] ", "", line.strip())
                if text and len(text) > 5:
                    tasks.append({
                        "text": text,
                        "done": False,
                        "priority": "medium",
                        "source": f"memory/{today}.md"
                    })
    
    data = {
        "tasks": tasks,
        "exported_at": datetime.now().isoformat()
    }
    
    with open(OUTPUT_DIR / "tasks.json", "w") as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"✅ Exported {len(tasks)} tasks to tasks.json")
    return data

def main():
    """Export all data."""
    print("📊 Exporting Command Center Data...\n")
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Export all data sources
    crm_data = export_crm()
    kb_data = export_knowledge_base()
    email_data = export_email_outreach()
    memory_data = export_memory()
    task_data = export_tasks()
    
    # Create summary
    summary = {
        "crm": crm_data.get("stats", {}),
        "knowledge_base": {"count": len(kb_data.get("entries", []))},
        "outreach": email_data.get("stats", {}),
        "memory": {"count": len(memory_data.get("entries", []))},
        "tasks": {"count": len(task_data.get("tasks", []))},
        "exported_at": datetime.now().isoformat()
    }
    
    with open(OUTPUT_DIR / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n✅ All data exported to {OUTPUT_DIR}")
    print(f"   Summary: {json.dumps(summary, indent=2)}")

if __name__ == "__main__":
    main()
