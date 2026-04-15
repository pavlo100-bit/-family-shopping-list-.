import os
import sqlite3
import json
from flask import Flask, render_template, request, redirect, jsonify
from google import genai

app = Flask(__name__)

# הגדרות מערכת
ALLOWED_GROUP_ID = '120363425281087335@g.us'
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# אתחול הלקוח
client = None
if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        print("✅ AI Client Initialized", flush=True)
    except Exception as e:
        print(f"❌ Failed to init Gemini: {e}", flush=True)

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
    raw_response = "no response"
    def fallback(t):
        import re
        parts = re.split(r',|;|\n| וגם ', t)
        return [{"name": p.strip(), "category": "כללי/אחר"} for p in parts if p.strip()]
    
    if not client:
        return fallback(text)
    
    try:
        categories_str = "\n".join(f"- {cat}" for cat in CATEGORY_ORDER)
        prompt = f"""אתה עוזר לסיווג מוצרי קניות לסופרמרקט.

המשימה שלך:
1. חלץ מהטקסט רק שמות מוצרים (התעלם ממילות בקשה כמו "תביא לי", "רק", "בבקשה")
2. אם יש כמה מוצרים במשפט — פצל אותם לפריטים נפרדים
3. סווג כל מוצר לקטגוריה המתאימה מהרשימה

קטגוריות (השתמש בדיוק בשמות האלה):
{categories_str}

פורמט פלט — JSON בלבד, בלי טקסט נוסף:
[{{"name": "שם המוצר", "category": "קטגוריה"}}]

דוגמאות:
קלט: "תביא לי רק עמק פרוס דק ולחם"
פלט: [{{"name": "עמק פרוס דק", "category": "מוצרי חלב וביצים"}}, {{"name": "לחם", "category": "מאפייה"}}]

טקסט לעיבוד: {text}"""

        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config={"temperature": 0}
        )
        
        raw_response = response.text.strip()
        if "```" in raw_response:
            raw_response = raw_response.split("```")[1].replace("json", "").strip()
            if "```" in raw_response:
                raw_response = raw_response.split("```")[0].strip()
        
        items = json.loads(raw_response)
        for item in items:
            if item.get('category') not in CATEGORY_ORDER:
                item['category'] = 'כללי/אחר'
        return items

    except Exception as e:
        print(f"❌ Gemini error: {e}")
        print(f"🔍 Raw response for failure: {raw_response}")
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
    except Exception as e:
        print(f"❌ Webhook error: {e}")
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
