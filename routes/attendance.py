import code

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Session, User, Attendance
from extensions import db
import random

attendance_bp = Blueprint('attendance', __name__)


def generate_code():
    return str(random.randint(100000, 999999))


@attendance_bp.route('/start', methods=['POST'])
@jwt_required()
def start_session():
    print("API HIT ")

    user_id = get_jwt_identity()
    print("User ID:", user_id)

    user = User.query.get(user_id)
    print("User fetched:", user)

    if user.role != "faculty":
        return jsonify({"msg": "Only faculty can start session"}), 403

    code = generate_code()
    print("Generated code:", code)

    session = Session(faculty_id=user_id, code=code)

    db.session.add(session)
    db.session.commit()

    print("Session saved")

    return jsonify({
        "session_id": session.id,
        "code": code
    }), 201

@attendance_bp.route('/session/<int:session_id>', methods=['GET'])
@jwt_required()
def get_attendance(session_id):
    user_id = get_jwt_identity()

    #verify faculty
    user = User.query.get(user_id)
    if user.role != "faculty":
        return jsonify({"msg": "Only faculty can start session"}), 403

    #fetch record
    records = Attendance.query.filter_by(session_id=session_id).all()

    result = []
    for r in records:
        result.append({
        "student_id": r.student_id,
        "time": r.timestamp
    })

    return jsonify(result), 200

@attendance_bp.route('/end/<int:session_id>', methods=['POST'])
@jwt_required()
def end_session(session_id):
    user_id = int(get_jwt_identity())

    # Get user
    user = User.query.get(user_id)

    # Only faculty allowed
    if user.role != "faculty":
        return jsonify({"msg": "Only faculty can end session"}), 403

    # Get session
    session = Session.query.get(session_id)

    if not session:
        return jsonify({"msg": "Session not found"}), 404

    # Optional: ensure same faculty owns session
    if session.faculty_id != user_id:
        return jsonify({"msg": "Unauthorized"}), 403

    # End session
    session.is_active = False
    db.session.commit()

    return jsonify({"msg": "Session ended successfully"}), 200

from flask import request

@attendance_bp.route('/mark', methods=['POST'])
@jwt_required()
def mark_attendance():
    user_id = int(get_jwt_identity())

    data = request.get_json()
    code = data.get("code")

    # Find active session
    session = Session.query.filter_by(code=code, is_active=True).first()

    if not session:
        return jsonify({"msg": "Invalid or expired code"}), 400

    # Check duplicate
    existing = Attendance.query.filter_by(
        session_id=session.id,
        student_id=user_id
    ).first()

    if existing:
        return jsonify({"msg": "Attendance already marked"}), 400

    # Mark attendance
    attendance = Attendance(
        session_id=session.id,
        student_id=user_id
    )
    print("SESSION ID SAVED:", session.id)


    db.session.add(attendance)
    db.session.commit()

    return jsonify({"msg": "Attendance marked successfully"}), 201

@attendance_bp.route('/my', methods=['GET'])
@jwt_required()
def my_attendance():
    user_id = int(get_jwt_identity())

    # Get all attendance records for this student
    records = Attendance.query.filter_by(student_id=user_id).all()

    result = []
    for r in records:
        result.append({
            "session_id": r.session_id,
            "time": r.timestamp
        })

    return jsonify(result), 200

