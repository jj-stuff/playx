from playwright.sync_api import sync_playwright
import os
import requests
import time
import re
import subprocess
from urllib.parse import urljoin


# Function to download image files
def download_file(url, folder_path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Extract the image ID from the URL
        img_id = url.split("/")[-1].split("?")[0]
        file_name = os.path.join(folder_path, f"{img_id}.jpg")

        with open(file_name, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        print(f"Downloaded: {file_name}")
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False


# Function to scroll the page to load more posts
def scroll_page(page, times=3):
    for i in range(times):
        # Use scrollBy for smaller, more controlled scrolls
        page.evaluate("window.scrollBy(0, 800)")
        time.sleep(2)
        print(f"Scroll {i+1}/{times} completed")


# Function to get high-quality image URL
def get_high_quality_image_url(url):
    # Replace any size parameters with 'large'
    if "format=" in url:
        base_url = url.split("?")[0]
        return f"{base_url}?format=jpg&name=large"
    else:
        return f"{url}?format=jpg&name=large"


# Main function to collect media links
def collect_media_links(username, max_scrolls=10, path_to_dlp="./dlp"):
    # Define the folder to store downloaded media
    folder_path = f"./{username}_media"
    os.makedirs(folder_path, exist_ok=True)

    # Track links
    image_urls = set()
    video_tweet_urls = set()
    downloaded_images = set()

    with sync_playwright() as p:
        try:
            # Connect to the existing Chrome instance
            print("Connecting to Chrome with remote debugging...")
            browser = p.chromium.connect_over_cdp("http://localhost:9222")

            # Create a new page in the browser context
            context = browser.contexts[0]
            page = context.new_page()

            # Navigate to the target profile's media page
            media_url = f"https://x.com/{username}/media"
            print(f"Navigating to {media_url}")
            page.goto(media_url)
            print("Waiting for page to load...")
            time.sleep(5)  # Wait for page to load

            scroll_count = 0

            while scroll_count < max_scrolls:
                print(f"Processing scroll {scroll_count+1}/{max_scrolls}")

                # Ensure we're on the media page before searching for content
                if "/media" not in page.url:
                    print(f"Not on media page. Current URL: {page.url}")
                    page.goto(media_url)
                    time.sleep(3)

                # Look for images
                print("Looking for images...")
                image_elements = page.query_selector_all(
                    'img[src*="pbs.twimg.com/media/"]'
                )
                print(f"Found {len(image_elements)} potential images")

                for img in image_elements:
                    src = img.get_attribute("src")
                    if (
                        src
                        and "pbs.twimg.com/media/" in src
                        and src not in image_urls
                        and "video_thumb" not in src  # Skip video thumbnails
                    ):
                        high_quality_url = get_high_quality_image_url(src)
                        image_urls.add(high_quality_url)
                        print(f"Found image: {high_quality_url}")

                        # Download the image immediately
                        if high_quality_url not in downloaded_images:
                            if download_file(high_quality_url, folder_path):
                                downloaded_images.add(high_quality_url)

                # Look for video links
                print("Looking for video links...")
                video_links = page.query_selector_all('a[href*="/video/"]')
                print(f"Found {len(video_links)} potential video links")

                for link in video_links:
                    href = link.get_attribute("href")
                    if href and "/video/" in href and href not in video_tweet_urls:
                        full_tweet_url = urljoin("https://x.com", href)
                        video_tweet_urls.add(full_tweet_url)
                        print(f"Found video tweet: {full_tweet_url}")

                # Scroll to load more content
                scroll_page(page)
                scroll_count += 1
                print(
                    f"Collected {len(image_urls)} images and {len(video_tweet_urls)} video links so far"
                )
                print(f"Downloaded {len(downloaded_images)} images")

            # After collecting all video links, save them to a batch file for yt-dlp
            if video_tweet_urls:
                batch_file = f"{username}_videos.txt"
                with open(batch_file, "w") as f:
                    for url in video_tweet_urls:
                        f.write(f"{url}\n")

                print(f"Saved {len(video_tweet_urls)} video URLs to {batch_file}")

                # Now download videos using yt-dlp
                if os.path.exists(path_to_dlp):
                    print("\nDownloading videos using yt-dlp...")

                    # Build the yt-dlp command
                    dlp_cmd = [
                        path_to_dlp,
                        "--cookies-from-browser",
                        "chrome",
                        "-a",
                        batch_file,
                        "-f",
                        "best",
                        "-o",
                        f"{folder_path}/%(title)s-%(id)s.%(ext)s",
                        "--concurrent-fragments",
                        "5",
                    ]

                    # Execute the command
                    try:
                        subprocess.run(dlp_cmd, check=True)
                        print("Video download completed successfully!")
                    except subprocess.CalledProcessError as e:
                        print(f"Error during video download: {e}")
                else:
                    print(
                        f"\nWarning: yt-dlp not found at {path_to_dlp}. Please download videos manually with:"
                    )
                    print(
                        f'./dlp --cookies-from-browser chrome -a {batch_file} -f best -o "{folder_path}/%(title)s-%(id)s.%(ext)s"'
                    )

            print(f"Finished collecting media from {username}'s posts.")
            print(f"Downloaded {len(downloaded_images)} images")
            print(f"Collected {len(video_tweet_urls)} video links")

        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    # Prompt for Chrome launch
    print("\n" + "=" * 60)
    print(" CHROME LAUNCH INSTRUCTIONS")
    print("=" * 60)
    print("\nBefore running this script, you need to manually launch Chrome with")
    print("the debugging flag enabled. This will allow the script to connect to")
    print("your existing Chrome profile with all your cookies and logins.")
    print("\nRun this in Terminal:")
    print(
        '"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --remote-debugging-port=9222'
    )
    print("\nOnce Chrome is running with debugging enabled, press Enter to continue")
    print("=" * 60)
    input("\nPress Enter once Chrome is running with debugging enabled...")

    # Prompt the user for the username and number of scrolls
    target_username = input("Enter the username of the target profile: ")
    try:
        max_scrolls = int(input("Enter max number of scrolls (default 10): ") or 10)
    except ValueError:
        max_scrolls = 10

    # Ask for yt-dlp path
    default_dlp_path = "./dlp"
    dlp_path = (
        input(f"Enter path to yt-dlp executable (default: {default_dlp_path}): ")
        or default_dlp_path
    )

    print(
        f"Starting media downloader for @{target_username} with {max_scrolls} scrolls"
    )
    collect_media_links(target_username, max_scrolls, dlp_path)
