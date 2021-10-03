from flask import flash, render_template, url_for, redirect
from app import app


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title="Trang chủ")

