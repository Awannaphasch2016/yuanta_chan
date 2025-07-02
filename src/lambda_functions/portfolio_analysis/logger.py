"""
Enhanced Logger for Portfolio Analysis Lambda Function
Provides structured logging with context for portfolio analysis operations
"""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional


class PortfolioAnalysisLogger:
    """
    Structured logger for portfolio analysis operations with enhanced context tracking
    """
    
    def __init__(self, name: str, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Create handler if it doesn't exist
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def info(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """Log info message with optional context"""
        log_data = self._prepare_log_data(message, context, **kwargs)
        self.logger.info(json.dumps(log_data))
    
    def warning(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """Log warning message with optional context"""
        log_data = self._prepare_log_data(message, context, **kwargs)
        self.logger.warning(json.dumps(log_data))
    
    def error(self, message: str, context: Optional[Dict[str, Any]] = None, 
              error: Optional[Exception] = None, **kwargs):
        """Log error message with optional context and exception details"""
        log_data = self._prepare_log_data(message, context, **kwargs)
        
        if error:
            log_data['error_details'] = {
                'type': type(error).__name__,
                'message': str(error),
                'traceback': self._get_traceback_string(error)
            }
        
        self.logger.error(json.dumps(log_data))
    
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """Log debug message with optional context"""
        log_data = self._prepare_log_data(message, context, **kwargs)
        self.logger.debug(json.dumps(log_data))
    
    def _prepare_log_data(self, message: str, context: Optional[Dict[str, Any]] = None, 
                         **kwargs) -> Dict[str, Any]:
        """Prepare structured log data"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'service': 'portfolio_analysis'
        }
        
        if context:
            log_data['context'] = context
        
        if kwargs:
            log_data.update(kwargs)
        
        return log_data
    
    def _get_traceback_string(self, error: Exception) -> str:
        """Get traceback as string"""
        import traceback
        return ''.join(traceback.format_exception(type(error), error, error.__traceback__))


def get_logger(name: str, level: int = logging.INFO) -> PortfolioAnalysisLogger:
    """
    Factory function to create a portfolio analysis logger
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        Configured PortfolioAnalysisLogger instance
    """
    return PortfolioAnalysisLogger(name, level) 