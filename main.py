import os
import json
import sqlite3
from flask import Flask, render_template, request, redirect, jsonify
import google.generativeai as genai

app = Flask(__name__)

# סימן זיהוי גרסה בלוגים
print("\n" + "="*50)
print("🚀 FAMILY LIST - VERSION 25.0 - WEBHOOK RESTORED")
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
        print("✅ AI Engine Ready", flush=True)
    except Exception as e:
        print(f"❌ AI Init Error: {e}", flush=True)

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
    print(f"🔍 Analyzing: {text}", flush=True)
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

### למה זה יעבוד עכשיו?
כי החזרנו את הפונקציה `def webhook()` לקוד. בלעדיה, השרת מחזיר שגיאת **404** ל-Green API כי הוא פשוט לא יודע מה לעשות עם המידע שמגיע מהוואטסאפ.

**תעדכן את שניהם עכשיו, וזה יחזור לעבוד כמו קסם.** תגיד לי כשיש ירוק ב-Railway!
