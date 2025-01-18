"""
Standard API response formats.
"""
from flask import jsonify
from typing import Any, Dict, Optional, Union

class APIResponse:
    """Standardized API response format."""
    
    @staticmethod
    def success(message: str = "Success", data: Optional[Any] = None) -> Dict:
        """
        Create a success response.
        
        Args:
            message: Success message
            data: Optional data to include in response
            
        Returns:
            dict: Formatted success response
        """
        response = {
            "status": "success",
            "message": message
        }
        
        if data is not None:
            response["data"] = data
            
        return jsonify(response)
    
    @staticmethod
    def error(message: str, 
             errors: Optional[Dict] = None,
             status_code: int = 400) -> tuple[Dict, int]:
        """
        Create an error response.
        
        Args:
            message: Error message
            errors: Optional dictionary of specific errors
            status_code: HTTP status code
            
        Returns:
            tuple: (Error response dict, status code)
        """
        response = {
            "status": "error",
            "message": message
        }
        
        if errors:
            response["errors"] = errors
            
        return jsonify(response), status_code

class ValidationError(Exception):
    """Raised when request data validation fails."""
    def __init__(self, message: str, errors: Optional[Dict] = None):
        super().__init__(message)
        self.message = message
        self.errors = errors

class AuthError(Exception):
    """Raised when authentication or authorization fails."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
