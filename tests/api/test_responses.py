import pytest
import json
from src.backend.middleware.response import APIResponse

def test_success_response():
    """Test success response format."""
    test_data = {'key': 'value'}
    response, status_code = APIResponse.success(
        data=test_data,
        message='Success message'
    )
    
    response_data = json.loads(response.get_data(as_text=True))
    
    assert status_code == 200
    assert response_data['success'] is True
    assert response_data['message'] == 'Success message'
    assert response_data['data'] == test_data

def test_success_response_with_custom_code():
    """Test success response with custom status code."""
    response, status_code = APIResponse.success(
        data={'created': True},
        message='Resource created',
        status_code=201
    )
    
    assert status_code == 201
    response_data = json.loads(response.get_data(as_text=True))
    assert response_data['success'] is True

def test_success_response_with_meta():
    """Test success response with metadata."""
    meta = {
        'page': 1,
        'total': 100,
        'per_page': 10
    }
    
    response, status_code = APIResponse.success(
        data=[1, 2, 3],
        message='Success with meta',
        meta=meta
    )
    
    response_data = json.loads(response.get_data(as_text=True))
    assert 'meta' in response_data
    assert response_data['meta'] == meta

def test_error_response():
    """Test error response format."""
    response, status_code = APIResponse.error(
        message='Error message',
        status_code=400,
        error_code='VALIDATION_ERROR'
    )
    
    response_data = json.loads(response.get_data(as_text=True))
    
    assert status_code == 400
    assert response_data['success'] is False
    assert response_data['message'] == 'Error message'
    assert response_data['error_code'] == 'VALIDATION_ERROR'

def test_error_response_with_details():
    """Test error response with validation details."""
    error_details = {
        'field1': ['Invalid input'],
        'field2': ['Required field']
    }
    
    response, status_code = APIResponse.error(
        message='Validation failed',
        status_code=400,
        error_code='VALIDATION_ERROR',
        errors=error_details
    )
    
    response_data = json.loads(response.get_data(as_text=True))
    assert 'errors' in response_data
    assert response_data['errors'] == error_details

def test_error_response_server_error():
    """Test internal server error response."""
    response, status_code = APIResponse.error(
        message='Internal server error',
        status_code=500,
        error_code='INTERNAL_ERROR'
    )
    
    assert status_code == 500
    response_data = json.loads(response.get_data(as_text=True))
    assert response_data['error_code'] == 'INTERNAL_ERROR'