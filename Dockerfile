# Python Dockerfile for envacare_project_frontend (Streamlit)

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . .

# Expose the Streamlit default port (8501)
EXPOSE 8501

# Run the Streamlit app (replace main.py with your actual Streamlit script if different)
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
