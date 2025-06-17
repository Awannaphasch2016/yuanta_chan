"""
Ticket Creation Lambda Function
Handles internal ticket creation and management for investment consultant workflows
Designed for Amazon Bedrock Agent integration
"""

import json
import sys
import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List

from logger import get_logger


class TicketCreationService:
    """
    Service for creating and managing internal tickets for investment consultant workflows.
    Integrates with internal ticketing systems and provides standardized ticket management.
    """
    
    def __init__(self):
        self.logger = get_logger("TicketCreationLambda")
        self.required_fields = ['title', 'description', 'category', 'requester']
        self.valid_categories = ['technical', 'research', 'client_service', 'platform', 'data', 'general']
        self.valid_priorities = ['low', 'medium', 'high', 'urgent']
        self.valid_statuses = ['open', 'in_progress', 'resolved', 'closed']
    
    def create_ticket(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new internal ticket
        
        Args:
            ticket_data: Dictionary containing ticket information
            
        Returns:
            Dictionary containing created ticket information or error details
        """
        try:
            self.logger.info("Creating new ticket", context={"ticket_data": ticket_data})
            
            # Validate required fields
            validation_result = self._validate_ticket_data(ticket_data)
            if not validation_result['valid']:
                return self._error_response(validation_result['error'])
            
            # Generate ticket ID
            ticket_id = self._generate_ticket_id()
            
            # Create ticket record
            ticket = {
                'ticket_id': ticket_id,
                'title': ticket_data['title'],
                'description': ticket_data['description'],
                'category': ticket_data['category'],
                'requester': ticket_data['requester'],
                'priority': ticket_data.get('priority', 'medium'),
                'status': 'open',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'assigned_to': ticket_data.get('assigned_to'),
                'tags': ticket_data.get('tags', []),
                'metadata': {
                    'source': 'bedrock_agent',
                    'created_via': 'lambda_function',
                    'system_version': '1.0'
                }
            }
            
            # Process ticket (in a real implementation, this would save to database)
            processed_ticket = self._process_ticket_creation(ticket)
            
            self.logger.info(f"Ticket created successfully: {ticket_id}")
            
            return {
                'success': True,
                'ticket_id': ticket_id,
                'title': ticket['title'],
                'description': ticket['description'],
                'category': ticket['category'],
                'status': ticket['status'],
                'created_at': ticket['created_at'],
                'message': 'Ticket created successfully'
            }
            
        except Exception as e:
            self.logger.error("Ticket creation failed", context=None, error=e)
            return self._error_response(f"Ticket creation failed: {str(e)}")
    
    def get_ticket_status(self, ticket_id: str) -> Dict[str, Any]:
        """
        Get status of an existing ticket
        
        Args:
            ticket_id: Ticket identifier
            
        Returns:
            Dictionary containing ticket status information
        """
        try:
            self.logger.info(f"Retrieving status for ticket: {ticket_id}")
            
            if not ticket_id:
                return self._error_response("Ticket ID is required")
            
            # In a real implementation, this would query a database
            # For now, return a mock status
            mock_status = {
                'ticket_id': ticket_id,
                'status': 'open',
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'message': 'This is a mock status response - database integration not implemented'
            }
            
            return {
                'success': True,
                'ticket_status': mock_status
            }
            
        except Exception as e:
            self.logger.error(f"Status retrieval failed for ticket {ticket_id}", context=None, error=e)
            return self._error_response(f"Status retrieval failed: {str(e)}")
    
    def update_ticket(self, ticket_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing ticket
        
        Args:
            ticket_id: Ticket identifier
            updates: Dictionary containing fields to update
            
        Returns:
            Dictionary containing update results
        """
        try:
            self.logger.info(f"Updating ticket: {ticket_id}", context={"updates": updates})
            
            if not ticket_id:
                return self._error_response("Ticket ID is required")
            
            # Validate update fields
            allowed_update_fields = ['status', 'priority', 'assigned_to', 'description', 'tags']
            invalid_fields = [field for field in updates.keys() if field not in allowed_update_fields]
            
            if invalid_fields:
                return self._error_response(f"Invalid update fields: {invalid_fields}")
            
            # Validate status if being updated
            if 'status' in updates and updates['status'] not in self.valid_statuses:
                return self._error_response(f"Invalid status: {updates['status']}. Valid statuses: {self.valid_statuses}")
            
            # Validate priority if being updated
            if 'priority' in updates and updates['priority'] not in self.valid_priorities:
                return self._error_response(f"Invalid priority: {updates['priority']}. Valid priorities: {self.valid_priorities}")
            
            # In a real implementation, this would update the database
            updated_ticket = {
                'ticket_id': ticket_id,
                'updated_fields': list(updates.keys()),
                'updated_at': datetime.now().isoformat(),
                'message': 'Ticket updated successfully (mock response)'
            }
            
            self.logger.info(f"Ticket updated successfully: {ticket_id}")
            
            return {
                'success': True,
                'ticket_update': updated_ticket
            }
            
        except Exception as e:
            self.logger.error(f"Ticket update failed for {ticket_id}", context=None, error=e)
            return self._error_response(f"Ticket update failed: {str(e)}")
    
    def list_tickets(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        List tickets with optional filtering
        
        Args:
            filters: Optional filtering criteria
            
        Returns:
            Dictionary containing list of tickets
        """
        try:
            self.logger.info("Listing tickets", context={"filters": filters})
            
            # In a real implementation, this would query a database
            # For now, return mock data
            mock_tickets = [
                {
                    'ticket_id': 'TIK-MOCK-001',
                    'title': 'Sample Technical Issue',
                    'category': 'technical',
                    'status': 'open',
                    'created_at': datetime.now().isoformat()
                },
                {
                    'ticket_id': 'TIK-MOCK-002',
                    'title': 'Research Request',
                    'category': 'research',
                    'status': 'in_progress',
                    'created_at': datetime.now().isoformat()
                }
            ]
            
            return {
                'success': True,
                'tickets': mock_tickets,
                'count': len(mock_tickets),
                'message': 'Mock ticket list - database integration not implemented'
            }
            
        except Exception as e:
            self.logger.error("Ticket listing failed", context=None, error=e)
            return self._error_response(f"Ticket listing failed: {str(e)}")
    
    def _validate_ticket_data(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate ticket data for required fields and valid values"""
        
        # Check required fields
        missing_fields = [field for field in self.required_fields if not ticket_data.get(field)]
        if missing_fields:
            return {
                'valid': False,
                'error': f"Missing required fields: {missing_fields}"
            }
        
        # Validate category
        category = ticket_data.get('category')
        if category not in self.valid_categories:
            return {
                'valid': False,
                'error': f"Invalid category: {category}. Valid categories: {self.valid_categories}"
            }
        
        # Validate priority if provided
        priority = ticket_data.get('priority')
        if priority and priority not in self.valid_priorities:
            return {
                'valid': False,
                'error': f"Invalid priority: {priority}. Valid priorities: {self.valid_priorities}"
            }
        
        # Validate title length
        title = ticket_data.get('title', '')
        if len(title) < 5:
            return {
                'valid': False,
                'error': "Title must be at least 5 characters long"
            }
        
        # Validate description length
        description = ticket_data.get('description', '')
        if len(description) < 10:
            return {
                'valid': False,
                'error': "Description must be at least 10 characters long"
            }
        
        return {'valid': True}
    
    def _generate_ticket_id(self) -> str:
        """Generate a unique ticket ID"""
        timestamp = datetime.now().strftime("%Y%m%d")
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"TIK-{timestamp}-{unique_id}"
    
    def _process_ticket_creation(self, ticket: Dict[str, Any]) -> Dict[str, Any]:
        """Process ticket creation (placeholder for database integration)"""
        
        # In a real implementation, this would:
        # 1. Save to database
        # 2. Send notifications
        # 3. Update tracking systems
        # 4. Apply business rules
        
        # For now, just log the creation
        self.logger.info(f"Processing ticket creation: {ticket['ticket_id']}")
        
        # Add processing metadata
        ticket['processing'] = {
            'processed_at': datetime.now().isoformat(),
            'processing_status': 'completed',
            'notes': 'Mock processing - database integration not implemented'
        }
        
        return ticket
    
    def _error_response(self, error_message: str) -> Dict[str, Any]:
        """Generate standardized error response"""
        return {
            'success': False,
            'error': error_message,
            'timestamp': datetime.now().isoformat()
        }


def lambda_handler(event, context):
    """
    AWS Lambda handler for ticket creation and management requests
    
    Expected event format:
    {
        "action": "create|status|update|list",
        "ticket_id": "TIK-xxx" (for status/update actions),
        "ticket_data": {...} (for create action),
        "updates": {...} (for update action),
        "filters": {...} (for list action)
    }
    """
    logger = get_logger("TicketCreationHandler")
    
    try:
        logger.info("Ticket Creation Lambda function invoked", context={"event": event})
        
        # Extract action from event
        action = event.get('action')
        
        if not action:
            error_response = {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'error': 'Missing required parameter: action',
                    'valid_actions': ['create', 'status', 'update', 'list'],
                    'timestamp': datetime.now().isoformat()
                })
            }
            logger.warning("Missing action parameter in request")
            return error_response
        
        # Initialize service
        service = TicketCreationService()
        
        # Route to appropriate action handler
        if action == 'create':
            ticket_data = event.get('ticket_data', {})
            result = service.create_ticket(ticket_data)
            
        elif action == 'status':
            ticket_id = event.get('ticket_id')
            if not ticket_id:
                result = {'success': False, 'error': 'Missing ticket_id for status action'}
            else:
                result = service.get_ticket_status(ticket_id)
                
        elif action == 'update':
            ticket_id = event.get('ticket_id')
            updates = event.get('updates', {})
            if not ticket_id:
                result = {'success': False, 'error': 'Missing ticket_id for update action'}
            else:
                result = service.update_ticket(ticket_id, updates)
                
        elif action == 'list':
            filters = event.get('filters')
            result = service.list_tickets(filters)
            
        else:
            result = {
                'success': False,
                'error': f'Invalid action: {action}',
                'valid_actions': ['create', 'status', 'update', 'list']
            }
        
        # Prepare Lambda response
        if result.get('success', False):
            response = {
                'statusCode': 200,
                'body': json.dumps(result),
                'headers': {
                    'Content-Type': 'application/json'
                }
            }
            logger.info(f"Ticket {action} action successful")
        else:
            response = {
                'statusCode': 400,
                'body': json.dumps(result),
                'headers': {
                    'Content-Type': 'application/json'
                }
            }
            logger.warning(f"Ticket {action} action failed")
        
        return response
        
    except Exception as e:
        logger.error("Ticket Creation Lambda handler failed", context=None, error=e)
        
        error_response = {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': f'Internal server error: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
        
        return error_response 