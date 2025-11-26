#!/bin/bash

# Exit immediately if a command fails
set -e

# Name of your virtual environment
ENV_NAME=".venv"

# Fixed port for FastAPI app
PORT=8000

# Step 1: Create virtual environment if not exists
if [ ! -d "$ENV_NAME" ]; then
  echo "Creating virtual environment..."
  python3 -m venv $ENV_NAME
fi

# Step 2: Activate environment
source $ENV_NAME/bin/activate

# Step 3: Upgrade pip
pip install --upgrade pip

# Step 4: Install dependencies
if [ -f "requirements.txt" ]; then
  echo "Installing dependencies..."
  pip install -r requirements.txt
else
  echo "No requirements.txt found!"
fi

# Step 5: Run FastAPI app on fixed port
echo "Starting FastAPI app on port $PORT..."
uvicorn main:app --reload --host 0.0.0.0 --port $PORT
