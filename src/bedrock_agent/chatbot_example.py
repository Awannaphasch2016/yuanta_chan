"""
Interactive CLI Chatbot for AWS Bedrock Agent
Demonstrates real LLM integration with investment analysis tools
"""

import sys
import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Ensure src is in the path for direct script execution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.bedrock_agent.bedrock_adapter import BedrockAgentAdapter

class InteractiveChatbot:
    """Interactive CLI chatbot with real AWS Bedrock LLM integration"""
    
    def __init__(self, region: str = None):
        self.adapter = BedrockAgentAdapter(region=region)
        self.conversation_history: List[str] = []
        self.session_active = True
        
    def start_conversation(self):
        """Start interactive chat loop"""
        self._display_welcome()
        
        while self.session_active:
            try:
                user_input = self._get_user_input()
                
                if self._handle_special_commands(user_input):
                    continue
                
                # Process user query through hybrid adapter
                response = self.adapter.handle_user_query(user_input)
                
                # Display response
                self._display_response(response)
                
                # Store in conversation history
                self._add_to_history(user_input, response)
                
            except KeyboardInterrupt:
                self._handle_exit()
                break
            except Exception as e:
                self._display_error(f"An error occurred: {str(e)}")
    
    def _display_welcome(self):
        """Display welcome message and instructions"""
        print("\n" + "="*60)
        print("🤖 AWS Bedrock Investment Analysis Chatbot")
        print("="*60)
        print("Welcome! I can help you with:")
        print("• Investment analysis (e.g., 'How does Apple make money?')")
        print("• Financial questions and general conversation")
        print("• Stock analysis for any publicly traded company")
        print("\nSpecial commands:")
        print("• 'help' - Show this help message")
        print("• 'history' - Show conversation history")
        print("• 'clear' - Clear conversation history")
        print("• 'status' - Show AWS connection status")
        print("• 'aws-debug' - Show detailed AWS configuration")
        print("• 'exit' or 'quit' - End conversation")
        print("• Ctrl+C - Quick exit")
        print("="*60)
        
        # Display connection status
        self._display_connection_status()
        print()
    
    def _display_connection_status(self):
        """Display current connection status"""
        if self.adapter.bedrock_runtime and self.adapter.credentials_configured:
            print("✅ Connected to AWS Bedrock LLM")
            print(f"   Region: {self.adapter.region}")
        elif self.adapter.credentials_configured:
            print("⚠️  AWS credentials configured but Bedrock connection failed")
            print("   (Investment analysis still available)")
        else:
            print("⚠️  Running in local mode - AWS credentials not configured")
            print("   (Investment analysis still available)")
    
    def _get_user_input(self) -> str:
        """Get user input with prompt"""
        try:
            return input("💬 You: ").strip()
        except EOFError:
            self._handle_exit()
            return ""
    
    def _handle_special_commands(self, user_input: str) -> bool:
        """Handle special commands, return True if command was processed"""
        command = user_input.lower()
        
        if command in ['exit', 'quit', 'bye']:
            self._handle_exit()
            return True
        
        elif command == 'help':
            self._display_help()
            return True
        
        elif command == 'history':
            self._display_history()
            return True
        
        elif command == 'clear':
            self._clear_history()
            return True
        
        elif command == 'status':
            self._display_status()
            return True
        
        elif command == 'aws-debug':
            self._display_aws_debug()
            return True
        
        elif command.strip() == '':
            return True  # Skip empty input
        
        return False
    
    def _display_response(self, response: str):
        """Display chatbot response with formatting"""
        print(f"\n🤖 Assistant: {response}\n")
    
    def _display_error(self, error_message: str):
        """Display error message"""
        print(f"\n❌ Error: {error_message}\n")
    
    def _add_to_history(self, user_input: str, response: str):
        """Add exchange to conversation history"""
        self.conversation_history.append(f"User: {user_input}")
        self.conversation_history.append(f"Assistant: {response[:100]}...")
    
    def _display_help(self):
        """Display help information"""
        print("\n📋 Help - Available Commands:")
        print("• Investment Analysis Examples:")
        print("  - 'How does Apple make money?'")
        print("  - 'Analyze MSFT stock'")
        print("  - 'Financial data for Tesla'")
        print("• General Questions:")
        print("  - 'What is a P/E ratio?'")
        print("  - 'Explain dividend yield'")
        print("• Special Commands:")
        print("  - 'help' - Show this help")
        print("  - 'history' - Show conversation history")
        print("  - 'clear' - Clear history")
        print("  - 'status' - Show connection status")
        print("  - 'aws-debug' - Show detailed AWS configuration")
        print("  - 'exit' - End conversation")
        print()
    
    def _display_history(self):
        """Display conversation history"""
        if not self.conversation_history:
            print("\n📝 No conversation history yet.\n")
            return
        
        print("\n📝 Conversation History:")
        print("-" * 40)
        for i, entry in enumerate(self.conversation_history[-10:], 1):  # Show last 10 entries
            print(f"{i}. {entry}")
        
        if len(self.conversation_history) > 10:
            print(f"... and {len(self.conversation_history) - 10} more entries")
        print()
    
    def _clear_history(self):
        """Clear conversation history"""
        self.conversation_history.clear()
        print("\n🗑️  Conversation history cleared.\n")
    
    def _display_status(self):
        """Display current connection and system status"""
        print("\n📊 System Status:")
        print("-" * 30)
        
        # Bedrock connection status
        if self.adapter.bedrock_runtime and self.adapter.credentials_configured:
            print("✅ AWS Bedrock LLM: Connected")
            print(f"   Model: {self.adapter.model_id}")
            print(f"   Region: {self.adapter.region}")
        elif self.adapter.credentials_configured:
            print("⚠️  AWS Bedrock LLM: Credentials configured but connection failed")
            print(f"   Region: {self.adapter.region}")
        else:
            print("❌ AWS Bedrock LLM: Not configured")
            print("   (Investment analysis still available)")
        
        # Investment analyzer status
        if self.adapter.analyzer:
            print("✅ Investment Analyzer: Available")
        else:
            print("❌ Investment Analyzer: Not available")
        
        # Conversation stats
        print(f"💬 Conversation entries: {len(self.conversation_history)}")
        print()
    
    def _display_aws_debug(self):
        """Display detailed AWS configuration for debugging"""
        print("\n🔧 AWS Debug Information:")
        print("-" * 40)
        
        status = self.adapter.get_aws_status()
        
        print(f"Credentials Configured: {status['credentials_configured']}")
        print(f"Bedrock Client Available: {status['bedrock_client_available']}")
        print(f"Region: {status['region']}")
        print(f"Model ID: {status['model_id']}")
        
        print("\nEnvironment Variables:")
        for key, value in status['environment_variables'].items():
            if value:
                print(f"  {key}: {value}")
            else:
                print(f"  {key}: Not set")
        
        print("\nTroubleshooting:")
        if not status['credentials_configured']:
            print("❌ AWS credentials not found. Please:")
            print("   1. Create a .env file with AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
            print("   2. Or set AWS_PROFILE to use AWS CLI profile")
            print("   3. Or configure AWS CLI with 'aws configure'")
        elif not status['bedrock_client_available']:
            print("❌ Bedrock client failed to initialize. Check:")
            print("   1. AWS credentials have Bedrock permissions")
            print("   2. Bedrock service is available in your region")
            print("   3. Model access is enabled in AWS console")
        else:
            print("✅ AWS configuration looks good!")
        print()
    
    def _handle_exit(self):
        """Handle graceful exit"""
        print("\n👋 Thank you for using the AWS Bedrock Investment Chatbot!")
        print("Have a great day! 📈")
        self.session_active = False
    
    def demo_queries(self):
        """Run demonstration queries for testing"""
        demo_queries = [
            "How does Apple make money?",
            "What is a good P/E ratio?",
            "Analyze MSFT stock",
            "Hello, how are you today?"
        ]
        
        print("\n🎯 Running Demo Queries:")
        print("=" * 50)
        
        # Show AWS status first
        print("\n🔧 AWS Configuration Status:")
        status = self.adapter.get_aws_status()
        print(f"Credentials: {'✅' if status['credentials_configured'] else '❌'}")
        print(f"Bedrock Client: {'✅' if status['bedrock_client_available'] else '❌'}")
        print(f"Region: {status['region']}")
        print("-" * 50)
        
        for query in demo_queries:
            print(f"\n💬 Demo Query: {query}")
            response = self.adapter.handle_user_query(query)
            print(f"🤖 Response: {response[:200]}...")
            print("-" * 50)

def main():
    """Main function to run the interactive chatbot"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AWS Bedrock Investment Analysis Chatbot")
    parser.add_argument("--region", help="AWS region for Bedrock service")
    parser.add_argument("--demo", action="store_true", help="Run demo queries instead of interactive mode")
    
    args = parser.parse_args()
    
    try:
        chatbot = InteractiveChatbot(region=args.region)
        
        if args.demo:
            chatbot.demo_queries()
        else:
            chatbot.start_conversation()
            
    except Exception as e:
        print(f"❌ Failed to start chatbot: {str(e)}")
        print("Please check your AWS credentials and Bedrock access.")
        print("Use 'aws-debug' command for detailed troubleshooting.")
        sys.exit(1)

if __name__ == "__main__":
    main() 