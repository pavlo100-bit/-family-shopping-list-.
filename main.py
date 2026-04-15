from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
import os

app = Flask(__name__)

# --- הגדרות ---
ALLOWED_GROUP_ID = '120363425281087335@g.us'

# סדר הקטגוריות שיוצג באתר (לפי סדר ההליכה בסופר)
CATEGORY_ORDER = [
    'יבשים ושימורים',
    'מוצרי חלב וביצים',
    'בשר ודגים',
    'פירות וירקות',
    'מאפייה',
    'קפואים',
    'חטיפים ומתוקים',
    'משקאות',
    'ניקיון ותחזוקה',
    'פארם והיגיינה',
    'כללי/אחר'
]

# --- יצירת בסיס הנתונים ---
def init_db():
    conn = sqlite3.connect('shopping.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS items 
                 (id INTEGER PRIMARY KEY, name TEXT, category TEXT, status INTEGER)''')
    conn.commit()
    conn.close()

init_db()

# --- לוגיקת הסיווג ---
def categorize(item_name):
    item_name = item_name.strip().lower()
    categories = {
        'פירות וירקות': ['עגבניה', 'מלפפון', 'בצל', 'תפוח', 'בננה', 'חסה', 'גזר', 'פלפל', 'קישוא', 'לימון', 'פירות', 'ירקות', 'תפו"א'],
        'מוצרי חלב וביצים': ['חלב', 'גבינה', 'יוגורט', 'קוטג', 'חמאה', 'שמנת', 'ביצים', 'צהובה', 'לבנה', 'מעדן', 'גבנצ'],
        'בשר ודגים': ['עוף', 'בקר', 'המבורגר', 'שניצל', 'נקניקיות', 'בשר', 'דג', 'טונה', 'פילה', 'טחון', 'קבב', 'פרגיות'],
        'מאפייה': ['לחם', 'פיתות', 'לחמניות', 'חלה', 'באגט', 'פירורי לחם', 'עוגה'],
        'יבשים ושימורים': ['אורז', 'פסטה', 'סוכר', 'קמח', 'עדשים', 'פתיתים', 'שימורים', 'שמן', 'רסק', 'קטשופ', 'קפה', 'תה', 'ספגטי', 'מלח'],
        'קפואים': ['צ\'יפס', 'פיצה', 'גלידה', 'מלווח', 'בורקס', 'קפוא', 'אפונה'],
        'חטיפים ומתוקים': ['במבה', 'ביסלי', 'שוקולד', 'עוגיות', 'וופל', 'מסטיק', 'סוכריות', 'פיצוחים'],
        'משקאות': ['מים', 'קולה', 'מיץ', 'סודה', 'בירה', 'יין', 'זירו'],
        'ניקיון ותחזוקה': ['אבקת כביסה', 'מרכך', 'נוזל כלים', 'אקונומיקה', 'סמרטוט', 'זבל', 'מטלית'],
        'פארם והיגיינה': ['שמפו', 'סבון', 'משחה', 'נייר טואלט', 'דאודורנט', 'חיתולים', 'מגבונים', 'קיסמים']
    }
    for cat, keywords in categories.items():
        if any(keyword in item_name for keyword in keywords):
            return cat
    return 'כללי/אחר'

# --- נתיבי האתר ---

@app.route('/')
def index():
    conn = sqlite3.connect('shopping.db')
    c = conn.cursor()
    
    # שאילתה שממיינת לפי הסדר שקבענו ב-CATEGORY_ORDER
    # אנחנו משתמשים ב-CASE כדי לתת משקל לכל קטגוריה
    order_query = "CASE category "
    for i, cat in enumerate(CATEGORY_ORDER):
        order_query += f"WHEN '{cat}' THEN {i} "
    order_query += "END"
    
    c.execute(f"SELECT * FROM items ORDER BY status ASC, {order_query} ASC")
    items = c.fetchall()
    conn.close()
    return render_template('index.html', items=items)

@app.route('/add', methods=['POST'])
def add_item():
    name = request.form.get('item_name')
    if name:
        # פירוק הודעות עם כמה שורות
        lines = name.split('\n')
        conn = sqlite3.connect('shopping.db')
        c = conn.cursor()
        for line in lines:
            if line.strip():
                category = categorize(line)
                c.execute("INSERT INTO items (name, category, status) VALUES (?, ?, 0)", (line.strip(), category))
        conn.commit()
        conn.close()
    return redirect('/')

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    try:
        if data.get('typeWebhook') == 'incomingMessageReceived':
            chat_id = data['senderData']['chatId']
            if chat_id == ALLOWED_GROUP_ID:
                full_text = data['messageData']['textMessageData']['textMessage']
                
                # פירוק הטקסט לשורות (אם יש)
                lines = full_text.split('\n')
                
                conn = sqlite3.connect('shopping.db')
                c = conn.cursor()
                for line in lines:
                    if line.strip():
                        category = categorize(line)
                        c.execute("INSERT INTO items (name, category, status) VALUES (?, ?, 0)", (line.strip(), category))
                conn.commit()
                conn.close()
                print(f"✅ נוספו {len(lines)} מוצרים מהקבוצה")
    except Exception as e:
        print(f"❌ שגיאה: {e}")
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
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
