---
title: AI Code Review Assistant
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

<div align="center">
  <img src="assets/project_banner.png" alt="AI Code Reviewer Banner" width="100%">
</div>

# AI-Powered Code Review Assistant


An AI agent that integrates with GitHub, reviews pull requests in real-time, detects potential bugs, security vulnerabilities, code smells, and performance bottlenecks, and then generates actionable inline review comments automatically.

## 🎥 Live Demo / Screenshots
> **Judges / Reviewers:** Watch the AI in action below!
> 
> 📹 **[Watch the full Video Demo Here](#)** *(Note: Upload your `ai_code_reviewer_demo.mp4` to YouTube or Google Drive and paste the link here!)*

### Automated PR Summaries & Code Reviews
![PR Summary Demo](assets/demo_1.png)

### Catching Security Vulnerabilities
![Security Demo](assets/demo_2.png)

### Generating Inline Fixes
![Auto-Fix Demo](assets/demo_3.png)


## 🚀 Features

- **Real-time Automated Reviews:** Listens to GitHub webhooks (`pull_request` events) to review code as soon as a PR is opened or updated.
- **Deep Code Analysis:** Uses AI to analyze git diffs for bugs, logic errors, security vulnerabilities, code smells, and performance bottlenecks.
- **One-Click "Suggested Changes" (Auto-Fixes):** Provides direct code fixes using GitHub's `suggestion` syntax, allowing developers to accept fixes with a single click.
- **Automated PR Summaries & Release Notes:** Generates a high-level summary of what changed, why it matters, and potential impact.
- **Custom Rules & Configurations (`.code-reviewer.yml`):** Enforce custom coding standards, style guides, or ignoring specific files using a repo-level config file.
- **Context-Aware Reviewing (RAG):** Fetches the full file content (not just the diff) for deeper, architectural understanding before reviewing.
- **Automated Test Generation:** Suggests unit tests for newly added or modified code.
- **Interactive Chat / Q&A:** Tag the bot or reply to its comments on the PR to ask follow-up questions, request clarifications, or discuss design decisions.
- **Multi-LLM Support:** Built with `litellm` to easily switch between Google Gemini, OpenAI (GPT-4o), and Anthropic (Claude).
- **FastAPI Backend:** Built on Python and FastAPI for blazing fast, asynchronous webhook processing.

## 🛠️ Technology Stack

- **Backend:** Python 3.11, FastAPI, Uvicorn
- **AI Integration:** LiteLLM (Supports Gemini 1.5 Pro, GPT-4o, Claude 3.5 Sonnet)
- **GitHub Integration:** PyGithub (GitHub App/PAT Support)
- **Deployment:** Docker

---

## ⚙️ Setup and Installation

### 1. Clone the repository
```bash
git clone https://github.com/sasikumar161106/AI_Powered_Code_Review_Assistant.git
cd AI_Powered_Code_Review_Assistant
```

### 2. Configure Environment Variables
Copy the `.env.example` file to `.env`:
```bash
cp .env.example .env
```
Fill in the necessary keys in `.env`:
- `GEMINI_API_KEY`: Get this from [Google AI Studio](https://aistudio.google.com/).
- `GITHUB_APP_ID`: The ID of your GitHub App.
- `GITHUB_PRIVATE_KEY_PATH`: Path to your downloaded GitHub App private key (`.pem` file).
- `GITHUB_WEBHOOK_SECRET`: Optional secret to verify GitHub payloads.

### 3. Run Locally (Using Python)
Make sure you have Python 3.11+ installed.
```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
python main.py
```

### 4. Run Locally (Using Docker)
If you prefer Docker, you can build and run the application container:
```bash
docker build -t ai-code-reviewer .
docker run -p 8000:8000 --env-file .env ai-code-reviewer
```

### 5. Deploy to a Free Cloud (Hugging Face Spaces) - No Credit Card Required!
Running locally requires keeping your PC awake. Deploying to Hugging Face Spaces is 100% free and doesn't require a credit card.

1. Create a free account at [HuggingFace.co](https://huggingface.co/).
2. Go to your profile and click **New Space**.
3. Give your Space a name (e.g., `ai-code-reviewer`).
4. **Important**: For the Space SDK, choose **Docker**, then select **Blank**.
5. Set Space Hardware to the free "CPU basic". Click **Create Space**.
6. Follow their instructions to push your repository to the Space, or simply upload your files via the UI.
7. Go to your Space's **Settings -> Variables and secrets**.
8. Under **Secrets**, add your API keys:
   - `GEMINI_API_KEY`
   - `GITHUB_APP_ID`
   - `GITHUB_PRIVATE_KEY` (copy the full content of the `.pem` file)
   - `GITHUB_WEBHOOK_SECRET`
9. Once the Space builds and says "Running", click the **"Embed this Space"** (three dots menu at the top right) to find the Direct URL (it looks like `https://username-ai-code-reviewer.hf.space`).
10. Update your GitHub App Settings so the Webhook URL points to: `https://username-ai-code-reviewer.hf.space/api/v1/webhook`.

You're done! The agent will now run 24/7 for free.

---

## 🔗 Connecting to GitHub (Local Testing Only)

Since your local server runs on `localhost:8000`, GitHub cannot send webhooks directly to it. You need to expose it using a tunneling tool like **ngrok**.

1. Download and install [ngrok](https://ngrok.com/).
2. Run ngrok to tunnel port 8000:
   ```bash
   ngrok http 8000
   ```
3. Copy the public URL provided by ngrok (e.g., `https://1a2b3c.ngrok.app`).
4. In your GitHub App Settings, set the **Webhook URL** to:
   ```
   https://1a2b3c.ngrok.app/api/v1/webhook
   ```

## 📝 How it Works
1. A developer opens or updates a Pull Request.
2. GitHub sends a webhook payload to the `/api/v1/webhook` endpoint.
3. The app fetches the changed files and parses the git diffs.
4. The diffs are sent to Google Gemini for analysis based on strict review prompts.
5. The AI returns structured JSON containing review comments mapped to exact line numbers.
6. The app uses the GitHub API to post the inline comments on the PR!
