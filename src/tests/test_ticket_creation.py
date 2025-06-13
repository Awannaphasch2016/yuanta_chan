"""
Unit tests for Ticket Creation Lambda function.
Tests the ticket management and creation capabilities.
"""

import unittest
import json
import sys
import os
from datetime import datetime

# Add the lambda function directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lambda_functions', 'ticket_creation'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

from lambda_function import TicketCreationService, lambda_handler

class TestTicketCreationService(unittest.TestCase):
    """Test cases for TicketCreationService class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.service = TicketCreationService()
        
        # Sample valid ticket data
        self.valid_ticket_data = {
            "title": "Platform login issues",
            "description": "Unable to access the trading platform after system update",
            "category": "technical",
            "requester": "John Smith"
        }
    
    def test_service_initialization(self):
        """Test service initialization."""
        service = TicketCreationService()
        self.assertIsNotNone(service)
    
    def test_create_ticket_success(self):
        """Test successful ticket creation."""
        result = self.service.create_ticket(self.valid_ticket_data)
        
        # Verify result structure
        self.assertIn("ticket_id", result)
        self.assertIn("title", result)
        self.assertIn("description", result)
        self.assertIn("category", result)
        self.assertEqual(result["title"], "Platform login issues")
        self.assertEqual(result["category"], "technical")
    
    def test_create_ticket_missing_fields(self):
        """Test ticket creation with missing required fields."""
        invalid_data = {"title": "Test"}  # Missing required fields
        
        result = self.service.create_ticket(invalid_data)
        
        # Verify error response
        self.assertIn("error", result)
        self.assertIn("Missing required fields", result["error"])
    
    def test_generate_ticket_id(self):
        """Test ticket ID generation."""
        ticket_id = self.service._generate_ticket_id()
        
        # Verify format starts with TIK-
        self.assertTrue(ticket_id.startswith("TIK-"))
        
        # Verify uniqueness
        ticket_id2 = self.service._generate_ticket_id()
        self.assertNotEqual(ticket_id, ticket_id2)


class TestLambdaHandler(unittest.TestCase):
    """Test cases for the Lambda handler function."""
    
    def test_lambda_handler_missing_action(self):
        """Test handler with missing action parameter."""
        event = {"ticket_data": {}}
        context = None
        
        result = lambda_handler(event, context)
        
        # Verify error response
        self.assertEqual(result["statusCode"], 400)
        body = json.loads(result["body"])
        self.assertIn("error", body)
    
    def test_lambda_handler_invalid_action(self):
        """Test handler with invalid action."""
        event = {"action": "invalid_action"}
        context = None
        
        result = lambda_handler(event, context)
        
        # Verify error response
        self.assertEqual(result["statusCode"], 400)
        body = json.loads(result["body"])
        self.assertIn("error", body)
    
    def test_lambda_handler_create_basic(self):
        """Test create action with valid data."""
        event = {
            "action": "create",
            "ticket_data": {
                "title": "Test ticket",
                "description": "Test description",
                "category": "technical",
                "requester": "Test User"
            }
        }
        context = None
        
        result = lambda_handler(event, context)
        
        # Should return 200 status
        self.assertEqual(result["statusCode"], 200)
        self.assertIn("body", result)


if __name__ == '__main__':
    unittest.main(verbosity=2) 