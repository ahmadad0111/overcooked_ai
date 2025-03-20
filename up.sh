#!/bin/bash
# activate env
conda activate overcooked-env

# Navigate to the overcooked_demo directory
cd src/overcooked_demo

# Copy Python files from the server directory
cp ./server/*.py ./

# Copy configuration files
cp ./server/config.json ./
cp ./server/db.json ./

# Copy static files
cp -r ./server/static ./static

# Copy the graphics.js file
cp ./server/graphics/overcooked_graphics_v2.2.js ./static/js/graphics.js

# Set the environment variables for Flask app
export FLASK_ENV=production  # Or your desired environment
export HOST=0.0.0.0
export PORT=5000
export CONF_PATH=config.json

cd ..

# Run the app
python -u app.py
