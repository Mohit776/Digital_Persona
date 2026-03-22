# PersonaEngine: Architecture & Design Write-up

## Overview
PersonaEngine was designed as a lightweight, highly responsive Retrieval-Augmented Generation (RAG) system wrapped in an intuitive, consumer-grade user interface. The primary goal was to transform raw LinkedIn profile data into an interactive, conversational experience seamlessly and quickly.

## Architecture

The system follows a classic decoupled client-server architecture, simplified for ease of deployment:

1. **Frontend (Vanilla HTML/CSS/JS):**
   - Served statically by FastAPI to keep the deployment footprint minimal without requiring a separate Node.js server.
   - Built with a modern, light-theme design system ("Persona Indigo").
   - Utilizes `marked.js` to render rich markdown responses (tables, bold text, lists) directly from the LLM.

2. **Backend Engine (FastAPI):**
   - **Session Management:** A UUID is generated upon analysis to key both the ChromaDB instance and the LLM chat history. This makes the backend strictly stateless from an HTTP perspective but maintains state in-memory per user session.
   - **LLM Orchestration:** Built heavily on LangChain, utilizing Groq (`llama-3.1-8b-instant`) for ultra-low latency inference, crucial for a snappy chat experience.

3. **Data Pipeline (Scraping & RAG):**
   - **Data Extraction:** Handled by `scraper.py` using LinkdAPI to fetch the URN, full profile payload, and recent posts.
   - **Formatting:** `formatter.py` aggressively flattens the complex JSON tree (experience, education, certifications, engagement metrics) into a highly structured markdown string.
   - **Chunking:** Handled by `RecursiveCharacterTextSplitter` (chunk size: 500, overlap: 50) in `rag.py`. This ensures contextual integrity compared to naive string splitting.
   - **Vector Store:** HuggingFace embeddings (`all-mpnet-base-v2`) embedded into an ephemeral, in-memory ChromaDB instance. 

## Design Decisions

### 1. In-Memory, Session-Based State
Instead of integrating PostgreSQL or Redis for state, we opted for purely in-memory dictionaries keyed by `session_id`.
* **Why:** Speed and simplicity. Persona analysis is fundamentally an ephemeral task. Storing vectors permanently for every searched profile would balloon costs and storage without providing recurring value, as LinkedIn data goes stale fast.

### 2. Groq for Inference
* **Why:** The primary bottleneck of any RAG system is Generation time. By using Groq's LPU architecture, text streams fast enough to negate the need for complex WebSocket streaming architectures on the frontend. The entire answer resolves fast enough via standard HTTP POST.

### 3. "AI Suggested Questions" Pre-computation
* **Why:** Friction reduction. Users often don't know what to ask when shown a blank chat box. By passing the first 2000 characters of the formatted profile back to the LLM *during* the initial analysis phase, we generate tailored prompts (e.g., "Ask Mohit about his time at Lakshmi IT"). This significantly boosts user engagement.

## Data Extraction Handling

Extracting data from LinkedIn is notoriously difficult due to dynamic rendering and aggressive anti-bot measures. 

**Handling Strategy:**
1. **API Abstraction:** We offloaded the heavy lifting to `LinkdAPI`, which acts as a reliable proxy.
2. **Multi-step Retrieval:** The scraper translates the public URL username into a proprietary `URN`, fetches the structured JSON profile, and then does a secondary fetch for `posts/activity` using the URN.
3. **Resiliency & Guards:**
   - **URL Parsing:** Strict string validation ensures we only attempt to fetch if `/in/username` is present, stripping query parameters `?`.
   - **Private/Not Found (404):** Handled proactively. If a profile hides public visibility, it raises a clean exception rather than crashing the parsing logic.
   - **Rate Limiting (429):** Handled upstream in `_make_request` to prevent retry cascades that could result in API bans.
   - **Robust JSON Traversing:** `formatter.py` exclusively relies on `.get(key, default)` ensuring missing keys (e.g., missing certifications or post counts) never throw `KeyError`.
