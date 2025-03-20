#!/bin/bash

# Create and activate the conda environment
conda create -n overcooked-env python=3.7 
conda activate overcooked-env

# Install dependencies from requirements.txt
pip install -r requirements.txt

# Update the system and install necessary libraries
sudo apt-get update
sudo apt-get install -y libgl1-mesa-dev

# Install additional Python dependencies
pip install pylsl
pip install eventlet

# Clone the overcooked_ai repository
#git clone --recursive https://github.com/ahmadad0111/overcooked_ai.git --branch master --single-branch

# Navigate to the human_aware_rl directory
#cd overcooked_ai/src/human_aware_rl/
cd src/human_aware_rl/


# Add the DATA_DIR setting to data_dir.py
echo "import os; DATA_DIR=os.path.abspath('.')" >> data_dir.py

cd ..
cd ..

# Install the overcooked_ai[harl] package
# cd ../../setup_folder
pip install -e '.[harl]'

echo "Setup is complete!"
