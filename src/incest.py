import random

def steal_fragment(shared_data, exclude_name):
    """Steal a short phrase (2–5 words) from another pillar’s output."""
    others = [v for k, v in shared_data.items() if k != exclude_name and v]
    if not others:
        return ""
    chosen_list = random.choice(others)
    if not chosen_list:
        return ""
    chosen_line = random.choice(chosen_list)
    words = chosen_line.split()
    if len(words) < 2:
        return chosen_line if words else ""
    w = random.randint(2, min(5, len(words)))
    start = random.randint(0, len(words) - w)
    return " ".join(words[start:start + w])
