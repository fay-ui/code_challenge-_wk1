from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
# Initialize the db object
metadata= MetaData()

db = SQLAlchemy(metadata=metadata)

# Association table for the many-to-many relationship
student_courses = db.Table('student_courses',
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True)
)

# Student Model for User Management
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer)

    # Many-to-many relationship with Course through the association table
    courses = db.relationship('Course', secondary=student_courses, back_populates='students')

    def __repr__(self):
        return f"<Student(name={self.name}, email={self.email})>"

# Course Model
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    credits = db.Column(db.Integer, nullable=False)

    # Many-to-many relationship with Student through the association table
    students = db.relationship('Student', secondary=student_courses, back_populates='courses')

    def __repr__(self):
        return f"<Course(name={self.name}, credits={self.credits})>"
