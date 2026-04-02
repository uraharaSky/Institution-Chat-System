import json

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
        options=data.get("options"),
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
    selected_options = data.get("options")  #  list

    poll = Poll.query.get(poll_id)
    if not poll:
        return jsonify({"msg": "Poll not found"}), 404

    if not selected_options or not isinstance(selected_options, list):
        return jsonify({"msg": "Invalid input"}), 400

    # ✅ Validate options
    for opt in selected_options:
        if opt not in poll.options:
            return jsonify({"msg": f"Invalid option: {opt}"}), 400

    # Check existing vote
    existing = Vote.query.filter_by(
        poll_id=poll_id,
        user_id=user_id
    ).first()

    import json

    if existing:
        existing.selected_options = json.dumps(selected_options)
        existing.selected_option = selected_options[0] if selected_options else None
    else:
        vote = Vote(
            poll_id=poll_id,
            user_id=user_id,
            selected_options=json.dumps(selected_options),
            selected_option=selected_options[0] if selected_options else None
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

    import json

    count = {}

    for v in votes:

        if not v.selected_options:
            continue

        try:
            selected_list = json.loads(v.selected_options)
        except:
            continue

        for opt in selected_list:
            count[opt] = count.get(opt, 0) + 1

    return jsonify(count), 200

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
            "multi_select": multi_select
        })

    return jsonify(result), 200