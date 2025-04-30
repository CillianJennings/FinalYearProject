import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import whisper

CONTENT_DIR = os.getenv("CONTENT_DIR", "./content")

#Load whisper model
print("Loading Whisper base.en model…")
whisper_model = whisper.load_model("base.en")
print("Whisper loaded.")

router = APIRouter()

#Create pydantic model schema for data validation, formatting etc.
class SubtitleRequest(BaseModel):
    movie: str
class SubtitleResponse(BaseModel):
    filename: str
    message: str

#Gets all the movies in the content directory for the dropdown menu
@router.get("/movies", response_model=list[str])
async def list_movies():
    try:
        files = os.listdir(CONTENT_DIR)
    except FileNotFoundError:
        raise HTTPException(500, detail=f"Content directory not found: {CONTENT_DIR}")
    videos = [f for f in files if f.lower().endswith((".mp4", ".mkv", ".avi", ".mov"))]
    return videos

@router.post("/generate-subs", response_model=SubtitleResponse)
async def generate_subtitles(req: SubtitleRequest):
    
    #Build path for the requested video
    video_path = os.path.join(CONTENT_DIR, req.movie)
    if not os.path.exists(video_path):
        raise HTTPException(404, detail=f"Video not found: {req.movie}")
    
    #Run whisper model transcription
    result = whisper_model.transcribe(video_path, fp16=False)
    segments = result.get("segments", [])

    #Function to format seconds into SRT timestamp
    def fmt(ts: float) -> str:
        h = int(ts//3600)
        m = int((ts%3600)//60)
        s = int(ts%60)
        ms = int((ts - int(ts)) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    #Create the srt file
    srt_name = os.path.splitext(req.movie)[0] + ".srt"
    out_path = os.path.join(CONTENT_DIR, srt_name)
    with open(out_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            f.write(f"{i}\n")
            f.write(f"{fmt(seg['start'])} --> {fmt(seg['end'])}\n")
            f.write(seg["text"].strip() + "\n\n")

    return SubtitleResponse(
        filename=srt_name,
        message=f"Subtitle saved as {srt_name}"
    )
