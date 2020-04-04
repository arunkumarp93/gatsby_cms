import os

from flask import Flask
from werkzeug.routing import BaseConverter
from core import views
from core.utils import make_dir

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

def create_app(config):

    environment = os.getenv('ENV') if 'DYNO' in os.environ else os.environ.get('ENV')
    app.url_map.converters['regex'] = RegexConverter

    if environment:
        app.config.from_object(config.get(environment))
    else:
        app.config.from_object(config.get('production'))

    folders = [app.config.get('STATIC'), app.config.get('UPLOAD_FOLDER')]

    register_blueprints(app)

    UPLOAD_FOLDER = os.getcwd() + '/temp'
    pages = os.getcwd() + '/static'

    folders = [pages, UPLOAD_FOLDER]

    for folder in folders:
        make_dir(folder)

    return app

def register_blueprints(app):
    app.register_blueprint(views.blueprint)
