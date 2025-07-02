# src/api/errors.py
from flask import jsonify

def bad_request(message):
    response = {
        'error': 'Bad Request',
        'message': message
    }
    return jsonify(response), 400