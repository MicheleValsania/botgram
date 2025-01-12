from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Import models
from .models.models import Account, Configuration, InteractionLog, TargetProfile
from .config.database import db

# Load environment variables
load_dotenv()

def create_app():
    # Initialize Flask app
    app = Flask(__name__)
    
    # Enable CORS
    CORS(app)

    # Configure app
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-this')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        'sqlite:///botgram.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-this')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 24 * 60 * 60  # 24 ore in secondi
    
    # Initialize database
    db.init_app(app)
    
    # Initialize migrations
    migrate = Migrate(app, db)

    # Register error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad Request', 'message': str(error)}), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'Unauthorized', 'message': str(error)}), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Forbidden', 'message': str(error)}), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not Found', 'message': str(error)}), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({'error': 'Internal Server Error', 'message': str(error)}), 500

    # Register blueprints
    from .api.routes import api
    app.register_blueprint(api)

    @app.route('/')
    def hello_world():
        return jsonify({'message': 'Botgram API is running'})

    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)