import os
import re
import shutil
import subprocess
from yt_dlp import YoutubeDL
from yt_dlp.utils import ExtractorError, DownloadError

def sanitize_filename(filename):
    """Remove invalid characters from filename."""
    return re.sub(r'[<>:"/\\|?*]', '', filename)

def check_ffmpeg():
    """Check if ffmpeg is installed and accessible."""
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def log_failure(url, error, log_file="failed_downloads.txt"):
    """Log failed downloads to a file."""
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{url}: {str(error)}\n")

def download_youtube_audio(url, output_path="/"):
    try:
        if not os.path.exists("/Volumes/NO NAME"):
            raise Exception("Pendrive não encontrado. Verifique se está conectado em '/Volumes/NO NAME/'")

        total, used, free = shutil.disk_usage("/Volumes/NO NAME")
        free_gb = free / (1024**3)

        if free_gb < 0.1:
            raise Exception(f"Espaço insuficiente no pendrive. Apenas {free_gb:.2f}GB disponível. Libere espaço e tente novamente.")

        print(f"Espaço disponível no pendrive: {free_gb:.2f}GB")

        if not check_ffmpeg():
            raise Exception("ffmpeg não está instalado ou não está no PATH. Instale o ffmpeg para converter para MP3.")

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(output_path, '%(title)s.mp3'),
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'verbose': True,
            'cookiefile': 'cookies.txt',
            'ignoreerrors': True,
        }

        # Download and convert to MP3
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if info:
                if 'entries' in info:  # Playlist
                    for entry in info['entries']:
                        if entry:
                            print(f"Audio saved as: {os.path.join(output_path, sanitize_filename(entry['title']) + '.mp3')}")
                        else:
                            print(f"Skipped unavailable video in playlist: {url}")
                else:  # Single video
                    print(f"Audio saved as: {os.path.join(output_path, sanitize_filename(info['title']) + '.mp3')}")
            else:
                print(f"Skipped unavailable content: {url}")

        return True

    except (ExtractorError, DownloadError) as e:
        print(f"Failed to download {url}: {str(e)}")
        log_failure(url, str(e))
        return False
    except Exception as e:
        print(f"An unexpected error occurred for {url}: {str(e)}")
        log_failure(url, str(e))
        return False

def read_urls_from_file(file_path):
    """Read URLs from a text file."""
    urls = []
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return urls

def main():
    urls_file = "urls.txt"
    urls = read_urls_from_file(urls_file)

    if urls:
        print(f"Found {len(urls)} URLs in {urls_file}. Processing...")
        for url in urls:
            print(f"\nProcessing: {url}")
            download_youtube_audio(url)
        print("\nFinished processing URLs from file.")

    while True:
        url = input("\nEnter YouTube URL (or 'quit' to exit): ")
        if url.lower() == 'quit':
            break

        if not url.startswith("https://www.youtube.com/"):
            print("Please enter a valid YouTube URL.")
            continue

        download_youtube_audio(url)

if __name__ == "__main__":
    main()