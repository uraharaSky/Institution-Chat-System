from flask import Blueprint, request, jsonify
from models import db, Group, GroupMember, GroupMessage, User
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

groups_bp = Blueprint("groups", __name__)

@groups_bp.route("/groups/create", methods=["POST"])
@jwt_required()
def create_group():

    from utils.notification import create_notification

    data = request.get_json()
    current_user = int(get_jwt_identity())

    name = data.get("name")
    members = data.get("members", [])

    if not name:
        return jsonify({"error": "Group name required"}), 400

    # ✅ Create group
    group = Group(name=name, created_by=current_user)
    db.session.add(group)
    db.session.flush()  # 🔥 get group.id without commit

    # ✅ Add creator also
    all_members = set(members + [current_user])

    for user_id in all_members:
        db.session.add(GroupMember(group_id=group.id, user_id=user_id))

        # 🔔 Notification for each member (except creator optional)
        if user_id != current_user:
            create_notification(
                user_id,
                "New Group",
                f"You were added to '{name}'",
                "group",
                ref_id=group.id,
                ref_type="group"
            )

    # ✅ One commit for everything
    db.session.commit()

    return jsonify({
        "message": "Group created",
        "group_id": group.id
    }), 200

@groups_bp.route("/groups/my", methods=["GET"])
@jwt_required()
def get_my_groups():
    current_user = get_jwt_identity()

    groups = db.session.query(Group).join(
        GroupMember, Group.id == GroupMember.group_id
    ).filter(
        GroupMember.user_id == current_user
    ).all()

    result = [
        {
            "id": g.id,
            "name": g.name
        }
        for g in groups
    ]

    return jsonify(result), 200


@groups_bp.route("/groups/send", methods=["POST"])
@jwt_required()
def send_group_message():

    from utils.notification import create_notification

    data = request.get_json()
    current_user = int(get_jwt_identity())

    group_id = data.get("group_id")
    content = data.get("content")

    # ✅ Validate input
    if not group_id or not content:
        return jsonify({"error": "Missing data"}), 400

    # ✅ Check membership
    is_member = GroupMember.query.filter_by(
        group_id=group_id,
        user_id=current_user
    ).first()

    if not is_member:
        return jsonify({"error": "Not a group member"}), 403

    # ✅ Save message
    msg = GroupMessage(
        group_id=group_id,
        sender_id=current_user,
        content=content
    )

    db.session.add(msg)

    # =========================
    # 🔔 NOTIFICATIONS
    # =========================

    members = GroupMember.query.filter_by(group_id=group_id).all()

    for m in members:
        if m.user_id != current_user:  # don't notify sender
            create_notification(
                m.user_id,
                "New Group Message",
                f"New message in group",
                "chat",
                ref_id=group_id,
                ref_type="group"
            )

    # ✅ single commit
    db.session.commit()

    return jsonify({"message": "Message sent"}), 200

@groups_bp.route("/groups/messages/<int:group_id>", methods=["GET"])
@jwt_required()
def get_group_messages(group_id):
    current_user = get_jwt_identity()

    # ✅ Check membership (SECURITY)
    is_member = GroupMember.query.filter_by(
        group_id=group_id,
        user_id=current_user
    ).first()

    if not is_member:
        return jsonify({"error": "Not authorized"}), 403

    # ✅ Fetch messages
    messages = GroupMessage.query.filter_by(
        group_id=group_id
    ).order_by(GroupMessage.timestamp).all()

    # ✅ Format response
    result = [
        {
            "id": msg.id,
            "sender_id": msg.sender_id,
            "sender_name": User.query.get(msg.sender_id).name,
            "content": msg.content,
            "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        for msg in messages
    ]

    return jsonify(result), 200