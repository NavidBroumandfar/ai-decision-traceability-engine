# LLM Server Setup Guide

## Quick Fix: Start Your LLM Server

Your application is configured to use a local LLM server (Ollama) but the server is not running.

### Option 1: Use Ollama (Recommended for Local Development)

1. **Install Ollama:**
   - Download from: https://ollama.ai
   - Install the Windows version
   - Ollama will be added to your PATH automatically

2. **Start Ollama Server:**
   - Open a new terminal/PowerShell window
   - Run: `ollama serve`
   - Keep this terminal open while using the application

3. **Pull the Required Model:**
   - In another terminal, run: `ollama pull qwen2.5-coder:7b-instruct`
   - Wait for the download to complete

4. **Verify Ollama is Running:**
   - Open a browser and go to: http://localhost:11434
   - You should see Ollama's API documentation

5. **Restart Your Streamlit App:**
   - Stop the current Streamlit app (Ctrl+C)
   - Run: `python -m streamlit run src/ui/app.py`
   - The connection error should be resolved

### Option 2: Use OpenAI API

If you prefer to use OpenAI's cloud API instead:

1. **Get an OpenAI API Key:**
   - Sign up at: https://platform.openai.com
   - Create an API key in your account settings

2. **Update your `.env` file:**
   ```env
   OPENAI_BASE_URL=
   OPENAI_API_KEY=sk-your-api-key-here
   OPENAI_MODEL=gpt-4o-mini
   LOG_LEVEL=INFO
   ```

3. **Restart Your Streamlit App:**
   - Stop the current Streamlit app (Ctrl+C)
   - Run: `python -m streamlit run src/ui/app.py`

### Option 3: Use LM Studio

1. **Install LM Studio:**
   - Download from: https://lmstudio.ai
   - Install and launch the application

2. **Start Local Server:**
   - In LM Studio, go to the "Local Server" tab
   - Click "Start Server"
   - Note the port (usually 1234)

3. **Update your `.env` file:**
   ```env
   OPENAI_BASE_URL=http://localhost:1234/v1
   OPENAI_API_KEY=
   OPENAI_MODEL=your-model-name
   LOG_LEVEL=INFO
   ```

4. **Restart Your Streamlit App**

## Troubleshooting

- **Connection Refused Error:** The LLM server is not running. Start it using one of the options above.
- **Model Not Found:** Make sure you've pulled/downloaded the model specified in your `.env` file.
- **Port Already in Use:** Another application might be using the port. Change the port in your `.env` file or stop the conflicting application.
