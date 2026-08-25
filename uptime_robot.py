import requests
import logging
from config import UPTIME_ROBOT_URL

logger = logging.getLogger(__name__)

def ping_uptime_robot():
    """Ping Uptime Robot to signal bot is alive"""
    if not UPTIME_ROBOT_URL:
        return False
    
    try:
        response = requests.get(UPTIME_ROBOT_URL, timeout=10)
        if response.status_code == 200:
            logger.info("✅ Uptime Robot pinged successfully")
            return True
        else:
            logger.warning(f"⚠️ Uptime Robot ping failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.warning(f"⚠️ Uptime Robot ping error: {e}")
        return False

async def async_ping_uptime_robot():
    """Async version for use in bot handlers"""
    return ping_uptime_robot()
