from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3, random

app = Flask(__name__)
app.secret_key = "your_secret_key"

USERNAME = "Deeksha"
PASSWORD = "mypassword"

def init_db():
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS habits
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  date TEXT,
                  category TEXT,
                  streak INTEGER DEFAULT 0,
                  progress INTEGER DEFAULT 0,
                  user_id INTEGER)''')
    conn.commit()
    conn.close()

init_db()

quotes = [
    "🌟 Keep pushing forward!",
    "🔥 Consistency builds success!",
    "💪 One step at a time!",
    "🏆 Small wins lead to big victories!",
    "📈 Progress, not perfection!"
]

@app.route('/')
def landing():
    return render_template('landing.html', title="Welcome")

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USERNAME and password == PASSWORD:
            session['user_id'] = 1
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash("❌ Invalid credentials!")
    return render_template('login.html', title="Login")

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    quote = random.choice(quotes)
    return render_template('dashboard.html', title="Dashboard", username=session['username'], quote=quote)

@app.route('/habits')
def habits():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()
    c.execute("SELECT * FROM habits WHERE user_id=?", (session['user_id'],))
    habits = c.fetchall()
    conn.close()
    total = len(habits)
    longest = max([h[4] for h in habits], default=0)
    average = int(sum([h[5] for h in habits])/total) if total>0 else 0
    return render_template('habits.html', title="Habits", habits=habits,
                           total=total, longest=longest, average=average)

@app.route('/add', methods=['POST'])
def add_habit():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    name = request.form['name']
    date = request.form['date']
    category = request.form['category']
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()
    c.execute("INSERT INTO habits (name,date,category,streak,progress,user_id) VALUES (?,?,?,?,?,?)",
              (name,date,category,0,0,session['user_id']))
    conn.commit()
    conn.close()
    flash("✨ New habit added!")
    return redirect(url_for('habits'))

@app.route('/checkin/<int:habit_id>', methods=['POST'])
def checkin(habit_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()
    c.execute("UPDATE habits SET streak=streak+1, progress=progress+10 WHERE id=? AND user_id=?",
              (habit_id,session['user_id']))
    conn.commit()
    conn.close()
    flash("🎉 Great job! Progress added for today!|confetti")
    return redirect(url_for('habits'))

@app.route('/delete/<int:habit_id>', methods=['POST'])
def delete_habit(habit_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()
    c.execute("DELETE FROM habits WHERE id=? AND user_id=?", (habit_id,session['user_id']))
    conn.commit()
    conn.close()
    flash("🗑️ Habit deleted!")
    return redirect(url_for('habits'))

@app.route('/analytics')
def analytics():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()
    c.execute("SELECT name,streak,progress,category FROM habits WHERE user_id=?",(session['user_id'],))
    habits = c.fetchall()
    conn.close()
    badges=[]
    for name,streak,prog,cat in habits:
        if streak>=7: badges.append(f"🔥 {name}: 7‑day streak")
        if streak>=30: badges.append(f"🏆 {name}: 30‑day milestone badge unlocked!")
        if streak>=100: badges.append(f"🥇 {name}: 100‑day champion")
    return render_template('analytics.html', title="Analytics", habits=habits, badges=badges)

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*),MAX(streak),AVG(progress) FROM habits WHERE user_id=?",(session['user_id'],))
    stats = c.fetchone()
    conn.close()
    return render_template('profile.html', title="Profile", username=session['username'],
                           total_habits=stats[0] or 0, longest_streak=stats[1] or 0,
                           average_progress=int(stats[2]) if stats[2] else 0)

@app.route('/settings')
def settings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('settings.html', title="Settings")

@app.route('/toggle-dark', methods=['POST'])
def toggle_dark():
    if 'dark_mode' in session:
        session['dark_mode'] = not session['dark_mode']
    else:
        session['dark_mode'] = True
    return redirect(request.referrer or url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__=="__main__":
    app.run(debug=True)