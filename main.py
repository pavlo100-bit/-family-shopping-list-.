import os
import json
import sqlite3
from flask import Flask, render_template, request, redirect, jsonify
import google.generativeai as genai

app = Flask(__name__)

ALLOWED_GROUP_ID = '120363425281087335@g.us'
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

model = None
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
    except:
        pass

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
    if not model: return fallback(text)
    try:
        prompt = "Identify shopping items in Hebrew. Categories: " + str(CATEGORY_ORDER) + ". Return ONLY JSON list: [{'name': 'item', 'category': 'cat'}]. Text: " + text
        response = model.generate_content(prompt)
        raw = response.text.strip()
        if "
http://googleusercontent.com/immersive_entry_chip/0

---

### 2. קובץ העיצוב: `templates/index.html`
```html
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>רשימת קניות</title>
    <style>
        body { font-family: system-ui, sans-serif; background: #f8fafc; margin: 0; padding: 0; direction: rtl; }
        .container { width: 100%; max-width: 800px; margin: 0 auto; background: white; min-height: 100vh; box-shadow: 0 0 20px rgba(0,0,0,0.05); }
        header { background: #4f46e5; color: white; padding: 40px 20px; text-align: center; }
        header h1 { font-size: 40px; margin: 0; }
        .input-box { padding: 30px; text-align: center; border-bottom: 2px solid #f1f5f9; }
        input { width: 90%; padding: 15px; font-size: 20px; border: 2px solid #ddd; border-radius: 10px; margin-bottom: 15px; }
        button { width: 90%; padding: 15px; font-size: 20px; background: #4f46e5; color: white; border: none; border-radius: 10px; cursor: pointer; font-weight: bold; }
        .cat-header { background: #f1f5f9; padding: 15px 25px; font-weight: 800; font-size: 20px; color: #64748b; border-right: 5px solid #4f46e5; }
        .item { display: flex; align-items: center; padding: 20px 25px; border-bottom: 1px solid #f1f5f9; text-decoration: none; color: #1e293b; }
        .checkbox { width: 30px; height: 30px; border: 3px solid #cbd5e1; border-radius: 50%; margin-left: 20px; flex-shrink: 0; }
        .checked-bg { background: #4f46e5; border-color: #4f46e5; }
        .text { font-size: 24px; font-weight: 600; }
        .done { text-decoration: line-through; opacity: 0.4; }
        .clear { display: block; width: 90%; margin: 30px auto; padding: 20px; background: #fff1f2; color: #e11d48; text-align: center; text-decoration: none; font-size: 20px; font-weight: 800; border-radius: 12px; border: 2px solid #fecdd3; }
    </style>
</head>
<body>
    <div class="container">
        <header><h1>רשימת קניות 🛒</h1></header>
        <div class="input-box">
            <form action="/add" method="POST"><input type="text" name="item_name" placeholder="להוסיף מוצר..."><br><button type="submit">הוסף</button></form>
        </div>
        <div>
            {% set ns = namespace(last_cat="") %}
            {% for item in items %}
                {% if item[2] != ns.last_cat %} <div class="cat-header">{{ item[2] }}</div> {% set ns.last_cat = item[2] %} {% endif %}
                <a href="/toggle/{{ item[0] }}" class="item">
                    <div class="checkbox {{ 'checked-bg' if item[3] == 1 }}"></div>
                    <span class="text {{ 'done' if item[3] == 1 }}">{{ item[1] }}</span>
                </a>
            {% endfor %}
        </div>
        {% if items %}<a href="/clear" class="clear">🗑️ נקה שנקנה</a>{% endif %}
    </div>
</body>
</html>
