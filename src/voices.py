# voices.py
import random
from incest import steal_fragment

# -------------------------
# All voices have the same signature:
# text, shared_data, self_name, corpus, depth
# Only Quentin actually uses depth
# -------------------------

def mrcompson_echo(text, shared_data, self_name, corpus, depth=0):
    """Mr Compson voice — echoes, occasionally grabs corpus fragments"""
    if corpus and random.random() < 0.25:
        snippet = " ".join(random.choice(corpus).split()[:6])
        text = f"{text} {snippet}"
    # Pillar interleaving
    frag = steal_fragment(shared_data, self_name)
    if frag:
        text = f"{text} {frag}"
    return text

def rosa_rhetorical(text, shared_data, self_name, corpus, depth=0):
    tics = ["unthinkable", "terrible", "monstrous", "damned", "an inherited shame"]
    text = f"{text} {random.choice(tics)}"
    frag = steal_fragment(shared_data, self_name)
    if frag and random.random() < 0.4:
        text = f"{frag} {text}"
    return text

def quentin_decay(text, shared_data, self_name, corpus, depth=1):
    """Quentin — manipulates text with depth-based decay"""
    # Add ellipsis, fragment shuffling, repetition
    if " " in text:
        parts = text.split(" ", 1)
        text = f"{parts[0]} ... {parts[1]}" if len(parts) > 1 else parts[0]
    if depth >= 2 and random.random() < min(0.9, 0.2 + depth * 0.12):
        text += " yes no yes no"
    if random.random() < 0.18:
        words = text.split()
        if len(words) >= 4:
            a, rest = words[:3], words[3:]
            text = " ".join(rest + a[::-1])
    frag = steal_fragment(shared_data, self_name)
    if frag:
        text = f"{text} {frag}"
    return text

def shreve_speculation(text, shared_data, self_name, corpus, depth=0):
    prefixes = ["perhaps", "it must have been", "surely he thought", "maybe"]
    if random.random() < 0.6:
        text = f"{random.choice(prefixes)} {text}"
    if random.random() < 0.35:
        text = f"{text} ?"
    frag = steal_fragment(shared_data, self_name)
    if frag and random.random() < 0.5:
        text = f"{text} {frag}?"
    return text
