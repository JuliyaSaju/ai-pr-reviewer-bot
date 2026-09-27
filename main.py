import os
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request

load_dotenv()

app = FastAPI()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

@app.get("/")
def read_root():
    return {"message": "My PR bot backend is alive!"}

@app.get("/check-keys")
def check_keys():
    gemini_key = os.getenv("GEMINI_API_KEY")
    github_token = os.getenv("GITHUB_TOKEN")
    return {
        "gemini_key_loaded": gemini_key is not None,
        "github_token_loaded": github_token is not None
    }

@app.post("/webhook")
async def github_webhook(request: Request):
    payload = await request.json()
    action = payload.get("action")
    print(f"Webhook received! Action: {action}")

    if action == "opened":
        repo_full_name = payload["repository"]["full_name"]  # e.g. "JuliyaSaju/ai-pr-reviewer-bot"
        pr_number = payload["pull_request"]["number"]

        files_url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}/files"
        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json"
        }
        response = requests.get(files_url, headers=headers)
        changed_files = response.json()

        for file in changed_files:
            print(f"File changed: {file['filename']}")
            print(f"Diff:\n{file.get('patch', 'No patch available')}")

    return {"status": "received"}