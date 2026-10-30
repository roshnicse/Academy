import os
import uuid
from urllib.parse import quote
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from .extensions import db
from .models import Admin, Course, Project, InternshipApplication

main_bp = Blueprint("main", __name__)
auth_bp = Blueprint("auth", __name__)
admin_bp = Blueprint("admin", __name__)
api_bp = Blueprint("api", __name__)

ALLOWED_EXTENSIONS = {"pdf", "doc", "docx"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@main_bp.route("/")
def home():
    courses = Course.query.limit(8).all()
    projects = Project.query.limit(3).all()
    whatsapp = os.getenv("WHATSAPP_NUMBER", "")
    return render_template("index.html", courses=courses, projects=projects, whatsapp=whatsapp)

@main_bp.route("/courses")
def courses():
    return render_template("courses.html", courses=Course.query.all())

@main_bp.route("/internships", methods=["GET", "POST"])
def internships():
    if request.method == "POST":
        data = request.form
        required = ["full_name", "email", "phone", "qualification", "program"]
        if any(not data.get(k, "").strip() for k in required):
            flash("Please complete all required fields.", "error")
            return redirect(url_for("main.internships"))

        resume = request.files.get("resume")
        filename = None
        if resume and resume.filename:
            if not allowed_file(resume.filename):
                flash("Resume must be PDF, DOC or DOCX.", "error")
                return redirect(url_for("main.internships"))
            safe = secure_filename(resume.filename)
            filename = f"{uuid.uuid4().hex}_{safe}"
            resume.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))

        application = InternshipApplication(
            full_name=data["full_name"].strip(),
            email=data["email"].strip(),
            phone=data["phone"].strip(),
            qualification=data["qualification"].strip(),
            program=data["program"].strip(),
            message=data.get("message", "").strip(),
            resume_filename=filename,
        )
        db.session.add(application)
        db.session.commit()
        flash("Application submitted successfully. Our team will contact you.", "success")
        return redirect(url_for("main.internships"))

    return render_template("internships.html")

@main_bp.route("/projects")
def projects():
    return render_template("projects.html", projects=Project.query.all())

@main_bp.route("/placements")
def placements():
    return render_template("placements.html")

@main_bp.route("/contact")
def contact():
    whatsapp = os.getenv("WHATSAPP_NUMBER", "")
    return render_template("contact.html", whatsapp=whatsapp)

@main_bp.route("/uploads/<path:filename>")
@login_required
def uploaded_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename, as_attachment=True)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        admin = Admin.query.filter_by(email=request.form.get("email", "").strip()).first()
        if admin and check_password_hash(admin.password_hash, request.form.get("password", "")):
            login_user(admin)
            return redirect(url_for("admin.dashboard"))
        flash("Invalid email or password.", "error")
    return render_template("admin/login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

@admin_bp.route("/")
@login_required
def dashboard():
    stats = {
        "courses": Course.query.count(),
        "projects": Project.query.count(),
        "applications": InternshipApplication.query.count(),
        "new_applications": InternshipApplication.query.filter_by(status="New").count(),
    }
    applications = InternshipApplication.query.order_by(InternshipApplication.created_at.desc()).limit(10).all()
    return render_template("admin/dashboard.html", stats=stats, applications=applications)

@admin_bp.route("/applications")
@login_required
def applications():
    items = InternshipApplication.query.order_by(InternshipApplication.created_at.desc()).all()
    return render_template("admin/applications.html", applications=items)

@admin_bp.route("/applications/<int:application_id>/status", methods=["POST"])
@login_required
def application_status(application_id):
    application = InternshipApplication.query.get_or_404(application_id)
    status = request.form.get("status", "New")
    if status not in {"New", "Reviewing", "Shortlisted", "Selected", "Rejected"}:
        status = "New"
    application.status = status
    db.session.commit()
    flash("Application status updated.", "success")
    return redirect(url_for("admin.applications"))

@api_bp.route("/chat", methods=["POST"])
def chat():
    from openai import OpenAI

    body = request.get_json(silent=True) or {}
    message = (body.get("message") or "").strip()
    if not message:
        return jsonify({"reply": "Please enter a question."}), 400

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return jsonify({"reply": "I’m Avatthar AI Academy’s assistant. I can help with courses, internships, projects and placement support. Please configure OPENAI_API_KEY in the .env file for AI-powered answers."})

    try:
        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5.5"),
            instructions=(
                "You are Avatthar AI Academy's website assistant. "
                "Answer clearly and professionally. Help visitors with courses, "
                "internships, real-world projects, placement preparation and contact information. "
                "Do not invent guarantees, fees, placement percentages, certifications or company claims. "
                "If information is not available, ask them to contact the academy."
            ),
            input=message,
        )
        return jsonify({"reply": response.output_text})
    except Exception as exc:
        current_app.logger.exception("Chatbot error")
        return jsonify({"reply": "The AI assistant is temporarily unavailable. Please use the WhatsApp button or contact form instead."}), 503

@api_bp.route("/whatsapp-link")
def whatsapp_link():
    number = os.getenv("WHATSAPP_NUMBER", "")
    message = request.args.get("message", "Hello Avatthar AI Academy, I would like to know more about your programs.")
    if not number:
        return jsonify({"url": "#"})
    return jsonify({"url": f"https://wa.me/{number}?text={quote(message)}"})

