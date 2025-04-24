import os
import requests
from dotenv import load_dotenv

load_dotenv()

IMGUR_UPLOAD_URL = "https://api.imgur.com/3/image"
IMGUR_REFRESH_URL = "https://api.imgur.com/oauth2/token"

CLIENT_ID = os.getenv("IMGUR_CLIENT_ID")
CLIENT_SECRET = os.getenv("IMGUR_CLIENT_SECRET")
ACCESS_TOKEN = os.getenv("IMGUR_ACCESS_TOKEN")
REFRESH_TOKEN = os.getenv("IMGUR_REFRESH_TOKEN")


def refresh_access_token():
    global ACCESS_TOKEN
    data = {
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
    }
    try:
        response = requests.post(IMGUR_REFRESH_URL, data=data)
        response.raise_for_status()
        new_data = response.json()
        ACCESS_TOKEN = new_data["access_token"]
        # optionally: save to .env or env file
        return ACCESS_TOKEN
    except Exception as e:
        print("❌ Failed to update token Imgur:", e)
        return None


def upload_to_imgur(image_path):
    global ACCESS_TOKEN
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    with open(image_path, "rb") as f:
        files = {"image": f}
        data = {"type": "file"}
        try:
            response = requests.post(IMGUR_UPLOAD_URL, headers=headers, files=files, data=data)
            response.raise_for_status()
            return response.json()["data"]["link"]
        except requests.HTTPError as e:
            if e.response.status_code == 403:
                print("🔄 Trying to update token Imgur...")
                if refresh_access_token():
                    return upload_to_imgur(image_path)  # retry
            print("❌ Error uploading to Imgur:", e)
            raise
