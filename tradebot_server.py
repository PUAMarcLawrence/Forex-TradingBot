from flask import Flask, redirect, url_for, render_template, request, session
from datetime import timedelta
# from waitress import serve

app = Flask(__name__)
app.secret_key = "hello"
app.permanent_session_lifetime = timedelta(minutes=5)

@app.route('/')
def home():
    return render_template("index.html",content="Trading Bot")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["nm"]
        password = request.form["pass"]
        session["user"] = user
        return redirect(url_for("user"))
    else:
        if "user" in session:
            return redirect(url_for("user"))

        return render_template("login.html")

@app.route("/user")
def user():
    if "user" in session:
        user = session["user"]
        return f"<h1>{user}</h1>"
    else:
        return redirect(url_for("login"))
    
@app.route("/logout")
def logout():
    session.pop("user", None)
    
    return redirect(url_for("login"))

if __name__ == "__main__":
    # serve(app, host ="0.0.0.0", port=8000)
    app.run(host ="0.0.0.0", port=8000,debug=True)