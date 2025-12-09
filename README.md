# AI Bug Tracker & Smart Debugger

An intelligent web application that analyzes error logs using AI to identify root causes, suggest fixes, and estimate severity.

## Demo Screenshots

![output](.\output.png)

## Features

- **Smart Analysis**: Uses LLMs (Groq/Llama3 or HuggingFace) to explain bugs.
- **Privacy First**: Automatically redacts sensitive data (IPs, Emails, Keys) before sending to AI.
- **Efficiency**: Hashes logs to detect duplicates and reuse cached analysis.
- **History**: Keeps track of uploaded logs and their analysis.

## Setup

1. **Clone/Download** the repository.
2. **Install Dependencies**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Configure API Keys**:
   - Rename `.env.example` to `.env`.
   - Add your `GROQ_API_KEY` or `HUGGINGFACEHUB_API_TOKEN`.
4. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

## Usage

1. Open the app in your browser (usually `http://localhost:8501`).
2. Drag and drop a `.log` or `.txt` file (use `sample_error.log` to test).
3. Click **Analyze Log**.
4. View the AI-generated Root Cause, Fix, and Severity.

## Tech Stack

- **Frontend**: Streamlit
- **AI**: LangChain, Groq/HuggingFace
- **Database**: SQLite
- **Backend**: Python
