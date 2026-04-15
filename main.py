import os
import sqlite3
import json
from flask import Flask, render_template, request, redirect, jsonify
from google import genai

app = Flask(__name__)

# הגדרות מערכת
ALLOWED_GROUP_ID = '120363425281087335@g.us'
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# אתחול הלקוח החדש של גוגל
client = None
if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except:
        client = None

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
    def fallback(t):
        parts = t.replace(' וגם ', ',').replace(' ו', ',').replace(';', ',').replace('\n', ',').split(',')
        return [{"name": p.strip(), "category": "כללי/אחר"} for p in parts if p.strip()]
    
    if not client: return fallback(text)
    
    try:
        prompt = f"Identify products in Hebrew. Categories ONLY: {CATEGORY_ORDER}. Return ONLY JSON list: [{{'name': 'product', 'category': 'category'}}]. Text: {text}"
        response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
        
        raw = response.text.strip()
        if "```" in raw:
            raw = raw.split("```")[1].replace("json", "").split("```")[0].strip()
        
        items = json.loads(raw)
        for item in items:
            if item.get('category') not in CATEGORY_ORDER:
                item['category'] = 'כללי/אחר'
        return items
    except:
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

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    try:
        if 'messageData' in data and 'textMessageData' in data['messageData']:
            full_text = data['messageData']['textMessageData']['textMessage']
            chat_id = data['senderData']['chatId']
            if chat_id == ALLOWED_GROUP_ID:
                results = analyze_message(full_text)
                conn = sqlite3.connect('shopping.db')
                c = conn.cursor()
                for item in results:
                    c.execute("INSERT INTO items (name, category, status) VALUES (?, ?, 0)", (item['name'], item['category']))
                conn.commit()
                conn.close()
    except:
        pass
    return jsonify({"status": "success"}), 200

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
