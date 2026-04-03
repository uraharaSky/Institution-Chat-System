from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from models import db, User, Message

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/users", methods=["GET"])
@jwt_required()
def get_chat_users():
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)

    users = User.query.all()

    result = []

    for user in users:
        if user.id == current_user_id:
            continue

        # 🔒 Role-based filtering
        if current_user.role == "student":
            if user.role not in ["student", "cr"]:
                continue

        elif current_user.role == "cr":
            if user.role not in ["student", "teacher"]:
                continue

        elif current_user.role == "teacher":
            if user.role != "cr":
                continue

        result.append({
            "id": user.id,
            "name": user.name,
            "role": user.role
        })

    return jsonify(result), 200

@chat_bp.route("/send", methods=["POST"])
@jwt_required()
def send_message():
    sender_id = int(get_jwt_identity())
    data = request.get_json()

    receiver_id = data.get("receiver_id")
    content = data.get("content")

    if not receiver_id or not content:
        return jsonify({"msg": "Invalid data"}), 400

    # 🔑 Create consistent chat_id
    chat_id = f"{min(sender_id, receiver_id)}_{max(sender_id, receiver_id)}"

    msg = Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        chat_id=chat_id,
        content=content,
        timestamp=datetime.utcnow(),
        status="sent"
    )

    db.session.add(msg)
    db.session.commit()

    return jsonify({"msg": "Message sent"}), 200

@chat_bp.route("/messages/<int:other_user_id>", methods=["GET"])
@jwt_required()
def get_messages(other_user_id):
    current_user_id = int(get_jwt_identity())

    chat_id = f"{min(current_user_id, other_user_id)}_{max(current_user_id, other_user_id)}"

    messages = Message.query.filter_by(chat_id=chat_id) \
        .order_by(Message.timestamp.asc()) \
        .all()

    result = []

    for m in messages:
        result.append({
            "id": m.id,
            "sender_id": m.sender_id,
            "receiver_id": m.receiver_id,
            "content": m.content,
            "timestamp": m.timestamp.strftime("%H:%M"),
            "status": m.status
        })

    return jsonify(result), 200