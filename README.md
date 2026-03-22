# PersonaEngine

PersonaEngine is an AI-powered professional analysis tool that allows users to explore any professional's digital footprint using their LinkedIn profile. It scrapes the profile, indexes the data using a Retrieval-Augmented Generation (RAG) system, and provides an interactive chatbot interface for users to ask questions about the person's career, skills, and posts.

## Features
- **Profile Analysis:** Extracts work experience, education, skills, certifications, and recent posts from LinkedIn.
- **RAG-Powered Chat:** Uses a local Chroma vector database and `RecursiveCharacterTextSplitter` to provide accurate, context-aware answers.
- **AI Suggested Questions:** Automatically generates relevant questions based on the analyzed profile.
- **Modern UI:** A clean, responsive, light-themed interface built with vanilla HTML/CSS/JS (powered by Stitch design system).
- **Session Management:** UUID-based sessions allow multiple concurrent users without overlapping chat histories or vector databases.

## Local Setup

### Prerequisites
- Python 3.9+
- A valid [Groq API Key](https://console.groq.com/) for the LLM
- A valid [LinkdAPI Key](https://linkdapi.com/) for LinkedIn scraping

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Mohit776/Digital_Persona.git
   cd Digital_Persona
   ```

2. **Create a Virtual Environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Create a `.env` file in the root directory and add your API keys:
   ```env
   LINKD_API_KEY=your_linkdapi_key_here
   GROQ_API_KEY=your_groq_api_key_here
   ```

### Running the Application

Start the FastAPI server using Uvicorn:
```bash
uvicorn main:app --reload
```

The application will be available at `http://127.0.0.1:8000`.

## Architecture Highlights
- **Backend Framework:** FastAPI
- **LLM Integration:** Groq (Llama-3.1-8b-instant) via LangChain
- **Vector Store:** ChromaDB (in-memory, session-keyed)
- **Embeddings:** HuggingFace (`all-mpnet-base-v2`)
- **Frontend:** Vanilla HTML/JS with Marked.js for markdown rendering

## Error Handling
The application includes basic guards to ensure robustness:
- **Invalid URLs:** Checks specifically for valid LinkedIn URLs containing `/in/username`.
- **Private Profiles/Not Found (404):** Caught during scraping and returned cleanly to the frontend.
- **Rate Limits (429):** Handled gracefully if the scraping API limit is exceeded. 
