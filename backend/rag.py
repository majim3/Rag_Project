import os
import json
from dotenv import load_dotenv
from dotenv import dotenv_values
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

print("GROQ_API_KEY:", "OK" if os.getenv("GROQ_API_KEY") else "PUUTTUU!")
print("HF_TOKEN:", "OK" if os.getenv("HF_TOKEN") else "PUUTTUU!")



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
    print(f"document list size:{len(documents)}")

    return documents

def split_docs(documents: list[Document], chunk_size: int = 1000, chunk_overlap: int = 200, add_start_index : bool = True) -> list[Document]:

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = chunk_size,
        chunk_overlap = chunk_overlap,
        add_start_index = add_start_index
    )
    
    all_splits = text_splitter.split_documents(documents)
    print(f"splitted documents: {len(all_splits)}")
   
    return all_splits

def embedding_docs(splitted_docs: list[Document], model_name: str = "all-MiniLM-L6-v2"):
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    vector_store = InMemoryVectorStore(embeddings)
    vector_store.add_documents(documents=splitted_docs)
    print(f"splitted documets added to vector store: {vector_store}")

    return vector_store

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def retrieval_and_generation(vector_store, userq : str = ""):
    retrived_docs = vector_store.as_retriever()
    prompt = ChatPromptTemplate.from_template("""Answer the question based only on the following context:

Context: {context}

Question: {question}
""")
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

    rag_chain = (
        {"context": retrived_docs | format_docs, "question" : RunnablePassthrough()}
        |prompt
        |llm
        |StrOutputParser()
    )

    return rag_chain.invoke(userq)

   

if __name__ == "__main__":
    __location__ = os.path.dirname(os.path.abspath(__file__)) 
    with open(os.path.join(__location__, "description_data.json"), "r", encoding="utf-8") as f:
        description_data_list = json.load(f)  
    load_data = load_data_from_scraper(description_data_list)
    splitted_docs = split_docs(load_data)
    vector_store = embedding_docs(splitted_docs)
    retrived_docs = retrieval_and_generation(vector_store, "find junior IT developer jobs")
    

    print (retrived_docs)


    





   
