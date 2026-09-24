from config import LLM_PRICE_IN, LLM_PRICE_OUT, EMBED_PRICE_IN


def llm_cost(input_tokens: int, output_tokens: int) -> float:
    return input_tokens / 1e6 * LLM_PRICE_IN + output_tokens / 1e6 * LLM_PRICE_OUT


def embed_cost(tokens: int) -> float:
    return tokens / 1e6 * EMBED_PRICE_IN


def estimate_tokens(text: str) -> int:
    return int(len(text.split()) * 1.4) + 1   # rough; only used for the tiny query-embedding cost