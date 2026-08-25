import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "8687426758:AAE6zG4ooxuvEHZQ8gHhiXZrEGu3D9p3MqY")
API_ENDPOINT = os.getenv("API_ENDPOINT", "https://electron-cursed.vercel.app/lookup")
API_KEY = os.getenv("API_KEY", "@ElectronCursed")

# Admin Configuration
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "8817422430").split(",")))

# Uptime Robot
UPTIME_ROBOT_URL = os.getenv("UPTIME_ROBOT_URL", "")

# Database
DATABASE_FILE = "data/channels.json"

# Render.com deployment
PORT = int(os.getenv("PORT", 8000))
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
