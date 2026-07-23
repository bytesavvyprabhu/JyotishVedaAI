"""
ask.py — JyotishVedaAI RAG pipeline (retrieval + generation)

The 5 RAG steps, mapped in code:
  1. Embed the question            -> Chroma does this internally on query
  2. Similarity search             -> collection.query(...)
  3. Metadata filter by chart      -> where={...} + chart-aware queries
  4. Augment (build the prompt)    -> build_prompt()
  5. Generate                      -> Groq Llama call

pip install chromadb sentence-transformers groq
export GROQ_API_KEY=...   (free key from console.groq.com)
"""
import os
from collections import defaultdict

import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

DB_DIR = "chroma_db"
COLLECTION = "jyotish_veda_ai"
EMBED_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "llama-3.3-70b-versatile"

# ---- Question topic routing -------------------------------------------------
# Maps question intent -> which houses/planets matter for retrieval.
# This is our "chart-aware retrieval" trick: we don't just search the
# user's words, we search the chart placements relevant to their intent.
TOPIC_MAP = {
    "marriage":   {"houses": [7, 2, 11], "planets": ["Venus", "Jupiter", "Saturn"], "topic": "marriage"},
    "career":     {"houses": [10, 6, 2], "planets": ["Sun", "Saturn", "Jupiter", "Rahu"], "topic": "career"},
    "wealth":     {"houses": [2, 11, 5], "planets": ["Jupiter", "Venus"], "topic": "wealth"},
    "health":     {"houses": [1, 6, 8],  "planets": ["Sun", "Mars", "Saturn"], "topic": "health"},
    "personality":{"houses": [1],        "planets": ["Sun", "Moon", "Mars"], "topic": "personality"},
    "remedy":     {"houses": [],         "planets": ["Saturn", "Rahu", "Ketu", "Mars"], "topic": "remedy"},
}
TOPIC_KEYWORDS = {
    "marriage": ["marriage", "marry", "spouse", "wife", "husband", "shaadi", "wedding", "partner"],
    "career":   ["career", "job", "work", "business", "promotion", "naukri", "profession"],
    "wealth":   ["money", "wealth", "rich", "finance", "property", "paisa", "income"],
    "health":   ["health", "disease", "illness", "body"],
    "remedy":   ["remedy", "remedies", "upay", "solution", "gemstone", "mantra", "puja", "dosha"],
}


def detect_topic(question: str) -> str:
    q = question.lower()
    for topic, words in TOPIC_KEYWORDS.items():
        if any(w in q for w in words):
            return topic
    return "personality"  # default / general


_collection = None
_groq_client = None


def get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=DB_DIR)
        embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBED_MODEL)
        _collection = client.get_collection(name=COLLECTION, embedding_function=embed_fn)
    return _collection


def get_groq_client():
    global _groq_client
    if _groq_client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not set (add it to .env or the environment).")
        _groq_client = Groq(api_key=api_key)
    return _groq_client


# ---- Steps 1-3: chart-aware retrieval --------------------------------------
def retrieve(col, chart: dict, question: str, k: int = 6) -> list[str]:
    topic = detect_topic(question)
    focus = TOPIC_MAP[topic]

    # Build retrieval queries FROM CHART FACTS, not just the raw question.
    # e.g. user has Saturn in house 7 and asks about marriage ->
    #      query "Saturn in the 7th house marriage"
    queries = [question]  # raw question always included
    for pname, pdata in chart["planets"].items():
        if pdata["house"] in focus["houses"] or pname in focus["planets"]:
            queries.append(
                f"{pname} in the {pdata['house']}th house in {pdata['sign']}")

    # conjunction detection: planets sharing a house
    by_house = defaultdict(list)
    for pname, pdata in chart["planets"].items():
        by_house[pdata["house"]].append(pname)
    for house, group in by_house.items():
        if len(group) >= 2:
            queries.append(f"{' '.join(group)} conjunction together effects")

    # current mahadasha is always relevant
    current_dasha = next((d for d in chart.get("mahadasha", [])
                          if d.get("current")), None)
    if current_dasha:
        queries.append(f"{current_dasha['lord']} Mahadasha effects")

    # Run all queries; Chroma embeds each and returns nearest rules
    seen, results = set(), []
    res = col.query(query_texts=queries, n_results=3)
    for docs in res["documents"]:
        for doc in docs:
            if doc not in seen:          # dedupe across queries
                seen.add(doc)
                results.append(doc)
    return results[:k], topic


# ---- Step 4: augment --------------------------------------------------------
def build_prompt(chart: dict, question: str, rules: list[str]) -> str:
    planets_str = "\n".join(
        f"- {p}: {d['sign']}, house {d['house']}, nakshatra {d['nakshatra']}"
        for p, d in chart["planets"].items())
    current_dasha = next((d for d in chart.get("mahadasha", [])
                          if d.get("current")), {})
    rules_str = "\n".join(f"[Rule {i+1}] {r}" for i, r in enumerate(rules))

    return f"""You are JyotishVedaAI, a warm and wise Vedic astrology guide.
Answer using ONLY the classical rules and chart facts below.

STRICT STYLE RULES:
- NEVER mention "Rule 1", "rules provided", "retrieved", or which rules apply or don't apply
- NEVER mention your reasoning process — speak directly about the chart
- Cite placements naturally: "Your Saturn in the 8th house indicates..."
- If the rules genuinely don't address the question, give general guidance from the chart placements you DO have, and gently say a deeper analysis would need more study
- Warm, confident, personal tone. 150-250 words.

BIRTH CHART:
Ascendant (Lagna): {chart['ascendant']['sign']}
Moon sign (Rashi): {chart['moon_sign']}
{planets_str}
Current Mahadasha: {current_dasha.get('lord', 'unknown')} ({current_dasha.get('start')}–{current_dasha.get('end')})

CLASSICAL RULES (retrieved):
{rules_str}

USER QUESTION: {question}

Give a warm, specific answer citing which placements you used. 150-250 words."""


# ---- Step 5: generate -------------------------------------------------------
def ask(chart: dict, question: str) -> str:
    col = get_collection()
    rules, topic = retrieve(col, chart, question)
    prompt = build_prompt(chart, question, rules)

    client = get_groq_client()
    resp = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,          # low temp = stick to the rules
        max_tokens=600,
    )
    return resp.choices[0].message.content


if __name__ == "__main__":
    from chart import compute_chart
    chart = compute_chart("1995-08-15", "10:30", 28.46, 77.03, 5.5)
    print(ask(chart, "When will I get married?"))