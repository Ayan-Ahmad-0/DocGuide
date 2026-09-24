import numpy as np
import psycopg
from psycopg.rows import dict_row
from pgvector.psycopg import register_vector
from config import DATABASE_URL, EMBED_DIM


def connect():
    conn = psycopg.connect(DATABASE_URL, autocommit=True, row_factory=dict_row)
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    register_vector(conn)
    return conn


def add_chunks(chunks: list[dict], embeddings: list[list[float]]) -> int:
    conn = connect()
    conn.execute("DROP TABLE IF EXISTS chunks")   # rebuild from scratch each time
    conn.execute(f"""
        CREATE TABLE chunks (
            chunk_id  text PRIMARY KEY,
            doc_id    text NOT NULL,
            type      text,
            number    int,
            title     text,
            chapter   text,
            citation  text NOT NULL,
            text      text NOT NULL,
            embedding vector({EMBED_DIM}) NOT NULL
        )
    """)
    rows = [
        (c["chunk_id"], c["doc_id"], c["type"], c["number"], c["title"] or "",
         c["chapter"] or "", c["citation"], c["text"],
         np.array(e, dtype=np.float32))
        for c, e in zip(chunks, embeddings)
    ]
    with conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO chunks VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", rows
        )
    # ~600 rows: an exact scan is instant and 100% accurate, so no ANN index yet.
    # At much larger scale you would add:
    #   CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops);
    n = conn.execute("SELECT count(*) AS n FROM chunks").fetchone()["n"]
    conn.close()
    return n


def search(query_vec: list[float], k: int) -> list[dict]:
    q = np.array(query_vec, dtype=np.float32)
    conn = connect()
    rows = conn.execute(
        """
        SELECT citation, doc_id, title, text, 1 - (embedding <=> %s) AS score
        FROM chunks
        ORDER BY embedding <=> %s
        LIMIT %s
        """,
        (q, q, k),
    ).fetchall()
    conn.close()
    return rows