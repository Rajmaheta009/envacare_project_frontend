# Frontend Setup Guide

This guide will help you set up and run the frontend for the Envacare Project.

## Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- (Optional) Virtual environment tool (venv or conda)

## Setup Steps

1. **Clone the Repository**
   ```sh
   git clone <your-repo-url>
   ```

2. **Navigate to the Frontend Directory**
   ```sh
   cd envacare_project_frontend
   ```

3. **(Optional) Create and Activate a Virtual Environment**
   - Using venv:
     ```sh
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - Using conda:
     ```sh
     conda create -n envacare-frontend python=3.10
     conda activate envacare-frontend
     ```

4. **Install Dependencies**
   ```sh
   pip install -r requirements.txt
   ```

5. **Run the Frontend Application**
   ```sh
   streamlit run main.py
   ```
   The application should now be running in your browser. Follow any additional instructions shown in the terminal.

## Docker (Optional)
If you prefer to use Docker:

1. Make sure Docker is installed and running.
2. In the `envacare_project_frontend` directory, run:
   ```sh
   docker-compose up --build
   ```

## Notes
- For authentication, see `auth_pages/login.py`.
- For UI customization, see `styles/style.css`.
- For PDF generation, see `pdf_converter_files/`.

For further help, refer to the `HELP.md` file or contact the project maintainer.
