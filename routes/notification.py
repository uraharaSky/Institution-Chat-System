from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models import Notification

notif_bp = Blueprint("notifications", __name__, url_prefix="/notifications")

#get notifications

@notif_bp.route("/", methods=["GET"])
@jwt_required()
def get_notifications():

    user_id = int(get_jwt_identity())

    notifications = Notification.query \
        .filter_by(user_id=user_id) \
        .order_by(Notification.created_at.desc()) \
        .limit(50) \
        .all()

    result = []

    for n in notifications:
        result.append({
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "type": n.type,
            "is_read": n.is_read,
            "created_at": n.created_at.strftime("%Y-%m-%d %H:%M")
        })

    return jsonify(result), 200

# mark as read

@notif_bp.route("/<int:notif_id>/read", methods=["POST"])
@jwt_required()
def mark_as_read(notif_id):

    user_id = int(get_jwt_identity())

    notif = Notification.query.get(notif_id)

    if not notif:
        return jsonify({"msg": "Notification not found"}), 404

    # 🔒 security check
    if notif.user_id != user_id:
        return jsonify({"msg": "Unauthorized"}), 403

    notif.is_read = True
    db.session.commit()

    return jsonify({"msg": "Marked as read"}), 200

#mark all as read

@notif_bp.route("/read-all", methods=["POST"])
@jwt_required()
def mark_all_read():

    user_id = int(get_jwt_identity())

    Notification.query \
        .filter_by(user_id=user_id, is_read=False) \
        .update({"is_read": True})

    db.session.commit()

    return jsonify({"msg": "All notifications marked as read"}), 200

#Delete Notifications

@notif_bp.route("/<int:notif_id>", methods=["DELETE"])
@jwt_required()
def delete_notification(notif_id):

    user_id = int(get_jwt_identity())

    notif = Notification.query.get(notif_id)

    if not notif:
        return jsonify({"msg": "Not found"}), 404

    if notif.user_id != user_id:
        return jsonify({"msg": "Unauthorized"}), 403

    db.session.delete(notif)
    db.session.commit()

    return jsonify({"msg": "Deleted"}), 200