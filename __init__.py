import os
from flask import Flask
from dotenv import load_dotenv
from .extensions import db, login_manager

load_dotenv()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(app.instance_path, "avatthar.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "..", "uploads")
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from .models import Admin, Course, Project, InternshipApplication
    from .routes import main_bp, auth_bp, admin_bp, api_bp
    from . import user_loader  # register login manager callback

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp, url_prefix="/api")

    with app.app_context():
        db.create_all()
        seed_data()

    return app

def seed_data():
    from .models import Admin, Course, Project
    from werkzeug.security import generate_password_hash

    if not Admin.query.first():
        email = os.getenv("ADMIN_EMAIL", "admin@avattharacademy.com")
        password = os.getenv("ADMIN_PASSWORD", "ChangeMe123!")
        db.session.add(Admin(email=email, password_hash=generate_password_hash(password)))

    if Course.query.count() == 0:
        courses = [
            Course(title="Artificial Intelligence", category="AI", duration="12 Weeks",
                   description="Build practical AI applications from fundamentals to deployment."),
            Course(title="Machine Learning", category="AI", duration="12 Weeks",
                   description="Learn supervised learning, evaluation, feature engineering and projects."),
            Course(title="Generative AI", category="AI", duration="10 Weeks",
                   description="Work with LLMs, prompt engineering, RAG and AI application development."),
            Course(title="Full Stack Development", category="Development", duration="16 Weeks",
                   description="Build production-style web applications with HTML, CSS, JavaScript and Python."),
            Course(title="Python Development", category="Development", duration="10 Weeks",
                   description="Learn Python programming, APIs, databases and backend development."),
            Course(title="Data Science", category="Data", duration="14 Weeks",
                   description="Analyze data, build models and create decision-ready dashboards."),
            Course(title="Cloud & DevOps", category="Cloud", duration="12 Weeks",
                   description="Learn deployment, containers, CI/CD fundamentals and cloud workflows."),
            Course(title="AI Automation", category="Automation", duration="10 Weeks",
                   description="Build business automations, chatbots and AI-assisted workflows."),
        ]
        db.session.add_all(courses)

    if Project.query.count() == 0:
        projects = [
            Project(title="AI Healthcare Platform", category="Artificial Intelligence", description="A practical healthcare workflow prototype using AI-assisted analysis.", image="project-healthcare.jpg"),
            Project(title="Business Automation", category="AI & Automation", description="Automate repetitive business workflows and customer interactions.", image="project-automation.jpg"),
            Project(title="Full Stack Platform", category="Web Development", description="A responsive full-stack application with Python backend and database.", image="project-fullstack.jpg"),
        ]
        db.session.add_all(projects)

    db.session.commit()
