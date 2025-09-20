import random
from incest import steal_fragment

def mrcompson_echo(text, shared_data, self_name, corpus):
    if random.random() < 0.25 and corpus:
        quote = random.choice(corpus).split()
        snippet = " ".join(quote[: min(6, len(quote))])
        text = f"{text} {snippet}"
    frag = steal_fragment(shared_data, self_name)
    if frag:
        text = f"{text} {frag}"
    return text


def rosa_rhetorical(text, shared_data, self_name):
    tics = ["unthinkable", "terrible", "monstrous", "damned", "an inherited shame"]
    text = f"{text} {random.choice(tics)}"
    if shared_data and random.random() < 0.4:
        frag = steal_fragment(shared_data, self_name)
        if frag:
            text = f"{frag} {text}"
    return text


def quentin_decay(text, depth):
    if " " in text:
        parts = text.split(" ", 1)
        text = f"{parts[0]} ... {parts[1]}" if len(parts) > 1 else parts[0]
    if depth >= 2 and random.random() < min(0.9, 0.2 + depth * 0.12):
        text += " yes no yes no"
    if random.random() < 0.18:
        words = text.split()
        if len(words) >= 4:
            a = words[:3]
            rest = words[3:]
            text = " ".join(rest + a[::-1])
    return text


def shreve_speculation(text, shared_data, self_name):
    prefixes = ["perhaps", "it must have been", "surely he thought", "maybe"]
    if random.random() < 0.6:
        text = f"{random.choice(prefixes)} {text}"
    if random.random() < 0.35:
        text = f"{text} ?"
    if shared_data and random.random() < 0.5:
        frag = steal_fragment(shared_data, self_name)
        if frag:
            text = f"{text} {frag}?"
    return text
