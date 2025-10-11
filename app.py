from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_bcrypt import Bcrypt
from config import get_connection
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
bcrypt = Bcrypt(app)

# 🏠 Home Page
@app.route('/')
def home():
    return render_template('home.html')

# 🧍 Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
            conn.commit()
            flash("Registration successful! Please log in.")
            return redirect(url_for('login'))
        except:
            flash("Email already exists.")
        finally:
            cursor.close()
            conn.close()
    return render_template('register.html')

# 🔐 Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and bcrypt.check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            flash("Logged-In Successfully.")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password.")
    return render_template('login.html')

# 🚪 Logout
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged-out successfully.")
    return redirect(url_for('home'))

# 📊 Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    page = int(request.args.get('page', 1))
    per_page = 5
    offset = (page - 1) * per_page

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Count total rows
    cursor.execute("SELECT COUNT(*) as count FROM expenses WHERE user_id=%s", (session['user_id'],))
    total_count = cursor.fetchone()['count']

    # Descending order, pagination applied
    cursor.execute(
        "SELECT * FROM expenses WHERE user_id=%s ORDER BY date DESC LIMIT %s OFFSET %s",
        (session['user_id'], per_page, offset)
    )
    expenses = cursor.fetchall()

    # Fetch user info for greeting
    cursor.execute("SELECT * FROM users WHERE id=%s", (session['user_id'],))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    total = sum([float(exp['amount']) for exp in expenses if exp['amount'] != ''])
    total_pages = max(1, (total_count + per_page - 1) // per_page)
    
    return render_template(
        'dashboard.html',
        expenses=expenses,
        total_expense=total,
        user=user,
        page=page,
        total_pages=total_pages
    )

# ➕ Add Expense
@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        amount = request.form['amount']
        category = request.form['category']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO expenses (user_id, title, amount, category, date) VALUES (%s, %s, %s, %s, %s)",
                       (session['user_id'], title, amount, category, date))
        conn.commit()
        cursor.close()
        conn.close()

        flash("Expense added successfully!")
        return redirect(url_for('dashboard'))
    return render_template('add_expense.html')

# 👤 Profile
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id=%s", (session['user_id'],))
    user = cursor.fetchone()

    cursor.execute("SELECT SUM(amount) as total_expense FROM expenses WHERE user_id=%s", (session['user_id'],))
    total_expense = cursor.fetchone()['total_expense'] or 0
    cursor.close()
    conn.close()
    
    return render_template('profile.html', user=user, total_expense=total_expense)

@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id=%s", (session['user_id'],))
    user = cursor.fetchone()

    if request.method == 'POST':
        new_name = request.form['new_name']
        password = request.form['password']

        # Check if current password matches
        if not user or not bcrypt.check_password_hash(user['password'], password):
            flash("Password is incorrect.")
            cursor.close()
            conn.close()
            return redirect(url_for('update_profile'))

        # Update profile name
        cursor.execute("UPDATE users SET name=%s WHERE id=%s", (new_name, session['user_id']))
        conn.commit()

        # Update session display name
        session['user_name'] = new_name

        flash("Profile updated successfully.")
        cursor.close()
        conn.close()
        return redirect(url_for('profile'))

    cursor.close()
    conn.close()
    return render_template('update_profile.html', user=user)

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_new_password = request.form['confirm_new_password']

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT password FROM users WHERE id=%s", (session['user_id'],))
        user = cursor.fetchone()

        if not user or not bcrypt.check_password_hash(user['password'], current_password):
            flash("Current password is incorrect.")
            cursor.close()
            conn.close()
            return redirect(url_for('change_password'))

        if new_password != confirm_new_password:
            flash("New passwords do not match.")
            cursor.close()
            conn.close()
            return redirect(url_for('change_password'))

        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        cursor.execute("UPDATE users SET password=%s WHERE id=%s", (hashed_password, session['user_id']))
        conn.commit()
        cursor.close()
        conn.close()

        # Clear session and redirect to login after password change
        session.clear()
        flash("Password updated successfully! Please log in again.")
        return redirect(url_for('login'))

    return render_template('change_password.html')

if __name__ == '__main__':
    app.run(debug=True)
