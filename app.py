"""
ChemVideo AI - Video Processor API (FastAPI).

External microservice. The Base44 app calls POST /process-video via
VIDEO_PROCESSOR_URL and receives a Stroke Timeline JSON.

Flow:
  Base44 -> VIDEO_PROCESSOR_URL -> this Python service -> FFmpeg + OpenCV
        -> Stroke Timeline JSON -> Base44
"""

import os
import asyncio
import tempfile

import requests
import cv2
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from processor import process_video, get_meta, ext_of, SUPPORTED_EXT

PORT = int(os.environ.get("PORT", "8000"))
PROCESSING_TIMEOUT = int(os.environ.get("PROCESSING_TIMEOUT_MS", str(15 * 60 * 1000))) / 1000
CROPS_DIR = os.environ.get("CROPS_DIR", os.path.join(os.path.dirname(__file__), "crops"))

os.makedirs(CROPS_DIR, exist_ok=True)

app = FastAPI(title="ChemVideo Video Processor", version="1.0.0")
app.mount("/crops", StaticFiles(directory=CROPS_DIR), name="crops")


def _has_ffmpeg():
    try:
        subprocess_res = __import__("subprocess")
        subprocess_res.run(["ffmpeg", "-version"], capture_output=True, timeout=10)
        return True
    except Exception:
        return False


def _has_opencv():
    try:
        import cv2 as _  # noqa
        return True
    except Exception:
        return False


@app.get("/health")
def health():
    return {
        "status": "ok" if (_has_ffmpeg() and _has_opencv()) else "degraded",
        "ffmpeg": _has_ffmpeg(),
        "opencv": _has_opencv(),
        "version": "1.0.0",
    }


def _download(url, dest):
    r = requests.get(url, stream=True, timeout=120)
    r.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)


@app.post("/process-video")
async def process_video_endpoint(request: Request):
    ct = request.headers.get("content-type", "")
    fps = None
    sensitivity = 0.5
    video_url = None
    upload = None
    tmp_path = None
    local_path = None

    try:
        if "application/json" in ct:
            data = await request.json()
            video_url = data.get("video_url")
            fps = data.get("fps")
            sensitivity = data.get("sensitivity", 0.5)
        elif "multipart/form-data" in ct:
            form = await request.form()
            fps = form.get("fps")
            sensitivity = form.get("sensitivity", 0.5)
            video_url = form.get("video_url")
            upload = form.get("video")
        else:
            return JSONResponse(status_code=415, content={
                "status": "error", "error": "unsupported_media_type",
                "message": "Use application/json or multipart/form-data.",
            })

        # --- missing video ---
        has_upload = upload is not None and hasattr(upload, "read")
        if not video_url and not has_upload:
            return JSONResponse(status_code=400, content={
                "status": "error", "error": "missing_video",
                "message": "Provide a video file (multipart) or a video_url.",
            })

        # --- unsupported format ---
        name = (upload.filename if has_upload else video_url) or ""
        e = ext_of(name)
        if e and e not in SUPPORTED_EXT:
            return JSONResponse(status_code=400, content={
                "status": "error", "error": "unsupported_format",
                "message": f"Format .{e} is not supported. Use {', '.join(sorted(SUPPORTED_EXT))}.",
            })

        # acquire local video
        if has_upload:
            ext2 = ext_of(upload.filename or "") or "mp4"
            tmp_path = os.path.join(tempfile.gettempdir(), f"chemvideo-upload-{os.getpid()}.{ext2}")
            with open(tmp_path, "wb") as f:
                f.write(await upload.read())
            local_path = tmp_path
        else:
            ext2 = ext_of(video_url) or "mp4"
            tmp_path = os.path.join(tempfile.gettempdir(), f"chemvideo-{os.getpid()}.{ext2}")
            try:
                _download(video_url, tmp_path)
            except Exception as ex:
                return JSONResponse(status_code=400, content={
                    "status": "error", "error": "download_failed", "message": str(ex),
                })
            local_path = tmp_path

        # --- corrupted video (ffprobe will fail) ---
        if not get_meta(local_path):
            return JSONResponse(status_code=422, content={
                "status": "error", "error": "corrupted_video",
                "message": "FFprobe could not read the video. The file may be corrupted or truncated.",
            })

        crops_base = str(request.base_url).rstrip("/")

        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(process_video, local_path, fps, sensitivity, CROPS_DIR, crops_base),
                timeout=PROCESSING_TIMEOUT,
            )
            return result
        except asyncio.TimeoutError:
            return JSONResponse(status_code=504, content={
                "status": "error", "error": "processing_timeout",
                "message": "Processing exceeded the time limit.",
            })
        except MemoryError:
            return JSONResponse(status_code=507, content={
                "status": "error", "error": "insufficient_resources",
                "message": "Not enough memory to process this video.",
            })
        except OSError as ex:
            if getattr(ex, "errno", None) == 28:  # ENOSPC
                return JSONResponse(status_code=507, content={
                    "status": "error", "error": "insufficient_resources",
                    "message": "Not enough disk space to extract frames.",
                })
            return JSONResponse(status_code=500, content={
                "status": "error", "error": "processing_failed", "message": str(ex),
            })
        except ValueError as ex:
            if str(ex) == "CORRUPTED":
                return JSONResponse(status_code=422, content={
                    "status": "error", "error": "corrupted_video", "message": "No video stream found.",
                })
            return JSONResponse(status_code=500, content={
                "status": "error", "error": "processing_failed", "message": str(ex),
            })
        except Exception as ex:
            return JSONResponse(status_code=500, content={
                "status": "error", "error": "processing_failed", "message": str(ex),
            })
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=PORT)