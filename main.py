from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware

from portfolio import Portfolio
import json

class Request(BaseModel):
    assets: List[str]
    start: str
    end: str
    algorithm: str
    population_size: int
    n_gen_per_iter: int
    n_iterations: int

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/optimize")
async def optimize(request: Request):
    portfolio = Portfolio(request.assets, request.start, request.end)
    result = portfolio.optimize(
      algorithm=request.algorithm,
      population_size=request.population_size,
      n_gen_per_iter=request.n_gen_per_iter,
      n_iterations=request.n_iterations)
    return json.loads(result.to_json(orient='records'))

app.mount("/", StaticFiles(directory="frontend/build",html = True), name="frontend")
