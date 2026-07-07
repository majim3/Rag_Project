import os
import json
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter




def load_data_from_scraper(datas: list[dict]) -> list[Document]:
    documents = []
    for data in datas:
        content = data.get("description", "")
        metadata = {
            "link": data.get("link", ""),
            "company": data.get("company", ""),
            "name": data.get("name", "")
        }
        document = Document(page_content=content, metadata=metadata)
        documents.append(document)

    return documents

def split_docs(documents: list[Document], chunk_size: int = 1000, chunk_overlap: int = 200, add_start_index : bool = True) -> list[Document]:

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = chunk_size,
        chunk_overlap = chunk_overlap,
        add_start_index = add_start_index
    )
    
    all_splits = text_splitter.split_documents(documents)

   
    return all_splits

def embedding_docs(splitted_docs: list[Document], model_name: str = "all-MiniLM-L6-v2"):
    load_dotenv()
    if not os.getenv("HUGGING_FACE"):
        print("you dont have key so download will be slower in hugging face")
    
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    vector_store = InMemoryVectorStore(embeddings)
    vector_store.add_documents(documents=splitted_docs)



    return vector_store

   



__location__ = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(__location__, "description_data.json"), "r", encoding="utf-8") as f:
    description_data_list = json.load(f)

docs = load_data_from_scraper(description_data_list)

splitted_docs = split_docs(docs)

vector_store = embedding_docs(splitted_docs)


print("splitted data:", len(docs))

print("splitted data:", len(splitted_docs))

print(vector_store)


# NEXT STEP retrieval  in langchain
   
