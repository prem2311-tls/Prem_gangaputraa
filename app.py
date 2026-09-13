from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>prem_gangaputraa</title>
    </head>
    <body>
        <h1>Welcome to prem_gangaputraa 🚀</h1>
        <p>My first website</p>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)