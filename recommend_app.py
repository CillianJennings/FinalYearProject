from fastapi import APIRouter
from pydantic import BaseModel
from llama_cpp import Llama
import os, re, ast

model_path = "/home/plex/Llama/models/Meta-Llama-3.1-8B-Instruct.Q4_K_M.gguf"
#Initialise Llama model
llm = Llama(
    model_path=model_path,
    n_ctx=4096,
    n_gpu_layers=32,
    n_threads=6,
    n_batch=512
)

router = APIRouter()

#Create pydantic model schema for data validation, formatting etc.
class MovieRequest(BaseModel):
    title: str
class MovieResponse(BaseModel):
    recommendations: list[str]


@router.post("/recommend", response_model=MovieResponse)
async def recommend_movie(req: MovieRequest):
    prompt = (
        f"Do NOT output any reasoning or steps. ONLY output the Python list. NOTHING else. List exactly ten movies similar to the movie: {req.title} as a python list. " 
        f"They must be unique. Do NOT include the year of the movies or a description. If {req.title} has a sequel include it in the list."
    )
    
    #Prompt the llama model and extract the response, params include: limit length, creativity, freq penalties
    resp = llm(prompt, max_tokens=128, temperature=0.7, top_p=0.9,
               repeat_penalty=1.1, frequency_penalty=0.5)
    text = resp["choices"][0]["text"].strip()
    print("Model text: " + text)

    #Extract the list
    match = re.search(r"\[.*?\]", text, re.DOTALL)
    if not match: 
        return MovieResponse(recommendations=["Error"])
    list_str = match.group(0)

    #Check to make sure its actually a list with correct formatting
    try:
        movies = ast.literal_eval(list_str)
        if not isinstance(movies, list):      
            raise ValueError("Not a list")
    except Exception as e:
        print("Parse error:", e)
        movies = ["Error"]

    print("Final movies list:", movies)
    return MovieResponse(recommendations=movies)
    
