# Envacare Project Frontend - Docker & .env Guide

## How to Run the Project with Docker

1. **Build the Docker image:**
   ```powershell
   docker build -t envacare-frontend .
   ```

2. **Run the Docker container:**
   ```powershell
   docker run -p 8501:8501 envacare-frontend
   ```
   This will start the Streamlit app and make it available at `http://localhost:8501`.

---

## .env File Example & Instructions

Create a `.env` file in the project root to store environment variables. Example:

```env
# Streamlit configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Custom app variables
API_URL=https://your-api-url.com
SECRET_KEY=your_secret_key_here
DEBUG=True
```

**Instructions:**
- Replace `API_URL` with your backend API endpoint.
- Set `SECRET_KEY` to a secure random string.
- Adjust other variables as needed for your environment.
- Streamlit will automatically read variables prefixed with `STREAMLIT_`.

---

For more details, see the official Streamlit and Docker documentation.
