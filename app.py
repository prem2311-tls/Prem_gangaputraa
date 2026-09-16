import os
from flask import Flask, request, redirect, session

from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.config["PERMANENT_SESSION_LIFETIME"] = 60 * 60 * 24 * 30
app.config["SESSION_PERMANENT"] = True
app.secret_key = os.environ.get("SECRET_KEY", "prem-local-development-key")
DATABASE = "users.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/typing")
def typing():
    return page("""
<style>
.typing-wrap{
    max-width:1100px;
    margin:40px auto;
    padding:20px;
}
.typing-title{
    text-align:center;
    font-size:clamp(32px,6vw,64px);
    font-weight:900;
    letter-spacing:2px;
    margin-bottom:8px;
}
.typing-sub{
    text-align:center;
    opacity:.7;
    margin-bottom:30px;
}
.game-panel{
    background:rgba(10,18,25,.88);
    border:1px solid rgba(0,255,180,.25);
    border-radius:24px;
    padding:25px;
    box-shadow:0 0 40px rgba(0,255,180,.08);
}
.levels{
    display:flex;
    gap:10px;
    flex-wrap:wrap;
    justify-content:center;
    margin-bottom:25px;
}
.level-btn{
    border:1px solid rgba(0,255,180,.25);
    background:#091119;
    color:#9fffe0;
    padding:10px 15px;
    border-radius:12px;
    cursor:pointer;
}
.level-btn.active{
    background:#00c98b;
    color:#00130d;
    font-weight:800;
}
.level-btn.locked{
    opacity:.35;
    cursor:not-allowed;
}
.stats{
    display:grid;
    grid-template-columns:repeat(6,1fr);
    gap:10px;
    margin-bottom:25px;
}
.stat{
    background:#071018;
    border:1px solid rgba(0,255,180,.15);
    border-radius:15px;
    padding:14px;
    text-align:center;
}
.stat small{
    display:block;
    opacity:.55;
    margin-bottom:5px;
}
.stat strong{
    font-size:20px;
}
.target-box{
    min-height:170px;
    display:flex;
    flex-direction:column;
    justify-content:center;
    align-items:center;
    background:radial-gradient(circle,#0b2420,#050b10 65%);
    border:1px solid rgba(0,255,180,.18);
    border-radius:20px;
    margin-bottom:20px;
}
.target-label{
    font-size:12px;
    letter-spacing:3px;
    opacity:.5;
}
.target{
    font-size:clamp(30px,7vw,65px);
    font-weight:900;
    color:#7dffd7;
    text-shadow:0 0 20px rgba(0,255,180,.45);
    margin-top:12px;
    word-break:break-word;
    text-align:center;
    padding:0 15px;
}
#typingInput{
    width:100%;
    box-sizing:border-box;
    padding:18px;
    border-radius:15px;
    border:1px solid rgba(0,255,180,.3);
    background:#03080c;
    color:#fff;
    outline:none;
    font-size:20px;
    text-align:center;
}
#typingInput:focus{
    border-color:#00e6a0;
    box-shadow:0 0 20px rgba(0,255,180,.15);
}
.controls{
    display:flex;
    gap:12px;
    justify-content:center;
    flex-wrap:wrap;
    margin-top:18px;
}
.game-btn{
    border:0;
    border-radius:13px;
    padding:13px 22px;
    cursor:pointer;
    font-weight:800;
    background:#00d995;
    color:#00150e;
}
.game-btn.secondary{
    background:#111c25;
    color:#9fffe0;
    border:1px solid rgba(0,255,180,.2);
}
.message{
    text-align:center;
    min-height:25px;
    margin-top:15px;
    color:#9fffe0;
}
.progress{
    height:8px;
    background:#111a20;
    border-radius:20px;
    overflow:hidden;
    margin-top:20px;
}
.progress-bar{
    height:100%;
    width:0%;
    background:#00d995;
    transition:.25s;
}
.instructions{
    margin-top:25px;
    padding:18px;
    border-radius:15px;
    background:#071018;
    border:1px solid rgba(0,255,180,.1);
    opacity:.8;
    line-height:1.7;
}
@media(max-width:750px){
    .stats{
        grid-template-columns:repeat(3,1fr);
    }
}
@media(max-width:430px){
    .typing-wrap{padding:10px}
    .game-panel{padding:15px}
    .stats{gap:6px}
    .stat{padding:10px 5px}
}
</style>

<div class="typing-wrap">

    <div class="typing-title">PREM TYPING QUEST</div>
    <div class="typing-sub">
        Train your speed. Build your accuracy. Become a typing pro.
    </div>

    <div class="game-panel">

        <div class="levels" id="levels"></div>

        <div class="stats">
            <div class="stat">
                <small>LEVEL</small>
                <strong id="levelName">Beginner</strong>
            </div>
            <div class="stat">
                <small>❤️ LIVES</small>
                <strong id="lives">3</strong>
            </div>
            <div class="stat">
                <small>⚡ SCORE</small>
                <strong id="score">0</strong>
            </div>
            <div class="stat">
                <small>🔥 COMBO</small>
                <strong id="combo">0</strong>
            </div>
            <div class="stat">
                <small>🚀 WPM</small>
                <strong id="wpm">0</strong>
            </div>
            <div class="stat">
                <small>🎯 ACCURACY</small>
                <strong id="accuracy">100%</strong>
            </div>
        </div>

        <div class="target-box">
            <div class="target-label">MISSION TARGET</div>
            <div class="target" id="target">PRESS START</div>
        </div>

        <input
            id="typingInput"
            type="text"
            placeholder="Type the target and press ENTER..."
            autocomplete="off"
            autocapitalize="none"
            spellcheck="false"
            disabled
        >

        <div class="progress">
            <div class="progress-bar" id="progressBar"></div>
        </div>

        <div class="message" id="message">
            Select a level and start your mission.
        </div>

        <div class="controls">
            <button class="game-btn" id="startBtn">
                START MISSION
            </button>

            <button class="game-btn secondary" id="resetBtn">
                RESET PROGRESS
            </button>
        </div>

        <div class="instructions">
            <b>🎮 HOW TO PLAY</b><br>
            1. Choose an unlocked level.<br>
            2. Press <b>START MISSION</b>.<br>
            3. Type the displayed word exactly.<br>
            4. Press <b>ENTER</b> to submit.<br>
            5. Correct words give XP, score and combo.<br>
            6. Wrong words cost a life.<br>
            7. Complete the level to unlock the next one.
        </div>

    </div>
</div>

<script>
const levels = [
    {
        name:"Beginner",
        words:[
            "home","key","type","game","fast",
            "jump","code","mouse","screen","play"
        ],
        wordsToWin:6
    },
    {
        name:"Basic",
        words:[
            "keyboard","practice","letter","laptop",
            "button","window","system","school",
            "student","computer"
        ],
        wordsToWin:7
    },
    {
        name:"Intermediate",
        words:[
            "python","terminal","browser","program",
            "network","server","website","database",
            "linux","developer"
        ],
        wordsToWin:8
    },
    {
        name:"Advanced",
        words:[
            "authentication","encryption","protocol",
            "firewall","database","security",
            "authorization","monitoring","password",
            "configuration"
        ],
        wordsToWin:9
    },
    {
        name:"Pro",
        words:[
            "cybersecurity","cryptography","vulnerability",
            "infrastructure","penetration","defensive",
            "architecture","authentication",
            "networksecurity","securedevelopment"
        ],
        wordsToWin:10
    },
    {
        name:"Elite",
        words:[
            "cybersecurity engineer",
            "secure authentication",
            "network monitoring",
            "defensive security",
            "secure development",
            "incident response",
            "security architecture",
            "digital protection",
            "threat detection",
            "security operations"
        ],
        wordsToWin:12
    }
];

let currentLevel = 0;
let unlocked = Number(localStorage.getItem("premTypingUnlocked") || 1);

let score = 0;
let xp = 0;
let combo = 0;
let lives = 3;
let completed = 0;
let correctChars = 0;
let totalTyped = 0;
let startTime = 0;
let timer = null;
let playing = false;
let target = "";

const levelName = document.getElementById("levelName");
const livesEl = document.getElementById("lives");
const scoreEl = document.getElementById("score");
const comboEl = document.getElementById("combo");
const wpmEl = document.getElementById("wpm");
const accuracyEl = document.getElementById("accuracy");
const targetEl = document.getElementById("target");
const input = document.getElementById("typingInput");
const message = document.getElementById("message");
const progressBar = document.getElementById("progressBar");
const levelsEl = document.getElementById("levels");

function renderLevels(){
    levelsEl.innerHTML = "";

    levels.forEach((level,index)=>{
        const btn = document.createElement("button");
        btn.className = "level-btn";

        if(index === currentLevel){
            btn.classList.add("active");
        }

        if(index >= unlocked){
            btn.classList.add("locked");
            btn.textContent = "🔒 " + level.name;
            btn.disabled = true;
        }else{
            btn.textContent = "⚡ " + level.name;
        }

        btn.onclick = ()=>{
            if(!playing){
                currentLevel = index;
                updateUI();
                renderLevels();
                message.textContent =
                    level.name + " selected. Press START MISSION.";
            }
        };

        levelsEl.appendChild(btn);
    });
}

function randomTarget(){
    const words = levels[currentLevel].words;
    target = words[Math.floor(Math.random() * words.length)];
    targetEl.textContent = target;
    input.value = "";
    input.focus();
}

function updateUI(){
    levelName.textContent = levels[currentLevel].name;
    livesEl.textContent = lives;
    scoreEl.textContent = score;
    comboEl.textContent = combo;

    const accuracy = totalTyped === 0
        ? 100
        : Math.round((correctChars / totalTyped) * 100);

    accuracyEl.textContent = Math.max(0,accuracy) + "%";

    if(startTime){
        const minutes = (Date.now() - startTime) / 60000;

        if(minutes > 0){
            const words = correctChars / 5;
            wpmEl.textContent = Math.round(words / minutes);
        }
    }

    const needed = levels[currentLevel].wordsToWin;
    progressBar.style.width =
        Math.min(100,(completed / needed) * 100) + "%";
}

function startGame(){
    score = 0;
    xp = 0;
    combo = 0;
    lives = 3;
    completed = 0;
    correctChars = 0;
    totalTyped = 0;
    startTime = Date.now();
    playing = true;

    input.disabled = false;
    document.getElementById("startBtn").textContent = "RESTART MISSION";

    message.textContent =
        "MISSION STARTED — TYPE THE TARGET!";

    randomTarget();
    updateUI();
    renderLevels();

    clearInterval(timer);

    timer = setInterval(()=>{
        if(playing){
            updateUI();
        }
    },500);
}

function submitWord(){
    if(!playing) return;

    const typed = input.value.trim();

    if(!typed){
        return;
    }

    totalTyped += typed.length;

    if(typed === target){

        correctChars += target.length;

        combo++;

        const multiplier = Math.min(combo,10);
        const gained = 100 * multiplier;

        score += gained;
        xp += 10;

        completed++;

        message.textContent =
            "✓ CORRECT +" + gained + " XP +" + (10 * multiplier);

        if(completed >= levels[currentLevel].wordsToWin){
            finishLevel();
            return;
        }

        randomTarget();

    }else{

        lives--;
        combo = 0;

        message.textContent =
            "✗ WRONG — Life lost. Try again!";

        input.value = "";

        if(lives <= 0){
            gameOver();
            return;
        }

        input.focus();
    }

    updateUI();
}

function finishLevel(){
    playing = false;
    clearInterval(timer);
    input.disabled = true;

    score += 500;
    xp += 100;

    const next = currentLevel + 1;

    if(next < levels.length && unlocked <= next){
        unlocked = next + 1;
        localStorage.setItem(
            "premTypingUnlocked",
            unlocked
        );
    }

    updateUI();
    renderLevels();

    if(next < levels.length){
        message.textContent =
            "🏆 LEVEL COMPLETE! " +
            levels[next].name +
            " UNLOCKED!";
    }else{
        message.textContent =
            "👑 ELITE COMPLETE! YOU BEAT TYPING QUEST!";
    }

    targetEl.textContent = "MISSION COMPLETE";
}

function gameOver(){
    playing = false;
    clearInterval(timer);
    input.disabled = true;

    message.textContent =
        "💥 GAME OVER — Press START MISSION to try again.";

    targetEl.textContent = "GAME OVER";

    updateUI();
}

document.getElementById("startBtn").onclick = startGame;

input.addEventListener("keydown",(event)=>{
    if(event.key === "Enter"){
        event.preventDefault();
        submitWord();
    }
});

document.getElementById("resetBtn").onclick = ()=>{
    if(playing){
        message.textContent =
            "Finish the current mission first.";
        return;
    }

    localStorage.removeItem("premTypingUnlocked");

    unlocked = 1;
    currentLevel = 0;

    score = 0;
    combo = 0;
    lives = 3;
    completed = 0;
    correctChars = 0;
    totalTyped = 0;

    targetEl.textContent = "PRESS START";
    message.textContent =
        "Progress reset. Beginner is unlocked.";

    updateUI();
    renderLevels();
};

renderLevels();
updateUI();
</script>
""")
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

    logged_in = "username" in session

    if logged_in:
        nav = """
        <a href="/">Home</a>
        <a href="/dashboard">Dashboard</a>
        <a href="/games">🎮 Cyber Arcade</a>
        <a href="/logout">Logout</a>
        """
    else:
        nav = """
        <a href="/">Home</a>
        <a href="/login">Login</a>
        <a class="nav-button" href="/register">Create Account</a>
        """

    return f"""
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width, initial-scale=1.0">

<title>PREM // SECURE</title>

<style>

* {{
    box-sizing: border-box;
    scroll-behavior: smooth;
}}

body {{
    margin: 0;
    background:
        radial-gradient(circle at 20% 20%, #063b2a 0, transparent 28%),
        radial-gradient(circle at 80% 10%, #062a3b 0, transparent 25%),
        #030609;
    color: #f5fffa;
    font-family: Arial, sans-serif;
}}

body::before {{
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    opacity: .06;
    background-image:
        linear-gradient(#00ff8844 1px, transparent 1px),
        linear-gradient(90deg, #00ff8844 1px, transparent 1px);
    background-size: 45px 45px;
}}

nav {{
    position: sticky;
    top: 0;
    z-index: 100;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 18px 7%;
    background: rgba(3, 6, 9, .86);
    backdrop-filter: blur(15px);
    border-bottom: 1px solid #15382b;
}}

.logo {{
    color: #00ff88;
    font-weight: 900;
    letter-spacing: 2px;
}}

nav a {{
    color: #b9c9c3;
    text-decoration: none;
    margin-left: 20px;
    font-size: 14px;
}}

nav a:hover {{
    color: #00ff88;
}}

.nav-button {{
    border: 1px solid #00ff88;
    padding: 9px 14px;
    border-radius: 7px;
    color: #00ff88;
}}

.hero {{
    min-height: 88vh;
    display: flex;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 70px 20px;
}}

.badge {{
    display: inline-block;
    border: 1px solid #155f43;
    background: #062016;
    color: #00ff88;
    padding: 8px 15px;
    border-radius: 30px;
    font-family: monospace;
    font-size: 13px;
}}

.hero h1 {{
    margin: 25px 0 5px;
    font-size: clamp(48px, 10vw, 100px);
    line-height: .95;
    letter-spacing: -4px;
}}

.hero h1 span {{
    color: #00ff88;
    text-shadow: 0 0 35px #00ff8844;
}}

.hero h2 {{
    color: #a7b8b1;
    font-weight: normal;
    font-size: 22px;
}}

.hero p {{
    max-width: 680px;
    margin: 25px auto;
    color: #84948e;
    line-height: 1.8;
    font-size: 17px;
}}

.btn {{
    display: inline-block;
    padding: 14px 25px;
    margin: 8px;
    border-radius: 8px;
    text-decoration: none;
    font-weight: bold;
}}

.primary {{
    background: #00ff88;
    color: #03110a;
}}

.secondary {{
    border: 1px solid #00ff88;
    color: #00ff88;
}}

.section {{
    max-width: 1100px;
    margin: auto;
    padding: 90px 20px;
}}

.section-label {{
    color: #00ff88;
    font-family: monospace;
    letter-spacing: 2px;
}}

.section h2 {{
    font-size: 38px;
    margin-top: 8px;
}}

.muted {{
    color: #899a93;
    line-height: 1.8;
}}

.cards {{
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(220px, 1fr));
    gap: 18px;
    margin-top: 35px;
}}

.card {{
    background: rgba(10, 18, 15, .8);
    border: 1px solid #17372b;
    border-radius: 14px;
    padding: 25px;
    transition: .25s;
}}

.card:hover {{
    transform: translateY(-5px);
    border-color: #00ff88;
    box-shadow: 0 10px 40px #00ff8812;
}}

.card h3 {{
    color: #00ff88;
}}

.card p {{
    color: #899a93;
    line-height: 1.7;
}}

.number {{
    color: #53635d;
    font-family: monospace;
}}

.project {{
    min-height: 230px;
}}

.project-tag {{
    color: #62ffc0;
    font-family: monospace;
    font-size: 12px;
}}

.terminal {{
    max-width: 850px;
    margin: 35px auto;
    padding: 28px;
    background: #010403;
    border: 1px solid #1c513c;
    border-radius: 14px;
    font-family: monospace;
    color: #00ff88;
    line-height: 1.9;
    box-shadow: 0 0 40px #00ff8809;
}}

.status {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    color: #00ff88;
}}

.dot {{
    width: 8px;
    height: 8px;
    background: #00ff88;
    border-radius: 50%;
    box-shadow: 0 0 12px #00ff88;
}}

.timeline {{
    border-left: 1px solid #214a39;
    padding-left: 25px;
}}

.timeline-item {{
    margin: 25px 0;
}}

.timeline-item strong {{
    color: #00ff88;
}}

.auth {{
    max-width: 450px;
    margin: 100px auto;
    padding: 35px;
    background: rgba(10, 18, 15, .9);
    border: 1px solid #1b4937;
    border-radius: 15px;
}}

.auth h1 {{
    color: #00ff88;
}}

input {{
    width: 100%;
    padding: 14px;
    margin: 9px 0;
    background: #030609;
    color: white;
    border: 1px solid #263d34;
    border-radius: 7px;
}}

button {{
    width: 100%;
    padding: 14px;
    margin-top: 10px;
    border: 0;
    border-radius: 7px;
    background: #00ff88;
    color: #03110a;
    font-weight: bold;
    cursor: pointer;
}}

footer {{
    border-top: 1px solid #15382b;
    padding: 35px;
    text-align: center;
    color: #53635d;
}}

@media(max-width: 650px) {{

    nav {{
        padding: 15px 4%;
    }}

    nav a {{
        margin-left: 8px;
        font-size: 12px;
    }}

    .hero h1 {{
        letter-spacing: -2px;
    }}

    .section {{
        padding: 60px 18px;
    }}
}}

</style>

</head>

<body>

<nav>

<div class="logo">PREM // SECURE</div>

<div>
{nav}
</div>

</nav>

{content}

<footer>
PREM // SECURE · 2026
<br>
<span>LEARN · BUILD · SECURE</span>
</footer>

</body>
</html>
"""


@app.route("/")
def home():

    if "username" in session:

        buttons = """
        <a class="btn primary" href="/dashboard">
        OPEN DASHBOARD
        </a>

        <a class="btn secondary" href="/logout">
        LOGOUT
        </a>
        """

    else:

        buttons = """
        <a class="btn primary" href="/register">
        CREATE ACCOUNT
        </a>

        <a class="btn secondary" href="/login">
        LOGIN
        </a>
        """

    return page(f"""

<section class="hero">

<div>

<div class="badge">
● SYSTEM ONLINE · SECURITY PORTFOLIO
</div>

<h1>
PREM <span>//</span><br>
SECURE
</h1>

<h2>
Cybersecurity Engineer in the Making
</h2>

<p>
Think like a defender. Build like an engineer.
Explore technology, understand digital systems,
and develop the skills required to build a more
secure digital world.
</p>

{buttons}

</div>

</section>


<section class="section">

<div class="section-label">
01 // THE MISSION
</div>

<h2>Learn. Build. Secure.</h2>

<p class="muted">
Cybersecurity is more than tools and commands.
It is understanding systems, thinking critically,
solving problems and building technology responsibly.
This portfolio documents my journey from learning
the fundamentals to creating real projects.
</p>

</section>


<section class="section">

<div class="section-label">
02 // CURRENT STACK
</div>

<h2>Skills & Technologies</h2>

<div class="cards">

<div class="card">
<span class="number">01</span>
<h3>Python</h3>
<p>
Programming, automation and project development.
</p>
</div>

<div class="card">
<span class="number">02</span>
<h3>Linux</h3>
<p>
Command line, system fundamentals and administration.
</p>
</div>

<div class="card">
<span class="number">03</span>
<h3>Networking</h3>
<p>
Learning protocols, addressing and network concepts.
</p>
</div>

<div class="card">
<span class="number">04</span>
<h3>Web Security</h3>
<p>
Understanding authentication and secure development.
</p>
</div>

<div class="card">
<span class="number">05</span>
<h3>Flask</h3>
<p>
Building lightweight Python web applications.
</p>
</div>

<div class="card">
<span class="number">06</span>
<h3>Git</h3>
<p>
Version control and collaborative development.
</p>
</div>

</div>

</section>


<section class="section">

<div class="section-label">
03 // PROJECT VAULT
</div>

<h2>Things I'm Building</h2>

<div class="cards">

<div class="card project">

<div class="project-tag">
PROJECT 001 · LIVE
</div>

<h3>Cyber Portfolio</h3>

<p>
A personal cybersecurity portfolio built with
Python, Flask and SQLite.
</p>

</div>


<div class="card project">

<div class="project-tag">
PROJECT 002 · LEARNING
</div>

<h3>Linux Lab</h3>

<p>
A personal environment for learning Linux,
system fundamentals and command-line skills.
</p>

</div>


<div class="card project">

<div class="project-tag">
PROJECT 003 · NEXT
</div>

<h3>Security Projects</h3>

<p>
Future projects focused on defensive security,
secure coding and cybersecurity education.
</p>

</div>

</div>

</section>


<section class="section">

<div class="section-label">
04 // BUILD LOG
</div>

<h2>My Learning Journey</h2>

<div class="timeline">

<div class="timeline-item">
<strong>01 · Python</strong>
<p class="muted">
Started learning programming and building small projects.
</p>
</div>

<div class="timeline-item">
<strong>02 · Linux</strong>
<p class="muted">
Started exploring Linux systems and the terminal.
</p>
</div>

<div class="timeline-item">
<strong>03 · Web Development</strong>
<p class="muted">
Built my first Flask website.
</p>
</div>

<div class="timeline-item">
<strong>04 · Git & GitHub</strong>
<p class="muted">
Learned version control and project deployment.
</p>
</div>

<div class="timeline-item">
<strong>05 · Cybersecurity</strong>
<p class="muted">
Continuing to build knowledge in networking,
secure development and defensive security.
</p>
</div>

</div>

</section>


<section class="section">

<div class="section-label">
05 // SECURITY LAB
</div>

<h2>Environment</h2>

<div class="terminal">

<div class="status">
<div class="dot"></div>
SYSTEM STATUS: ONLINE
</div>

<br><br>

$ environment<br>
Linux / Python / Flask

<br><br>

$ focus<br>
Cybersecurity Fundamentals

<br><br>

$ philosophy<br>
Learn → Build → Test → Improve

<br><br>

$ mission<br>
Build technology with security in mind.

</div>

</section>

""")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        if len(username) < 3 or len(password) < 6:

            return page("""
            <div class="auth">

            <h1>Account Error</h1>

            <p class="muted">
            Username must have at least 3 characters
            and password must have at least 6 characters.
            </p>

            <a class="btn primary" href="/register">
            TRY AGAIN
            </a>

            </div>
            """)

        hashed = generate_password_hash(password)

        try:

            conn = get_db()

            conn.execute(
                "INSERT INTO users (username,password) VALUES (?,?)",
                (username, hashed)
            )

            conn.commit()
            conn.close()

            return redirect("/login")

        except sqlite3.IntegrityError:

            return page("""
            <div class="auth">

            <h1>Username Exists</h1>

            <p class="muted">
            Please choose another username.
            </p>

            <a class="btn primary" href="/register">
            TRY AGAIN
            </a>

            </div>
            """)

    return page("""

<div class="auth">

<h1>CREATE ACCOUNT</h1>

<p class="muted">
Join the PREM // SECURE community.
</p>

<form method="POST">

<input
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

<button>
CREATE ACCOUNT
</button>

</form>

<p class="muted">
Already registered?
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
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(
            user["password"],
            password
        ):
            session.permanent = True
            session["username"] = username

            return redirect("/dashboard")

        return page("""
        <div class="auth">

        <h1>ACCESS DENIED</h1>

        <p class="muted">
        Incorrect username or password.
        </p>

        <a class="btn primary" href="/login">
        TRY AGAIN
        </a>

        </div>
        """)

    return page("""

<div class="auth">

<h1>LOGIN</h1>

<p class="muted">
Access your PREM // SECURE dashboard.
</p>

<form method="POST">

<input
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

<button>
AUTHENTICATE
</button>

</form>

<p class="muted">
New here?
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

<section class="section">

<div class="section-label">
USER // DASHBOARD
</div>

<h1>
WELCOME, {username}
</h1>

<p class="muted">
Your secure portfolio dashboard.
</p>


<div class="cards">

<div class="card">

<div class="number">
STATUS
</div>

<h3>
● ACTIVE
</h3>

<p>
Your session is authenticated.
</p>

</div>


<div class="card">

<div class="number">
FOCUS
</div>

<h3>
CYBERSECURITY
</h3>

<p>
Learning and building security projects.
</p>

</div>


<div class="card">

<div class="number">
MISSION
</div>

<h3>
LEARN → BUILD
</h3>

<p>
Keep improving technical skills.
</p>

</div>

</div>


<div class="terminal">

$ authenticated_user<br>
{username}

<br><br>

$ account_status<br>
ACTIVE

<br><br>

$ security_mindset<br>
LEARN · BUILD · SECURE

</div>

<a class="btn secondary" href="/logout">
LOGOUT
</a>

</section>

""")


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

@app.route("/games")
def games():
    return page("""
<style>
.arcade-wrap{
    max-width:1100px;
    margin:40px auto;
    padding:20px;
}
.arcade-title{
    text-align:center;
    font-size:42px;
    margin-bottom:10px;
}
.arcade-sub{
    text-align:center;
    opacity:.75;
    margin-bottom:35px;
}
.arcade-grid{
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(240px,1fr));
    gap:20px;
}
.game-card{
    padding:24px;
    border:1px solid rgba(0,255,255,.25);
    border-radius:18px;
    background:rgba(10,20,35,.7);
    transition:.2s;
}
.game-card:hover{
    transform:translateY(-5px);
    border-color:#00ffff;
}
.game-icon{
    font-size:42px;
}
.game-card h2{
    margin:12px 0 8px;
}
.game-card p{
    opacity:.75;
    min-height:45px;
}
.game-btn{
    display:inline-block;
    margin-top:12px;
    padding:10px 16px;
    border-radius:10px;
    text-decoration:none;
    background:#00ffff;
    color:#001014;
    font-weight:bold;
}
</style>

<div class="arcade-wrap">

    <div class="arcade-title">🎮 CYBER ARCADE</div>

    <div class="arcade-sub">
        Train your cybersecurity skills through interactive challenges.
    </div>

    <div class="arcade-grid">

        <div class="game-card">
            <div class="game-icon">⌨️</div>
            <h2>Typing Quest</h2>
            <p>Improve your typing speed through cybersecurity-themed levels.</p>
            <a class="game-btn" href="/typing">Play</a>
        </div>

        <div class="game-card">
            <div class="game-icon">🎣</div>
            <h2>Phishing Detective</h2>
            <p>Learn to identify suspicious messages and fictional phishing clues.</p>
            <a class="game-btn" href="/games#phishing">Play</a>
        </div>

        <div class="game-card">
            <div class="game-icon">🔐</div>
            <h2>Password Defender</h2>
            <p>Learn the basics of creating strong passwords.</p>
            <a class="game-btn" href="/games#password">Play</a>
        </div>

        <div class="game-card">
            <div class="game-icon">🐞</div>
            <h2>Bug Hunter</h2>
            <p>Find fictional bugs in safe example code.</p>
            <a class="game-btn" href="/games#bugs">Play</a>
        </div>

        <div class="game-card">
            <div class="game-icon">🌐</div>
            <h2>Network Defender</h2>
            <p>Practice identifying safe and suspicious network events.</p>
            <a class="game-btn" href="/games#network">Play</a>
        </div>

        <div class="game-card">
            <div class="game-icon">🐧</div>
            <h2>Linux Command Quest</h2>
            <p>Learn useful Linux commands through simple challenges.</p>
            <a class="game-btn" href="/games#linux">Play</a>
        </div>

        <div class="game-card">
            <div class="game-icon">🔢</div>
            <h2>Crypto Puzzle</h2>
            <p>Solve beginner-friendly encoding and logic puzzles.</p>
            <a class="game-btn" href="/games#crypto">Play</a>
        </div>

        <div class="game-card">
            <div class="game-icon">🧠</div>
            <h2>Cyber Quiz Battle</h2>
            <p>Test your cybersecurity knowledge with quick questions.</p>
            <a class="game-btn" href="/games#quiz">Play</a>
        </div>

    </div>
</div>
""")
init_db()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
