# Use official Python image as base
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        ffmpeg \
        libgl1 \
        libglib2.0-0 \
        && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --upgrade pip && \
    pip install poetry

# Copy project files
COPY . /app/

# Install Python dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

# Create .streamlit directory at root and set permissions
RUN mkdir -p /.streamlit && chmod -R 777 /.streamlit
# Set write permission for existing data and docs folders in doc_agent and root docs folder
RUN chmod -R 777 /app/docs

ENV XDG_CONFIG_HOME=/.streamlit

# Expose Streamlit port
EXPOSE 8501

# Set environment variables for Streamlit (optional, for production)
ENV STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ENABLECORS=false



# Use Poetry to run Streamlit so the correct environment is used
CMD ["poetry", "run", "streamlit", "run", "agent/ui/ui.py"]

#docker build --platform=linux/amd64 -t gcr.io/gen-lang-client-0735085293/team11:team11-v4 .
