import json

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Poll, Vote, User
from extensions import db
from collections import Counter

poll_bp = Blueprint('poll', __name__)

#creating a poll

@poll_bp.route('/', methods=['POST'])
@jwt_required()
def create_poll():

    from utils.notification import create_notification

    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    # 🔒 Only faculty or CR
    if user.role not in ["faculty", "cr"]:
        return jsonify({"msg": "Not allowed"}), 403

    data = request.get_json()

    question = data.get("question")
    options = data.get("options")

    if not question or not options or len(options) < 2:
        return jsonify({"msg": "Invalid poll data"}), 400

    # ✅ Create poll
    poll = Poll(
        question=question,
        options=options,
        created_by=user_id
    )

    db.session.add(poll)
    db.session.flush()   # 🔥 get poll.id without commit

    # =========================
    # 🔔 NOTIFICATIONS
    # =========================

    students = User.query.filter(User.role == "student").all()

    for s in students:
        create_notification(
            s.id,
            "New Poll",
            f"{question}",
            "poll",
            ref_id=poll.id,
            ref_type="poll"
        )

    # ✅ single commit
    db.session.commit()

    return jsonify({
        "msg": "Poll created",
        "poll_id": poll.id
    }), 201


# voting in poll
@poll_bp.route('/<int:poll_id>/vote', methods=['POST'])
@jwt_required()
def vote_poll(poll_id):

    from utils.notification import create_notification

    user_id = int(get_jwt_identity())
    data = request.get_json()

    option_indices = data.get("option_indices", [])

    poll = Poll.query.get(poll_id)
    if not poll:
        return jsonify({"msg": "Poll not found"}), 404

    # ✅ Validate input
    if not option_indices or not isinstance(option_indices, list):
        return jsonify({"msg": "Invalid input"}), 400

    # ✅ Validate indices
    for idx in option_indices:
        if not isinstance(idx, int) or idx < 0 or idx >= len(poll.options):
            return jsonify({"msg": f"Invalid option index: {idx}"}), 400

    # ✅ Single select restriction
    if not poll.multi_select and len(option_indices) > 1:
        return jsonify({"msg": "Only one option allowed"}), 400

    # 🧹 Remove old votes
    Vote.query.filter_by(
        poll_id=poll_id,
        user_id=user_id
    ).delete()

    # ✅ Insert new votes
    for idx in option_indices:
        vote = Vote(
            poll_id=poll_id,
            user_id=user_id,
            option_index=idx
        )
        db.session.add(vote)

    # =========================
    # 🔔 NOTIFY POLL CREATOR
    # =========================

    if poll.created_by != user_id:
        create_notification(
            poll.created_by,
            "Poll Update",
            "Someone voted on your poll",
            "poll",
            ref_id=poll_id,
            ref_type="poll"
        )

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

    # ✅ Count votes using option_index
    counts = Counter([v.option_index for v in votes])

    total_votes = len(votes)

    results = []

    for idx, option in enumerate(poll.options):
        vote_count = counts.get(idx, 0)
        percentage = (vote_count / total_votes * 100) if total_votes > 0 else 0

        results.append({
            "option": option,
            "votes": vote_count,
            "percentage": round(percentage, 2)
        })

    return jsonify({
        "question": poll.question,
        "total_votes": total_votes,
        "results": results
    }), 200

@poll_bp.route('/', methods=['GET'])
@jwt_required()
def get_polls():

    polls = Poll.query.order_by(Poll.id.desc()).all()

    result = []

    import json

    for p in polls:

        # 🔒 SAFE options parsing
        if isinstance(p.options, list):
            options = p.options
        elif isinstance(p.options, str):
            try:
                options = json.loads(p.options)
            except:
                options = []
        else:
            options = []

        # 🔒SAFE multi_select (in case column missing in old rows)
        multi_select = getattr(p, "multi_select", False)

        result.append({
            "id": p.id,
            "question": p.question,
            "options": options,
            "multi_select": bool(p.multi_select)
        })

    return jsonify(result), 200