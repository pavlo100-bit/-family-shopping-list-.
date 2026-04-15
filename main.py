from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
import os
import json
import google.generativeai as genai

app = Flask(__name__)

# הדפסה לווידוא שהשרת עלה
print("\n" + "="*50)
print("🚀 FAMILY SHOPPING LIST - VERSION 11.0 IS ONLINE")
print("="*50 + "\n", flush=True)

# הגדרות - וודא שהמפתח נמצא ב-Variables ב-Railway
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

def analyze_message(text):
    print(f"🔍 Analyzing: {text}", flush=True)
    if model:
        try:
            prompt = f"Identify products in Hebrew. Split by commas or 'and'. Clean prefixes like 'bring me'. Categories: {CATEGORY_ORDER}. Return JSON list: [{{'name': 'product', 'category': 'cat'}}]. Text: '{text}'"
            response = model.generate_content(prompt)
            raw = response.text.strip()
            if "
