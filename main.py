import os
import requests
import time
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import FastAPI, Request

load_dotenv()

app = FastAPI()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-3.8-flash")

@app.get("/")
def read_root():
    return {"message": "My PR bot backend is alive!"}

@app.get("/check-keys")
def check_keys():
    return {
        "gemini_key_loaded": GEMINI_API_KEY is not None,
        "github_token_loaded": GITHUB_TOKEN is not None
    }

def get_ai_review(filename, patch):
    prompt = f"""You are a code reviewer. Review this code diff from a file called {filename}.
Point out any bugs, security issues, or bad practices. Be concise, use bullet points.
If there is nothing wrong, just say "No major issues found."

Diff:
{patch}
"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"(AI review skipped due to an error: {e})"

def post_pr_comment(repo_full_name, pr_number, comment_body):
    url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    data = {"body": comment_body}
    response = requests.post(url, headers=headers, json=data)
    print(f"Comment post status: {response.status_code}")
    return response.status_code

@app.post("/webhook")
async def github_webhook(request: Request):
    payload = await request.json()
    action = payload.get("action")
    print(f"Webhook received! Action: {action}")

    if action == "opened":
        repo_full_name = payload["repository"]["full_name"]
        pr_number = payload["pull_request"]["number"]

        files_url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}/files"
        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json"
        }
        response = requests.get(files_url, headers=headers)
        changed_files = response.json()

        all_reviews = []
        for file in changed_files:
            filename = file["filename"]
            patch = file.get("patch", "")
            if patch:
                print(f"\n--- Reviewing {filename} ---")
                review = get_ai_review(filename, patch)
                print(f"AI Review:\n{review}")
                all_reviews.append(f"### 📄 `{filename}`\n{review}")
                time.sleep(15)

        if all_reviews:
            comment_body = "## 🤖 AI Code Review\n\n" + "\n\n---\n\n".join(all_reviews)
            post_pr_comment(repo_full_name, pr_number, comment_body)
                
    return {"status": "received"}