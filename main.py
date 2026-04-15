import sys
from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
import os
import json

# הדפסה לווידוא שהשרת עלה
print("\n" + "#"*60, flush=True)
print("###  SYSTEM RESTORED: VERSION 9.0 (FAMILY LIST)       ###", flush=True)
print("#"*60 + "\n", flush=True)

try:
    import google.generativeai as genai
    print("✅ AI Library Loaded", flush=True)
except ImportError:
    print("❌ Error: google-generativeai missing", flush=True)

app = Flask(__name__)

# הגדרות
ALLOWED_GROUP_ID = '120363425281087335@g.us'
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# אתחול AI
model = None
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("🤖 Gemini AI Ready", flush=True)
    except Exception as e:
        print(f"❌ AI Init Error: {e}", flush=True)

CATEGORY_ORDER = [
    'יבשים ושימורים', 'מוצרי חלב וביצים', 'בשר ודגים', 'פירות וירקות',
    'מאפייה', 'קפואים', 'חטיפים ומתוקים', 'משקאות', 'ניקיון ותחזוקה',
    'פארם והיגיינה', 'כללי/אחר'
]

def init_db():
    conn = sqlite3.connect('shopping.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS items 
                 (id INTEGER PRIMARY KEY, name TEXT, category TEXT, status INTEGER)''')
    conn.commit()
    conn.close()

init_db()

def analyze_message_logic(text):
    if model:
        try:
            prompt = f"Identify shopping products in Hebrew. Split items by commas or 'and'. Clean prefixes. Categories: {CATEGORY_ORDER}. Return JSON list: [{{'name': 'product', 'category': 'cat'}}]. Text: '{text}'"
            response = model.generate_content(prompt)
            raw = response.text.strip()
            if "
http://googleusercontent.com/immersive_entry_chip/0
http://googleusercontent.com/immersive_entry_chip/1

---

### מה לעשות עכשיו?
1. **GitHub:** תעדכן את שלושת הקבצים (ב-Repo של המשפחה!).
2. **Railway:** כנס ל-Deployments, תוודא שהפעם הוא מצליח (Active ירוק).
3. **בדיקה:** ברגע שזה ירוק, האתר אמור לחזור לעבוד.

תעדכן אותי אם הצלחת להעלות הכל!
