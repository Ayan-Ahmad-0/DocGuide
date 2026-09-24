import time
from google.genai import errors, types
from config import LLM_MODEL, MAX_OUTPUT_TOKENS
from src.embed import _get_client
from src.retrieve import retrieve
from src.prompts import SYSTEM_PROMPT, NOT_FOUND_TOKEN, NOT_FOUND_MESSAGE, build_user_message
from src.citations import extract_citations, find_unsupported
from src.cost import llm_cost, embed_cost, estimate_tokens


def _generate(user_message: str):
    for attempt in range(5):
        try:
            return _get_client().models.generate_content(
                model=LLM_MODEL,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.0,
                    max_output_tokens=MAX_OUTPUT_TOKENS,
                ),
            )
        except errors.APIError as e:
            if e.code not in (429, 500, 503) or attempt == 4:
                raise
            wait = 15 * (attempt + 1)
            print(f"  LLM busy (HTTP {e.code}), retrying in {wait}s")
            time.sleep(wait)


def ask(question: str) -> dict:
    t0 = time.time()
    chunks = retrieve(question)
    resp = _generate(build_user_message(question, chunks))

    text = (resp.text or "").strip()
    if not text:
        raise RuntimeError("Empty response from the model. Try raising MAX_OUTPUT_TOKENS in config.py.")

    u = resp.usage_metadata
    in_tok = (u.prompt_token_count or 0) if u else 0
    # "thinking" tokens are billed as output, so count them
    out_tok = ((u.candidates_token_count or 0) + (u.thoughts_token_count or 0)) if u else 0
    q_tok = estimate_tokens(question)

    refused = text.startswith(NOT_FOUND_TOKEN)
    cites = [] if refused else extract_citations(text)
    unsupported = [] if refused else find_unsupported(cites, [c["citation"] for c in chunks])

    return {
        "question": question,
        "answer": NOT_FOUND_MESSAGE if refused else text,
        "refused": refused,
        "citations": cites,
        "unsupported_citations": unsupported,
        "uncited": (not refused) and not cites,
        "sources": chunks,
        "usage": {"input_tokens": in_tok, "output_tokens": out_tok, "query_embed_tokens_est": q_tok},
        "cost_usd": llm_cost(in_tok, out_tok) + embed_cost(q_tok),
        "latency_s": round(time.time() - t0, 2),
    }