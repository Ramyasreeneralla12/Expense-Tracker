from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# ✅ Initialize the database on first request
@app.before_first_request
def init_db():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            purpose TEXT
        )
    ''')
    conn.commit()
    conn.close()

# ✅ Home page with filter options
@app.route('/')
def index():
    filter_option = request.args.get('filter', 'all')
    today = datetime.today().date()

    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()

    if filter_option == 'week':
        start = today - timedelta(days=today.weekday())
        c.execute("SELECT * FROM expenses WHERE date >= ? ORDER BY date DESC", (start.isoformat(),))
        expenses = c.fetchall()
        c.execute("SELECT SUM(amount) FROM expenses WHERE date >= ?", (start.isoformat(),))
    elif filter_option == 'month':
        start = today.replace(day=1)
        c.execute("SELECT * FROM expenses WHERE date >= ? ORDER BY date DESC", (start.isoformat(),))
        expenses = c.fetchall()
        c.execute("SELECT SUM(amount) FROM expenses WHERE date >= ?", (start.isoformat(),))
    elif filter_option == 'year':
        start = today.replace(month=1, day=1)
        c.execute("SELECT * FROM expenses WHERE date >= ? ORDER BY date DESC", (start.isoformat(),))
        expenses = c.fetchall()
        c.execute("SELECT SUM(amount) FROM expenses WHERE date >= ?", (start.isoformat(),))
    else:
        c.execute("SELECT * FROM expenses ORDER BY date DESC")
        expenses = c.fetchall()
        c.execute("SELECT SUM(amount) FROM expenses")

    total = c.fetchone()[0]
    conn.close()

    return render_template('index.html', expenses=expenses, total=total if total else 0, selected_filter=filter_option)

# ✅ Add expense route
@app.route('/add', methods=['POST'])
def add():
    amount = request.form['amount']
    date = request.form['date']
    purpose = request.form['purpose']

    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("INSERT INTO expenses (amount, date, purpose) VALUES (?, ?, ?)", (amount, date, purpose))
    conn.commit()
    conn.close()
    return redirect('/')

# ✅ Delete expense route
@app.route('/delete/<int:expense_id>')
def delete(expense_id):
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()
    return redirect('/')

# ✅ Health check route
@app.route('/health')
def health():
    return "✅ Flask app is running on Render!"

# ✅ Main block for Render deployment
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
