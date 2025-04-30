import os
import subprocess
import sys
import shlex
import shutil
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

CONTENT_DIR = os.getenv("CONTENT_DIR", "./content")
PYTHON_EXEC = sys.executable

#Function to execture shell command
def run_command(cmd: str):
    print("", cmd)
    res = subprocess.run(cmd, shell=True)
    if res.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}")

router = APIRouter()

#Create pydantic model schema for data validation, formatting etc.
class UpscaleRequest(BaseModel):
    movie: str
class UpscaleResponse(BaseModel):
    filename: str
    message: str

@router.post("/upscale", response_model=UpscaleResponse)
async def upscale_movie(req: UpscaleRequest):
    inp = os.path.join(CONTENT_DIR, req.movie)
    if not os.path.isfile(inp):
        raise HTTPException(404, detail="Movie not found")

    name, ext = os.path.splitext(req.movie)
    temp_frames    = "frames"
    tmp_up_frames  = "upscaled_frames"
    temp_video     = "up_temp.mp4"
    audio_file     = "audio.aac"
    out_name       = f"{name}_upscaled{ext}"
    out_path       = os.path.join(CONTENT_DIR, out_name)

    #Delete and remake frames directories to get rid of previous frames
    for d in (temp_frames, tmp_up_frames):
        if os.path.isdir(d):
            shutil.rmtree(d)
    for f in (temp_video, audio_file):
        if os.path.exists(f):
            os.remove(f)
    os.makedirs(temp_frames, exist_ok=True)
    os.makedirs(tmp_up_frames, exist_ok=True)

    try:
        #Extract frames
        run_command(
            f"ffmpeg -i {shlex.quote(inp)} -qscale:v 2 {temp_frames}/frame_%06d.png"
        )
        #Upscale frames using RealESRGAN
        run_command(
            f"{PYTHON_EXEC} inference_realesrgan.py "
            f"-n RealESRGAN_x4plus_anime_6B "
            f"--model_path weights/RealESRGAN_x4plus_anime_6B.pth "
            f"-i {temp_frames} -o {tmp_up_frames}"
        )
        #Get movies frame 
        fps_cmd = (
            f"ffprobe -v 0 -select_streams v:0 "
            f"-show_entries stream=r_frame_rate -of csv=p=0 {shlex.quote(inp)}"
        )
        fps_proc = subprocess.run(fps_cmd, shell=True, capture_output=True, text=True)
        num,den = fps_proc.stdout.strip().split('/')
        fps = float(num)/float(den)
        #Assemble the upscaled frames into video
        run_command(
            f"ffmpeg -framerate {fps} -i {tmp_up_frames}/frame_%06d_out.png "
            f"-c:v libx264 -pix_fmt yuv420p {temp_video}"
        )
        #Extract orignal audio and merge into upsaled video
        run_command(f"ffmpeg -i {shlex.quote(inp)} -vn -acodec copy {audio_file}")
        run_command(f"ffmpeg -i {temp_video} -i {audio_file} -c:v copy -c:a copy {shlex.quote(out_path)}")
    except Exception as e:
        raise HTTPException(500, detail=str(e))
    finally:
        #Delete temporary directories
        shutil.rmtree(temp_frames,     ignore_errors=True)
        shutil.rmtree(tmp_up_frames,    ignore_errors=True)
        for f in (temp_video, audio_file):
            if os.path.exists(f):
                os.remove(f)

    return UpscaleResponse(
        filename=out_name,
        message=f"Upscaled video saved as {out_name}"
    )
