# 🚀 AI Shopping Agent Deployment Guide

This guide provides instructions for deploying the AI Shopping Agent to production environments.

## 1. Local Production Run (Docker)
If you have Docker installed, you can run the production-ready container locally:

```bash
# Build the image
docker build -t ai-shopping-agent .

# Run the container (pass your OpenAI key)
docker run -p 8501:8501 -e OPENAI_API_KEY="your_key_here" ai-shopping-agent
```

## 2. Streamlit Community Cloud (Quickest)
The fastest way to go live is using [Streamlit Cloud](https://share.streamlit.io/):
1. Push your code to a GitHub repository.
2. Connect your GitHub account to Streamlit Cloud.
3. Select this repository and `app.py` as the entry point.
4. **Important**: Add your `OPENAI_API_KEY` in the **Advanced Settings -> Secrets** section:
   ```toml
   OPENAI_API_KEY = "sk-..."
   ```

## 3. Cloud Deployment (AWS/GCP/Heroku)
For professional hosting, use the provided `Dockerfile`:
- **AWS App Runner** or **ECS**: Direct Docker support.
- **Google Cloud Run**: Ideal for serverless scaling.
- **Heroku**: Use the `heroku/python` buildpack or Docker.

### 🔐 Security & Secrets
- Never commit your `.env` file to version control.
- Use environment variables or Secret Management systems (like AWS Secrets Manager or Streamlit Secrets) to handle your OpenAI API key.

### 💾 Data Persistence
- In production containers, the local `data/` directory will reset on every deploy.
- For true production persistence, consider mounting a volume to the `/app/data` directory or migrating to a cloud database (MongoDB/Supabase).
