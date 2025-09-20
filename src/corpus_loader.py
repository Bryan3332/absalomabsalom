import os

def load_corpus(filename):
    if not os.path.isabs(filename):
        base = os.path.dirname(__file__)
        filename = os.path.join(base, filename)
    if not os.path.exists(filename):
        print(f"[!] Corpus file not found: {filename} — using fallback corpus.")
        return [
            "as if the past were not a thing but a place",
            "the old haunted silence of the south",
            "a monstrous unholy betrayal",
            "like a ghost returning to a house long dead",
            "an inherited curse",
        ]
    with open(filename, "r", encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip()]
