from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error
import hashlib
import os

app = Flask(__name__)
app.secret_key = 'cloud_quiz_secret_key_2024'

# ─── Database Configuration ───────────────────────────────────────────────────
DB_CONFIG = {
    'host': 'localhost',
    'database': 'cloud_quiz_db',
    'user': 'root',
    'password': 'Manish6022@'  # Change this to your MySQL password
}

def get_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"DB Error: {e}")
        return None

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('student_dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        confirm=request.form['confirm_password']
        role = request.form.get('role', 'student')

        if not username or not password:
            flash('All fields are required.', 'error')
            return render_template('register.html')

        conn = get_db()
        if not conn:
            flash('Database connection failed.', 'error')
            return render_template('register.html')

        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            flash('Username already exists.', 'error')
            conn.close()
            return render_template('register.html')
        if password == confirm:
            cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, hash_password(password))
        )
            conn.commit()
            conn.close()
            flash('Registration successful! Please login.', 'success')
        else:
            flash('Enter password is not match','error')
        
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        conn = get_db()
        if not conn:
            flash('Database connection failed.', 'error')
            return render_template('login.html')

        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM users WHERE username = %s AND password = %s",
            (username, hash_password(password))
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid credentials.', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ─── Student Routes ────────────────────────────────────────────────────────────

@app.route('/student')
def student_dashboard():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.id, a.score, a.total, a.taken_at
        FROM attempts a
        WHERE a.user_id = %s
        ORDER BY a.taken_at DESC
        LIMIT 5
    """, (session['user_id'],))
    attempts = cursor.fetchall()
    conn.close()

    return render_template('student_dashboard.html', attempts=attempts)

@app.route('/quiz/start')
def start_quiz():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM questions ORDER BY RAND() LIMIT 12")
    questions = cursor.fetchall()
    conn.close()

    if not questions:
        flash('No questions available yet. Please check back later.', 'error')
        return redirect(url_for('student_dashboard'))

    session['quiz_questions'] = [q['id'] for q in questions]
    session['current_q'] = 0
    session['answers'] = {}

    return redirect(url_for('quiz_question'))

@app.route('/quiz/question', methods=['GET', 'POST'])
def quiz_question():
    if 'user_id' not in session or 'quiz_questions' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        q_id = request.form.get('question_id')
        answer = request.form.get('answer')
        if q_id and answer:
            session['answers'][str(q_id)] = answer
            session['current_q'] += 1
            session.modified = True

    current = session['current_q']
    questions = session['quiz_questions']

    if current >= len(questions):
        return redirect(url_for('quiz_result'))

    q_id = questions[current]
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM questions WHERE id = %s", (q_id,))
    question = cursor.fetchone()
    conn.close()

    return render_template('quiz_question.html',
                           question=question,
                           current=current + 1,
                           total=len(questions))

@app.route('/quiz/result')
def quiz_result():
    if 'user_id' not in session or 'quiz_questions' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    score = 0
    results = []
    for q_id in session['quiz_questions']:
        cursor.execute("SELECT * FROM questions WHERE id = %s", (q_id,))
        q = cursor.fetchone()
        user_ans = session['answers'].get(str(q_id), '')
        correct = (user_ans == q['correct_option'])
        if correct:
            score += 1
        results.append({
            'question': q['question_text'],
            'user_answer': user_ans,
            'correct_answer': q['correct_option'],
            'correct': correct
        })

    total = len(session['quiz_questions'])
    cursor.execute(
        "INSERT INTO attempts (user_id, score, total) VALUES (%s, %s, %s)",
        (session['user_id'], score, total)
    )
    conn.commit()
    conn.close()

    # Clear quiz session
    session.pop('quiz_questions', None)
    session.pop('current_q', None)
    session.pop('answers', None)

    return render_template('quiz_result.html', score=score, total=total, results=results)

# ─── Admin Routes ──────────────────────────────────────────────────────────────

@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) as count FROM questions")
    q_count = cursor.fetchone()['count']
    cursor.execute("SELECT COUNT(*) as count FROM users WHERE role='student'")
    s_count = cursor.fetchone()['count']
    cursor.execute("SELECT COUNT(*) as count FROM attempts")
    a_count = cursor.fetchone()['count']
    cursor.execute("SELECT * FROM questions ORDER BY created_at DESC")
    questions = cursor.fetchall()
    conn.close()

    return render_template('admin_dashboard.html',
                           q_count=q_count, s_count=s_count,
                           a_count=a_count, questions=questions)

@app.route('/admin/add-question', methods=['GET', 'POST'])
def add_question():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        text = request.form['question_text'].strip()
        opt_a = request.form['option_a'].strip()
        opt_b = request.form['option_b'].strip()
        opt_c = request.form['option_c'].strip()
        opt_d = request.form['option_d'].strip()
        correct = request.form['correct_option']

        if not all([text, opt_a, opt_b, opt_c, opt_d, correct]):
            flash('All fields are required.', 'error')
            return render_template('add_question.html')

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO questions (question_text, option_a, option_b, option_c, option_d, correct_option)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (text, opt_a, opt_b, opt_c, opt_d, correct))
        conn.commit()
        conn.close()
        flash('Question added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('add_question.html')

@app.route('/admin/delete-question/<int:q_id>', methods=['POST'])
def delete_question(q_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM questions WHERE id = %s", (q_id,))
    conn.commit()
    conn.close()
    flash('Question deleted.', 'success')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)