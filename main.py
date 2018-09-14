from flask import Flask
from flask import render_template

app = Flask(__name__)
app.debug = True

@app.route("/h")
def hello():
    return "Hello World!"

@app.route("/")
def index(name=None):
	return render_template('index.html', name=name)