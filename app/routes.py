from flask import render_template
from app import app

@app.route('/')
def home():
    return render_template('index.html', title="OmTechAI Limited")

@app.route('/services')
def services():
    return render_template('services.html', title="Our Services")

@app.route('/tools')
def tools():
    return render_template('tools.html', title="Our Tools")

@app.route('/contact')
def contact():
    return render_template('contact.html', title="Contact Us")