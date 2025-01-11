from flask import Blueprint, jsonify

# Create Blueprint
api = Blueprint('api', __name__)

@api.route('/api/status')
def get_status():
    return jsonify({
        'status': 'online',
        'version': '0.1.0'
    })