from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def create_app():
    # Initialize Flask app
    app = Flask(__name__)

    # Configure app
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-this')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///botgram.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db = SQLAlchemy(app)
    migrate = Migrate(app, db)

    # Register blueprints
    from src.backend.api.routes import api
    app.register_blueprint(api)

    @app.route('/')
    def hello_world():
        return jsonify({'message': 'Botgram API is running'})

    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)