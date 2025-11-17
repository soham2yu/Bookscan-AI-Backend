# Backend/app.py
import os
import uuid
import tempfile
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from moviepy.editor import VideoFileClip
from PIL import Image
from fpdf import FPDF

app = Flask(__name__)

# --------------------------------------------------
# ✅ CORS FIX FOR VERCEL → RENDER
# --------------------------------------------------
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://bookscan-ai-frontend.vercel.app",  # your frontend
            "http://localhost:3000"                    # local dev
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Limit upload size to 200MB
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024


# --------------------------------------------------
# 🔥 HEALTH CHECK / HOME ROUTE
# --------------------------------------------------
@app.route("/")
def home():
    return {"status": "Backend Running Successfully"}


# --------------------------------------------------
# Extract frames from video
# --------------------------------------------------
def extract_frames(video_path, interval_seconds=2, max_frames=200):
    clip = VideoFileClip(video_path)
    duration = clip.duration
    frames = []
    t = 0.0
    count = 0

    while t < duration and count < max_frames:
        try:
            frame = clip.get_frame(t)
            img = Image.fromarray(frame)
            frames.append(img.convert("RGB"))
            count += 1
            t += interval_seconds
        except:
            t += interval_seconds

    clip.reader.close()
    clip.audio = None
    return frames


# --------------------------------------------------
# Convert images → PDF
# --------------------------------------------------
def images_to_pdf(images, out_path):
    pdf = FPDF(unit="pt")
    for img in images:
        w, h = img.size
        pdf.add_page(format=(w, h))
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpeg")
        tmp_name = tmp.name
        img.save(tmp_name, "JPEG", quality=85)
        tmp.close()
        pdf.image(tmp_name, 0, 0, w, h)
        os.unlink(tmp_name)
    pdf.output(out_path)


# --------------------------------------------------
# Upload Route
# --------------------------------------------------
@app.route("/upload", methods=["POST"])
def upload():
    if "video" not in request.files:
        return jsonify({"error": "Missing 'video' file"}), 400

    video = request.files["video"]
    if video.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    try:
        interval = float(request.form.get("interval", 2.0))
        if interval <= 0:
            interval = 2.0
    except:
        interval = 2.0

    out_dir = tempfile.mkdtemp(prefix="bookscan_")
    video_path = os.path.join(out_dir, f"{uuid.uuid4().hex}_{video.filename}")
    video.save(video_path)

    try:
        frames = extract_frames(video_path, interval_seconds=interval, max_frames=400)
        if len(frames) == 0:
            return jsonify({"error": "No frames extracted"}), 400

        pdf_path = os.path.join(out_dir, f"{uuid.uuid4().hex}.pdf")
        images_to_pdf(frames, pdf_path)

        return send_file(pdf_path, as_attachment=True, download_name="bookscan_output.pdf")

    except Exception as e:
        return jsonify({"error": "Conversion failed", "details": str(e)}), 500

    finally:
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
        except:
            pass


# --------------------------------------------------
# Run locally
# --------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
