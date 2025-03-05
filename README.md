# PlayX

A Python script for downloading images and videos from X (formerly Twitter) profiles using Playwright.

## Features

- Downloads all available images from a user's media feed
- Collects video links and downloads them using yt-dlp
- Uses an existing Chrome session with your cookies (no login required if already logged in)
- Handles pagination by scrolling to load more content
- Saves images in high-quality format

## Benefits of Using an Existing Session

- No need to manually log in each time
- Bypasses login restrictions or CAPTCHA challenges
- Works seamlessly with your active account (Person 1)
- Uses stored cookies to access media without authentication prompts

## Requirements

- Python 3.6+
- Chrome browser
- yt-dlp (for video downloads)

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/jj-stuff/playx.git
   cd playx
   ```

2. Install dependencies using pnpm:

   ```bash
   pnpm install
   ```

3. Install Python dependencies:

   ```bash
   pip install playwright requests
   ```

4. Install Playwright browsers:

   ```bash
   python -m playwright install
   ```

5. Download yt-dlp for your platform from [their GitHub releases](https://github.com/yt-dlp/yt-dlp/releases) and save it as `dlp` in the project directory.

## Usage

1. Start Chrome with remote debugging enabled:

   ```bash
   "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --remote-debugging-port=9222
   ```

2. Run the script:

   ```bash
   python playx.py
   ```

3. Follow the prompts:
   - Enter the username of the target profile
   - Specify the number of scrolls to load more content
   - Provide the path to the yt-dlp executable

## How It Works

1. The script connects to your already running Chrome instance with remote debugging
2. It navigates to the user's media page on X
3. Images are collected and downloaded immediately
4. Video links are saved to a text file
5. yt-dlp is used to download the videos using your browser cookies

## File Structure

- `playx.py`: Main Python script
- `dlp`: yt-dlp executable
- `username_media/`: Folder where downloads are saved
- `username_videos.txt`: List of video URLs for batch downloading

## Limitations

- Requires manual Chrome launch with debugging enabled
- Might be affected by X's rate limiting
- Dependent on X's current DOM structure

## License

MIT

