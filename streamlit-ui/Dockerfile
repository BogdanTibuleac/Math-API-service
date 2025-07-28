FROM python:3.11-slim

# Install system-level dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    graphviz \
    libgraphviz-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy source code
COPY . .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

CMD streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.runOnSave=true
