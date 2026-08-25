import json
import os
from config import DATABASE_FILE

def ensure_db_exists():
    """Ensure database directory and file exist"""
    os.makedirs(os.path.dirname(DATABASE_FILE), exist_ok=True)
    if not os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'w') as f:
            json.dump([], f)

def load_channels():
    """Load all channels from database"""
    ensure_db_exists()
    try:
        with open(DATABASE_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_channels(channels):
    """Save channels to database"""
    ensure_db_exists()
    with open(DATABASE_FILE, 'w') as f:
        json.dump(channels, f, indent=2)

async def add_channel_db(channel_data):
    """Add a new channel to database"""
    channels = load_channels()
    
    # Check if channel already exists
    if any(c["channel_id"] == channel_data["channel_id"] for c in channels):
        return False
    
    channels.append(channel_data)
    save_channels(channels)
    return True

async def remove_channel_db(channel_id):
    """Remove a channel from database"""
    channels = load_channels()
    channels = [c for c in channels if c["channel_id"] != channel_id]
    save_channels(channels)
    return True

def get_channel(channel_id):
    """Get a specific channel"""
    channels = load_channels()
    return next((c for c in channels if c["channel_id"] == channel_id), None)
