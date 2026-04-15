<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>רשימת קניות משפחתית</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Assistant', sans-serif; background-color: #f3f4f6; }
        .item-checked { text-decoration: line-through; color: #9ca3af; }
        .category-header { background: #e5e7eb; padding: 4px 12px; font-weight: bold; border-radius: 6px; margin-top: 12px; }
    </style>
</head>
<body class="p-4">
    <div class="max-w-md mx-auto bg-white rounded-xl shadow-md overflow-hidden p-6">
        <h1 class="text-2xl font-bold text-center mb-6 text-indigo-600">🛒 רשימת קניות משפחתית</h1>
        
        <form action="/add" method="POST" class="mb-6 flex gap-2">
            <input type="text" name="item_name" placeholder="הוסף מוצר..." class="flex-1 border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-400">
            <button type="submit" class="bg-indigo-600 text-white px-4 py-2 rounded-lg font-bold">הוסף</button>
        </form>

        <div class="space-y-1">
            {% set last_cat = "" %}
            {% for item in items %}
                {% if item[2] != last_cat %}
                    <div class="category-header text-sm text-gray-600">{{ item[2] }}</div>
                    {% set last_cat = item[2] %}
                {% endif %}
                
                <div class="flex items-center justify-between p-3 border-b last:border-0">
                    <a href="/toggle/{{ item[0] }}" class="flex-1 flex items-center gap-3">
                        <div class="w-6 h-6 border-2 rounded-full flex items-center justify-center {{ 'bg-green-500 border-green-500' if item[3] == 1 else 'border-gray-300' }}">
                            {% if item[3] == 1 %}
                                <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path></svg>
                            {% endif %}
                        </div>
                        <span class="text-lg {{ 'item-checked' if item[3] == 1 }}">{{ item[1] }}</span>
                    </a>
                </div>
            {% endfor %}
        </div>

        {% if items %}
        <div class="mt-8">
            <a href="/clear" class="block w-full text-center py-3 bg-red-100 text-red-600 rounded-lg font-bold hover:bg-red-200 transition">
                🗑️ נקה מוצרים שנקנו
            </a>
        </div>
        {% endif %}
    </div>
    
    <div class="text-center mt-6 text-gray-400 text-xs">
        מחובר לקבוצה המשפחתית בוואטסאפ 🟢
    </div>
</body>
</html>
