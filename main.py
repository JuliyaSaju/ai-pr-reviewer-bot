import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request

load_dotenv()

app = FastAPI()

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
    return {"status": "received"}