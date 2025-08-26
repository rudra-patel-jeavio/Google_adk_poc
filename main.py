#!/usr/bin/env python3
"""
Main entry point for the Multi-Agent Content Creation POC.
This script provides easy ways to run and interact with the system.
"""

import os
import sys
import subprocess
import argparse
import asyncio
from pathlib import Path
from config.settings import settings

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def run_streamlit():
    """Run the Streamlit web interface."""
    streamlit_app = project_root / "frontend" / "streamlit_app.py"
    
    if not streamlit_app.exists():
        print("❌ Streamlit app not found!")
        return False
    
    print("🚀 Starting Streamlit Multi-Agent Content Creator...")
    print("🌐 The app will open in your default web browser")
    print("📍 URL: http://localhost:8501")
    print("\nPress Ctrl+C to stop the application\n")
    
    try:
        print(f"\n\n\n\n\n\n\n\n\n\n\n\n{sys.executable} -m streamlit run {streamlit_app} --server.port 8501 --server.address localhost\n\n\n\n\n\n\n")
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(streamlit_app),
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
        return True
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")
        return False

async def test_agents():
    """Test the multi-agent system directly."""
    print("🧪 Testing Multi-Agent System...")
    
    try:
        from utils.session_manager import session_manager
        import uuid
        
        # Create a test session
        user_id = "test_user"
        session_id = await session_manager.create_session(user_id)
        
        print(f"✅ Created test session: {session_id}")
        
        # Test with a sample message
        test_message = "Give me some ideas for a blog post about artificial intelligence"
        print(f"🗨️  Sending test message: {test_message}")
        
        response = await session_manager.run_agent(user_id, session_id, test_message)
        print(f"🤖 Agent Response:\n{response}")
        
        # Get workflow status
        status = await session_manager.get_workflow_status(user_id, session_id)
        print(f"📊 Workflow Status: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing agents: {e}")
        return False

def check_environment():
    """Check if the environment is properly configured."""
    print("🔍 Checking environment configuration...")
    
    # Check for .env file
    env_file = project_root / ".env"
    if not env_file.exists():
        print("⚠️  No .env file found. Creating template...")
        create_env_template()
    
    # Check required environment variables
    required_vars = ["GOOGLE_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not settings.google_api_key:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("📝 Please edit the .env file and add your API keys")
        return False
    
    print("✅ Environment configuration looks good!")
    return True

def create_env_template():
    """Create a template .env file."""
    env_template = """# Google ADK Multi-Agent System Environment Variables
# Copy this file to .env and fill in your actual API keys

# Required: Google API Key (for Gemini models)
GOOGLE_API_KEY=your_google_api_key_here

# Optional: Other API Keys (if using different models)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional: Google Cloud Settings
GOOGLE_CLOUD_PROJECT=your_project_id_here
GOOGLE_APPLICATION_CREDENTIALS=path_to_your_service_account_key.json

# Application Settings
DEBUG_MODE=True
STREAMLIT_PORT=8501
MAX_TOKENS=2000
TEMPERATURE=0.7
"""
    
    env_file = project_root / ".env.template"
    with open(env_file, 'w') as f:
        f.write(env_template)
    
    print(f"📝 Created environment template at: {env_file}")
    print("🔧 Please copy this to .env and fill in your API keys")

def show_project_info():
    """Display project information and usage instructions."""
    print("""
🤖 Multi-Agent Content Creation POC
=====================================

This is a proof of concept for using Google ADK (Agent Development Kit) 
to create a multi-agent content creation system.

🏗️  Architecture:
  • Orchestrator Agent: Routes requests to specialized agents
  • Ideate Agent: Generates creative ideas
  • Outline Agent: Creates structured content outlines  
  • Draft Agent: Writes complete content drafts
  • Persona Feedback Agent: Provides expert feedback and chat
  • SEO Agent: Optimizes content for search engines

💾 Features:
  • InMemorySession storage for conversation state
  • Streamlit chat interface
  • Workflow progress tracking
  • Multi-agent coordination

🚀 Usage:
  python main.py --web          # Run Streamlit web interface (recommended)
  python main.py --test         # Test the agent system directly
  python main.py --check-env    # Check environment configuration
  python main.py --info         # Show this information

🔧 Setup:
  1. Install dependencies: pip install -r requirements.txt
  2. Set up your .env file with API keys
  3. Run: python main.py --web

📚 Documentation:
  • Google ADK: https://github.com/google/adk-python
  • Streamlit: https://streamlit.io
  
""")

def main():
    """Main function with command line argument handling."""
    parser = argparse.ArgumentParser(
        description="Multi-Agent Content Creation POC using Google ADK"
    )
    parser.add_argument(
        "--web", action="store_true", 
        help="Run the Streamlit web interface (default)"
    )
    parser.add_argument(
        "--test", action="store_true",
        help="Test the multi-agent system directly"
    )
    parser.add_argument(
        "--check-env", action="store_true",
        help="Check environment configuration"
    )
    parser.add_argument(
        "--info", action="store_true",
        help="Show project information"
    )
    
    args = parser.parse_args()
    
    # If no arguments provided, default to web interface
    if not any([args.web, args.test, args.check_env, args.info]):
        args.web = True
    
    if args.info:
        show_project_info()
        return
    
    if args.check_env:
        check_environment()
        return
    
    if args.test:
        if not check_environment():
            return
        asyncio.run(test_agents())
        return
    
    if args.web:
        if not check_environment():
            print("❌ Environment not properly configured. Please fix the issues above.")
            return
        run_streamlit()

if __name__ == "__main__":
    main() 