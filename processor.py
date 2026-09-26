"""
ChemVideo AI - Video Processor (Python)

Real frame-by-frame stroke detection using FFmpeg + OpenCV.

Pipeline:
  1. ffprobe validates the video and reads duration / dimensions.
  2. FFmpeg extracts PNG frames at the requested FPS.
  3. OpenCV converts each frame to grayscale.
  4. Absolute difference between consecutive frames isolates newly appearing ink.
  5. Threshold + morphological opening removes noise / static UI (cursor, borders).
  6. Contours below a min area are ignored (static elements / speckle).
  7. Contours are tracked across frames (overlap / center proximity) into stroke objects.
  8. Each stroke gets a bounding box, start/end time, stroke path points, and a crop image.
  9. Objects are ordered chronologically and returned as a Stroke Timeline.

No timestamps, bounding boxes, or stroke data are invented: every value comes
from a real extracted frame and a real detected contour.
"""

import os
import json
import uuid
import shutil
import tempfile
import subprocess

import cv2

SUPPORTED_EXT = {"mp4", "mov", "webm", "mkv", "avi"}
MAX_FRAMES = 4000


def ext_of(filename):
    if not filename or "." not in filename:
        return ""
    return filename.rsplit(".", 1)[-1].lower()


def get_meta(path):
    """Return {duration, width, height} via ffprobe, or None if unreadable."""
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-print_format", "json",
             "-show_format", "-show_streams", path],
            capture_output=True, text=True, timeout=60,
        )
        if out.returncode != 0:
            return None
        data = json.loads(out.stdout)
    except Exception:
        return None
    v = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    return {
        "duration": float(data.get("format", {}).get("duration") or 0),
        "width": int(v["width"]) if v else 0,
        "height": int(v["height"]) if v else 0,
    }


def extract_frames(path, fps, out_dir):
    subprocess.run(
        ["ffmpeg", "-y", "-i", path, "-vf", f"fps={fps}", "-vsync", "0",
         os.path.join(out_dir, "frame_%05d.png")],
        check=True, capture_output=True,
    )


def _iou(a, b):
    x1 = max(a["x"], b["x"]); y1 = max(a["y"], b["y"])
    x2 = min(a["x"] + a["w"], b["x"] + b["w"]); y2 = min(a["y"] + a["h"], b["y"] + b["h"])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    union = a["w"] * a["h"] + b["w"] * b["h"] - inter
    return inter / union if union > 0 else 0


def _union(a, b):
    x1 = min(a["x"], b["x"]); y1 = min(a["y"], b["y"])
    x2 = max(a["x"] + a["w"], b["x"] + b["w"]); y2 = max(a["y"] + a["h"], b["y"] + b["h"])
    return {"x": x1, "y": y1, "w": x2 - x1, "h": y2 - y1}


def process_video(video_path, fps=2, sensitivity=0.5, crops_dir=None, crops_base_url=""):
    fps = max(1, min(30, int(fps)))
    sensitivity = max(0.0, min(1.0, float(sensitivity)))

    meta = get_meta(video_path)
    if not meta or not meta["width"] or not meta["height"]:
        raise ValueError("CORRUPTED")
    width, height, duration = meta["width"], meta["height"], meta["duration"]

    work_dir = tempfile.mkdtemp(prefix="chemvideo-")
    frames_dir = os.path.join(work_dir, "frames")
    os.makedirs(frames_dir)

    try:
        extract_frames(video_path, fps, frames_dir)
        files = sorted(f for f in os.listdir(frames_dir) if f.endswith(".png"))
        if len(files) < 2:
            return {
                "status": "completed",
                "video_duration": round(duration, 3),
                "frame_rate": fps,
                "timeline": [],
                "analysis_precision": "frame_based",
                "note": "Not enough frames extracted to detect strokes.",
            }

        diff_threshold = int(round(40 - sensitivity * 25))   # ~15..40
        min_area = int(round(150 - sensitivity * 120))      # ~30..150
        idle_to_close = max(1, round(fps * 0.4))
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

        active = []
        closed = []
        prev_gray = None

        for i, fname in enumerate(files):
            curr = cv2.imread(os.path.join(frames_dir, fname))
            if curr is None:
                continue
            curr_gray = cv2.cvtColor(curr, cv2.COLOR_BGR2GRAY)

            if prev_gray is not None:
                diff = cv2.absdiff(prev_gray, curr_gray)
                _, thresh = cv2.threshold(diff, diff_threshold, 255, cv2.THRESH_BINARY)
                opened = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
                contours, _ = cv2.findContours(opened, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                detected = []
                for c in contours:
                    if cv2.contourArea(c) < min_area:
                        continue
                    x, y, w, h = cv2.boundingRect(c)
                    detected.append({"x": x, "y": y, "w": w, "h": h,
                                     "cx": x + w / 2, "cy": y + h / 2})

                used = set()
                for stroke in active:
                    best = None
                    best_score = 0
                    for idx, d in enumerate(detected):
                        if idx in used:
                            continue
                        overlap = _iou(stroke["bbox"], d)
                        dist = ((stroke["cx"] - d["cx"]) ** 2 + (stroke["cy"] - d["cy"]) ** 2) ** 0.5
                        score = overlap if overlap > 0 else (0.1 if dist < 60 else 0)
                        if score > best_score:
                            best_score = score
                            best = (idx, d)
                    if best:
                        idx, d = best
                        used.add(idx)
                        stroke["last_frame"] = i
                        stroke["idle"] = 0
                        stroke["bbox"] = _union(stroke["bbox"], d)
                        stroke["cx"] = d["cx"]
                        stroke["cy"] = d["cy"]
                        stroke["points"].append({"x": d["cx"] / width, "y": d["cy"] / height, "t": i / fps})
                    else:
                        stroke["idle"] = stroke.get("idle", 0) + 1
                        if stroke["idle"] >= idle_to_close:
                            stroke["closed"] = True
                            closed.append(stroke)

                for idx, d in enumerate(detected):
                    if idx in used:
                        continue
                    active.append({
                        "id": str(uuid.uuid4()),
                        "start_frame": i,
                        "last_frame": i,
                        "idle": 0,
                        "closed": False,
                        "bbox": {"x": d["x"], "y": d["y"], "w": d["w"], "h": d["h"]},
                        "cx": d["cx"], "cy": d["cy"],
                        "points": [{"x": d["cx"] / width, "y": d["cy"] / height, "t": i / fps}],
                    })

            prev_gray = curr_gray

        for s in active:
            if not s.get("closed"):
                closed.append(s)
        closed.sort(key=lambda s: s["start_frame"])

        os.makedirs(crops_dir, exist_ok=True)
        timeline = []
        for idx, s in enumerate(closed):
            start_time = s["start_frame"] / fps
            end_time = (s["last_frame"] + 1) / fps
            crop_url = None
            frame_file = f"frame_{str(s['start_frame'] + 1).zfill(5)}.png"
            frame_path = os.path.join(frames_dir, frame_file)
            try:
                if os.path.exists(frame_path):
                    img = cv2.imread(frame_path)
                    if img is not None:
                        x = max(0, int(s["bbox"]["x"]))
                        y = max(0, int(s["bbox"]["y"]))
                        w = min(width - x, max(1, int(s["bbox"]["w"])))
                        h = min(height - y, max(1, int(s["bbox"]["h"])))
                        crop = img[y:y + h, x:x + w]
                        crop_name = f"{s['id']}.png"
                        cv2.imwrite(os.path.join(crops_dir, crop_name), crop)
                        crop_url = f"{crops_base_url}/crops/{crop_name}"
            except Exception:
                pass
            b = s["bbox"]
            timeline.append({
                "id": s["id"],
                "order": idx + 1,
                "start_time": round(start_time, 3),
                "end_time": round(end_time, 3),
                "x": round(b["x"] / width, 4),
                "y": round(b["y"] / height, 4),
                "width": round(b["w"] / width, 4),
                "height": round(b["h"] / height, 4),
                "stroke_data": [
                    {"x": round(p["x"], 4), "y": round(p["y"], 4), "t": round(p["t"], 3)}
                    for p in s["points"]
                ],
                "crop_url": crop_url,
                "recognized_content": "",
                "object_type": "unknown",
                "confidence": 0,
            })

        return {
            "status": "completed",
            "video_duration": round(duration, 3),
            "frame_rate": fps,
            "frames_processed": len(files),
            "analysis_precision": "frame_based",
            "timeline": timeline,
        }
    finally:
        try:
            shutil.rmtree(work_dir, ignore_errors=True)
        except Exception:
            pass