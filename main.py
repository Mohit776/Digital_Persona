import uuid
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from scraper import fetch_profile
from formatter import format_profile
from rag import create_db, query_db, reset_db
from llm import ask_llm, reset_history, generate_questions
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="PersonaEngine API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store formatted text per session for question generation
session_texts = {}


class AnalyzeRequest(BaseModel):
    url: str

class ChatRequest(BaseModel):
    query: str
    session_id: str

class SuggestRequest(BaseModel):
    session_id: str


# Serve the frontend
@app.get("/")
async def root():
    return FileResponse("index.html")


@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    try:
        session_id = str(uuid.uuid4())

        # 1. Fetch profile data
        raw_data = fetch_profile(req.url)

        # 2. Format into structured text
        formatted_text = format_profile(raw_data)

        # 3. Index into vector DB
        create_db(session_id, formatted_text)

        # Store text for question generation
        session_texts[session_id] = formatted_text

        profile = raw_data.get("profile", {})

        # 4. Generate suggested questions
        questions = generate_questions(formatted_text[:2000])

        return {
            "status": "success",
            "message": "Profile analyzed and indexed",
            "session_id": session_id,
            "suggested_questions": questions,
            "data": {
                "name": f"{profile.get('firstName', '')} {profile.get('lastName', '')}".strip(),
                "headline": profile.get("headline", ""),
                "summary": profile.get("summary", ""),
                "profilePicture": profile.get("profilePicture", ""),
                "followerCount": profile.get("followerCount", 0),
                "connectionsCount": profile.get("connectionsCount", 0),
                "location": profile.get("locationName", "") or profile.get("geoLocationName", ""),
                "industry": profile.get("industryName", "") or profile.get("industry", ""),
                "urn": raw_data.get("urn"),
                "username": raw_data.get("username"),
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        docs = query_db(req.session_id, req.query)
        context = "\n".join([d.page_content for d in docs])

        answer = ask_llm(req.session_id, context, req.query)

        return {
            "status": "success",
            "answer": answer,
            "context_used": len(docs) > 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/suggest")
async def suggest(req: SuggestRequest):
    """Generate new suggested questions for the session."""
    try:
        text = session_texts.get(req.session_id, "")
        questions = generate_questions(text[:2000])
        return {"status": "success", "questions": questions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reset")
async def reset():
    reset_db()
    reset_history()
    session_texts.clear()
    return {"status": "success", "message": "Session reset"}


@app.get("/health")
async def health():
    return {"status": "healthy"}