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
# Enable CORS for all routes
CORS(app)
# Limit upload size (example: 200MB). Adjust to your needs.
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024

def extract_frames(video_path, interval_seconds=2, max_frames=200):
    """
    Extract frames from video_path every interval_seconds.
    Returns list of PIL.Image objects.
    Caps at max_frames to avoid memory blowups.
    """
    clip = VideoFileClip(video_path)
    duration = clip.duration
    frames = []
    t = 0.0
    count = 0
    while t < duration and count < max_frames:
        try:
            frame = clip.get_frame(t)  # numpy array (H,W,3) uint8
            img = Image.fromarray(frame)
            frames.append(img.convert("RGB"))
            count += 1
            t += interval_seconds
        except Exception as e:
            # skip problematic timestamps
            t += interval_seconds
    clip.reader.close()
    clip.audio = None
    return frames

def images_to_pdf(images, out_path):
    """
    Save list of PIL.Image (RGB) to a multi-page PDF at out_path using fpdf2 for stable behavior.
    We'll save each image temporarily as JPEG, then add to PDF pages.
    """
    pdf = FPDF(unit="pt")  # using points for pixel-friendly sizes
    for img in images:
        # Resize page to image size
        w, h = img.size
        # fpdf expects sizes in points; use same numbers for pixel ~ point (works for typical cases)
        pdf.add_page(format=(w, h))
        # save temp jpeg
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpeg")
        tmp_name = tmp.name
        img.save(tmp_name, "JPEG", quality=85)
        tmp.close()
        pdf.image(tmp_name, 0, 0, w, h)
        os.unlink(tmp_name)
    pdf.output(out_path)

@app.route("/upload", methods=["POST"])
def upload():
    """
    Receives multipart form with file field 'video' and optional 'interval' seconds.
    Returns generated PDF file.
    """
    if 'video' not in request.files:
        return jsonify({"error": "Missing 'video' file"}), 400

    video = request.files['video']
    if video.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    try:
        interval = float(request.form.get('interval', 2.0))
        if interval <= 0:
            interval = 2.0
    except:
        interval = 2.0

    # create safe temp dir
    out_dir = tempfile.mkdtemp(prefix="bookscan_")
    video_path = os.path.join(out_dir, f"{uuid.uuid4().hex}_{video.filename}")
    video.save(video_path)

    try:
        frames = extract_frames(video_path, interval_seconds=interval, max_frames=400)
        if len(frames) == 0:
            return jsonify({"error": "No frames extracted. Try smaller interval or different video."}), 400

        pdf_path = os.path.join(out_dir, f"{uuid.uuid4().hex}.pdf")
        images_to_pdf(frames, pdf_path)

        return send_file(pdf_path, as_attachment=True, download_name="bookscan_output.pdf")
    except Exception as e:
        return jsonify({"error": "Conversion failed", "details": str(e)}), 500
    finally:
        # cleanup: video file removed (PDF may be in use until sent)
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
        except:
            pass

if __name__ == "__main__":
    # dev server
    app.run(host="0.0.0.0", port=5000, debug=True)
