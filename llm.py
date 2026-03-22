import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# Session-based chat history: {session_id: [messages]}
chat_histories = {}

SYSTEM_PROMPT = {
    "role": "system",
    "content": """You are PersonaEngine, an AI analyst specializing in professional profiles.
You have been given context from a person's LinkedIn profile, including career history, education, skills, certifications, and recent posts/activity.

## Response Guidelines:
- **BE EXTREMELY CONCISE.** Keep answers as short as possible while answering the core question.
- Do NOT hallucinate. Only use the provided context.
- Use **bold** for names, titles, and key highlights.
- Use short bullet points instead of paragraphs.
- If information is missing, simply state: "Not available in profile."
- Do not repeat the user's question or provide unnecessary introductions.
- Limit responses to 2-3 short sentences or a brief bulleted list unless the user explicitly asks for a detailed analysis.
"""
}

QUESTION_GENERATOR_PROMPT = {
    "role": "system",
    "content": """Based on the profile context provided, generate exactly 5 interesting and insightful questions a user might want to ask about this person. 
Return ONLY a JSON array of strings, nothing else. Example: ["Question 1?", "Question 2?", "Question 3?", "Question 4?", "Question 5?"]
Make questions specific to the person's actual profile data — reference their company names, skills, or roles when possible."""
}


def ask_llm(session_id, context, question):
    if not GROQ_API_KEY:
        return "GROQ_API_KEY is missing in .env"

    history = chat_histories.get(session_id, [])

    messages = [SYSTEM_PROMPT] + history + [
        {
            "role": "user",
            "content": f"""Context from the person's profile:
{context}

User's question: {question}"""
        }
    ]

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.3,
            max_tokens=2048,
        )
        answer = response.choices[0].message.content
    except Exception as e:
        answer = f"Error: {str(e)}"

    # Store in session history
    if session_id not in chat_histories:
        chat_histories[session_id] = []
    chat_histories[session_id].append({"role": "user", "content": question})
    chat_histories[session_id].append({"role": "assistant", "content": answer})

    return answer


def generate_questions(context):
    """Generate suggested questions based on profile context."""
    if not GROQ_API_KEY:
        return []

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                QUESTION_GENERATOR_PROMPT,
                {"role": "user", "content": f"Profile context:\n{context}"}
            ],
            temperature=0.7,
            max_tokens=512,
        )
        import json
        raw = response.choices[0].message.content.strip()
        # Try to extract JSON array from the response
        if "[" in raw:
            raw = raw[raw.index("["):raw.rindex("]") + 1]
        return json.loads(raw)
    except Exception:
        return [
            "Summarize their career trajectory",
            "What are their top skills?",
            "Analyze their recent posts",
            "What companies have they worked at?",
            "What is their educational background?"
        ]


def reset_history(session_id=None):
    """Reset chat history for a session or all sessions."""
    if session_id:
        chat_histories.pop(session_id, None)
    else:
        chat_histories.clear()