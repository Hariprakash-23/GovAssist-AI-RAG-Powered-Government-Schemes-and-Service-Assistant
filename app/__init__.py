from flask import Flask

from app.api.routes import chat_api


def create_app():

    app = Flask(__name__)

    app.register_blueprint(chat_api)

    return app