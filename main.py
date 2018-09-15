from flask import Flask
from flask import Blueprint,render_template
import views

app = Flask(__name__)
app.debug = True


@app.route("/h")
def hello():
    return "Hello World!"


@app.route("/")
def index():
    return render_template('default/index.html')

def setting_modules(app, modules):
    for module, url_prefix in modules:
        app.register_blueprint(module, url_prefix=url_prefix)

DEFAULT_MODULES = (
    (views.frontend, "/"),
)
setting_modules(DEFAULT_MODULES, url_prefix=url_prefix)




if __name__ == "__main__":
    app.run()
