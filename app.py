from flask import Flask, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

DATABASE = "users.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def page(content):
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Prem | Cybersecurity</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            font-family: Arial, sans-serif;
            background: #05070a;
            color: white;
        }}

        nav {{
            padding: 18px 7%;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #080d12;
            border-bottom: 1px solid #1f2937;
        }}

        nav h2 {{
            color: #00ff88;
            margin: 0;
        }}

        nav a {{
            color: #00ff88;
            text-decoration: none;
            margin-left: 15px;
        }}

        .container {{
            max-width: 900px;
            margin: auto;
            padding: 70px 20px;
            text-align: center;
        }}

        h1 {{
            font-size: 48px;
            color: #00ff88;
        }}

        h2 {{
            color: #00ff88;
        }}

        p {{
            color: #9ca3af;
            line-height: 1.7;
        }}

        .button {{
            display: inline-block;
            padding: 13px 25px;
            margin: 8px;
            background: #00ff88;
            color: #03120a;
            border-radius: 8px;
            text-decoration: none;
            font-weight: bold;
        }}

        .button.secondary {{
            background: transparent;
            color: #00ff88;
            border: 1px solid #00ff88;
        }}

        .card {{
            max-width: 450px;
            margin: auto;
            padding: 30px;
            background: #0d1117;
            border: 1px solid #1f2937;
            border-radius: 12px;
        }}

        input {{
            width: 100%;
            padding: 14px;
            margin: 10px 0;
            border-radius: 7px;
            border: 1px solid #374151;
            background: #05070a;
            color: white;
        }}

        button {{
            width: 100%;
            padding: 14px;
            margin-top: 10px;
            border: none;
            border-radius: 7px;
            background: #00ff88;
            color: #03120a;
            font-weight: bold;
            cursor: pointer;
        }}

        .terminal {{
            background: #000;
            border: 1px solid #00ff88;
            border-radius: 10px;
            padding: 20px;
            text-align: left;
            color: #00ff88;
            font-family: monospace;
        }}

        footer {{
            text-align: center;
            padding: 30px;
            border-top: 1px solid #1f2937;
            color: #6b7280;
        }}
    </style>
</head>

<body>

<nav>
    <h2>PREM_SEC</h2>

    <div>
        <a href="/">Home</a>
        <a href="/register">Create Account</a>
        <a href="/login">Login</a>
    </div>
</nav>

<div class="container">
    {content}
</div>

<footer>
    © 2026 Prem Gangaputraa | Cybersecurity
</footer>

</body>
</html>
"""


@app.route("/")
def home():

    if "username" in session:
        account_button = f"""
        <a class="button" href="/dashboard">Dashboard</a>
        <a class="button secondary" href="/logout">Logout</a>
        """
    else:
        account_button = """
        <a class="button" href="/register">Create Account</a>
        <a class="button secondary" href="/login">Login</a>
        """

    return page(f"""
        <h1>PREM // CYBERSECURITY</h1>

        <h2>B.Tech Cybersecurity Student</h2>

        <p>
            Python • Linux • Networking • Web Security
        </p>

        <div class="terminal">
            $ whoami<br>
            prem<br><br>

            $ status<br>
            Learning Cybersecurity...
        </div>

        <br>

        {account_button}
    """)


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        if not username or not password:
            return page("""
                <h2>Please fill all fields.</h2>
                <a class="button" href="/register">Try Again</a>
            """)

        hashed_password = generate_password_hash(password)

        try:
            conn = get_db()

            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password)
            )

            conn.commit()
            conn.close()

            return redirect("/login")

        except sqlite3.IntegrityError:

            return page("""
                <h2>Username already exists.</h2>
                <a class="button" href="/register">Try Again</a>
            """)

    return page("""
        <div class="card">

            <h2>CREATE ACCOUNT</h2>

            <p>Create your cybersecurity portfolio account.</p>

            <form method="POST">

                <input
                    type="text"
                    name="username"
                    placeholder="Username"
                    required
                >

                <input
                    type="password"
                    name="password"
                    placeholder="Password"
                    required
                >

                <button type="submit">
                    Create Account
                </button>

            </form>

            <p>
                Already have an account?
                <a href="/login" style="color:#00ff88;">
                    Login
                </a>
            </p>

        </div>
    """)


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(user["password"], password):

            session["username"] = username

            return redirect("/dashboard")

        return page("""
            <h2>Invalid username or password.</h2>

            <a class="button" href="/login">
                Try Again
            </a>
        """)

    return page("""
        <div class="card">

            <h2>LOGIN</h2>

            <form method="POST">

                <input
                    type="text"
                    name="username"
                    placeholder="Username"
                    required
                >

                <input
                    type="password"
                    name="password"
                    placeholder="Password"
                    required
                >

                <button type="submit">
                    Login
                </button>

            </form>

            <p>
                Don't have an account?
                <a href="/register" style="color:#00ff88;">
                    Create Account
                </a>
            </p>

        </div>
    """)


@app.route("/dashboard")
def dashboard():

    if "username" not in session:
        return redirect("/login")

    username = session["username"]

    return page(f"""
        <h1>Welcome, {username} 👨‍💻</h1>

        <h2>Cybersecurity Dashboard</h2>

        <p>
            You are successfully logged in.
        </p>

        <div class="terminal">
            $ user<br>
            {username}<br><br>

            $ security_status<br>
            ACCOUNT_ACTIVE<br><br>

            $ learning_status<br>
            CYBERSECURITY_IN_PROGRESS
        </div>

        <br>

        <a class="button" href="/">
            Home
        </a>

        <a class="button secondary" href="/logout">
            Logout
        </a>
    """)


@app.route("/logout")
def logout():

    session.pop("username", None)

    return redirect("/")


init_db()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
