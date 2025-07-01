"""
Centralized logging configuration for Portfolio News Lambda
Provides structured logging with context and error handling
"""

import logging
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional


class LambdaLogger:
    """
    Custom logger for AWS Lambda with structured logging support
    """
    
    def __init__(self, logger_name: str, level: str = "INFO"):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Only add handler if none exists to avoid duplicates
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def _format_message(self, message: str, context: Optional[Dict[str, Any]] = None, 
                       error: Optional[Exception] = None) -> str:
        """
        Format log message with context and error information
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'message': message
        }
        
        if context:
            log_entry['context'] = context
            
        if error:
            log_entry['error'] = {
                'type': type(error).__name__,
                'message': str(error)
            }
        
        return json.dumps(log_entry, default=str)
    
    def info(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log info message with optional context"""
        formatted_message = self._format_message(message, context)
        self.logger.info(formatted_message)
    
    def warning(self, message: str, context: Optional[Dict[str, Any]] = None, 
               error: Optional[Exception] = None):
        """Log warning message with optional context and error"""
        formatted_message = self._format_message(message, context, error)
        self.logger.warning(formatted_message)
    
    def error(self, message: str, context: Optional[Dict[str, Any]] = None, 
             error: Optional[Exception] = None):
        """Log error message with optional context and error"""
        formatted_message = self._format_message(message, context, error)
        self.logger.error(formatted_message)
    
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log debug message with optional context"""
        formatted_message = self._format_message(message, context)
        self.logger.debug(formatted_message)


def get_logger(name: str, level: str = "INFO") -> LambdaLogger:
    """
    Factory function to create and configure a logger instance
    
    Args:
        name: Logger name (typically module or function name)
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Configured LambdaLogger instance
    """
    return LambdaLogger(name, level) 