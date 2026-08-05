from fastapi import FastAPI
from pydantic import BaseModel
from rag import load_data_from_scraper, split_docs, embedding_docs, retrieval_and_generation
import json
import os
from fastapi.middleware.cors import CORSMiddleware

class UsrPrompt(BaseModel):
    UsrPrompt:str

app = FastAPI()

origins = [
    "http://localhost:5173"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

__location__ = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(__location__, "description_data.json"), encoding="utf-8") as f:
    data = json.load(f)
docs = load_data_from_scraper(data)
splitted_docs = split_docs(docs)
vector_store = embedding_docs(splitted_docs)

@app.post("/prompt")
async def create_item(UsrPrompt: UsrPrompt):
    print("got item", UsrPrompt.UsrPrompt)
    print("now retriving awnser")
    retriver = retrieval_and_generation(vector_store, UsrPrompt.UsrPrompt)
    if(retriver):
        print("retrived awnser:", retriver)
    else:
        print("didnt get awnser")

    return retriver

