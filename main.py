from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
import os

app = Flask(__name__)

# --- הגדרת הקבוצה המורשית ---
ALLOWED_GROUP_ID = '120363425281087335@g.us'

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
    item_name = item_name.lower()
    categories = {
        'פירות וירקות': ['עגבניה', 'מלפפון', 'בצל', 'תפוח', 'בננה', 'חסה', 'גזר', 'פלפל', 'קישוא', 'לימון', 'פירות', 'ירקות', 'תפו"א'],
        'מוצרי חלב וביצים': ['חלב', 'גבינה', 'יוגורט', 'קוטג', 'חמאה', 'שמנת', 'ביצים', 'צהובה', 'לבנה', 'מעדן'],
        'בשר ודגים': ['עוף', 'בקר', 'המבורגר', 'שניצל', 'נקניקיות', 'בשר', 'דג', 'טונה', 'פילה', 'טחון'],
        'מאפייה': ['לחם', 'פיתות', 'לחמניות', 'חלה', 'באגט', 'פירורי לחם'],
        'יבשים ושימורים': ['אורז', 'פסטה', 'סוכר', 'קמח', 'עדשים', 'פתיתים', 'שימורים', 'שמן', 'רסק', 'קטשופ', 'קפה', 'תה'],
        'קפואים': ['צ\'יפס', 'פיצה', 'גלידה', 'מלווח', 'בורקס', 'קפוא'],
        'חטיפים ומתוקים': ['במבה', 'ביסלי', 'שוקולד', 'עוגיות', 'וופל', 'מסטיק', 'סוכריות'],
        'משקאות': ['מים', 'קולה', 'מיץ', 'סודה', 'בירה', 'יין'],
        'ניקיון ותחזוקה': ['אבקת כביסה', 'מרכך', 'נוזל כלים', 'אקונומיקה', 'סמרטוט', 'זבל'],
        'פארם והיגיינה': ['שמפו', 'סבון', 'משחה', 'נייר טואלט', 'דאודורנט', 'חיתולים', 'מגבונים']
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
    # מיון: מה שטרם נקנה למעלה, ואז לפי קטגוריות
    c.execute("SELECT * FROM items ORDER BY status ASC, category ASC")
    items = c.fetchall()
    conn.close()
    return render_template('index.html', items=items)

# הוספה ידנית מהאתר
@app.route('/add', methods=['POST'])
def add_item():
    name = request.form.get('item_name')
    if name:
        category = categorize(name)
        conn = sqlite3.connect('shopping.db')
        c = conn.cursor()
        c.execute("INSERT INTO items (name, category, status) VALUES (?, ?, 0)", (name, category))
        conn.commit()
        conn.close()
    return redirect('/')

# קבלת הודעות מוואטסאפ (Webhook)
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    
    try:
        if data.get('typeWebhook') == 'incomingMessageReceived':
            chat_id = data['senderData']['chatId']
            
            # הבדיקה הקריטית: האם ההודעה מהקבוצה המשפחתית?
            if chat_id == ALLOWED_GROUP_ID:
                message_text = data['messageData']['textMessageData']['textMessage']
                category = categorize(message_text)
                
                conn = sqlite3.connect('shopping.db')
                c = conn.cursor()
                c.execute("INSERT INTO items (name, category, status) VALUES (?, ?, 0)", (message_text, category))
                conn.commit()
                conn.close()
                print(f"✅ מוצר נוסף מהקבוצה: {message_text}")
            else:
                print(f"⚠️ התעלמתי מהודעה מכתובת לא מורשית: {chat_id}")
                
    except Exception as e:
        print(f"❌ שגיאה בעיבוד הודעה: {e}")
        
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
