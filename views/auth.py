from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from models import db, Student

auth_bp = Blueprint('auth', __name__)

# Register a new student (POST /register)
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Validate required fields
    required_fields = ['name', 'email', 'password']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"message": f"Missing {field}"}), 400

    # Check if student already exists
    if Student.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "Student already exists"}), 400

    # Create new student with hashed password
    new_student = Student(
        name=data["name"],
        email=data["email"],
        password=generate_password_hash(data["password"])
    )

    db.session.add(new_student)
    db.session.commit()

    return jsonify({"message": "Student registered successfully!"}), 201

# Login (POST /login)
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # Validate required fields
    if not data.get('email') or not data.get('password'):
        return jsonify({"message": "Missing email or password"}), 400

    student = Student.query.filter_by(email=data["email"]).first()

    # Check if student exists and password is correct
    if not student or not check_password_hash(student.password, data["password"]):
        return jsonify({"message": "Invalid credentials"}), 401

    # Generate access token
    access_token = create_access_token(identity=student.id)
    return jsonify({"access_token": access_token}), 200
