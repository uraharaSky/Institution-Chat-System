from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, current_user
from datetime import datetime

from models import db, User, Message, Group, GroupMessage, GroupMember

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
            if user.role not in ["student", "cr","faculty"]:
                continue

        elif current_user.role == "cr":
            if user.role not in ["student", "faculty", "cr"]:
                continue

        elif current_user.role == "faculty":
            if user.role not in ["cr","student", "faculty"]:
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

    from utils.notification import create_notification

    sender_id = int(get_jwt_identity())
    data = request.get_json()

    receiver_id = data.get("receiver_id")
    content = data.get("content")

    if not receiver_id or not content:
        return jsonify({"msg": "Invalid data"}), 400

    # 🔑 Create consistent chat_id
    chat_id = f"{min(sender_id, receiver_id)}_{max(sender_id, receiver_id)}"

    # ✅ Save message
    msg = Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        chat_id=chat_id,
        content=content,
        timestamp=datetime.utcnow(),
        status="sent"
    )

    db.session.add(msg)

    # =========================
    # 🔔 NOTIFICATION
    # =========================

    sender = User.query.get(sender_id)

    create_notification(
        receiver_id,
        "New Message",
        f"{sender.name} sent you a message",
        "chat",
        ref_id=chat_id,
        ref_type="user"
    )

    # ✅ single commit
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

