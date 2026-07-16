import json
import sqlite3
import urllib
import numpy as np
import ollama

MODEL_NAME = 'qwen2.5:3b'

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

    results  = []
    for text, embedding in knowledge_base:
        similarity = cosine_similarity(query_embed, embedding)

        if similarity > 0.60:
            results.append((similarity, text))
        
    results = sorted(results, reverse=True)
    
    return results[:3]


def get_embedding(text):
    url = "http://localhost:11434/api/embeddings"
    data = json.dumps({"model": "nomic-embed-text", "prompt": text}).encode('utf-8')

    try:
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
    
            embedding = result["embedding"]
            
            return np.array(embedding)
            
    except Exception as e:
        print(f"(get_embedding) Error: {e}")


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

    conn = sqlite3.connect("notes_manager.db")

    top_chunks = retrieve_from_db(conn, msg)
    if not top_chunks:
        conn.close()
        return "البيانات غير موجودة في المذكرات الخاصة بك"
    context = "\n\n".join([chunk[1] for chunk in top_chunks])

    system_prompt = f"""
                    أنت مساعد يعتمد فقط على النص التالي.

                    إذا لم تجد الإجابة داخله فاكتب:

                    لا أعرف.

                    لا تضف أي معلومة من معرفتك.

                    ======================

                    {context}

                    ======================
                    """

    messages = [
    {"role":"system","content":system_prompt},
    {"role":"user","content":msg}
]
    
    response = ollama.chat(
    model=MODEL_NAME,
    messages=messages,
    options={
        "temperature": 0,
        "num_predict": 1024
    }
)
    
    conn.close()
    return response["message"]["content"]
