# ChemVideo AI — Video Processor (Python)

External video-processing microservice for ChemVideo AI. Accepts an uploaded
chemistry-solution video, extracts frames with **FFmpeg**, detects newly
appearing handwriting with **OpenCV** (consecutive-frame differencing), and
returns a structured **Stroke Timeline** JSON.

```
Base44  →  VIDEO_PROCESSOR_URL  →  Python Video Processor  →  FFmpeg + OpenCV
                                                              →  Stroke Timeline JSON
                                                              →  Base44
```

> ⚠️ The Base44 worker runtime **cannot** run FFmpeg/OpenCV or expose a public
> long-running processing endpoint. This service must be **deployed separately**
> (a VPS, Docker host, Google Cloud Run, AWS ECS, etc.) and connected to the
> Base44 app via the `VIDEO_PROCESSOR_URL` secret.

---

## How it works (real, not faked)

1. `ffprobe` validates the video and reads duration + dimensions.
2. `ffmpeg` extracts PNG frames at the requested FPS.
3. OpenCV converts each frame to grayscale.
4. Absolute difference between consecutive frames isolates newly appearing ink.
5. Threshold + morphological opening removes noise, cursor, borders, static UI.
6. Contours below a minimum area are discarded (static elements / speckle).
7. Contours are tracked across frames (overlap + center proximity) into stroke objects.
8. Each stroke gets a bounding box, start/end time, stroke path, and a saved crop image.
9. Objects are ordered chronologically and returned as the Stroke Timeline.

No timestamps, bounding boxes, or stroke paths are invented — every value
comes from a real extracted frame and a real detected contour.

`recognized_content`, `object_type`, and `confidence` are returned empty
(`""` / `"unknown"` / `0`) by this service. Content recognition (chemistry OCR)
is performed by the Base44 app via its vision LLM on the `crop_url` images —
see `base44/functions/analyzeStrokes/entry.ts`.

---

## API

### `GET /health`
```json
{ "status": "ok", "ffmpeg": true, "opencv": true, "version": "1.0.0" }
```

### `POST /process-video`

**Input** — either:
- `application/json`: `{ "video_url": "...", "fps": 2, "sensitivity": 0.5 }`  ← used by the Base44 app
- `multipart/form-data`:  `video` (file) · `fps` (optional) · `sensitivity` (optional, 0–1)

**Output**
```json
{
  "status": "completed",
  "video_duration": 18.42,
  "frame_rate": 2,
  "frames_processed": 36,
  "analysis_precision": "frame_based",
  "timeline": [
    {
      "id": "9b1c...",
      "order": 1,
      "start_time": 0.0,
      "end_time": 1.5,
      "x": 0.12, "y": 0.34, "width": 0.18, "height": 0.09,
      "stroke_data": [{ "x": 0.2, "y": 0.38, "t": 0.0 }, { "x": 0.21, "y": 0.38, "t": 0.5 }],
      "crop_url": "https://<processor-host>/crops/9b1c....png",
      "recognized_content": "",
      "object_type": "unknown",
      "confidence": 0
    }
  ]
}
```

### Error handling
| HTTP | `error` | cause |
|------|---------|-------|
| 400 | `missing_video` | no file and no `video_url` |
| 400 | `unsupported_format` | extension not in mp4/mov/webm/mkv/avi |
| 415 | `unsupported_media_type` | not JSON or multipart |
| 422 | `corrupted_video` | ffprobe cannot read the file |
| 504 | `processing_timeout` | exceeded `PROCESSING_TIMEOUT_MS` |
| 507 | `insufficient_resources` | out of memory / disk (ENOSPC) |
| 500 | `processing_failed` | unexpected |

---

## Local development

```bash
# 1. System deps (Ubuntu/Debian)
sudo apt-get install -y ffmpeg libgl1 libglib2.0-0

# 2. Python env
cd video-processor
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000     # http://localhost:8000
```

## Docker deployment

```bash
cd video-processor
docker build -t chemvideo-processor .
docker run -p 8000:8000 \
  -e PROCESSING_TIMEOUT_MS=900000 \
  --tmpfs /tmp:size=1g \
  chemvideo-processor
```

## Connect to the Base44 app

Once the service has a public URL (e.g. `https://processor.yourdomain.com`):

1. In the Base44 app dashboard → **Secrets**, set:
   ```
   VIDEO_PROCESSOR_URL = https://processor.yourdomain.com
   ```
2. The `analyzeStrokes` backend function POSTs `video_url` + `fps` +
   `sensitivity` to `POST /process-video`, maps the returned `timeline` into
   `StrokeObject` records, runs chemistry OCR on each `crop_url`, and stores the
   result. The Stroke Timeline debug view (`/videos/:id/strokes`) then displays
   the real detected strokes.

The ChemVideo AI frontend workflow is unchanged.