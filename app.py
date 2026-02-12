#!/usr/bin/env python3
"""
Kelly's Command Center - Local Web App
Connects to your existing SQLite CRM
Run with: python app.py
Then open: http://localhost:5000
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
import sqlite3
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__, static_folder='.', template_folder='.')

# Database path
CRM_DB = os.path.expanduser('~/.openclaw/crm/helioflux_crm.sqlite')
LOCAL_DATA = os.path.join(os.path.dirname(__file__), 'data')

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(CRM_DB)
    conn.row_factory = sqlite3.Row
    return conn

# ============ PAGES ============

@app.route('/')
def dashboard():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

# ============ API ENDPOINTS ============

@app.route('/api/contacts')
def get_contacts():
    """Get all contacts from CRM"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM contacts 
            ORDER BY 
                CASE status 
                    WHEN 'Committed' THEN 1 
                    WHEN 'In Conversation' THEN 2 
                    WHEN 'Warm Lead' THEN 3 
                    WHEN 'Cold Outreach' THEN 4 
                    ELSE 5 
                END,
                priority ASC
        ''')
        contacts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(contacts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>')
def get_contact(contact_id):
    """Get single contact"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,))
        contact = cursor.fetchone()
        conn.close()
        if contact:
            return jsonify(dict(contact))
        return jsonify({'error': 'Not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts', methods=['POST'])
def add_contact():
    """Add new contact"""
    try:
        data = request.json
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO contacts (name, email, company, title, category, status, priority, notes, linkedin)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('name'),
            data.get('email'),
            data.get('company'),
            data.get('title'),
            data.get('category', 'Other'),
            data.get('status', 'Cold'),
            data.get('priority', 'C'),
            data.get('notes'),
            data.get('linkedin')
        ))
        conn.commit()
        contact_id = cursor.lastrowid
        conn.close()
        return jsonify({'id': contact_id, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    """Update contact"""
    try:
        data = request.json
        conn = get_db()
        cursor = conn.cursor()
        
        # Build update query dynamically
        fields = []
        values = []
        for key in ['name', 'email', 'company', 'title', 'category', 'status', 'priority', 'notes', 'linkedin', 'last_contact', 'next_action']:
            if key in data:
                fields.append(f'{key} = ?')
                values.append(data[key])
        
        if fields:
            values.append(contact_id)
            cursor.execute(f'UPDATE contacts SET {", ".join(fields)} WHERE id = ?', values)
            conn.commit()
        
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pipeline')
def get_pipeline():
    """Get pipeline stats"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT status, COUNT(*) as count 
            FROM contacts 
            GROUP BY status
        ''')
        stats = {row['status']: row['count'] for row in cursor.fetchall()}
        conn.close()
        
        # Ensure all statuses are present
        pipeline = {
            'Committed': stats.get('Committed', 0),
            'In Conversation': stats.get('In Conversation', 0),
            'Warm Lead': stats.get('Warm Lead', 0),
            'Cold Outreach': stats.get('Cold Outreach', 0),
            'Cold': stats.get('Cold', 0),
            'total': sum(stats.values())
        }
        return jsonify(pipeline)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/followups')
def get_followups():
    """Get contacts needing follow-up"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, last_contact, next_action
            FROM contacts 
            WHERE status IN ('Warm Lead', 'In Conversation', 'Cold Outreach')
            AND last_contact IS NOT NULL
            ORDER BY last_contact ASC
            LIMIT 10
        ''')
        followups = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(followups)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ TASKS ============

@app.route('/api/tasks')
def get_tasks():
    """Get tasks from local JSON"""
    try:
        tasks_file = os.path.join(LOCAL_DATA, 'tasks.json')
        if os.path.exists(tasks_file):
            with open(tasks_file, 'r') as f:
                tasks = json.load(f)
            return jsonify(tasks)
        return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks', methods=['POST'])
def add_task():
    """Add new task"""
    try:
        data = request.json
        tasks_file = os.path.join(LOCAL_DATA, 'tasks.json')
        
        tasks = []
        if os.path.exists(tasks_file):
            with open(tasks_file, 'r') as f:
                tasks = json.load(f)
        
        # Generate new ID
        new_id = max([t.get('id', 0) for t in tasks], default=0) + 1
        
        new_task = {
            'id': new_id,
            'title': data.get('title'),
            'description': data.get('description', ''),
            'due_date': data.get('due_date'),
            'priority': data.get('priority', 3),
            'status': 'pending',
            'category': data.get('category', 'HelioFlux'),
            'created_at': datetime.now().strftime('%Y-%m-%d')
        }
        tasks.append(new_task)
        
        with open(tasks_file, 'w') as f:
            json.dump(tasks, f, indent=2)
        
        return jsonify({'success': True, 'id': new_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update task (toggle status, etc)"""
    try:
        data = request.json
        tasks_file = os.path.join(LOCAL_DATA, 'tasks.json')
        
        with open(tasks_file, 'r') as f:
            tasks = json.load(f)
        
        for task in tasks:
            if task['id'] == task_id:
                for key, value in data.items():
                    task[key] = value
                if data.get('status') == 'done' and 'completed_at' not in task:
                    task['completed_at'] = datetime.now().strftime('%Y-%m-%d')
                break
        
        with open(tasks_file, 'w') as f:
            json.dump(tasks, f, indent=2)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ INVESTORS ============

@app.route('/api/investors')
def get_investors():
    """Get investors from local JSON"""
    try:
        investors_file = os.path.join(LOCAL_DATA, 'investors.json')
        if os.path.exists(investors_file):
            with open(investors_file, 'r') as f:
                investors = json.load(f)
            
            # Sort by fit score
            investors.sort(key=lambda x: x.get('fit_score', 0), reverse=True)
            return jsonify(investors)
        return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/investors/search')
def search_investors():
    """Search/filter investors"""
    try:
        investors_file = os.path.join(LOCAL_DATA, 'investors.json')
        with open(investors_file, 'r') as f:
            investors = json.load(f)
        
        # Filter parameters
        investor_type = request.args.get('type')
        sector = request.args.get('sector')
        min_score = request.args.get('min_score', type=int)
        warm_only = request.args.get('warm_only', type=bool)
        
        results = investors
        
        if investor_type:
            results = [i for i in results if i.get('type') == investor_type]
        if sector:
            results = [i for i in results if sector.lower() in str(i.get('sector_focus', [])).lower()]
        if min_score:
            results = [i for i in results if i.get('fit_score', 0) >= min_score]
        if warm_only:
            results = [i for i in results if i.get('warm_intro')]
        
        results.sort(key=lambda x: x.get('fit_score', 0), reverse=True)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ DOCUMENTS ============

@app.route('/api/documents')
def get_documents():
    """List documents in vault"""
    try:
        docs_dir = os.path.join(os.path.dirname(__file__), 'docs')
        documents = []
        
        for root, dirs, files in os.walk(docs_dir):
            for file in files:
                if file.endswith('.md'):
                    rel_path = os.path.relpath(os.path.join(root, file), docs_dir)
                    category = os.path.dirname(rel_path) or 'general'
                    documents.append({
                        'name': file.replace('.md', '').replace('-', ' ').title(),
                        'path': rel_path,
                        'category': category,
                        'type': 'markdown'
                    })
        
        return jsonify(documents)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents/<path:doc_path>')
def get_document(doc_path):
    """Get document content"""
    try:
        docs_dir = os.path.join(os.path.dirname(__file__), 'docs')
        full_path = os.path.join(docs_dir, doc_path)
        
        if os.path.exists(full_path):
            with open(full_path, 'r') as f:
                content = f.read()
            return jsonify({'content': content, 'path': doc_path})
        return jsonify({'error': 'Not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ MAIN ============

if __name__ == '__main__':
    print("\n" + "="*50)
    print("  KELLY'S COMMAND CENTER")
    print("="*50)
    print(f"\n  Open in browser: http://localhost:5000")
    print(f"  CRM Database: {CRM_DB}")
    print(f"\n  Press Ctrl+C to stop\n")
    
    app.run(debug=True, port=5000)
