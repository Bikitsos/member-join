# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install uv for package management
RUN pip install uv

# Copy project files
COPY pyproject.toml ./
COPY main.py ./
COPY view_members.py ./

# Install dependencies using uv
RUN uv pip install --system -r pyproject.toml

# Create directory for database
RUN mkdir -p /app/data

# Expose port 8085
EXPOSE 8085

# Set environment variables
ENV PYTHONPATH=/app
ENV DATABASE_PATH=/app/data/members.db
ENV HOST=0.0.0.0
ENV SHOW_BROWSER=false

# Run the application
CMD ["python", "main.py"]