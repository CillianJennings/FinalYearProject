#Script takes the PNG frames created before and turns them into vectors using CLIP, also creates the metadata file
import os, json, re, time, pathlib
import numpy as np
from tqdm import tqdm
from PIL import Image
import torch, clip                    

FRAME_ROOT = "/home/plex/MovieFrames"      
OUTPUT_DIR = "/home/plex/embeddings"     

BATCH_SIZE   = 64
DEVICE       = "cuda" if torch.cuda.is_available() else "cpu"
TIMESTAMP_RE = re.compile(r"_(\d{6})\.png$")     

def all_pngs(root):
    for movie in sorted(os.listdir(root)):
        mov_dir = os.path.join(root, movie)
        if not os.path.isdir(mov_dir):
            continue
        for png in sorted(pathlib.Path(mov_dir).rglob("*.png")):
            yield movie, str(png.resolve())

def sec_from_filename(fname):
    m = TIMESTAMP_RE.search(fname)
    if not m:
        return None
    idx = int(m.group(1)) - 1
    return idx * 5

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    model, preprocess = clip.load("ViT-B/32", DEVICE)
    model.eval()

    paths, movies, seconds = [], [], []
    for movie, p in all_pngs(FRAME_ROOT):
        paths.append(p); movies.append(movie); seconds.append(sec_from_filename(p))

    N = len(paths)
    print(f"Found {N:,} frames")

    all_embeds = np.empty((N, 512), dtype="float32")
    metadata_path = os.path.join(OUTPUT_DIR, "metadata.jsonl")
    t0 = time.time()

    with torch.no_grad(), open(metadata_path, "w", encoding="utf-8") as meta_f:
        for start in tqdm(range(0, N, BATCH_SIZE)):
            end   = min(start + BATCH_SIZE, N)
            batch = []
            for p in paths[start:end]:
                img = Image.open(p).convert("RGB")
                batch.append(preprocess(img))
            batch = torch.stack(batch).to(DEVICE)

            embeds = model.encode_image(batch).cpu().numpy().astype("float32")
            all_embeds[start:end] = embeds / np.linalg.norm(embeds, axis=1, keepdims=True)

            for i, idx in enumerate(range(start, end)):
                meta = {
                    "index": idx,
                    "movie": movies[idx],
                    "frame_path": paths[idx],
                    "seconds": seconds[idx],
                }
                meta_f.write(json.dumps(meta, ensure_ascii=False) + "\n")

    np.save(os.path.join(OUTPUT_DIR, "embeddings.npy"), all_embeds)
    dt = time.time() - t0
    print(f"Done. Saved embeddings + metadata to {OUTPUT_DIR} in {dt/60:.1f} min.")

if __name__ == "__main__":
    main()
