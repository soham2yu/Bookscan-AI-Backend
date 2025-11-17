import os
import subprocess
import uuid
import glob

def extract_frames(video_path):
    """
    Extract frames from video at regular intervals (every 2 seconds for faster processing)
    """
    out_dir = f"frames_{uuid.uuid4()}"
    os.makedirs(out_dir, exist_ok=True)

    # Extract frames at 0.5 fps (every 2 seconds) for faster processing
    cmd = [
        "ffmpeg", "-i", video_path,
        "-vf", "fps=0.5",  # Extract every 2 seconds
        "-q:v", "2",  # Good quality
        f"{out_dir}/frame_%04d.jpg"
    ]

    try:
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, timeout=300)
        if result.returncode != 0:
            print(f"FFmpeg failed with return code {result.returncode}")
            return []
    except subprocess.TimeoutExpired:
        print("FFmpeg timed out")
        return []
    except Exception as e:
        print(f"FFmpeg error: {e}")
        return []

    frames = sorted(glob.glob(f"{out_dir}/*.jpg"))

    # If no frames extracted, try a different approach
    if not frames:
        # Fallback: extract frames at 0.25 fps
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vf", "fps=0.25",
            "-q:v", "2",
            f"{out_dir}/frame_%04d.jpg"
        ]
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, timeout=300)
            frames = sorted(glob.glob(f"{out_dir}/*.jpg"))
        except:
            pass

    return frames
