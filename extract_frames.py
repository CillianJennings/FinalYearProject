#Script extracts frames from your media(legally acquired movies!) using FFmpeg
import os
import subprocess
import sys

INPUT_FOLDER = "/mnt/md0/Media/Movies"
OUTPUT_BASE = "/home/plex/MovieFrames"
MAX_FILES = 50
EXTENSIONS = (".mp4", ".mkv")
FFMPEG_FPS_FILTER = "fps=1/5"

def find_video_files(folder, exts, limit):
    files = [f for f in os.listdir(folder) if f.lower().endswith(exts)]
    files.sort()
    return files[:limit]

def extract_frames(movie_path, out_dir, fps_filter):
    os.makedirs(out_dir, exist_ok=True)
    
    cmd = [
        "ffmpeg",
        "-hide_banner", "-loglevel", "error",
        "-i", movie_path,
        "-vf", fps_filter,
        os.path.join(out_dir, os.path.splitext(os.path.basename(movie_path))[0] + "_%06d.png")
    ]
    subprocess.run(cmd, check=True)

def main():
    if not os.path.isdir(INPUT_FOLDER):
        print(f"Error: input folder not found: {INPUT_FOLDER}", file=sys.stderr)
        sys.exit(1)

    videos = find_video_files(INPUT_FOLDER, EXTENSIONS, MAX_FILES)
    if not videos:
        print("No video files found.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(videos)} videos—processing up to {MAX_FILES}...")

    for vid in videos:
        movie_path = os.path.join(INPUT_FOLDER, vid)
        base_name = os.path.splitext(vid)[0]
        output_dir = os.path.join(OUTPUT_BASE, base_name)
        print(f"[{videos.index(vid)+1}/{len(videos)}] Extracting from '{vid}' → '{output_dir}'")
        try:
            extract_frames(movie_path, output_dir, FFMPEG_FPS_FILTER)
        except subprocess.CalledProcessError:
            print(f"ffmpeg failed on {vid}, skipping.", file=sys.stderr)

    print("All done!")

if __name__ == "__main__":
    main()
