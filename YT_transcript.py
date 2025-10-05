# YouTube Transcript Loader
# This module handles fetching YouTube transcripts

from youtube_transcript_api import YouTubeTranscriptApi
import re

def get_video_id(url):
    """Extract video ID from YouTube URL."""
    match = re.search(r'(?:v=|youtu.be/)([\w-]+)', url)
    return match.group(1) if match else url

def load_transcript_text(video_url_or_id):
    """Load transcript and return as concatenated text."""
    video_id = get_video_id(video_url_or_id)
    try:
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id, languages=['en'])
        return " ".join([entry.text for entry in transcript])
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return ""

if __name__ == "__main__":
    # Test the function
    video_url = "https://www.youtube.com/watch?v=pidnIHdA1Y8"
    transcript = load_transcript_text(video_url)
    if transcript:
        print(f"Transcript loaded successfully. Length: {len(transcript)} characters")
        print("First 200 characters:")
        print(transcript[:200] + "...")
    else:
        print("Failed to load transcript")