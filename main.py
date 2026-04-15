import sys
from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
import os
import json

# הדפסה שתופיע בראש הלוגים לווידוא גרסה
print("\n" + "#"*60, flush=True)
print("###  SYSTEM RESTORED: VERSION 8.0 (FAMILY LIST)       ###", flush=True)
print("###  AI POWERED & MULTI-ITEM SPLITTING ENABLED        ###", flush=True)
print("#"*60 + "\n", flush=True)

try:
    import google.generativeai as genai
    print("✅ AI Library (google-generativeai) Loaded", flush=True)
except ImportError:
    print("❌ Error: google-generativeai missing! Check requirements.txt", flush=True)

app = Flask(__name__)

# --- הגדרות קבוצה ומפתחות ---
# ה-ID של הקבוצה המשפחתית שלך
ALLOWED_GROUP_ID = '120363425281087335@g.us'
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# אתחול ה-AI
model = None
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("🤖 Gemini AI Engine Ready", flush=True)
    except Exception as e:
        print(f"❌ AI Init Error: {e}", flush=True)
else:
    print("⚠️ Warning: GEMINI_API_KEY missing in Railway Variables", flush=True)

# קטגוריות
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
    print(f"🔍 Analyzing message: {text}", flush=True)
    
    if model:
        try:
            prompt = f"""
            Identify shopping products in this Hebrew text. 
            STRICT RULES:
            1. Split multiple items (vav-hahibur or commas). 
            2. Clean words like 'תביא', 'רק', 'לי', 'בבקשה', 'תקנה'.
            3. Fix prefixes: 'ורסק' becomes 'רסק', 'וחלב' becomes 'חלב'.
            4. Categories: {CATEGORY_ORDER}. 
            Return JSON list: [{{"name": "product", "category": "cat"}}]
            Text: "{text}"
            """
            response = model.generate_content(prompt)
            raw = response.text.strip()
            if "
