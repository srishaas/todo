from flask import Flask, render_template, request, redirect, url_for, session
import pymysql

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection
def get_db_connection():
    return pymysql.connect(host='localhost', user='root', password='', db='todo_db', cursorclass=pymysql.cursors.DictCursor)

# Home Route
@app.route('/')
def home():
    if 'user' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE username=%s", (session['user'],))
        tasks = cursor.fetchall()
        conn.close()
        return render_template('index.html', tasks=tasks)
    return redirect('/login')

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        conn.close()
        return redirect('/login')
    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['user'] = username
            return redirect('/')
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

# Add Task
@app.route('/add', methods=['POST'])
def add():
    task = request.form['task']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (task, complete, username) VALUES (%s, %s, %s)", (task, False, session['user']))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/edit/<int:task_id>', methods=['GET']) #GET
def show_edit(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE username=%s", (session['user'],))
    tasks = cursor.fetchall()
    conn.close()
    return render_template('index.html', tasks=tasks, edit_id=task_id)


# Update Task (complete)
@app.route('/update/<int:task_id>', methods=['POST']) #POST
def update(task_id):
    new_task = request.form['task']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET task = %s WHERE id = %s AND username = %s", (new_task, task_id, session['user']))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/complete/<int:task_id>')
def complete(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET complete = NOT complete WHERE id = %s AND username = %s", (task_id, session['user']))
    conn.commit()
    conn.close()
    return redirect('/')

# Delete Task
@app.route('/delete/<int:task_id>')
def delete(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
