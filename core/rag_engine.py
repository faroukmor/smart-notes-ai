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

NOT_FOUND_REPLY = "The requested information was not found in your notes."

_ollama_client = ollama.Client(host=OLLAMA_HOST)


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


def chat_function(msg):
    """Classic RAG: retrieve sources, let the AI answer ONLY from them."""
    conn = sqlite3.connect(DB_PATH)
    try:
        top_chunks = retrieve_from_db(conn, msg)
    finally:
        conn.close()

    if not top_chunks:
        return NOT_FOUND_REPLY

    # The embedding search results are the ONLY allowed sources.
    sources = "\n\n".join([chunk[1] for chunk in top_chunks])

    system_prompt = f"""You are an assistant. These sources below are the ONLY
thing you are allowed to answer from.

Rules:
- Answer the user's question in your own words, based strictly on the sources.
- Do NOT use any knowledge outside the sources.
- If the sources do not contain the answer, reply with exactly:
  The requested information was not found in your notes.

======================
{sources}
======================"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": msg},
    ]

    response = _ollama_client.chat(
        model=LLM_MODEL,
        messages=messages,
        options={
            "temperature": TEMPERATURE,
            "num_predict": NUM_PREDICT,
            "repeat_penalty": REPEAT_PENALTY,
        },
    )

    return response["message"]["content"].strip()
