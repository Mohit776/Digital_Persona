from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

embedding = HuggingFaceEmbeddings()

# Session-based storage: {session_id: Chroma instance}
sessions = {}

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", ". ", ", ", " ", ""]
)

def create_db(session_id, text):
    """Create a vector DB for a session from raw text."""
    if not text:
        return
    chunks = text_splitter.split_text(text)
    if not chunks:
        return
    sessions[session_id] = Chroma.from_texts(chunks, embedding)

def query_db(session_id, query, k=5):
    """Query the vector DB for a session."""
    db = sessions.get(session_id)
    if db is None:
        return []
    return db.similarity_search(query, k=k)

def reset_db(session_id=None):
    """Reset a specific session or all sessions."""
    if session_id:
        sessions.pop(session_id, None)
    else:
        sessions.clear()