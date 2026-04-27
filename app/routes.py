from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from flask import Blueprint, current_app, jsonify, render_template, request

site_bp = Blueprint('site', __name__)

COMPANY = {
    'name': 'OmtechEI Limited',
    'tagline': 'Empowering Intelligence',
    'description': (
        'OmtechEI Limited is a technology-driven software development company focused on '
        'building intelligent, scalable, and user-centric digital solutions for education, '
        'finance, business automation, and interactive web platforms.'
    ),
    'email': 'omtechei@hotmail.com',
    'phone': '+234 706 5894 127',
    'location': 'Nigeria',
}

NAV_ITEMS = [
    {'label': 'Home', 'href': '/'},
    {'label': 'Services', 'href': '/services'},
    {'label': 'Solutions', 'href': '/tools'},
    {'label': 'Projects', 'href': '/projects'},
    {'label': 'Contact', 'href': '/contact'},
]

HERO_STATS = [
    {'value': 'Fullstack', 'label': 'Flask, FastAPI, Django, Node.js'},
    {'value': 'Databases', 'label': 'MySQL, PostgreSQL, Neon, SQLAlchemy'},
    {'value': 'AI + Cloud', 'label': 'automation, APIs, and scaling'},
    {'value': 'Mobile first', 'label': 'responsive UI/UX systems'},
]

CORE_EXPERTISE = [
    {'title': 'Fullstack web application development', 'body': 'Building reliable web platforms with Flask, FastAPI, Django, and Node.js.'},
    {'title': 'Database architecture and optimization', 'body': 'Designing data layers with MySQL, PostgreSQL, Neon, and SQLAlchemy.'},
    {'title': 'UI/UX design', 'body': 'Crafting responsive, mobile-first interfaces that feel clear and modern.'},
    {'title': 'API development and integration', 'body': 'Connecting systems with clean APIs and practical integrations.'},
    {'title': 'Automation and AI-assisted solutions', 'body': 'Embedding intelligence into workflows, content, and internal tools.'},
    {'title': 'Education and fintech platforms', 'body': 'Building systems for schools, monetized products, and referral models.'},
]

SERVICES = [
    {'title': 'Web platforms', 'body': 'We build interactive web platforms, admin dashboards, and client portals.'},
    {'title': 'Learning systems', 'body': 'We create SSME and exam platforms for schools and training organizations.'},
    {'title': 'Fintech systems', 'body': 'We design monetized subscription systems, referral logic, and admin controls.'},
    {'title': 'AI features', 'body': 'We add AI lesson planning, content generation, and workflow automation.'},
    {'title': 'Cloud deployment', 'body': 'We prepare modern apps for reliable deployment, monitoring, and scale.'},
    {'title': 'Product design', 'body': 'We make software feel structured, intuitive, and usable across devices.'},
]

PRODUCTS = [
    {
        'name': 'Referral Subscription Platform',
        'summary': 'A scalable monetized system with package-based restrictions, tracking, and admin oversight.',
        'highlights': ['Referral commission structure', 'Income tracking', 'Secure dashboards'],
    },
    {
        'name': 'Learning Management System',
        'summary': 'An e-learning platform for courses, content, blog and podcast modules, and role-based access.',
        'highlights': ['Admin, teacher, student roles', 'Digital library', 'Learning materials'],
    },
    {
        'name': 'Online Examination Platform',
        'summary': 'A robust examination engine with online and offline capabilities for institutions.',
        'highlights': ['Timed exams', 'Question filtering', 'Anti-cheating controls'],
    },
    {
        'name': 'AI Lesson Planner',
        'summary': 'An AI productivity system that generates structured lesson plans and exports them for schools.',
        'highlights': ['DOCX/PDF export', 'Template support', 'Curriculum-aligned planning'],
    },
    {
        'name': 'Smart Notification System',
        'summary': 'A push notification backend with topic broadcasts and real-time delivery support.',
        'highlights': ['Firebase integration', 'Broadcast topics', 'Scalable messaging'],
    },
    {
        'name': 'AI Presentation Generator',
        'summary': 'An in-development engine for converting AI text into structured presentation decks.',
        'highlights': ['Slide structuring', 'Visual flow', 'PPTX export'],
    },
]

PROJECTS = [
    {
        'title': 'Referral-based monetization system',
        'detail': 'A package-driven platform with income tracking, commission logic, and an admin panel for financial monitoring.',
        'tags': ['Fintech', 'Monetization', 'Admin'],
    },
    {
        'title': 'Educational SSME',
        'detail': 'A modular learning system with course enrollment, library access, and content modules for institutions.',
        'tags': ['EdTech', 'SSME', 'Role-based access'],
    },
    {
        'title': 'Institutional exam platform',
        'detail': 'An exam system with teacher-controlled questions, randomized order, offline mode, and auto-save support.',
        'tags': ['Exams', 'Offline first', 'Security'],
    },
    {
        'title': 'AI lesson planner',
        'detail': 'An AI-assisted teacher productivity tool for generating curriculum-aligned lesson plans with exports.',
        'tags': ['AI', 'Education', 'DOCX/PDF'],
    },
    {
        'title': 'Health monitoring IoT system',
        'detail': 'An Arduino-based health prototype for real-time oxygen monitoring and LCD-based patient status display.',
        'tags': ['IoT', 'Healthcare', 'Embedded'],
    },
    {
        'title': 'Smart notification backend',
        'detail': 'A messaging infrastructure for scalable push delivery and topic-based broadcasting.',
        'tags': ['Backend', 'Messaging', 'Push'],
    },
]

PROCESS = [
    {'step': '01', 'title': 'Discover', 'body': 'We map your goals, audience, technical constraints, and launch timeline.'},
    {'step': '02', 'title': 'Design', 'body': 'We turn the strategy into interfaces, architecture, and a delivery plan.'},
    {'step': '03', 'title': 'Build', 'body': 'We ship in tight cycles and keep stakeholders aligned with working progress.'},
    {'step': '04', 'title': 'Scale', 'body': 'We monitor, improve, and extend the product once the first release proves value.'},
]

TESTIMONIALS = [
    {'quote': 'OmtechEI turns complex ideas into software that is practical, secure, and easy to use.', 'name': 'Client feedback', 'role': 'Platform delivery'},
    {'quote': 'Their systems feel like they were built by people who understand both product and engineering.', 'name': 'Project stakeholder', 'role': 'Digital transformation'},
    {'quote': 'The team works across education, finance, and automation without losing quality or speed.', 'name': 'Partner review', 'role': 'Cross-sector systems'},
]

FAQS = [
    {'question': 'What industries do you focus on?', 'answer': 'Education, finance, business automation, and interactive web platforms are our main focus areas.'},
    {'question': 'What technologies do you use?', 'answer': 'We work with Flask, FastAPI, Django, Node.js, MySQL, PostgreSQL, Neon, and SQLAlchemy.'},
    {'question': 'Can you build both products and internal tools?', 'answer': 'Yes. We design public-facing platforms, admin systems, and internal automation tools.'},
]

SITE_DATA = {
    'company': COMPANY,
    'nav_items': NAV_ITEMS,
    'hero_stats': HERO_STATS,
    'core_expertise': CORE_EXPERTISE,
    'services': SERVICES,
    'products': PRODUCTS,
    'projects': PROJECTS,
    'process': PROCESS,
    'testimonials': TESTIMONIALS,
    'faqs': FAQS,
}

@site_bp.app_context_processor
def inject_globals():
    return {'company': COMPANY, 'nav_items': NAV_ITEMS}

@site_bp.route('/')
def home():
    return render_template('index.html', title='OmtechEI Limited', **SITE_DATA)

@site_bp.route('/services')
def services():
    return render_template('services.html', title='Services', **SITE_DATA)

@site_bp.route('/tools')
def tools():
    return render_template('tools.html', title='Products', **SITE_DATA)

@site_bp.route('/projects')
def projects():
    return render_template('projects.html', title='Projects', **SITE_DATA)

@site_bp.route('/contact')
def contact():
    return render_template('contact.html', title='Contact', **SITE_DATA)

@site_bp.route('/api/contact', methods=['POST'])
def api_contact():
    data = request.get_json(silent=True) or request.form.to_dict()
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip()
    company = (data.get('company') or '').strip()
    message = (data.get('message') or '').strip()
    service = (data.get('service') or '').strip()
    if not name or not email or not message or not service:
        return jsonify({'error': 'Name, email, service, and message are required.'}), 400
    payload = {'name': name, 'email': email, 'company': company, 'service': service, 'message': message, 'created_at': datetime.utcnow().isoformat(timespec='seconds') + 'Z'}
    leads_path = Path(current_app.instance_path) / 'leads.jsonl'
    leads_path.parent.mkdir(parents=True, exist_ok=True)
    with leads_path.open('a', encoding='utf-8') as handle:
        handle.write(json.dumps(payload) + '\n')
    return jsonify({'message': 'Thanks. OmtechEI Limited received your inquiry.', 'lead': payload})

@site_bp.route('/health')
def health():
    return jsonify({'status': 'ok', 'brand': COMPANY['name']})
