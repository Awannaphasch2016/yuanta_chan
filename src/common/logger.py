"""
Centralized logging utility for AWS Lambda functions
Provides structured logging for CloudWatch integration
"""

import json
import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional


class CloudWatchLogger:
    """
    Centralized logger for AWS Lambda functions with CloudWatch integration.
    Provides structured JSON logging for better CloudWatch analysis.
    """
    
    def __init__(self, function_name: str, log_level: str = "INFO"):
        self.function_name = function_name
        self.logger = logging.getLogger(function_name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Remove existing handlers to avoid duplicates
        for handler in self.logger.handlers:
            self.logger.removeHandler(handler)
        
        # Create console handler for CloudWatch
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)
    
    def _format_message(self, level: str, message: str, 
                       context: Optional[Dict[str, Any]] = None,
                       error: Optional[Exception] = None) -> str:
        """Format log message as structured JSON for CloudWatch"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "function": self.function_name,
            "message": message
        }
        
        if context:
            log_entry["context"] = context
            
        if error:
            log_entry["error"] = {
                "type": type(error).__name__,
                "message": str(error)
            }
        
        return json.dumps(log_entry)
    
    def info(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log info level message"""
        self.logger.info(self._format_message("INFO", message, context))
    
    def warning(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log warning level message"""
        self.logger.warning(self._format_message("WARNING", message, context))
    
    def error(self, message: str, context: Optional[Dict[str, Any]] = None, 
              error: Optional[Exception] = None):
        """Log error level message"""
        self.logger.error(self._format_message("ERROR", message, context, error))
    
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log debug level message"""
        self.logger.debug(self._format_message("DEBUG", message, context))


def get_logger(function_name: str, log_level: str = "INFO") -> CloudWatchLogger:
    """
    Factory function to create a CloudWatch logger instance
    
    Args:
        function_name: Name of the Lambda function
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        CloudWatchLogger instance
    """
    return CloudWatchLogger(function_name, log_level)


def get_lambda_logger(function_name: str, log_level: str = "INFO") -> CloudWatchLogger:
    """
    Factory function to create a CloudWatch logger instance for Lambda functions
    (Alias for get_logger for Lambda function compatibility)
    
    Args:
        function_name: Name of the Lambda function
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        CloudWatchLogger instance
    """
    return CloudWatchLogger(function_name, log_level) 