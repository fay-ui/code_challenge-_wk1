from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Course, Student

course_bp = Blueprint('course_bp', __name__)

# Create a new course (POST /course)
@course_bp.route("/course", methods=["POST"])
@jwt_required()
def create_course():
    data = request.get_json()

    # Validate required fields
    required_fields = ["name", "description", "credits"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"message": f"Missing {field}"}), 400

    # Check if course exists
    if Course.query.filter_by(name=data["name"]).first():
        return jsonify({"message": "Course with this name already exists"}), 400

    course = Course(
        name=data["name"],
        description=data["description"],
        credits=data["credits"]
    )

    db.session.add(course)
    db.session.commit()

    return jsonify({"message": "Course created successfully!", "course_id": course.id}), 201

# Get all courses (GET /course)
@course_bp.route("/course", methods=["GET"])
def get_courses():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    courses = Course.query.paginate(page, per_page, False)
    course_list = [{"id": course.id, "name": course.name, "description": course.description, "credits": course.credits} for course in courses.items]
    
    return jsonify(course_list), 200

# Enroll student in a course (POST /course/enroll)
@course_bp.route("/course/enroll", methods=["POST"])
@jwt_required()
def enroll_in_course():
    data = request.get_json()
    student_id = get_jwt_identity()
    student = Student.query.get_or_404(student_id)
    course_id = data.get("course_id")

    course = Course.query.get_or_404(course_id)

    if course in student.courses:
        return jsonify({"message": "Student is already enrolled in this course"}), 400

    student.courses.append(course)
    db.session.commit()

    return jsonify({
        "message": "Student enrolled in course successfully!",
        "course_id": course.id,
        "student_id": student.id
    }), 200

# Update a course (PATCH /course/<course_id>)
@course_bp.route("/course/<int:course_id>", methods=["PATCH"])
@jwt_required()
def update_course(course_id):
    course = Course.query.get_or_404(course_id)
    data = request.get_json()

    # Update course fields if provided
    course.name = data.get("name", course.name)
    course.description = data.get("description", course.description)
    course.credits = data.get("credits", course.credits)
    
    db.session.commit()

    return jsonify({"message": "Course updated successfully!", "course_id": course.id}), 200

# Delete course (DELETE /course/<course_id>)
@course_bp.route("/course/<int:course_id>", methods=["DELETE"])
@jwt_required()
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)

    # Check if any students are enrolled in the course
    if course.students:
        return jsonify({"message": "Cannot delete course because students are enrolled."}), 400

    db.session.delete(course)
    db.session.commit()

    return jsonify({"message": "Course deleted successfully!", "course_id": course.id}), 200
