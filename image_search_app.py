from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
import faiss, clip, torch, numpy as np, json, io
from PIL import Image

INDEX_PATH  = "/home/plex/embeddings/faiss_hnsw.index"
IDMAP_PATH  = "/home/plex/embeddings/id2meta.json"
DEVICE      = "cuda" if torch.cuda.is_available() else "cpu" #Choose GPU for faster search

#Load the FAISS index
index = faiss.read_index(INDEX_PATH)

#Load the metadata map
with open(IDMAP_PATH, "r", encoding="utf-8") as f:
    id2meta = json.load(f)

#Load the clip model
model, preprocess = clip.load("ViT-B/32", DEVICE)
model.eval()

router = APIRouter()

#Create pydantic model schema for data validation, formatting etc.
class ImageResult(BaseModel):
    movie: str
    seconds: int
    frame_path: str
    score: float

@router.post("/search-image", response_model=ImageResult)
async def search_image(file: UploadFile = File(...)):
    #Read the image in, use PIL to accept any type of image file
    data = await file.read()
    try:
        img = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")
    #Turn the image into vector using CLIP
    with torch.no_grad():
        token = preprocess(img).unsqueeze(0).to(DEVICE)
        vec = model.encode_image(token).cpu().numpy().astype("float32")
    vec /= np.linalg.norm(vec, axis=1, keepdims=True)
    #Query FAISS index for closest match using nearest neighbour
    D, I = index.search(vec, 1)
    idx, dist = int(I[0][0]), float(D[0][0])
    #Retrieve the metadata for the matched index
    meta = id2meta[idx]
    if not meta:
        raise HTTPException(status_code=502, detail="No metadata for index")

    return ImageResult(
        movie      = meta["movie"],
        seconds    = meta["seconds"],
        frame_path = meta["frame_path"],
        score      = dist
    )
