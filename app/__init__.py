from flask import Flask
import os

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'omtechei-dev-secret')
    app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024
    app.config['LEADS_PATH'] = os.environ.get('LEADS_PATH', '/tmp/leads.jsonl')
    from app.routes import site_bp
    app.register_blueprint(site_bp)
    return app
