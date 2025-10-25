from fastapi import FastAPI, Request
import httpx
import os
load_dotenv()
app = FastAPI()

TELEGRAM_BOT_TOKEN = os.getenv('TOKEN')
TELEGRAM_CHAT_ID = ""  

async def send_to_telegram(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        await client.post(url, data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        })

@app.post("/github-webhook")
async def github_webhook(request: Request):
    payload = await request.json()
    event = request.headers.get("X-GitHub-Event", "ping")

    repo = payload.get("repository", {}).get("full_name", "❓ Unknown repo")

    if event == "ping":
        await send_to_telegram(f"🔔 <b>Webhook ulandi!</b>\n📦 Repo: <b>{repo}</b>")
        return {"msg": "pong"}

    # 🔹 Push event
    elif event == "push":
        pusher = payload.get("pusher", {}).get("name", "Unknown")
        ref = payload.get("ref", "refs/heads/main").split("/")[-1]
        commits = payload.get("commits", [])
        commit_messages = "\n".join(
            [f"   • <code>{c['id'][:7]}</code> — {c['message']} (<i>{c['author']['name']}</i>)"
             for c in commits]
        )
        url = f"https://github.com/{repo}/commits/{ref}"
        text = (f"📌 <b>Push event</b>\n"
                f"📦 Repo: <a href='https://github.com/{repo}'>{repo}</a>\n"
                f"🌿 Branch: <code>{ref}</code>\n"
                f"👤 By: <a href='https://github.com/{pusher}'>{pusher}</a>\n"
                f"📝 Total commits: {len(commits)}\n\n"
                f"{commit_messages}\n\n"
                f"🔗 <a href='{url}'>View commits</a>")
        await send_to_telegram(text)

    # 🔹 Issues
    elif event == "issues":
        action = payload.get("action")
        issue = payload.get("issue", {})
        user = issue.get("user", {}).get("login", "unknown")
        url = issue.get("html_url")
        text = (f"🐞 <b>Issue {action}</b>\n"
                f"📦 Repo: <b>{repo}</b>\n"
                f"📌 Title: <i>{issue.get('title')}</i>\n"
                f"👤 By: <a href='https://github.com/{user}'>{user}</a>\n"
                f"🔗 <a href='{url}'>View issue</a>")
        await send_to_telegram(text)

    # 🔹 Pull Request
    elif event == "pull_request":
        action = payload.get("action")
        pr = payload.get("pull_request", {})
        user = pr.get("user", {}).get("login", "unknown")
        url = pr.get("html_url")
        text = (f"🔀 <b>Pull Request {action}</b>\n"
                f"📦 Repo: <b>{repo}</b>\n"
                f"📌 Title: <i>{pr.get('title')}</i>\n"
                f"👤 By: <a href='https://github.com/{user}'>{user}</a>\n"
                f"💬 Comments: {pr.get('comments')}\n"
                f"🔗 <a href='{url}'>View PR</a>")
        await send_to_telegram(text)

    # 🔹 Workflow (GitHub Actions)
    elif event == "workflow_run":
        workflow = payload.get("workflow", {}).get("name", "Workflow")
        run = payload.get("workflow_run", {})
        status = run.get("conclusion", "in_progress")
        url = run.get("html_url")
        text = (f"⚙️ <b>GitHub Actions</b>\n"
                f"📦 Repo: <b>{repo}</b>\n"
                f"📌 Workflow: <i>{workflow}</i>\n"
                f"📊 Status: <b>{status}</b>\n"
                f"🔗 <a href='{url}'>View run</a>")
        await send_to_telegram(text)

    # 🔹 Star
    elif event == "star":
        action = payload.get("action")
        sender = payload.get("sender", {}).get("login", "unknown")
        text = (f"⭐ <b>Repository {action} starred</b>\n"
                f"📦 Repo: <b>{repo}</b>\n"
                f"👤 By: <a href='https://github.com/{sender}'>{sender}</a>")
        await send_to_telegram(text)

    # 🔹 Fork
    elif event == "fork":
        forkee = payload.get("forkee", {})
        user = payload.get("sender", {}).get("login", "unknown")
        url = forkee.get("html_url")
        text = (f"🍴 <b>Repository forked</b>\n"
                f"📦 Repo: <b>{repo}</b>\n"
                f"👤 By: <a href='https://github.com/{user}'>{user}</a>\n"
                f"🔗 <a href='{url}'>View fork</a>")
        await send_to_telegram(text)

    elif event == "release":
        action = payload.get("action")
        rel = payload.get("release", {})
        user = rel.get("author", {}).get("login", "unknown")
        url = rel.get("html_url")
        text = (f"📦 <b>Release {action}</b>\n"
                f"Repo: <b>{repo}</b>\n"
                f"🏷️ Version: {rel.get('tag_name')}\n"
                f"👤 By: <a href='https://github.com/{user}'>{user}</a>\n"
                f"🔗 <a href='{url}'>View release</a>")
        await send_to_telegram(text)

    elif event == "repository":
        action = payload.get("action")
        repo_info = payload.get("repository", {})
        user = payload.get("sender", {}).get("login", "unknown")
        url = repo_info.get("html_url")
        text = (f"📂 <b>Repository {action}</b>\n"
                f"📦 Name: <b>{repo}</b>\n"
                f"👤 By: <a href='https://github.com/{user}'>{user}</a>\n"
                f"🔗 <a href='{url}'>View repo</a>")
        await send_to_telegram(text)

    else:
        sender = payload.get("sender", {}).get("login", "unknown")
        text = (f"ℹ️ <b>Event:</b> {event}\n"
                f"📦 Repo: <b>{repo}</b>\n"
                f"👤 By: <a href='https://github.com/{sender}'>{sender}</a>")
        await send_to_telegram(text)

    return {"msg": "ok"}
