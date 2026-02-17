#!/bin/bash
# Quick setup script for File-to-API Platform

set -e

echo "🚀 File-to-API Platform Setup"
echo "=============================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "❌ Python 3 not found. Please install Python 3.10+"; exit 1; }

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "⚠️  Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Setup .env file
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    
    # Generate SECRET_KEY
    SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
    sed -i "s/your-secret-key-here-change-in-production/$SECRET_KEY/" .env
    
    # Generate API_KEY_SALT
    API_SALT=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    sed -i "s/your-api-key-salt-here/$API_SALT/" .env
    
    echo "✅ .env file created with generated secrets"
else
    echo "⚠️  .env file already exists"
fi

# Run migrations
echo "Running database migrations..."
python manage.py makemigrations
python manage.py migrate
echo "✅ Database initialized"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput
echo "✅ Static files collected"

echo ""
echo "=============================="
echo "✅ Setup complete!"
echo ""
echo "To start the development server:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "Then visit:"
echo "  • API: http://localhost:8000/api/v1/"
echo "  • Docs: http://localhost:8000/api/docs/"
echo "  • Admin: http://localhost:8000/admin/"
echo ""
