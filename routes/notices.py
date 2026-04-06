from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Notice, User, NoticeReaction
from extensions import db


notice_bp = Blueprint('notice', __name__)


@notice_bp.route('/', methods=['POST'])
@jwt_required()
def create_notice():
    user_id = int(get_jwt_identity())

    # Get user
    user = User.query.get(user_id)

    # Only faculty or CR allowed
    if user.role not in ["faculty", "cr"]:
        return jsonify({"msg": "Only faculty or CR can post notices"}), 403

    data = request.get_json()

    title = data.get("title")
    content = data.get("content")

    # Validation
    if not title or not content:
        return jsonify({"msg": "Title and content required"}), 400

    # Create notice
    notice = Notice(
        title=title,
        content=content,
        posted_by=user_id
    )

    db.session.add(notice)

    # =========================
    # 🔔 ADD NOTIFICATIONS HERE
    # =========================
    from utils.notification import create_notification

    users = User.query.all()   # or filter students if needed

    for u in users:
        create_notification(
            u.id,
            "New Notice",
            f"{title}",
            "notice",
            ref_id=notice.id,
            ref_type="notice"
        )

    db.session.commit()

    return jsonify({
        "msg": "Notice created successfully",
        "notice_id": notice.id
    }), 201


@notice_bp.route('/', methods=['GET'])
@jwt_required()
def get_notices():
    notices = Notice.query.order_by(Notice.created_at.desc()).all()

    result = []

    for n in notices:
        # Get reactions for this notice
        reactions = NoticeReaction.query.filter_by(notice_id=n.id).all()

        reaction_count = {}

        for r in reactions:
            reaction_count[r.reaction] = reaction_count.get(r.reaction, 0) + 1

        result.append({
            "id": n.id,
            "title": n.title,
            "content": n.content,
            "posted_by": n.posted_by,
            "time": n.created_at,
            "reactions": reaction_count
        })

    return jsonify(result), 200

@notice_bp.route('/<int:notice_id>/react', methods=['POST'])
@jwt_required()
def react_to_notice(notice_id):
    user_id = int(get_jwt_identity())

    data = request.get_json()
    reaction_type = data.get("reaction")

    # Validate input
    if not reaction_type:
        return jsonify({"msg": "Reaction required"}), 400

    # Check notice exists
    notice = Notice.query.get(notice_id)
    if not notice:
        return jsonify({"msg": "Notice not found"}), 404

    # Check existing reaction
    existing = NoticeReaction.query.filter_by(
        notice_id=notice_id,
        user_id=user_id
    ).first()

    if existing:
        # Update reaction
        existing.reaction = reaction_type
    else:
        # Create new reaction
        new_reaction = NoticeReaction(
            notice_id=notice_id,
            user_id=user_id,
            reaction=reaction_type
        )
        db.session.add(new_reaction)

    db.session.commit()

    return jsonify({
        "msg": "Reaction recorded",
        "reaction": reaction_type
    }), 200