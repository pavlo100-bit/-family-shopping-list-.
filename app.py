from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "השרת של רשימת הקניות עובד! שלב 1 הצליח."

if __name__ == '__main__':
    app.run()