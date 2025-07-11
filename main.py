from fastapi import FastAPI, Form
from fastapi.responses import PlainTextResponse

import subprocess
import re
import requests

app = FastAPI()

TINYURL_API = "http://tinyurl.com/api-create.php?url="

def get_video_download_url(video_url: str) -> str:
    try:
        result = subprocess.run(
            ["yt-dlp", "-g", "-f", "best", video_url],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip().split("\n")[0]
    except subprocess.CalledProcessError:
        return None

def shorten_url(url: str) -> str:
    try:
        resp = requests.get(TINYURL_API + url)
        return resp.text.strip()
    except:
        return url

@app.post("/webhook")
async def whatsapp_webhook(Body: str = Form(...), From: str = Form(...)):
    yt_match = re.search(r"(https?://\S*youtube\.com\S+|https?://youtu\.be/\S+)", Body)
    if not yt_match:
        return PlainTextResponse(
            content="<Response><Message>❌ Please send a valid YouTube link.</Message></Response>",
            media_type="application/xml"
        )

    video_url = yt_match.group(1)
    download_url = get_video_download_url(video_url)

    if not download_url:
        return PlainTextResponse(
            content="<Response><Message>⚠️ Could not fetch download link. Try again later.</Message></Response>",
            media_type="application/xml"
        )

    short_link = shorten_url(download_url)
    return PlainTextResponse(
        content=f"<Response><Message>✅ Download ready: {short_link}</Message></Response>",
        media_type="application/xml"
    )
