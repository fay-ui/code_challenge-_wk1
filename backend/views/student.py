from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Student

student_bp = Blueprint('student_bp', __name__)

# Create a new student (POST /student)
@student_bp.route("/student", methods=["POST"])
def create_student():
    data = request.get_json()

    # Validate required fields
    required_fields = ["name", "email", "password"]
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
        password=generate_password_hash(data["password"]),
        age=data.get("age")
    )

    db.session.add(new_student)
    db.session.commit()

    return jsonify({"message": "Student created successfully!"}), 201

# Get current student profile (GET /student)
@student_bp.route("/student", methods=["GET"])
@jwt_required()
def get_student():
    student_id = get_jwt_identity()
    student = Student.query.get_or_404(student_id)
    return jsonify({"name": student.name, "email": student.email, "age": student.age}), 200

# Update student profile (PATCH /student)
@student_bp.route("/student", methods=["PATCH"])
@jwt_required()
def update_student():
    student_id = get_jwt_identity()
    student = Student.query.get_or_404(student_id)
    data = request.get_json()

    # Update fields if provided
    student.name = data.get("name", student.name)
    student.email = data.get("email", student.email)
    student.age = data.get("age", student.age)
    
    db.session.commit()

    return jsonify({"message": "Profile updated successfully!"}), 200

# Delete student (DELETE /student)
@student_bp.route("/student", methods=["DELETE"])
@jwt_required()
def delete_student():
    student_id = get_jwt_identity()
    student = Student.query.get_or_404(student_id)

    db.session.delete(student)
    db.session.commit()

    return jsonify({"message": "Student deleted successfully!"}), 200
