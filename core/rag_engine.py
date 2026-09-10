import json
import sqlite3
import numpy as np
import ollama

from core.config import (
    DB_PATH,
    EMBED_MODEL,
    LLM_MODEL,
    OLLAMA_HOST,
    SIMILARITY_THRESHOLD,
    TOP_K,
    TEMPERATURE,
    NUM_PREDICT,
    REPEAT_PENALTY,
)

_ollama_client = ollama.Client(host=OLLAMA_HOST)


def content_embeding(conn):
    cur = conn.cursor()
    cur.execute("Select id,content from notes where embedding is NULL")
    chunks = cur.fetchall()

    for chunk in chunks:
        embedding = get_embedding(chunk[1])
        if embedding is None: continue
        embedding = json.dumps(embedding.tolist())
        cur.execute("UPDATE notes set embedding = ? where id = ?", (embedding,chunk[0]))
    print("content emmbeding done")
    conn.commit()

def cosine_similarity(v1, v2):
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)

    if norm1 == 0 or norm2 == 0:
        return 0

    dot_product = np.dot(v1, v2)
    return dot_product / (norm1 * norm2)


def get_top_chunks(user_input, knowledge_base):
    query_embed = get_embedding(user_input)

    if query_embed is None:
        raise RuntimeError(
            f"Could not get an embedding from Ollama "
            f"(host={OLLAMA_HOST}, model={EMBED_MODEL}). "
            "Make sure Ollama is running and the model is pulled."
        )

    results  = []
    for text, embedding in knowledge_base:
        similarity = cosine_similarity(query_embed, embedding)

        if similarity > SIMILARITY_THRESHOLD:
            results.append((similarity, text))

    results = sorted(results, reverse=True)

    return results[:TOP_K]


def get_embedding(text):
    try:
        result = _ollama_client.embeddings(
            model=EMBED_MODEL,
            prompt=text,
        )
        return np.array(result["embedding"])
    except Exception as e:
        print(f"(get_embedding) Error: {e}")
        return None


def retrieve_from_db(conn, user_input):
    cur = conn.cursor()
    cur.execute("SELECT content,embedding FROM notes")
    rows = cur.fetchall()
    knowledge_base = []
    for text, embedding_json in rows:
        if not embedding_json: continue
        embedding_array = np.array(json.loads(embedding_json))
        knowledge_base.append((text, embedding_array))

    top_chunks = get_top_chunks(user_input, knowledge_base)
    return top_chunks


NOT_FOUND_REPLY = "The requested information was not found in your notes."


def chat_function(msg):
    """Answer strictly from the user's notes.

    Anti-hallucination by construction: instead of letting the model
    generate an answer (small models paraphrase/invent), we ask it only
    to CLASSIFY which note answers the question. The returned text is
    then the stored note itself, so nothing can be invented.
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        top_chunks = retrieve_from_db(conn, msg)
    finally:
        conn.close()

    if not top_chunks:
        return NOT_FOUND_REPLY

    notes_section = ""
    for i, (_score, text) in enumerate(top_chunks, start=1):
        notes_section += f"[{i}] {text}\n\n"

    system_prompt = f"""You are a strict classifier. The user asks a question
and you have numbered notes below.

Task: reply with ONLY the number (e.g. 1, 2 or 3) of the single note that
actually contains the answer to the question.

Rules:
- Reply with the number only, nothing else.
- If NO note contains the answer, reply with exactly: NONE
- Never guess. If unsure, reply NONE.

======================
{notes_section}======================"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": msg},
    ]

    response = _ollama_client.chat(
        model=LLM_MODEL,
        messages=messages,
        options={
            "temperature": TEMPERATURE,
            "num_predict": 16,
        },
    )

    reply = response["message"]["content"].strip()

    # Parse the classifier's choice deterministically.
    digits = "".join(ch for ch in reply if ch.isdigit())
    if digits:
        index = int(digits) - 1
        if 0 <= index < len(top_chunks):
            return top_chunks[index][1]

    return NOT_FOUND_REPLY
