import pytest
import json
from flask import Flask, jsonify
from src.backend.middleware.logging import log_request, init_logging

def test_request_logging(caplog):
    """Test that requests are properly logged"""
    # Create a test Flask app
    app = Flask(__name__)
    init_logging(app)
    
    # Create a test route with logging
    @app.route('/test', methods=['POST'])
    @log_request()
    def test_route():
        return jsonify({'status': 'success'}), 200
    
    # Create a test client
    client = app.test_client()
    
    # Test data with sensitive information
    test_data = {
        'username': 'testuser',
        'password': 'secret123',
        'email': 'test@example.com'
    }
    
    # Make a request
    with app.test_request_context():
        response = client.post('/test', json=test_data)
        
        # Check response
        assert response.status_code == 200
        
        # Check logs
        for record in caplog.records:
            # Convert log message to string for easy checking
            message = record.getMessage()
            
            # Check if request was logged
            if "Incoming request" in message:
                # Parse the JSON part of the log message
                log_data = json.loads(message.split("Incoming request: ")[1])
                
                # Verify sensitive data is redacted
                assert log_data['body']['password'] == '[REDACTED]'
                assert 'username' in log_data['body']
                assert log_data['method'] == 'POST'
                assert log_data['url'] == '/test'
            
            # Check if response was logged
            elif "Request completed" in message:
                # Parse the JSON part of the log message
                log_data = json.loads(message.split("Request completed: ")[1])
                
                # Verify response logging
                assert log_data['status_code'] == 200
                assert 'duration' in log_data