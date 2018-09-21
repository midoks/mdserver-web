from flask import Flask
from flask import Blueprint,render_template
from views import *

app = Flask(__name__)
app.debug = True

# @app.route("/")
# def index():
#     return render_template('default/index.html')

# def setting_modules(app, modules):
#     for module, url_prefix in modules:
#     	print modules
#     	print url_prefix
#         app.register_blueprint(module, url_prefix=url_prefix)

# DEFAULT_MODULES = (
#     (views.frontend, "/"),
# )
# setting_modules(app,DEFAULT_MODULES)

app.register_blueprint(frontend, url_prefix="")

# simple_page = Blueprint('simple_page', __name__, template_folder='templates')
# @simple_page.route("/")
# def index():
#     return render_template('default/index.html')

# app.register_blueprint(simple_page,url_prefix="/")

if __name__ == "__main__":
    app.run()
