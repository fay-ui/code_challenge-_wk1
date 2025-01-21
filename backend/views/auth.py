from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from flask_mail import Message
from models import db, Student, Course
from datetime import datetime, timezone

auth_bp = Blueprint('auth', __name__)

# Register a new student (POST /register)
@auth_bp.route('/register', methods=['POST'])
def register():
    from app import mail

    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")

    # Validate required fields
    required_fields = ['name', 'email', 'password']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"message": f"Missing {field}"}), 400

    # Check if the student already exists
    if Student.query.filter_by(email=email).first():
        return jsonify({"message": "Student already exists"}), 409

    # Hash the password
    hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

    # Create new student and save
    new_student = Student(name=name, email=email, password=hashed_password)
    db.session.add(new_student)
    db.session.commit()

    # Send a welcome email
    msg = Message(
        "Welcome to AfriHouse Realtors",
        recipients=[email],
        body=f"Hello {name},\n\nThank you for registering with us! We're excited to have you on board.\n\nBest regards,\nAfriHouse Customer Service"
    )
    try:
        mail.send(msg)
    except Exception as e:
        print(f"Error sending email: {e}")
        return jsonify({"message": "Failed to send welcome email"}), 500

    return jsonify({"message": "Student registered successfully"}), 201

# Login (POST /login)
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    student = Student.query.filter_by(email=email).first()

    if not student or not check_password_hash(student.password, password):
        return jsonify({"message": "Invalid email or password"}), 401

    # Generate access token
    access_token = create_access_token(identity=student.id)

    return jsonify({
        "message": "Login successful",
        "student": {
            "email": student.email,
            "name": student.name
        },
        "access_token": access_token
    }), 200

# Current Student Info (GET /current_user)
@auth_bp.route("/current_user", methods=["GET"])
@jwt_required()
def current_user():
    current_user_id = get_jwt_identity()
    student = Student.query.get(current_user_id)

    if student:
        return jsonify({
            "id": student.id,
            "email": student.email,
            "name": student.name
        }), 200

    return jsonify({"message": "Student not found"}), 404

# Update Student Profile (PUT /user/update)
@auth_bp.route("/user/update", methods=["PUT"])
@jwt_required()
def update_profile():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    student = Student.query.get(current_user_id)
    if not student:
        return jsonify({"message": "Student not found"}), 404

    name = data.get("name", student.name)
    email = data.get("email", student.email)

    # Check if the new email already exists
    if email != student.email and Student.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 400

    student.name = name
    student.email = email
    db.session.commit()

    return jsonify({
        "message": "Student profile updated successfully",
        "student": {
            "id": student.id,
            "name": student.name,
            "email": student.email
        }
    }), 200

# Logout (DELETE /logout)
@auth_bp.route("/logout", methods=["DELETE"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    now = datetime.now(timezone.utc)

    # Add the JWT to the blocklist
    db.session.add(TokenBlocklist(jti=jti, created_at=now))
    db.session.commit()

    return jsonify({"message": "Logged out successfully"}), 200

# Delete Student Account (DELETE /user/delete_account)
@auth_bp.route("/user/delete_account", methods=["DELETE"])
@jwt_required()
def delete_account():
    current_user_id = get_jwt_identity()
    student = Student.query.get(current_user_id)

    if not student:
        return jsonify({"message": "Student not found"}), 404

    db.session.delete(student)
    db.session.commit()

    return jsonify({"message": "Student account deleted successfully"}), 200
