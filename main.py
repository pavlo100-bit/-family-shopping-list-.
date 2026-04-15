import sys
from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
import os
import json
import google.generativeai as genai

# הגדרת האפליקציה - השם חייב להיות 'app' עבור Gunicorn ב-Railway
app = Flask(__name__)

# הדפסה לווידוא שהשרת עלה בגרסה הנכונה
print("\n" + "="*50)
print("🚀 FAMILY LIST - VERSION 14.0 - FINAL FIX")
print("="*50 + "\n", flush=True)

# --- הגדרות מערכת ---
ALLOWED_GROUP_ID = '120363425281087335@g.us'
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# אתחול ה-AI
model = None
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ Gemini AI Engine Ready", flush=True)
    except Exception as e:
        print(f"❌ AI Init Error: {e}", flush=True)

# סדר הקטגוריות להצגה
CATEGORY_ORDER = [
    'יבשים ושימורים', 'מוצרי חלב וביצים', 'בשר ודגים', 'פירות וירקות',
    'מאפייה', 'קפואים', 'חטיפים ומתוקים', 'משקאות', 'ניקיון ותחזוקה',
    'פארם והיגיינה', 'כללי/אחר'
]

def init_db():
    try:
        conn = sqlite3.connect('shopping.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS items 
                     (id INTEGER PRIMARY KEY, name TEXT, category TEXT, status INTEGER)''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ Database Error: {e}", flush=True)

init_db()

def analyze_message(text):
    print(f"🔍 Analyzing: {text}", flush=True)

    def basic_parser(text):
        cleaned = text
        for phrase in ["תביא לי", "תביא", "צריך", "לקנות", "נא לקנות", "אפשר להוסיף"]:
            cleaned = cleaned.replace(phrase, "")

        cleaned = cleaned.replace(" וגם ", ",").replace(" ו", ",").replace(";", ",").replace("\n", ",")
        parts = cleaned.split(",")
        results = []

        for part in parts:
            name = part.strip(" .-")
            # הסרת 'ו' מיותרת בתחילת מילה
            if name.startswith('ו') and len(name) > 3:
                name = name[1:]
            if name:
                results.append({"name": name, "category": "כללי/אחר"})
        return results

    if not model:
        print("⚠️ Gemini not available, using fallback", flush=True)
        return basic_parser(text)

    try:
        prompt = f"""
        Extract items from Hebrew shopping list.
        Rules:
        1. Split multiple items.
        2. Clean unnecessary words.
        3. Categories: {json.dumps(CATEGORY_ORDER, ensure_ascii=False)}
        Return ONLY valid JSON array: [{{"name": "product", "category": "cat"}}]
        Text: {text}
        """
        response = model.generate_content(prompt)
        raw = (response.text or "").strip()
        
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()
            
        items = json.loads(raw)
        return items if isinstance(items, list) else basic_parser(text)
    except Exception as e:
        print(f"❌ AI Error: {e}", flush=True)
        return basic_parser(text)

@app.route('/')
def index():
    try:
        conn = sqlite3.connect('shopping.db')
        c = conn.cursor()
        order_query = "CASE category "
        for i, cat in enumerate(CATEGORY_ORDER):
            order_query += f"WHEN '{cat}' THEN {i} "
        order_query += "END"
        c.execute(f"SELECT * FROM items ORDER BY status ASC, {order_query} ASC")
        items = c.fetchall()
        conn.close()
        return render_template('index.html', items=items)
    except Exception as e:
        return f"Database error: {e}"

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
            chat_id = data['senderData']['chatId']
            if chat_id == ALLOWED_GROUP_ID:
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
    # הרצה מקומית בפורט 8080
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
