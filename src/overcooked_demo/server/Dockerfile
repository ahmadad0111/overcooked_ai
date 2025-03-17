# Use Miniconda as the base image
FROM continuumio/miniconda3

# Set build arguments
ARG BUILD_ENV
ARG OVERCOOKED_BRANCH
ARG GRAPHICS

# Set working directory
WORKDIR /app

# Update Conda and install liblsl
RUN conda update -n base -c defaults conda && \
    conda install -c conda-forge liblsl && \
    conda clean --all -y  # Clean up to reduce image size

# Install system dependencies (avoid separate `apt-get update`)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-dev \
    && rm -rf /var/lib/apt/lists/*  # Cleanup

# Copy requirements and install Python dependencies
COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install eventlet only if in production mode
RUN if [ "$BUILD_ENV" = "production" ] ; then pip install --no-cache-dir eventlet ; fi

# Clone the Overcooked AI repository
RUN git clone --recursive https://github.com/ahmadad0111/overcooked_ai.git --branch $OVERCOOKED_BRANCH --single-branch /overcooked_ai

# Prevent missing data directory issue
RUN echo "import os; DATA_DIR=os.path.abspath('.')" >> /overcooked_ai/src/human_aware_rl/data_dir.py

# Install Chai dependencies
RUN pip install --no-cache-dir -e '/overcooked_ai[harl]'

# Copy application files
COPY ./static ./static
COPY ./*.py ./
COPY ./graphics/$GRAPHICS ./static/js/graphics.js
COPY ./config.json ./config.json
COPY ./db.json ./db.json

# Set environment variables
ENV HOST=0.0.0.0
ENV PORT=5000
ENV CONF_PATH=config.json

# Expose the application port
EXPOSE 5000

# Run the application
CMD ["python", "-u", "app.py"]
