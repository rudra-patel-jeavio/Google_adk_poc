#!/bin/bash

# 🤖 Multi-Agent Content Creation POC - Setup Script
# This script automates the setup process for the Google ADK project

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if Python 3.8+ is installed
check_python() {
    if command -v python3 &> /dev/null; then
        python_version=$(python3 --version 2>&1 | awk '{print $2}')
        major=$(echo $python_version | cut -d. -f1)
        minor=$(echo $python_version | cut -d. -f2)
        
        if [[ $major -ge 3 && $minor -ge 8 ]]; then
            print_status "Python $python_version found ✅"
            return 0
        else
            print_error "Python 3.8+ required, found $python_version"
            return 1
        fi
    else
        print_error "Python 3 not found. Please install Python 3.8 or higher."
        return 1
    fi
}

# Create and activate virtual environment
setup_venv() {
    print_step "Setting up virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_status "Virtual environment created"
    else
        print_status "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    print_status "Virtual environment activated"
    
    # Upgrade pip
    pip install --upgrade pip
}

# Install Python dependencies
install_dependencies() {
    print_step "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_status "Dependencies installed successfully ✅"
    else
        print_error "requirements.txt not found!"
        return 1
    fi
}

# Set up environment variables
setup_env() {
    print_step "Setting up environment variables..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.template" ]; then
            cp .env.template .env
            print_status "Created .env file from template"
        else
            # Create basic .env file
            cat > .env << EOF
# Google ADK Multi-Agent System Environment Variables
GOOGLE_API_KEY=your_google_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
DEBUG_MODE=True
STREAMLIT_PORT=8501
MAX_TOKENS=2000
TEMPERATURE=0.7
EOF
            print_status "Created basic .env file"
        fi
        
        print_warning "⚠️  Please edit .env file and add your API keys!"
        print_warning "   You need at least a GOOGLE_API_KEY to run the system"
        print_warning "   Get one at: https://aistudio.google.com/"
    else
        print_status ".env file already exists"
    fi
}

# Test the installation
test_installation() {
    print_step "Testing installation..."
    
    if python main.py --check-env; then
        print_status "Installation test passed ✅"
        return 0
    else
        print_warning "Installation test had issues. Check your .env configuration."
        return 1
    fi
}

# Main installation flow
main() {
    echo "🤖 Multi-Agent Content Creation POC - Setup"
    echo "========================================="
    echo
    
    # Check Python version
    if ! check_python; then
        exit 1
    fi
    
    # Setup virtual environment
    setup_venv
    
    # Install dependencies
    install_dependencies
    
    # Setup environment variables
    # setup_env
    
    # Test installation
    test_installation
    
    echo
    print_status "🎉 Setup complete!"
    echo
    echo "Next steps:"
    echo "1. Edit the .env file and add your Google API key"
    echo "2. Run: python main.py --web"
    echo "3. Open your browser to http://localhost:8501"
    echo
    echo "For help, run: python main.py --info"
}

# Run if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 