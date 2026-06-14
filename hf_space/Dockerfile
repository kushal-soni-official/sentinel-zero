FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (cache layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source files
COPY app.py .
COPY core/ core/
COPY sift_mcp_server/ sift_mcp_server/
COPY demo_data/ demo_data/

# Create logs directory
RUN mkdir -p logs

# HF Spaces requires port 7860
ENV PORT=7860

EXPOSE 7860

# Run FastAPI via uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860", "--timeout-keep-alive", "120"]
