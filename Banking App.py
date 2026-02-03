from flask import Flask, request, redirect, session, flash, render_template_string
import mysql.connector

app = Flask(__name__)
app.secret_key = "your_secret_key"

# ------------------ DATABASE CONNECTION ------------------
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="tharani",
        database="bank"
    )

# ------------------ USER FUNCTIONS ------------------
def create_account(username, email, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, email, password, balance) VALUES (%s, %s, %s, %s)",
        (username, email, password, 0.0)
    )
    conn.commit()
    cursor.close()
    conn.close()

def login_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_id, username, balance FROM users WHERE email=%s AND password=%s",
        (email, password)
    )
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

# ------------------ TRANSACTION FUNCTIONS ------------------
def deposit(user_id, amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = balance + %s WHERE user_id = %s", (amount, user_id))
    cursor.execute(
        "INSERT INTO transactions (user_id, transaction_type, amount, details) VALUES (%s, %s, %s, %s)",
        (user_id, "Deposit", amount, "Self Deposit")
    )
    conn.commit()
    cursor.close()
    conn.close()

def withdraw(user_id, amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id=%s", (user_id,))
    balance = cursor.fetchone()[0]
    if balance >= amount:
        cursor.execute("UPDATE users SET balance = balance - %s WHERE user_id=%s", (amount, user_id))
        cursor.execute(
            "INSERT INTO transactions (user_id, transaction_type, amount, details) VALUES (%s, %s, %s, %s)",
            (user_id, "Withdrawal", amount, "Self Withdrawal")
        )
        conn.commit()
        success = True
    else:
        success = False
    cursor.close()
    conn.close()
    return success

def view_transactions(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT transaction_type, amount, details, date_time FROM transactions WHERE user_id=%s ORDER BY date_time DESC",
        (user_id,)
    )
    transactions = cursor.fetchall()
    cursor.close()
    conn.close()
    return transactions

# ------------------ SINGLE-FILE HTML TEMPLATE ------------------
template = """
<!DOCTYPE html>
<html>
<head>
    <title>SBIA Bank</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { padding: 20px; max-width: 800px; margin: auto; }
        .card { margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        {% for msg in messages %}
          <div class="alert alert-info">{{ msg }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}

    {% if 'user_id' in session %}
        <h2>Welcome, {{ session['username'] }}</h2>
        <div class="card p-3">
            <h5>Balance: ₹{{ session['balance'] }}</h5>
        </div>

        <div class="card p-3">
            <h5>Deposit Money</h5>
            <form method="post" action="/deposit" class="d-flex gap-2">
                <input type="number" step="0.01" name="amount" class="form-control" placeholder="Amount" required>
                <button class="btn btn-success" type="submit">Deposit</button>
            </form>
        </div>

        <div class="card p-3">
            <h5>Withdraw Money</h5>
            <form method="post" action="/withdraw" class="d-flex gap-2">
                <input type="number" step="0.01" name="amount" class="form-control" placeholder="Amount" required>
                <button class="btn btn-danger" type="submit">Withdraw</button>
            </form>
        </div>

        <div class="card p-3">
            <h5>Transaction History</h5>
            {% if transactions %}
                <ul class="list-group">
                {% for t in transactions %}
                    <li class="list-group-item">{{ t[3] }} - {{ t[0] }}: ₹{{ t[1] }} ({{ t[2] }})</li>
                {% endfor %}
                </ul>
            {% else %}
                <p>No transactions yet.</p>
            {% endif %}
        </div>

        <a href="/logout" class="btn btn-secondary mt-3">Logout</a>

    {% else %}
        {% if page == 'home' %}
            <h1>Welcome to SBIA Bank</h1>
            <a href="/register" class="btn btn-primary">Register</a>
            <a href="/login" class="btn btn-success">Login</a>

        {% elif page == 'register' %}
            <h2>Register</h2>
            <form method="post">
                <input type="text" name="username" class="form-control mb-2" placeholder="Name" required>
                <input type="email" name="email" class="form-control mb-2" placeholder="Email" required>
                <input type="password" name="password" class="form-control mb-2" placeholder="Password" required>
                <button type="submit" class="btn btn-primary">Register</button>
            </form>
            <a href="/login" class="btn btn-link">Already have an account? Login</a>

        {% elif page == 'login' %}
            <h2>Login</h2>
            <form method="post">
                <input type="email" name="email" class="form-control mb-2" placeholder="Email" required>
                <input type="password" name="password" class="form-control mb-2" placeholder="Password" required>
                <button type="submit" class="btn btn-success">Login</button>
            </form>
            <a href="/register" class="btn btn-link">Register</a>
        {% endif %}
    {% endif %}
    </div>
</body>
</html>
"""

# ------------------ FLASK ROUTES ------------------
@app.route('/')
def home():
    return render_template_string(template, page='home')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        create_account(request.form['username'], request.form['email'], request.form['password'])
        flash("Account created successfully!")
        return redirect('/login')
    return render_template_string(template, page='register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = login_user(request.form['email'], request.form['password'])
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['balance'] = user[2]
            return redirect('/dashboard')
        else:
            flash("Invalid email or password!")
    return render_template_string(template, page='login')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    transactions = view_transactions(session['user_id'])
    return render_template_string(template, transactions=transactions)

@app.route('/deposit', methods=['POST'])
def deposit_route():
    amount = float(request.form['amount'])
    deposit(session['user_id'], amount)
    session['balance'] = float(session['balance']) + amount
    flash(f"Deposited ₹{amount} successfully!")
    return redirect('/dashboard')

@app.route('/withdraw', methods=['POST'])
def withdraw_route():
    amount = float(request.form['amount'])
    success = withdraw(session['user_id'], amount)
    if success:
        session['balance'] = float(session['balance']) - amount
        flash(f"Withdrawn ₹{amount} successfully!")
    else:
        flash("Insufficient balance!")
    return redirect('/dashboard')


@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!")
    return redirect('/login')

if __name__ == "__main__":
    app.run(debug=True)
