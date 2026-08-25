# 📱 Phone Number Lookup Telegram Bot

A powerful Telegram bot that looks up phone numbers with detailed information. Features admin panel, force-join channels, and Uptime Robot integration.

## ✨ Features

- 🔍 **Phone Number Lookup** - Get instant info about any phone number
- 👨‍💼 **Admin Panel** - Manage force-join channels easily
- 📢 **Force Join Channels** - Require users to join channels before using bot
- ⏰ **Uptime Robot Integration** - External monitoring support
- 🎯 **Premium Emojis** - Beautiful UI with premium Telegram emojis
- 🚀 **Render Deployment Ready** - One-click deployment to Render

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Telegram Bot Token
- Render.com account (for deployment)

### Local Development

1. **Clone and setup:**
```bash
git clone <your-repo>
cd telegram-bot
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your values
```

3. **Run locally:**
```bash
python main.py
```

## 📦 Deployment to Render

1. **Push to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Create Render Service:**
   - Go to [render.com](https://render.com)
   - Click "New +"
   - Select "Web Service"
   - Connect your GitHub repo
   - Name: `telegram-bot`
   - Runtime: Python 3
   - Build command: `pip install -r requirements.txt`
   - Start command: `python main.py`

3. **Set Environment Variables:**
   - Go to Environment tab
   - Add all variables from `.env.example`:
     - `BOT_TOKEN`
     - `API_ENDPOINT`
     - `API_KEY`
     - `ADMIN_IDS`
     - `UPTIME_ROBOT_URL` (optional)

4. **Deploy:**
   - Click "Deploy"
   - Wait for deployment to complete

## ⚙️ Configuration

### Environment Variables

```env
BOT_TOKEN=your_bot_token_here
API_ENDPOINT=https://electron-cursed.vercel.app/lookup
API_KEY=@ElectronCursed
ADMIN_IDS=8817422430,1234567890  # comma-separated
UPTIME_ROBOT_URL=https://uptimerobot.com/api/v2/monitorWebhook/[id]
PORT=8000
```

### Admin IDs
- Get your Telegram user ID: Use `@userinfobot`
- Add multiple admins by separating with commas in `ADMIN_IDS`

### Uptime Robot Setup (Optional)

1. Go to [UptimeRobot.com](https://uptimerobot.com)
2. Create a new "Monitor" with type "Webhook"
3. Copy the webhook URL
4. Add to `UPTIME_ROBOT_URL` in environment

## 📖 Usage

### For Users
- `/start` - Start the bot
- `/help` - Show help message
- Send any phone number (10+ digits) for lookup

### For Admins
- `/admin` - Access admin panel
- Add/remove force-join channels
- View active channels

## 🛠️ File Structure

```
telegram-bot/
├── main.py                 # Main bot file
├── config.py              # Configuration
├── admin_panel.py         # Admin functions
├── database.py            # Database operations
├── uptime_robot.py        # Uptime monitoring
├── requirements.txt       # Dependencies
├── Procfile              # Render deployment
├── .env.example          # Environment template
├── .gitignore            # Git ignore file
├── README.md             # This file
└── data/
    └── channels.json     # Stored channels (auto-created)
```

## 📊 Database

The bot uses JSON for storing channels data at `data/channels.json`:

```json
[
  {
    "channel_id": -1001234567890,
    "name": "My Channel",
    "invite_link": "https://t.me/mychannel"
  }
]
```

## 🔒 Force Join Feature

When configured:
1. Users must join all configured channels
2. If not joined, they see a message with join button
3. After joining, they can use the bot normally
4. Check happens automatically on each lookup

## ⚡ Uptime Robot Integration

The bot pings Uptime Robot on startup to signal it's alive. This helps monitor uptime and get alerts if the bot goes down.

### Setting up Uptime Robot:
1. Create webhook monitor on UptimeRobot
2. Copy webhook URL
3. Add to environment variable `UPTIME_ROBOT_URL`
4. Bot will ping on startup and periodically

## 🐛 Troubleshooting

### Bot not responding
- Check `BOT_TOKEN` is correct
- Verify bot is running: `systemctl status` or check Render logs
- Check Render deploy log for errors

### Admin panel not working
- Verify your ID is in `ADMIN_IDS`
- Check Telegram user ID is correct
- Restart the bot

### Force join not working
- Ensure channel ID is correct (negative number like -1001234567890)
- Check bot is member of the channel with right permissions
- Verify invite link is valid

### API lookup failing
- Check internet connection
- Verify API endpoint URL
- Check if API key is correct
- Check phone number format

## 📞 Support

For issues or questions, contact bot admin or check logs on Render dashboard.

## 📄 License

This project is for educational purposes.

---

**Made with ❤️ by ElectronCursed**

6767 - Stay safe, baby.
