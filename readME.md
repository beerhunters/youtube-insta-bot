# YouTube & Instagram Video Downloader Bot

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Docker](https://img.shields.io/badge/Docker-supported-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

A Telegram bot that downloads videos from YouTube (360p) and Instagram (reels/videos) and sends them directly to your chat. Built with Python, `aiogram`, `yt-dlp`, and `instaloader`.

## Features
- **YouTube**: Downloads videos in 360p (H.264 + AAC) with a maximum duration of 5 minutes and file size of 50 MB.
- **Instagram**: Downloads public reels and videos, saving them as MP4 files.
- **Telegram Integration**: Sends downloaded videos directly to your Telegram chat.
- **Docker Support**: Easily deployable with a pre-configured Dockerfile.
- **Animation**: Displays a loading animation during processing.

## Prerequisites
- Python 3.11+
- Docker (optional, for containerized deployment)
- Telegram Bot Token (get one from [BotFather](https://t.me/BotFather))

## Installation

### Manual Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/youtube-insta-bot.git
   cd youtube-insta-bot
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
3. Install ffmpeg:
   - On Ubuntu/Debian: sudo apt install ffmpeg
   - On macOS: brew install ffmpeg
   - On Windows: Download from ffmpeg.org and add to PATH

4. Replace the BOT_TOKEN in bot.py with your Telegram Bot Token:
   ```python
   BOT_TOKEN = 'your-bot-token-here'
### Docker Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/youtube-insta-bot.git
   cd youtube-insta-bot
2. Build the Docker image:
   ```bash
   docker build -t youtube-insta-bot .
3. Run the container:
   ```bash
   docker run -d --name bot-container youtube-insta-bot
## Usage
1. Start the bot:
   - Manual: python bot.py
   - Docker: Use the docker run command above
2. Open Telegram, find your bot, and send /start.
3. Send a link to a YouTube video (up to 5 minutes) or a public Instagram reel/video.
4. Wait for the bot to process and send the video back to you.
#### Example Commands
   - YouTube: https://youtu.be/example
   - Instagram: https://www.instagram.com/reel/example/

## Project Structure
   ```text
   youtube-insta-bot/
   ├── bot.py           # Main bot script
   ├── Dockerfile       # Docker configuration
   ├── requirements.txt # Python dependencies
   └── README.md        # This file
   ```
   
### Dependencies
  - aiogram: Telegram Bot API framework
  - yt-dlp: YouTube video downloader
  - instaloader: Instagram video downloader
  - ffmpeg: Required for video processing
  
Listed in requirements.txt with specific versions for compatibility.

### Notes
  - YouTube videos are downloaded in 360p (format 18) to ensure compatibility with mobile devices and Telegram's 50 MB limit. 
  - Instagram downloads work only for public posts. 
  - Temporary files are stored in a downloads/ folder and deleted after sending.

### Contributing
Feel free to submit issues or pull requests! Contributions are welcome.

### License
This project is licensed under the MIT License - see the LICENSE file for details.

### Acknowledgments
  - Built with love and coffee ☕
  - Thanks to the open-source communities behind aiogram, yt-dlp, and instaloader. 

Made by [Beerhunters](https://t.me/beerhunters) | [GitHub Profile](https://github.com/beerhunters/) | 2025