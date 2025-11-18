from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('instance/sessions', exist_ok=True)
    app.run(debug=True)