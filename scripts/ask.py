import sys
from src.answer import ask

sys.stdout.reconfigure(encoding="utf-8")

DEMO = [
    "What are the maximum fines for infringements?",
    "How long can personal data be stored?",
    "Does a company need my consent to send me marketing emails?",
    "What is the penalty for violating the CCPA?",   # out of scope: should be refused
    "Who won the 2022 World Cup?",                    # out of scope: should be refused
]


def show(r):
    print("=" * 78)
    print("Q:", r["question"])
    print("\nA:", r["answer"])
    if r["citations"]:
        print("\nCited:", ", ".join(dict.fromkeys(r["citations"])))
    if r["unsupported_citations"]:
        print("!! UNSUPPORTED CITATIONS:", r["unsupported_citations"])
    if r["uncited"]:
        print("!! ANSWER HAS NO CITATIONS")
    print("\nRetrieved:", ", ".join(s["citation"] for s in r["sources"]))
    u = r["usage"]
    print(f"Tokens in/out: {u['input_tokens']}/{u['output_tokens']} | "
          f"cost ${r['cost_usd']:.5f} | {r['latency_s']}s")


if __name__ == "__main__":
    for q in (sys.argv[1:] or DEMO):
        show(ask(q))