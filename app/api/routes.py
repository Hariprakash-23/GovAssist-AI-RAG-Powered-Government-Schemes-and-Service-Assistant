from flask import Blueprint
from flask import jsonify
from flask import request

from app.api.controller import ChatController

chat_api = Blueprint(
    "chat_api",
    __name__
)

controller = ChatController()


@chat_api.route(
    "/chat",
    methods=["POST"]
)
def chat():

    data = request.get_json()

    question = data.get("question", "")
    session_id = data.get("session_id", "default")

    response = controller.chat(question, session_id=session_id)

    return jsonify(response)
