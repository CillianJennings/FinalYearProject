#Creates FAISS HNSW index and adds all the vectors created before to it + creates python dict of the metadata
import json, os, faiss, numpy as np, pathlib, time

EMB_PATH   = "/home/plex/embeddings/embeddings.npy"
META_PATH  = "/home/plex/embeddings/metadata.jsonl"
INDEX_OUT  = "/home/plex/embeddings/faiss_hnsw.index"
IDMAP_OUT  = "/home/plex/embeddings/id2meta.json"

def main():
    print("Loading embeddings …")
    xb = np.load(EMB_PATH).astype("float32")        
    N, dim = xb.shape
    print(f"  vectors: {N:,}  dim: {dim}")

    M = 32                      
    index = faiss.IndexHNSWFlat(dim, M, faiss.METRIC_INNER_PRODUCT)
    index.hnsw.efConstruction = 200

    print("Adding vectors …")
    t0 = time.time()
    index.add(xb)               
    print(f"  added in {time.time()-t0:.1f}s")

    print(f"Saving index → {INDEX_OUT}")
    faiss.write_index(index, INDEX_OUT)

    print("Saving id→meta map …")
    id2meta = []
    with open(META_PATH, "r", encoding="utf-8") as f:
        for line in f:
            id2meta.append(json.loads(line))
    assert len(id2meta) == N
    with open(IDMAP_OUT, "w", encoding="utf-8") as f:
        json.dump(id2meta, f)

    print("Done")

if __name__ == "__main__":
    main()
