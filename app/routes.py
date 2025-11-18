from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return render_template('index.html', title="OmTechAI Limited")

@main_bp.route('/services')
def services():
    return render_template('services.html', title="Our Services")

@main_bp.route('/tools')
def tools():
    return render_template('tools.html', title="Our Tools")

@main_bp.route('/projects')
def projects():
    return render_template('projects.html', title="Projects & Innovations")

@main_bp.route('/contact')
def contact():
    return render_template('contact.html', title="Contact Us")