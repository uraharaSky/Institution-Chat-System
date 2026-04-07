from flask import Blueprint, request, jsonify
from models import User
from extensions import db, bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth_bp = Blueprint('auth', __name__)

#Register User API

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')

    # Validate input
    if not name or not email or not password or not role:
        return jsonify({"msg": "All fields are required"}), 400

    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"msg": "User already exists"}), 400

    # Hash password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Create user
    new_user = User(
        name=name,
        email=email,
        password=hashed_password,
        role=role
    )

    existing_user = User.query.filter_by(email=email).first()

    print("🔍 Checking email:", email)
    print("🔍 Found user:", existing_user)

    if existing_user:
        return jsonify({"msg": "User already exists"}), 400

    # Save to DB
    try:
        db.session.add(new_user)
        db.session.commit()
        print("User object:", new_user.name, new_user.email, new_user.role)
        print("✅ User committed:", new_user.id)

        return jsonify({"msg": "User created successfully"}), 201  # ✅ ADD THIS

    except Exception as e:
        db.session.rollback()
        print("❌ ERROR:", e)
        return jsonify({"error": str(e)}), 500



# Login User API

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    #Find user
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"msg": "User not found"}), 404

    # Check password
    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"msg": "Invalid password"}), 401

    # Create JWT token
    # token = create_access_token(identity={
    #     "id": user.id,
    #     "role": user.role
    # })

    # token = create_access_token(identity={
    #     "id" : str(user.id),
    #     "role" : user.role
    # })

    token = create_access_token(identity=str(user.id))

    return jsonify({
        "token": token,
        "user": {
            "id": user.id,
            "role": user.role
        }
    }), 200

# Check for recognising user

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    user_id = get_jwt_identity()

    user = User.query.get(user_id)

    return jsonify({
        "id": user.id,
        "role": user.role
    })