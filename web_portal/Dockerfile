FROM python:3.9-slim

WORKDIR /app

# Copy requirements
COPY web_portal/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
# We copy the necessary directories to maintain the structure expected by main.py
# main.py expects:
#   ../../platform_gateway
#   ../../policies
#   ../frontend

COPY web_portal /app/web_portal
COPY platform_gateway /app/platform_gateway
COPY policies /app/policies
COPY terraform /app/terraform

# Set workdir to backend where main.py resides
WORKDIR /app/web_portal/backend

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
