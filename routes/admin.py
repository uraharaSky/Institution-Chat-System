from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Attendance, Session, Notice, Poll
from extensions import db

admin_bp = Blueprint('admin', __name__)

def is_admin(user):
    return user.role == "admin"

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not is_admin(user):
        return jsonify({"msg": "Admin only"}), 403

    users = User.query.all()

    result = []
    for u in users:
        result.append({
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role
        })

    return jsonify(result), 200


@admin_bp.route('/attendance-report', methods=['GET'])
@jwt_required()
def attendance_report():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not is_admin(user):
        return jsonify({"msg": "Admin only"}), 403

    sessions = Session.query.all()

    report = []

    for s in sessions:
        count = Attendance.query.filter_by(session_id=s.id).count()

        report.append({
            "session_id": s.id,
            "faculty_id": s.faculty_id,
            "attendance_count": count
        })

    return jsonify(report), 200

@admin_bp.route('/summary', methods=['GET'])
@jwt_required()
def system_summary():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not is_admin(user):
        return jsonify({"msg": "Admin only"}), 403

    total_users = User.query.count()
    total_notices = Notice.query.count()
    total_polls = Poll.query.count()
    total_sessions = Session.query.count()

    return jsonify({
        "users": total_users,
        "notices": total_notices,
        "polls": total_polls,
        "sessions": total_sessions
    }), 200

