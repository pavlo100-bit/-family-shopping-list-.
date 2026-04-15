import os
import json
import sqlite3
from flask import Flask, render_template, request, redirect, jsonify
import google.generativeai as genai

app = Flask(__name__)

# סימן זיהוי גירסה - לוודא שגרסה 23 נטענה
print("\n" + "="*50)
print("🚀 FAMILY LIST - VERSION 23.0 - DESKTOP & AI FIX")
print("="*50 + "\n", flush=True)

# --- הגדרות מערכת ---
ALLOWED_GROUP_ID = '120363425281087335@g.us'
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# אתחול ה-AI
model = None
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ AI Engine Ready - Version 23", flush=True)
    except Exception as e:
        print(f"❌ AI Init Error: {e}", flush=True)
else:
    print("⚠️ WARNING: GEMINI_API_KEY is not defined in Railway Variables!", flush=True)

CATEGORY_ORDER = [
    'מוצרי חלב וביצים', 'בשר ודגים', 'מאפייה', 'פירות וירקות',
    'יבשים ושימורים', 'קפואים', 'חטיפים ומתוקים', 'משקאות', 
    'ניקיון ותחזוקה', 'פארם והיגיינה', 'כללי/אחר'
]

def init_db():
    conn = sqlite3.connect('shopping.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT, category TEXT, status INTEGER)")
    conn.commit()
    conn.close()

init_db()

def analyze_message(text):
    print(f"🔍 Analyzing text: {text}", flush=True)
    
    def fallback(t):
        parts = t.replace(' וגם ', ',').replace(' ו', ',').replace(';', ',').replace('\n', ',').split(',')
        return [{"name": p.strip(), "category": "כללי/אחר"} for p in parts if p.strip()]

    if not model:
        print("⚠️ Model not initialized - check API Key", flush=True)
        return fallback(text)

    try:
        # פרומפט חזק ומדויק
        prompt = f"Identify products in Hebrew. Categories ONLY: {CATEGORY_ORDER}. Return ONLY a JSON list: [{{'name': 'product', 'category': 'category'}}]. Text: {text}"
        response = model.generate_content(prompt)
        raw = response.text.strip()
        
        # ניקוי JSON במידה וה-AI מוסיף שטויות
        if "```" in raw:
            raw = raw.split("```")[1].replace("json", "").split("```")[0].strip()
        
        print(f"🤖 AI Response: {raw}", flush=True)
        items = json.loads(raw)
        
        for item in items:
            if item.get('category') not in CATEGORY_ORDER:
                item['category'] = "כללי/אחר"
        return items
    except Exception as e:
        print(f"❌ AI Error: {e}", flush=True)
        return fallback(text)

@app.route('/')
def index():
    conn = sqlite3.connect('shopping.db')
    c = conn.cursor()
    order_query = "CASE category "
    for i, cat in enumerate(CATEGORY_ORDER):
        order_query += f"WHEN '{cat}' THEN {i} "
    order_query += "END"
    c.execute(f"SELECT * FROM items ORDER BY status ASC, {order_query} ASC, name ASC")
    items = c.fetchall()
    conn.close()
    return render_template('index.html', items=items)

@app.route('/add', methods=['POST'])
def add_item():
    name = request.form.get('item_name')
    if name:
        results = analyze_message(name)
        conn = sqlite3.connect('shopping.db')
        c = conn.cursor()
        for item in results:
            c.execute("INSERT INTO items (name, category, status) VALUES (?, ?, 0)", (item['name'], item['category']))
        conn.commit()
        conn.close()
    return redirect('/')

@app.route('/toggle/<int:item_id>')
def toggle_item(item_id):
    conn = sqlite3.connect('shopping.db')
    c = conn.cursor()
    c.execute("UPDATE items SET status = 1 - status WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/clear')
def clear_list():
    conn = sqlite3.connect('shopping.db')
    c = conn.cursor()
    c.execute("DELETE FROM items WHERE status = 1")
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
