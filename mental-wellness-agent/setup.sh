#!/bin/bash

# Setup script for Mental Wellness Q&A Agent

echo "=========================================="
echo "Mental Wellness Q&A Agent - Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your OPENAI_API_KEY"
    echo "   You can edit it with: nano .env"
else
    echo ""
    echo "✓ .env file already exists"
fi

echo ""
echo "=========================================="
echo "✓ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Set your OpenAI API key:"
echo "   export OPENAI_API_KEY='your-key-here'"
echo "   Or edit the .env file"
echo ""
echo "3. Run the agent:"
echo "   python agent.py              # Command line demo"
echo "   streamlit run streamlit_app.py   # Interactive UI"
echo "   python evaluation.py         # Run evaluation"
echo ""
