# app.py
from flask import Flask
import yaml
import os
from src.api.routes import init_routes
from src.utils.logging import setup_logging

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.secret_key = 'your-secret-key'  # Add for session support
    
    # Load configuration
    with open('configs/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    app.config.update(config)
    
    # Ensure upload and log folders exist
    os.makedirs(app.config['paths']['upload_folder'], exist_ok=True)
    os.makedirs(app.config['paths']['log_folder'], exist_ok=True)
    
    # Setup logging
    logger = setup_logging(app.config['logging'])
    app.logger = logger
    
    # Initialize routes
    init_routes(app)
    
    app.logger.info("Flask application initialized")
    return app


app = create_app()  # Important: define app at global level for deployment

if __name__ == '__main__':
    # Read PORT from environment (fallback to config.yaml or 5000)
    port = int(os.environ.get('PORT', app.config['server'].get('port', 5000)))
    host = app.config['server'].get('host', '0.0.0.0')
    debug = app.config['server'].get('debug', False)

    app.run(
        host=host,
        port=port,
        debug=debug
    )
