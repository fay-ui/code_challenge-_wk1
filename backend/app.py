from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from views.auth import auth_bp  # Blueprint for authentication
from views.course import course_bp  # Blueprint for course-related functionality
from views.student import student_bp  # Blueprint for student-related functionality
from models import db
# Initialize extensions

migrate = Migrate()
jwt = JWTManager()

# Create Flask app instance
app = Flask(__name__)


# Configure the app
class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///student.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'hyvcefuevfeufinsuif'

app.config.from_object(Config)

# Initialize extensions with app
db.init_app(app)
migrate.init_app(app, db)
jwt.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(course_bp)
app.register_blueprint(student_bp)

# Create database tables on startup (only in development)
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
