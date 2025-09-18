# corpus_loader.py
def load_corpus(path="absalom-clean.txt"):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return [line.strip() for line in lines if line.strip()]
