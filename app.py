from flask import Flask
# from flask import Blueprint,render_template
from views import dashboard
from views import site
from views import files
from views import soft
from views import config
from views import plugins

app = Flask(__name__)
app.debug = True

DEFAULT_MODULES = (
    (dashboard, "/"),
    (site, "/site"),
    (files, "/files"),
    (soft, "/soft"),
    (config, "/config"),
    (plugins, "/plugins"),
)


def setting_modules(app, modules):
    for module, url_prefix in modules:
        app.register_blueprint(module, url_prefix=url_prefix)

setting_modules(app, DEFAULT_MODULES)


if __name__ == "__main__":
    app.run()
