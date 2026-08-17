import os
from dotenv import load_dotenv
import yt_dlp
from pydub import AudioSegment

load_dotenv()

DOWNLOAD_DIR = 'downloades'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


import os
from dotenv import load_dotenv
import yt_dlp
from pydub import AudioSegment

load_dotenv()

DOWNLOAD_DIR = 'downloades'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_youtube_audio(url: str) -> str:
    """Downloads audio from YouTube, bypasses 403 blocks, and converts to WAV format."""
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    
    ydl_opts = {
        "format": "m4a/bestaudio/best",
        "outtmpl": output_path,
        # Updated extractor arguments to bypass modern YouTube 403/PoToken restrictions
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "ios", "mweb"],
                "player_skip": ["configs", "webpage"],
            }
        },
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        },
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "no_warnings": True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        base_name, _ = os.path.splitext(filename)
        wav_filename = f"{base_name}.wav"
        
    return wav_filename


def convert_to_wav(input_path: str) -> str:
    """Converts local audio/video files to standard 16kHz mono WAV format."""
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(output_path, format="wav")
    return output_path


def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:
    """Splits audio into smaller segments (16kHz mono) to prevent memory overload."""
    audio = AudioSegment.from_wav(wav_path)
    # Ensure all chunks are standardized to 16kHz mono for speech recognition
    audio = audio.set_channels(1).set_frame_rate(16000)
    chunk_ms = chunk_minutes * 60 * 1000 

    chunks = []
    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start : start + chunk_ms]
        chunk_path = f"{os.path.splitext(wav_path)[0]}_chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)
    
    return chunks


def process_input(source: str) -> list:
    """Main pipeline function to handle local files or YouTube links."""
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks


if __name__ == "__main__":
    test_source = input("Enter YouTube URL or file path: ").strip()
    if test_source:
        res = process_input(test_source)
        print("Generated chunks:", res)
