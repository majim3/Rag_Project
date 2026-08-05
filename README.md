# Duunitori RAG

A job search application that scrapes IT job listings from Duunitori, indexes them in a vector store, and answers natural-language questions using a RAG (Retrieval-Augmented Generation) architecture. A user can ask something like "find me junior IT jobs" and get an answer grounded in real, current listings — including links.

Built as a learning project alongside an active job search: the goal was to build a complete full-stack + AI application (scraping → RAG pipeline → API → UI) as independently as possible, using free tools throughout.

## What the pipeline does

The app consists of two deliberately separated stages:

### 1. Scraping (run occasionally, collects the data)

`scraper.py` fetches job listings from Duunitori in two steps:

1. From the search results page (`duunitori.fi/tyopaikat?haku=...`), it extracts each listing's title, company, and link.
2. Each link is then visited individually, and the full listing text (responsibilities, requirements, company description) is fetched and cleaned into plain text (HTML tags stripped).

The result is saved to `description_data.json`. A delay (`sleep`) is added between requests to be polite to the server.

**Why the data is saved to a file instead of scraping on every run:** scraping is slow (network requests + delays) and would put unnecessary load on Duunitori if it ran every time the app was used. Scraping is therefore done once (or as an occasional refresh), and the rest of the pipeline works from the already-collected data.

### 2. RAG pipeline (indexing runs once at server startup, querying runs per request)

`rag.py` contains the full pipeline from stored data to an answer:

| Step | What happens | Runs |
|---|---|---|
| **Load** | The JSON is read and each job is converted into a LangChain `Document` (description = content, link/company/name = metadata) | Once (at server startup) |
| **Split** | Long descriptions are chunked into smaller, overlapping pieces (`RecursiveCharacterTextSplitter`) so retrieval and the LLM's context window work efficiently | Once |
| **Embed** | Each chunk is turned into a vector using a multilingual embedding model and stored in a vector store | Once |
| **Retrieve** | The user's question is embedded, and the vector store returns the most semantically similar chunks | Per question |
| **Generate** | The retrieved chunks + the question are passed to the LLM, which is instructed to answer strictly from context and never invent information | Per question |

**Key architectural decision:** indexing (load–split–embed) happens exactly once, when the FastAPI server starts — not on every question. If indexing ran on every request, each question would take seconds due to recomputing embeddings. As it stands, only retrieval and the LLM call happen per request, so responses are fast.

### 3. Backend and frontend

- **FastAPI** exposes an endpoint that accepts a user's question, runs it through the RAG chain, and returns the answer.
- **React (Vite)** frontend sends the question to the backend and displays the answer.

## Quality issues found and fixed along the way

Several RAG quality problems came up during development and were fixed — these are part of what the project demonstrates, not just the end result:

- **Language:** the default embedding model was English-biased, so Finnish-language questions failed to retrieve relevant results. Fixed by switching to a multilingual embedding model.
- **Metadata vs. content:** the LLM only sees text that is explicitly passed to it — metadata alone (link, company) isn't enough unless it's folded into the context text itself.
- **Hallucination:** without explicit instruction, the LLM filled in missing details (e.g. requirements) with plausible-sounding but invented generalizations. Fixed by instructing the prompt to answer strictly from context and mark missing information as "not mentioned."
- **Data relevance:** the search term used during scraping directly determines which domain of results end up in the vector store — filtering by criteria (e.g. experience level) belongs in retrieval, not in data collection.

## Tech stack

**Backend / RAG**
- Python
- FastAPI — web API
- LangChain — RAG pipeline orchestration
- Groq API (`llama-3.3-70b-versatile`) — LLM for answer generation
- HuggingFace `sentence-transformers` — embedding model (multilingual)
- LangChain `InMemoryVectorStore` — vector store
- `requests` + `BeautifulSoup4` — scraping
- `python-dotenv` — environment variable management

**Frontend**
- React
- Vite
- Axios — HTTP calls to the backend
- TypeScript

**Other**
- Git / GitHub — version control

The entire pipeline runs on free tools: the embedding model runs locally (no API cost), and Groq provides a free developer tier for LLM calls.

## Getting it running

### Prerequisites

- Python 3.11+
- Node.js and npm
- A free Groq API key: [console.groq.com/keys](https://console.groq.com/keys)

### 1. Clone the repo

```bash
git clone https://github.com/majim3/Rag_Project.git
cd Rag_Project
```

### 2. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt
```

Create a `backend/.env` file and add your own Groq key:

```
GROQ_API_KEY=gsk_your_key_here
```

**(Optional)** re-run the scraper to fetch fresh data:

```bash
python scraper.py
```

This creates/updates `description_data.json`. If you skip this step, the app will use the sample data already included in the repo.

Start the backend server:

```bash
uvicorn main:app --reload
```

The server starts at `http://localhost:8000`. On first startup you'll see the indexing steps run in the terminal (data load, splitting, embedding). Open `http://localhost:8000/docs` to test the API without the frontend.

### 3. Frontend

In a new terminal:

```bash
cd frontend/duunitori_front
npm install
npm run dev
```

The frontend starts at `http://localhost:5173` by default.

### 4. Try it out

Open the frontend in your browser, type a question (e.g. "junior IT jobs" or in Finnish "etsi minulle junior IT-työt") and submit. The answer will include relevant job listings with links, pulled directly from the actual Duunitori postings.

## Known limitations / future improvements

- Data only covers what the scraper collected in a single run — not continuously updated.
- Only one search term/page is scraped at a time; broader coverage would require looping over multiple search terms and pagination, plus deduplication (by link).
- The vector store is in-memory (`InMemoryVectorStore`) — it doesn't persist across server restarts. A persistent store (e.g. Chroma on disk, or pgvector) would let the index survive restarts.
