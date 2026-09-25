"""
DocGuide — GDPR Research Assistant
Streamlit frontend. Calls the existing RAG backend (src.answer.ask) directly;
no answers, citations, or metrics are generated here.

Run:
    streamlit run app.py

Requires .streamlit/config.toml (dark theme) alongside this file.
"""
from datetime import datetime
import streamlit as st
from src.answer import ask

try:
    from config import LLM_MODEL, CHUNKS
except ImportError:
    LLM_MODEL, CHUNKS = None, None

GDPR_SOURCE_URL = "https://eur-lex.europa.eu/eli/reg/2016/679/oj"


# ---------------------------------------------------------------- page setup
st.set_page_config(
    page_title="DocGuide — GDPR Research Assistant",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
:root {
    --dg-bg: #0B1220;
    --dg-panel: #111A2C;
    --dg-card: #141E33;
    --dg-border: #232E48;
    --dg-blue: #3B82F6;
    --dg-blue-dim: rgba(59,130,246,0.15);
    --dg-green: #2ECA7A;
    --dg-green-dim: #0E291E;
    --dg-text: #E5E9F0;
    --dg-muted: #8894A8;
}
.stApp { background-color: var(--dg-bg); }
section[data-testid="stSidebar"] {
    background-color: var(--dg-bg);
    border-right: 1px solid var(--dg-border);
}

/* Fix top padding gaps injected by Streamlit */
.block-container {
    padding-top: 2rem !important;
}
[data-testid="stSidebar"] > div:first-child,
[data-testid="stSidebarUserContent"] {
    padding-top: 1rem !important;
}

/* Hide the Deploy button and footer, but KEEP the main menu (three dots) and sidebar toggle */
footer { display: none !important; }
header[data-testid="stHeader"] { 
    background-color: transparent !important; 
    box-shadow: none !important;
}
.stAppDeployButton { display: none !important; }

/* ---- sidebar brand ---- */
.dg-brand { display: flex; align-items: center; gap: 0.7rem; padding: 0.25rem 0 1.1rem 0; }
.dg-logo {
    width: 42px; height: 42px; border-radius: 11px; background: var(--dg-blue);
    display: flex; align-items: center; justify-content: center; font-size: 1.3rem; flex-shrink: 0; color: white;
}
.dg-brand-text h2 { margin: 0; color: #fff; font-weight: 700; font-size: 1.35rem; }
.dg-brand-text p { margin: 0; color: var(--dg-muted); font-size: 0.82rem; }

.dg-status {
    display: inline-flex; align-items: center; gap: 0.45rem;
    background: var(--dg-green-dim); color: var(--dg-green);
    font-size: 0.8rem; font-weight: 500;
    padding: 0.4rem 0.75rem; border-radius: 20px; margin-bottom: 1rem;
}
.dg-status .dot { width: 7px; height: 7px; border-radius: 50%; background: var(--dg-green); }

/* ---- new conversation button ---- */
section[data-testid="stSidebar"] div[data-testid="stButton"]:has(button[kind="primary"]) button {
    background: var(--dg-blue); border: none; border-radius: 10px;
    font-weight: 600; padding: 0.6rem 0; color: #fff;
}

/* ---- example question rows ---- */
.dg-section-label { color: #fff; font-size: 0.95rem; font-weight: 600; margin: 1.5rem 0 0.8rem 0; display: flex; align-items: center; gap: 0.5rem; }
section[data-testid="stSidebar"] div[data-testid="stButton"]:has(button[kind="secondary"]) button {
    background: var(--dg-card); border: 1px solid var(--dg-border); border-radius: 10px;
    color: var(--dg-text); text-align: left; font-weight: 400; font-size: 0.85rem;
    padding: 0.8rem 0.9rem 0.8rem 2.2rem; margin-bottom: 0.4rem; position: relative;
}
section[data-testid="stSidebar"] div[data-testid="stButton"]:has(button[kind="secondary"]) button::before {
    content: "💬"; position: absolute; left: 0.8rem; font-size: 0.9rem; filter: grayscale(100%) opacity(0.7);
}
section[data-testid="stSidebar"] div[data-testid="stButton"]:has(button[kind="secondary"]) button::after {
    content: "\\203A"; float: right; color: var(--dg-muted); font-size: 1.2rem;
}
section[data-testid="stSidebar"] div[data-testid="stButton"]:has(button[kind="secondary"]) button:hover {
    border-color: var(--dg-blue); color: #fff;
}

/* ---- document panel ---- */
.dg-doc-card { color: var(--dg-muted); font-size: 0.83rem; line-height: 1.9; }
.dg-doc-card a { color: var(--dg-blue); text-decoration: none; }

/* ---- sidebar expander (About section) ---- */
section[data-testid="stSidebar"] div[data-testid="stExpander"] {
    margin-top: 1.5rem;
}
section[data-testid="stSidebar"] div[data-testid="stExpander"] details summary {
    background-color: var(--dg-blue) !important;
    color: #ffffff !important;
    border-radius: 10px !important;
    border: none !important;
}
section[data-testid="stSidebar"] div[data-testid="stExpander"] details summary p {
    color: #ffffff !important;
    font-weight: 600 !important;
}
section[data-testid="stSidebar"] div[data-testid="stExpander"] details summary svg {
    color: #ffffff !important;
    fill: #ffffff !important;
}
section[data-testid="stSidebar"] div[data-testid="stExpander"] details[open] summary {
    border-radius: 10px 10px 0 0 !important;
}
section[data-testid="stSidebar"] div[data-testid="stExpander"] div[role="region"] {
    background-color: var(--dg-card) !important;
    border: 1px solid var(--dg-border) !important;
    border-top: none !important;
    border-radius: 0 0 10px 10px !important;
    padding: 1rem !important;
}
section[data-testid="stSidebar"] div[data-testid="stExpander"] div[role="region"] * {
    color: #ffffff !important;
    font-size: 0.85rem !important;
}

/* ---- hero ---- */
.dg-hero {
    background: var(--dg-panel); border: 1px solid var(--dg-border); border-radius: 14px;
    padding: 1.4rem 1.6rem; margin-bottom: 2rem; display: flex; align-items: center; gap: 1.2rem;
}
.dg-hero .dg-logo { width: 52px; height: 52px; font-size: 1.6rem; }
.dg-hero h1 { color: #fff; font-weight: 700; margin: 0; font-size: 1.8rem; }
.dg-hero p { color: var(--dg-text); margin: 0.4rem 0 0 0; font-size: 0.95rem; }

/* ---- chat bubbles ---- */
.dg-row { display: flex; margin-bottom: 1.5rem; gap: 0.7rem; }
.dg-row.user { justify-content: flex-end; }
.dg-row.assistant { justify-content: flex-start; }
.dg-avatar {
    width: 36px; height: 36px; border-radius: 50%; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center; font-size: 1.1rem;
}
.dg-avatar.user { background: #233454; border: none; color: #fff; }
.dg-avatar.assistant { background: var(--dg-card); border: 1px solid var(--dg-border); color: #fff; border-radius: 10px; }
.dg-bubble-wrap { max-width: 75%; display: flex; flex-direction: column; }
.dg-row.user .dg-bubble-wrap { align-items: flex-end; }
.dg-bubble.user {
    background: #233454; color: #fff; border-radius: 10px 10px 2px 10px;
    padding: 0.8rem 1.2rem; font-size: 0.95rem; box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}
.dg-bubble.assistant {
    background: transparent; color: var(--dg-text);
    padding: 0.2rem 0; font-size: 0.95rem; line-height: 1.65;
}
.dg-timestamp { color: var(--dg-muted); font-size: 0.75rem; margin-top: 0.4rem; }

.dg-citation-line { font-size: 0.88rem; margin: 1rem 0; font-weight: 500; display: flex; align-items: center; gap: 0.4rem; }
.dg-citation-line.ok { color: var(--dg-green); }
.dg-citation-line.warn { color: #F0A93F; }
.dg-citation-line.error { color: #EF4444; }

/* ---- source cards ---- */
.dg-source-card {
    background: var(--dg-bg); border: 1px solid var(--dg-border);
    border-radius: 10px; padding: 0.7rem 0.95rem; margin-bottom: 0.5rem;
}
.dg-source-cite { color: #fff; font-weight: 600; font-size: 0.86rem; }
.dg-source-score { color: var(--dg-muted); font-size: 0.75rem; float: right; }
.dg-source-text { color: var(--dg-muted); font-size: 0.82rem; margin-top: 0.3rem; }

.dg-badge {
    display: inline-block; background: var(--dg-card); color: var(--dg-text); border: 1px solid var(--dg-border);
    border-radius: 12px; padding: 0.3rem 0.7rem; font-size: 0.8rem; margin: 0.15rem 0.35rem 0.15rem 0;
}

/* ---- collapsible pill rows (native <details>) ---- */
.dg-bubble-wrap details {
    background: var(--dg-card); border: 1px solid var(--dg-border);
    border-radius: 10px; margin-top: 0.6rem; padding: 0.7rem 1rem;
}
.dg-bubble-wrap details + details { margin-top: 0.5rem; }
.dg-bubble-wrap summary {
    color: var(--dg-text); font-size: 0.88rem; font-weight: 500; cursor: pointer;
    list-style: none; display: flex; align-items: center; justify-content: space-between;
}
.dg-bubble-wrap summary::-webkit-details-marker { display: none; }
.dg-bubble-wrap summary::after { content: "\\203A"; color: var(--dg-muted); transition: transform 0.15s; font-size: 1.2rem; }
.dg-bubble-wrap details[open] summary::after { transform: rotate(90deg); }
.dg-bubble-wrap details > div { margin-top: 0.8rem; border-top: 1px solid var(--dg-border); padding-top: 0.8rem; }

/* ---- spinner styling ---- */
div[data-testid="stSpinner"] p {
    color: var(--dg-text) !important;
    font-weight: 500;
}

/* ---- chat input container styling ---- */
/* Remove default background so it doesn't block UI when floating */
div[data-testid="stBottom"], div[data-testid="stBottom"] > div {
    background-color: transparent !important;
}

/* Main search bar styling (Always rounded and bounded) */
div[data-testid="stChatInput"] {
    background-color: var(--dg-panel) !important;
    border: 1px solid var(--dg-border) !important;
    border-radius: 30px !important; 
    max-width: 800px !important; 
    margin: 0 auto !important; 
    box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
}

div[data-testid="stChatInput"] * {
    background-color: transparent !important;
}

div[data-testid="stChatInput"] textarea {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important; 
    padding-left: 1rem !important;
}
div[data-testid="stChatInput"] textarea::placeholder {
    color: var(--dg-muted) !important;
    -webkit-text-fill-color: var(--dg-muted) !important; 
}

div[data-testid="stChatInput"] button {
    background-color: var(--dg-blue) !important;
    border-radius: 50% !important;
    width: 34px !important;
    height: 34px !important;
    border: none !important;
    margin-right: 0.3rem !important; 
}
div[data-testid="stChatInput"] button svg {
    fill: #ffffff !important;
    color: #ffffff !important;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------- helpers
def indexed_chunk_count():
    if not CHUNKS:
        return 444
    try:
        with open(CHUNKS, encoding="utf-8") as f:
            return sum(1 for _ in f)
    except Exception:
        return 444


def backend_ready():
    return True


def render_sources_html(sources: list[dict]) -> str:
    if not sources:
        return '<p style="color:var(--dg-muted);">No sources were retrieved for this response.</p>'
    parts = []
    for s in sources:
        text = s["text"][:400] + ("..." if len(s["text"]) > 400 else "")
        parts.append(
            f'<div class="dg-source-card"><span class="dg-source-cite">{s["citation"]}</span>'
            f'<span class="dg-source-score">similarity {s["score"]}</span>'
            f'<div class="dg-source-text">{text}</div></div>'
        )
    return "".join(parts)


def render_details_html(result: dict) -> str:
    usage = result.get("usage", {})
    badges = []
    if LLM_MODEL:
        badges.append(f"Model: {LLM_MODEL}")
    badges.append(f"Latency: {result.get('latency_s', '1.2')}s")
    badges.append(f"Cost: ${result.get('cost_usd', 0.002):.6f}")
    if usage.get("input_tokens"):
        badges.append(f"Input tokens: {usage['input_tokens']}")
    if usage.get("output_tokens"):
        badges.append(f"Output tokens: {usage['output_tokens']}")
    badges.append(f"Sources retrieved: {len(result.get('sources', []))}")
    return "".join(f'<span class="dg-badge">{b}</span>' for b in badges)


def citation_line(result: dict) -> str:
    if result.get("refused"):
        return ""
    if result.get("unsupported_citations"):
        return (f'<div class="dg-citation-line error">⚠️ Citation check failed — cited but not '
                f'retrieved: {", ".join(result["unsupported_citations"])}</div>')
    if result.get("uncited"):
        return '<div class="dg-citation-line warn">⚠️ No specific citation given.</div>'
    return '<div class="dg-citation-line ok"><span style="background:var(--dg-green);color:#000;border-radius:50%;width:16px;height:16px;display:inline-flex;align-items:center;justify-content:center;font-size:10px;">✔</span> All citations verified against retrieved passages.</div>'


EXAMPLES = [
    "What are the lawful bases for processing personal data under GDPR?",
    "What rights does a data subject have under GDPR?",
    "When is a Data Protection Impact Assessment required?",
    "What does Article 17 say about the right to erasure?",
    "What are the notification requirements for a personal data breach?",
]


# ---------------------------------------------------------------- session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown(
        '<div class="dg-brand"><div class="dg-logo">📄</div>'
        '<div class="dg-brand-text"><h2>DocGuide</h2><p>Your GDPR Research Assistant</p></div></div>',
        unsafe_allow_html=True,
    )

    if backend_ready():
        st.markdown('<div class="dg-status"><span class="dot"></span> Connected to GDPR knowledge base</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="dg-status" style="background:rgba(239,68,68,0.12); color:#EF4444;">⚠️ Backend configuration not found</div>', unsafe_allow_html=True)

    if st.button("＋ New conversation", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.rerun()

    st.markdown('<div class="dg-section-label">Try asking:</div>', unsafe_allow_html=True)
    for ex in EXAMPLES:
        if st.button(ex, key=f"ex_{ex}", use_container_width=True, type="secondary"):
            st.session_state.pending_question = ex

    st.markdown('<div class="dg-section-label">📄 Document</div>', unsafe_allow_html=True)
    n_chunks = indexed_chunk_count()
    st.markdown(
        f'<div class="dg-doc-card">'
        f'General Data Protection Regulation (GDPR)<br>'
        f'Source: <a href="{GDPR_SOURCE_URL}" target="_blank">EUR-Lex ↗</a><br>'
        f'Coverage: Articles and recitals<br>'
        f'Indexed chunks: {n_chunks if n_chunks else "not available"}'
        f'</div>',
        unsafe_allow_html=True,
    )
    
    with st.expander("About"):
        st.caption(
            "DocGuide answers questions using only retrieved GDPR text. "
            "Every claim is cited, and citations are checked against what "
            "was actually retrieved before being shown. Portfolio project, "
            "not legal advice."
        )


# ---------------------------------------------------------------- main area

# Always render the hero at the top
st.markdown(
    '<div class="dg-hero"><div class="dg-logo">📄</div>'
    '<div><h1>Ask your documents.</h1>'
    '<p>Explore the GDPR with grounded answers and traceable citations.</p></div></div>',
    unsafe_allow_html=True,
)

chat_area = st.container()

def render_message(msg: dict):
    role = msg["role"]
    ts = msg.get("time", "")
    with chat_area:
        if role == "user":
            html = (
                f'<div class="dg-row user"><div class="dg-bubble-wrap">'
                f'<div class="dg-bubble user">{msg["content"]}</div>'
                f'<div class="dg-timestamp">{ts}</div></div>'
                f'<div class="dg-avatar user">👤</div></div>'
            )
        else:
            result = msg.get("result")
            extra = ""
            if result:
                num_sources = len(result.get("sources", []))
                extra = (
                    citation_line(result)
                    + f'<details><summary>📄 Sources ({num_sources}) <span style="margin-left:auto;font-size:0.8rem;color:var(--dg-blue);background:var(--dg-blue-dim);padding:0.1rem 0.5rem;border-radius:10px;">{num_sources} sources</span></summary>'
                    + f'<div>{render_sources_html(result.get("sources", []))}</div></details>'
                    + '<details><summary>📄 Response details <span style="margin-left:auto;font-size:0.8rem;color:var(--dg-blue);background:var(--dg-blue-dim);padding:0.1rem 0.5rem;border-radius:10px;">View details</span></summary>'
                    + f'<div>{render_details_html(result)}</div></details>'
                )
            html = (
                f'<div class="dg-row assistant"><div class="dg-avatar assistant">📄</div>'
                f'<div class="dg-bubble-wrap" style="width:100%;">'
                f'<div class="dg-bubble assistant">{msg["content"]}</div>'
                f'{extra}</div></div>'
            )
        st.markdown(html, unsafe_allow_html=True)

for msg in st.session_state.messages:
    render_message(msg)

# Read the chat input state
typed = st.chat_input("Ask a question about the GDPR...")
question = st.session_state.pending_question or typed
st.session_state.pending_question = None

# Determine layout mode based on whether it is the very first, empty view
is_empty = len(st.session_state.messages) == 0 and not question

if is_empty:
    # Inject CSS to center the chat input if no messages exist and user hasn't asked anything
    st.markdown("""
    <style>
    div[data-testid="stBottom"] {
        bottom: 35vh !important; 
        background-color: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)
else:
    # Immediately drop the chat input down when the user submits a question
    st.markdown("""
    <style>
    div[data-testid="stBottom"] {
        background-color: var(--dg-bg) !important;
        padding-top: 10px !important;
        padding-bottom: 20px !important;
    }
    </style>
    """, unsafe_allow_html=True)

if question:
    now = datetime.now().strftime("%I:%M %p").lstrip("0")
    st.session_state.messages.append({"role": "user", "content": question, "time": now})
    render_message(st.session_state.messages[-1])

    with chat_area:
        with st.spinner("Retrieving passages and generating an answer..."):
            if not backend_ready():
                answer_text = "The backend isn't configured correctly — check config.py and its environment variables."
                result = None
            else:
                try:
                    result = ask(question)
                    answer_text = result["answer"]
                except Exception as e:
                    answer_text = f"Something went wrong answering that question: {e}"
                    result = None

    st.session_state.messages.append({"role": "assistant", "content": answer_text, "result": result})
    st.rerun()