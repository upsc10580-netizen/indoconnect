from flask import Flask, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "indoconnect_secret"

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE,
                  password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS posts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user TEXT,
                  content TEXT,
                  likes INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

init_db()

def page_template(title, content):
    return f"""
    <html>
    <head>
        <title>{title}</title>
        <style>
            body {{
                font-family: Arial;
                background:#f0f2f5;
                margin:0;
            }}
            nav {{
                background:#1877f2;
                color:white;
                padding:15px;
                display:flex;
                justify-content:space-between;
            }}
            .container {{
                width:50%;
                margin:auto;
                margin-top:20px;
            }}
            input {{
                width:100%;
                padding:10px;
                margin:5px 0;
            }}
            button {{
                padding:10px;
                background:#1877f2;
                color:white;
                border:none;
                cursor:pointer;
            }}
            .post {{
                background:white;
                padding:15px;
                margin-top:10px;
                border-radius:5px;
            }}
            a {{
                text-decoration:none;
                color:#1877f2;
            }}
        </style>
    </head>
    <body>
        <nav>
            <div><b>IndoConnect</b></div>
            <div>
                {"Logged in as: " + session['user'] + " | <a href='/logout' style='color:white;'>Logout</a>" if 'user' in session else ""}
            </div>
        </nav>
        <div class="container">
            {content}
        </div>
    </body>
    </html>
    """

@app.route('/')
def home():
    if 'user' not in session:
        return redirect('/login')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM posts ORDER BY id DESC")
    posts = c.fetchall()
    conn.close()

    post_html = """
    <form method="post" action="/post">
        <input name="content" placeholder="What's on your mind?" required>
        <button type="submit">Post</button>
    </form>
    <hr>
    """

    for post in posts:
        post_html += f"""
        <div class="post">
            <b>{post[1]}</b>
            <p>{post[2]}</p>
            ❤️ {post[3]} 
            <a href="/like/{post[0]}">Like</a>
        </div>
        """

    return page_template("Home", post_html)

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (username,password) VALUES (?,?)",(username,password))
            conn.commit()
            conn.close()
            return redirect('/login')
        except:
            return "Username already exists"

    content = """
    <h3>Signup</h3>
    <form method="post">
        <input name="username" placeholder="Username" required>
        <input name="password" type="password" placeholder="Password" required>
        <button>Signup</button>
    </form>
    <p>Already have account? <a href="/login">Login</a></p>
    """
    return page_template("Signup", content)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?",(username,password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user'] = username
            return redirect('/')
        else:
            return "Invalid Credentials"

    content = """
    <h3>Login</h3>
    <form method="post">
        <input name="username" placeholder="Username" required>
        <input name="password" type="password" placeholder="Password" required>
        <button>Login</button>
    </form>
    <p>New user? <a href="/signup">Signup</a></p>
    """
    return page_template("Login", content)

@app.route('/post', methods=['POST'])
def post():
    if 'user' not in session:
        return redirect('/login')
    content = request.form['content']
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO posts (user,content) VALUES (?,?)",(session['user'],content))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/like/<int:id>')
def like(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("UPDATE posts SET likes = likes + 1 WHERE id=?",(id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/login')

if __name__ == "__main__":
    app.run(debug=True)
