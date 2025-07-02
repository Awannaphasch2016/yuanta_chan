"""
Ticket Creation Lambda Function
Handles internal ticket creation and management for investment consultant workflows
Designed for Amazon Bedrock Agent integration

BEDROCK AGENT PARAMETER GUIDE (5 PARAMETERS MAX):
=================================================

CONSOLIDATED PARAMETERS:
-----------------------
1. action (string, required): The operation to perform
   - Valid values: "create", "status", "update", "list"
   - Example: "create" for creating new tickets

2. ticket_data (string, required for create): JSON string containing ticket information
   - Format: JSON object with ticket fields
   - Example: '{"title": "API issue", "description": "Rate limiting problem", "category": "technical", "requester": "john@company.com"}'
   - Required fields for create: title, description, category, requester
   - Optional fields: priority, assigned_to, tags

3. ticket_id (string, required for status/update): Existing ticket identifier
   - Format: "TIK-YYYYMMDD-XXXXXXXX"
   - Example: "TIK-20241201-ABC12345"

4. update_data (string, optional for update): JSON string containing fields to update
   - Format: JSON object with update fields
   - Example: '{"status": "in_progress", "assigned_to": "bob@company.com"}'
   - Valid fields: status, priority, assigned_to, description, tags

5. filters (string, optional for list): JSON string containing filter criteria
   - Format: JSON object with filter fields
   - Example: '{"category": "technical", "status": "open"}'
   - Valid filters: category, status, requester

ACTION-SPECIFIC EXAMPLES:
========================
CREATE TICKET:
- action: "create"
- ticket_data: '{"title": "API rate limiting issue", "description": "Yahoo Finance API returning 429 errors", "category": "technical", "requester": "alice@company.com", "priority": "high", "tags": "api,urgent"}'

CHECK STATUS:
- action: "status"
- ticket_id: "TIK-20241201-ABC12345"

UPDATE TICKET:
- action: "update"
- ticket_id: "TIK-20241201-ABC12345"
- update_data: '{"status": "in_progress", "assigned_to": "bob@company.com"}'

LIST TICKETS:
- action: "list"
- filters: '{"category": "technical", "status": "open"}'
"""

import json
import sys
import os
import uuid
import time
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
    Optimized for Amazon Bedrock Agent integration
    
    Expected event format from Bedrock Agent:
    {
        "messageVersion": "1.0",
        "actionGroup": "TicketManagementActionGroup",
        "function": "manageTickets",
        "parameters": [
            {"name": "action", "value": "create|status|update|list"},
            {"name": "ticket_data", "value": "{\"title\": \"...\", \"description\": \"...\", \"category\": \"...\", \"requester\": \"...\"}"},
            {"name": "ticket_id", "value": "TIK-YYYYMMDD-XXXXXXXX"},
            {"name": "update_data", "value": "{\"status\": \"...\", \"assigned_to\": \"...\"}"},
            {"name": "filters", "value": "{\"category\": \"...\", \"status\": \"...\"}"}
        ]
    }
    
    Parameter Examples for Bedrock Agent:
    - action: "create" (e.g., "create", "status", "update", "list")
    - ticket_data: '{"title": "API issue", "description": "Rate limiting problem", "category": "technical", "requester": "john@company.com"}' (JSON string for create)
    - ticket_id: "TIK-20241201-ABC12345" (e.g., existing ticket identifier)
    - update_data: '{"status": "in_progress", "assigned_to": "bob@company.com"}' (JSON string for updates)
    - filters: '{"category": "technical", "status": "open"}' (JSON string for filtering)
    """
    logger = get_logger("TicketCreationHandler")
    print(f"DEBUG: Full event received by Lambda: {json.dumps(event, indent=2)}")
    
    # Extract required values for Bedrock Agent response structure
    actionGroup = event.get('actionGroup', 'TicketManagementActionGroup')
    function = event.get('function', 'manageTickets')
    messageVersion = event.get('messageVersion', '1.0')
    
    try:
        logger.info("Ticket Creation Lambda function invoked", context={"event": event})
        
        # Extract parameters following Bedrock Agent format (consolidated to 5 parameters)
        action = ''
        ticket_id = ''
        ticket_data = {}
        update_data = {}
        filters = {}
        
        # 1. Extract parameters from 'parameters' list (Bedrock Agent format)
        if 'parameters' in event and isinstance(event['parameters'], list):
            for param in event['parameters']:
                param_name = param.get('name')
                param_value = param.get('value')
                
                if param_name == 'action' and param_value:
                    action = str(param_value).lower()
                elif param_name == 'ticket_id' and param_value:
                    ticket_id = str(param_value)
                elif param_name == 'ticket_data' and param_value:
                    try:
                        ticket_data = json.loads(str(param_value))
                    except json.JSONDecodeError:
                        ticket_data = {}
                elif param_name == 'update_data' and param_value:
                    try:
                        update_data = json.loads(str(param_value))
                    except json.JSONDecodeError:
                        update_data = {}
                elif param_name == 'filters' and param_value:
                    try:
                        filters = json.loads(str(param_value))
                    except json.JSONDecodeError:
                        filters = {}
        
        # 2. Fallback to direct key extraction (for testing or other integrations)
        if not action and event.get('action'):
            action = str(event['action']).lower()
        if not ticket_id and event.get('ticket_id'):
            ticket_id = str(event['ticket_id'])
        if not ticket_data and event.get('ticket_data'):
            if isinstance(event['ticket_data'], str):
                try:
                    ticket_data = json.loads(event['ticket_data'])
                except json.JSONDecodeError:
                    ticket_data = {}
            elif isinstance(event['ticket_data'], dict):
                ticket_data = event['ticket_data']
        if not update_data and event.get('update_data'):
            if isinstance(event['update_data'], str):
                try:
                    update_data = json.loads(event['update_data'])
                except json.JSONDecodeError:
                    update_data = {}
            elif isinstance(event['update_data'], dict):
                update_data = event['update_data']
        if not filters and event.get('filters'):
            if isinstance(event['filters'], str):
                try:
                    filters = json.loads(event['filters'])
                except json.JSONDecodeError:
                    filters = {}
            elif isinstance(event['filters'], dict):
                filters = event['filters']
            
        print(f"DEBUG: Extracted parameters - action: '{action}', ticket_id: '{ticket_id}', ticket_data: {ticket_data}, update_data: {update_data}, filters: {filters}")
        
        request_id = event.get('requestId', f'req-{int(datetime.now().timestamp())}')
        
        # Validate action parameter
        if not action:
            service = TicketCreationService()
            error_details = service._error_response("Missing required parameter: action. Valid actions: create, status, update, list")
            
            responseBody_for_error = {
                "TEXT": {
                    "body": json.dumps(error_details, default=str)
                }
            }
            return {
                'messageVersion': messageVersion,
                'response': {
                    'actionGroup': actionGroup,
                    'function': function,
                    'functionResponse': {
                        'responseBody': responseBody_for_error
                    }
                }
            }
        
        logger.info(f"🎫 Processing ticket {action} request", 
                   context={
                       'requestId': request_id, 
                       'action': action,
                       'ticket_id': ticket_id if ticket_id else 'N/A'
                   })
        
        # Initialize service
        service = TicketCreationService()
        
        # Route to appropriate action handler
        if action == 'create':
            # Use consolidated ticket_data parameter
            if not ticket_data:
                result = service._error_response('Missing ticket_data for create action')
            else:
                result = service.create_ticket(ticket_data)
            
        elif action == 'status':
            if not ticket_id:
                result = service._error_response('Missing ticket_id for status action')
            else:
                result = service.get_ticket_status(ticket_id)
                
        elif action == 'update':
            if not ticket_id:
                result = service._error_response('Missing ticket_id for update action')
            else:
                # Use consolidated update_data parameter
                if not update_data:
                    result = service._error_response('Missing update_data for update action')
                else:
                    result = service.update_ticket(ticket_id, update_data)
                
        elif action == 'list':
            # Use consolidated filters parameter
            result = service.list_tickets(filters if filters else None)
            
        else:
            result = service._error_response(f'Invalid action: {action}. Valid actions: create, status, update, list')
        
        logger.info(f"✅ Ticket {action} action completed", 
                   context={
                       'requestId': request_id, 
                       'action': action,
                       'success': result.get('success', False)
                   })
        
        # *** Format response for Bedrock Agent ***
        responseBody_for_success = {
            "TEXT": {
                "body": json.dumps(result, default=str)
            }
        }
        
        action_response = {
            'actionGroup': actionGroup,
            'function': function,
            'functionResponse': {
                'responseBody': responseBody_for_success
            }
        }

        final_response = {
            'messageVersion': messageVersion,
            'response': action_response
        }
        
        print(f"DEBUG: Final Lambda response: {json.dumps(final_response, indent=2)}")
        return final_response
        
    except Exception as e:
        logger.error(f"❌ Ticket Creation Lambda execution failed", 
                    context={'requestId': event.get('requestId', 'unknown')}, 
                    error=e)
        
        # *** Format error response for Bedrock Agent ***
        service = TicketCreationService()
        error_details = service._error_response(f"Internal server error: {str(e)}")
        
        responseBody_for_error = {
            "TEXT": {
                "body": json.dumps(error_details, default=str)
            }
        }
        
        error_action_response = {
            'actionGroup': actionGroup,
            'function': function,
            'functionResponse': {
                'responseBody': responseBody_for_error
            }
        }
        
        final_error_response = {
            'messageVersion': messageVersion,
            'response': error_action_response
        }
        
        print(f"DEBUG: Final Lambda error response: {json.dumps(final_error_response, indent=2)}")
        return final_error_response 