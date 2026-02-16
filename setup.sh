#!/bin/bash

# Self-Healing Code Auditor - Setup Script

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     Self-Healing Code Auditor - Setup Wizard             ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"

# Setup environment file
if [ ! -f ".env" ]; then
    echo "⚙️  Setting up environment variables..."
    cp .env.example .env
    echo "✓ .env file created from template"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your NVIDIA_API_KEY"
    echo "   Get your API key from: https://build.nvidia.com/"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                    Setup Complete!                        ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your NVIDIA_API_KEY"
echo "2. Run: python main.py"
echo "3. Open: http://localhost:8000"
echo ""
echo "For help, see README.md"
