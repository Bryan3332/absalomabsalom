import random

def ground_devour(fragment, bite_size=4, drop_prob=0.28):
    """Chew a fragment and return a short distorted line."""
    words = fragment.split()
    if not words:
        return ""
    devoured = []
    i = 0
    while i < len(words) and len(devoured) < bite_size:
        chunk = words[i:i + bite_size]
        kept = [w for w in chunk if random.random() > drop_prob]
        if kept and random.random() < 0.22:
            idx = random.randrange(len(kept))
            w = kept[idx]
            kept[idx] = w[::-1] if random.random() < 0.5 else w[: max(1, len(w)//2)]
        devoured.extend(kept)
        i += bite_size
    if not devoured:
        return random.choice(["dirt", "root", "bone", "rot"])
    return " ".join(devoured)


def distort(text):
    """Optional extra distortion layer for ground fragments."""
    if not text:
        return ""
    words = text.split()
    for i in range(len(words)):
        if random.random() < 0.15:
            words[i] = words[i][::-1]  # reverse occasionally
    return " ".join(words)
