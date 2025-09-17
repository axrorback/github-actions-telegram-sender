from fastapi import FastAPI, Request
import httpx
import os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# 🔑 Telegram sozlamalari
TELEGRAM_TOKEN = os.getenv("TOKEN", "YOUR_BOT_TOKEN_HERE")
CHANNEL_ID = os.getenv('ID')

# 👤 GitHub profil
ACTION_BY_NAME = "Ahrorjon Ibrohimjonov"
ACTION_BY_URL = "https://github.com/axrorback"

async def send_telegram(message: str):
    """
    Telegram kanaliga xabar yuboradi
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        await client.post(url, data={
            "chat_id": CHANNEL_ID,
            "text": message,
            "parse_mode": "Markdown"
        })

@app.post("/github-webhook")
async def github_webhook(request: Request):
    payload = await request.json()
    event = request.headers.get("X-GitHub-Event")

    msg = f"📢 *GitHub Event:* `{event}`\n"

    if event == "push":
        repo = payload["repository"]["full_name"]
        commits = payload.get("commits", [])
        commit_msgs = "\n".join([f"- {c['message']} by {c['author']['name']}" for c in commits])
        msg += (
            f"Repo: `{repo}`\n"
            f"Actor: [{ACTION_BY_NAME}]({ACTION_BY_URL})\n"
            f"Commits:\n{commit_msgs}"
        )

    elif event == "pull_request":
        action = payload["action"]
        pr = payload["pull_request"]
        msg += (
            f"PR *{action}*: {pr['title']}\n"
            f"Repo: `{payload['repository']['full_name']}`\n"
            f"By: [{ACTION_BY_NAME}]({ACTION_BY_URL})"
        )

    elif event == "issues":
        action = payload["action"]
        issue = payload["issue"]
        msg += (
            f"Issue *{action}*: {issue['title']}\n"
            f"Repo: `{payload['repository']['full_name']}`\n"
            f"By: [{ACTION_BY_NAME}]({ACTION_BY_URL})"
        )

    elif event == "workflow_run":
        workflow = payload["workflow_run"]
        msg += (
            f"Workflow: `{workflow['name']}`\n"
            f"Status: {workflow['conclusion']}\n"
            f"By: [{ACTION_BY_NAME}]({ACTION_BY_URL})"
        )

    elif event == "release":
        release = payload["release"]
        msg += (
            f"Release *{release['tag_name']}* published\n"
            f"Repo: `{payload['repository']['full_name']}`\n"
            f"By: [{ACTION_BY_NAME}]({ACTION_BY_URL})"
        )

    else:
        msg += "ℹ️ Event details: (not formatted yet)"

    await send_telegram(msg)
    return {"ok": True}
