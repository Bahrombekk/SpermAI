import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(config):
    logger = logging.getLogger('SpermAI')
    logger.setLevel(getattr(logging, config['level']))
    
    # Use log_folder from config
    log_path = os.path.join(config['log_folder'], 'app.log')
    handler = RotatingFileHandler(
        log_path,
        maxBytes=config['max_size'],
        backupCount=config['backup_count']
    )
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger