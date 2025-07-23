FROM python:3.12-slim

# Install system dependencies first (as root)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv as root
RUN pip install --no-cache-dir uv

# Copy requirements and install dependencies AS ROOT
COPY requirements.txt .
RUN uv pip install --system --no-cache-dir -r requirements.txt

# Create a non-root user AFTER installing packages
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Create app directory and set ownership
RUN mkdir -p /app && chown -R appuser:appuser /app

# Set working directory
WORKDIR /app

# Copy application code with proper ownership
COPY --chown=appuser:appuser streamlit_app .

# Switch to non-root user for running the app
USER appuser

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_GATHER_USAGE_STATS=false

# Run the application
CMD ["streamlit", "run", "streamlit_app/root_page.py", \
     "--server.address=0.0.0.0", \
     "--server.port=8501", \
     "--server.headless=true", \
     "--server.enableCORS=false", \
     "--server.enableXsrfProtection=false", \
     "--theme.base=light", \
     "--theme.primaryColor=#FF6B6B", \
     "--theme.backgroundColor=#FFFFFF", \
     "--theme.secondaryBackgroundColor=#F0F2F6", \
     "--theme.textColor=#262730"]

# Add metadata labels
LABEL maintainer="mikhail.solovyanov@gmail.com" \
      version="1.0.0" \
      description="Streamlit webapp for drug search app" \
      org.opencontainers.image.licenses="MIT" \
      Name="hotels-price-absorber-streamlit"
