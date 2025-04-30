import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from recommend_app import router as rec_router
from image_search_app import router as img_router
from subtitle_app import router as subs_router
from upscaling_app  import router as up_router

#Create FastAPI app
app = FastAPI(title="All-in-One Media API")

#Allow frontend work with both URLs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://192.168.50.46:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

#Mount each router
app.include_router(rec_router,    prefix="/api")
app.include_router(img_router,    prefix="/api")
app.include_router(subs_router,   prefix="/api")
app.include_router(up_router,     prefix="/api")

#Let frontend directly access 'content' directory
app.mount("/content", StaticFiles(directory="content"), name="content")

if __name__ == "__main__":
    #Start web server
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
