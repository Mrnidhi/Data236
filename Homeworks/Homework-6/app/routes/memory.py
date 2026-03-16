from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Optional
from bson import ObjectId

from app.database import messages_col, summaries_col, episodes_col
from app.models import ChatRequest, ProfileUpdateReq
from app.llm import call_ollama, embed_text, cosine_similarity, extract_memory_data

router = APIRouter(prefix="/api", tags=["memory"])

SHORT_TERM_N = 10
SUMMARIZE_EVERY_USER_MSGS = 5
TOP_K_EPISODES = 3

@router.post("/chat")
def chat(req: ChatRequest):
    user_id = req.user_id
    user_msg = req.message.strip()
    session_id = req.session_id or f"sess_{datetime.utcnow().strftime('%Y%m%d')}"

    if not user_id or not user_msg:
        raise HTTPException(status_code=400, detail="user_id and message are required")

    # save user message (short-term memory)
    messages_col.insert_one({
        "user_id": user_id, "session_id": session_id,
        "role": "user", "content": user_msg,
        "created_at": datetime.utcnow()
    })

    # short-term: last N messages from this session
    short_term = list(
        messages_col.find({"user_id": user_id, "session_id": session_id})
        .sort("created_at", -1).limit(SHORT_TERM_N)
    )[::-1]

    history_text = ""
    for m in short_term:
        role = "Student" if m["role"] == "user" else "Tutor"
        history_text += f"{role}: {m['content']}\n"

    # long-term: pull lifetime + session summaries
    user_lifetime = summaries_col.find_one({"user_id": user_id, "scope": "user"})
    session_sum = summaries_col.find_one({"user_id": user_id, "session_id": session_id, "scope": "session"})

    long_term_text = f"USER PROFILE: {user_lifetime['text'] if user_lifetime else 'New student.'}\n"
    long_term_text += f"SESSION SO FAR: {session_sum['text'] if session_sum else 'Conversation starting.'}"

    # episodic: embed current message + cosine similarity against stored episodes
    query_vector = embed_text(user_msg)
    relevant_facts = []
    if query_vector:
        all_episodes = list(episodes_col.find({"user_id": user_id}))
        scored = [(cosine_similarity(query_vector, ep.get("embedding", [])), ep) for ep in all_episodes]
        scored.sort(key=lambda x: x[0], reverse=True)
        relevant_facts = [x[1]["fact"] for x in scored[:TOP_K_EPISODES] if x[0] > 0.3]

    episodic_context = "\n".join([f"- {f}" for f in relevant_facts]) if relevant_facts else "No specific related facts found."

    # compose prompt with all three memory types
    prompt = f"""You are an expert, encouraging AI study tutor with a perfect memory.

LONG-TERM CONTEXT:
{long_term_text}

EPISODIC FACTS FOUND:
{episodic_context}

RECENT CONVERSATION:
{history_text}

Tutor:"""

    response_text = call_ollama(prompt)
    if not response_text:
        raise HTTPException(status_code=500, detail="Failed to generate response from local LLM")

    # save assistant reply
    messages_col.insert_one({
        "user_id": user_id, "session_id": session_id,
        "role": "assistant", "content": response_text,
        "created_at": datetime.utcnow()
    })

    # summarization trigger: every SUMMARIZE_EVERY_USER_MSGS user messages
    user_msg_count = messages_col.count_documents({"user_id": user_id, "session_id": session_id, "role": "user"})
    if user_msg_count % SUMMARIZE_EVERY_USER_MSGS == 0:
        summary_prompt = f"Summarize this study session so far in 2-3 bullet points:\n{history_text}"
        new_session_text = call_ollama(summary_prompt)
        if new_session_text:
            summaries_col.update_one(
                {"user_id": user_id, "session_id": session_id, "scope": "session"},
                {"$set": {"text": new_session_text, "created_at": datetime.utcnow()}},
                upsert=True
            )
            # rebuild lifetime summary by condensing all session summaries
            all_session_sums = list(summaries_col.find({"user_id": user_id, "scope": "session"}))
            combined = " | ".join([s["text"] for s in all_session_sums])
            summaries_col.update_one(
                {"user_id": user_id, "scope": "user"},
                {"$set": {"text": f"Lifetime profile: {combined}", "session_id": None, "created_at": datetime.utcnow()}},
                upsert=True
            )

    # extract episodic facts + embed them for future retrieval
    extracted = extract_memory_data(user_msg, response_text)
    new_facts = []
    for field in ["topics_studied", "difficult_areas", "learning_goals"]:
        for item in extracted.get(field, []):
            if item:
                fact = f"{field}: {item}"
                new_facts.append(fact)
                fact_vector = embed_text(fact)
                episodes_col.insert_one({
                    "user_id": user_id, "session_id": session_id,
                    "fact": fact, "importance": 0.8,
                    "embedding": fact_vector,
                    "created_at": datetime.utcnow()
                })

    # immediately update lifetime user summary with new facts
    if new_facts:
        existing = summaries_col.find_one({"user_id": user_id, "scope": "user"})
        old_text = existing["text"] if existing else "New student."
        updated_text = old_text + " | " + " | ".join(new_facts)
        summaries_col.update_one(
            {"user_id": user_id, "scope": "user"},
            {"$set": {"text": updated_text, "session_id": None, "created_at": datetime.utcnow()}},
            upsert=True
        )

    return {
        "response": response_text,
        "memory_saved": extracted,
        "debug": {
            "shortTermMessagesCount": len(short_term),
            "longTermSummaryUsed": long_term_text,
            "episodicFactsRetrieved": relevant_facts
        }
    }

@router.get("/memory/{user_id}")
def get_memory(user_id: str):
    msgs = list(messages_col.find({"user_id": user_id}).sort("created_at", -1).limit(16))
    for m in msgs: m.pop("_id")

    session_sum = summaries_col.find_one({"user_id": user_id, "scope": "session"}, sort=[("created_at", -1)])
    user_sum = summaries_col.find_one({"user_id": user_id, "scope": "user"})
    if session_sum: session_sum.pop("_id")
    if user_sum: user_sum.pop("_id")

    eps = list(episodes_col.find({"user_id": user_id}).sort("created_at", -1).limit(20))
    for e in eps:
        e.pop("_id")
        e["embedding"] = e["embedding"][:5]  # truncate for display

    return {
        "messages": msgs[::-1],
        "session_summary": session_sum,
        "user_summary": user_sum,
        "episodes": eps
    }

@router.get("/aggregate/{user_id}")
def get_aggregate(user_id: str):
    # MongoDB aggregation: daily message counts grouped by date
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    daily_counts = list(messages_col.aggregate(pipeline))

    summaries = list(summaries_col.find({"user_id": user_id}).sort("created_at", -1).limit(5))
    for s in summaries: s.pop("_id")

    return {
        "daily_message_counts": daily_counts,
        "recent_summaries": summaries
    }

@router.post("/profile/update")
def update_profile(req: ProfileUpdateReq):
    user_summary = summaries_col.find_one({"user_id": req.student_id, "scope": "user"})
    if not user_summary:
        summaries_col.insert_one({
            "user_id": req.student_id, "session_id": None,
            "scope": "user", "text": f"New user. | {req.field}: {req.value}",
            "created_at": datetime.utcnow()
        })
    else:
        new_text = user_summary["text"] + f" | {req.field}: {req.value}"
        summaries_col.update_one(
            {"user_id": req.student_id, "scope": "user"},
            {"$set": {"text": new_text, "created_at": datetime.utcnow()}}
        )
    return {"success": True}

@router.get("/profile")
def get_profile(student_id: str):
    profile = summaries_col.find_one({"user_id": student_id, "scope": "user"})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    profile.pop("_id", None)
    return profile
