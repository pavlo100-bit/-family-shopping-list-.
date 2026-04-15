import os
import json
import sqlite3
from flask import Flask, render_template, request, redirect, jsonify
import google.generativeai as genai

app = Flask(__name__)

# וידוא גרסה בלוגים של Railway
print("\n" + "="*50)
print("🚀 FAMILY LIST - VERSION 18.0 - AI CLASSIFIER FIX")
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
        print("✅ AI Engine Ready for classification", flush=True)
    except Exception as e:
        print(f"❌ AI Init Error: {e}", flush=True)

# רשימת הקטגוריות הרשמית
CATEGORY_ORDER = [
    'מוצרי חלב וביצים', 'בשר ודגים', 'מאפייה', 'פירות וירקות',
    'יבשים ושימורים', 'קפואים', 'חטיפים ומתוקים', 'משקאות', 
    'ניקיון ותחזוקה', 'פארם והיגיינה', 'כללי/אחר'
]

def init_db():
    conn = sqlite3.connect('shopping.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS items 
                 (id INTEGER PRIMARY KEY, name TEXT, category TEXT, status INTEGER)''')
    conn.commit()
    conn.close()

init_db()

def analyze_message(text):
    print(f"🔍 Analyzing text: {text}", flush=True)
    
    def fallback(t):
        parts = t.replace(' וגם ', ',').replace(' ו', ',').replace(';', ',').replace('\n', ',').split(',')
        return [{"name": p.strip(), "category": "כללי/אחר"} for p in parts if p.strip()]

    if not model:
        return fallback(text)

    try:
        prompt = f"""
        Extract items from this Hebrew shopping list: "{text}"
        STRICT RULES:
        1. Split multiple items.
        2. Assign category ONLY from: {CATEGORY_ORDER}.
        3. Clean item names.
        4. Return ONLY a valid JSON array of objects.
        Format: [{{"name": "item", "category": "category"}}]
        """
        response = model.generate_content(prompt)
        raw = response.text.strip()
        
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"): raw = raw[4:]
            raw = raw.split("```")[0].strip()
        
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

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    try:
        if 'messageData' in data and 'textMessageData' in data['messageData']:
            full_text = data['messageData']['textMessageData']['textMessage']
            if data['senderData']['chatId'] == ALLOWED_GROUP_ID:
                results = analyze_message(full_text)
                conn = sqlite3.connect('shopping.db')
                c = conn.cursor()
                for item in results:
                    c.execute("INSERT INTO items (name, category, status) VALUES (?, ?, 0)", (item['name'], item['category']))
                conn.commit()
                conn.close()
    except Exception as e:
        print(f"❌ Webhook Error: {e}", flush=True)
    return jsonify({"status": "success"}), 200

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
