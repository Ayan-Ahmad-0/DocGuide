import sys
from google import genai
from google.genai import errors, types
from config import EMBED_MODEL, EMBED_DIM

sys.stdout.reconfigure(encoding="utf-8")

client = genai.Client()   # reads GEMINI_API_KEY from .env
try:
    r = client.models.embed_content(
        model=EMBED_MODEL,
        contents=["test sentence"],
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT", output_dimensionality=EMBED_DIM
        ),
    )
    print("OK, vector length:", len(r.embeddings[0].values))
except errors.APIError as e:
    print("HTTP code:", e.code)
    print("status:", getattr(e, "status", None))
    print("message:", e.message)
    print("details:", getattr(e, "details", None))