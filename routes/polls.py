from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Poll, Vote, User
from extensions import db

poll_bp = Blueprint('poll', __name__)

#creating a poll

@poll_bp.route('/', methods=['POST'])
@jwt_required()
def create_poll():
    user_id = int(get_jwt_identity())

    user = User.query.get(user_id)

    # 🔒 Only faculty or CR
    if user.role not in ["faculty", "cr"]:
        return jsonify({"msg": "Not allowed"}), 403

    data = request.get_json()

    question = data.get("question")
    options = data.get("options")  # list

    if not question or not options or len(options) < 2:
        return jsonify({"msg": "Invalid poll data"}), 400

    poll = Poll(
        question=question,
        options=options,
        created_by=user_id
    )

    db.session.add(poll)
    db.session.commit()

    return jsonify({
        "msg": "Poll created",
        "poll_id": poll.id
    }), 201

# voting in poll

@poll_bp.route('/<int:poll_id>/vote', methods=['POST'])
@jwt_required()
def vote_poll(poll_id):
    user_id = int(get_jwt_identity())

    data = request.get_json()
    selected = data.get("option")

    poll = Poll.query.get(poll_id)
    if not poll:
        return jsonify({"msg": "Poll not found"}), 404

    if selected not in poll.options:
        return jsonify({"msg": "Invalid option"}), 400

    # Check if already voted
    existing = Vote.query.filter_by(
        poll_id=poll_id,
        user_id=user_id
    ).first()

    if existing:
        existing.selected_option = selected
    else:
        vote = Vote(
            poll_id=poll_id,
            user_id=user_id,
            selected_option=selected
        )
        db.session.add(vote)

    db.session.commit()

    return jsonify({"msg": "Vote recorded"}), 200

# poll results

@poll_bp.route('/<int:poll_id>/results', methods=['GET'])
@jwt_required()
def poll_results(poll_id):
    poll = Poll.query.get(poll_id)

    if not poll:
        return jsonify({"msg": "Poll not found"}), 404

    votes = Vote.query.filter_by(poll_id=poll_id).all()

    result = {option: 0 for option in poll.options}

    for v in votes:
        result[v.selected_option] += 1

    return jsonify(result), 200


@poll_bp.route('/', methods=['GET'])
@jwt_required()
def get_polls():
    polls = Poll.query.all()

    result = []
    for p in polls:
        result.append({
            "id": p.id,
            "question": p.question,
            "options": p.options
        })

    return jsonify(result), 200