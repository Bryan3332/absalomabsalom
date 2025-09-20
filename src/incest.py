import random

def steal_fragment(shared_data, exclude_name):
    """
    Pull a fragment from another pillar's most recent line.
    shared_data should be a dict: {pillar_name: latest_line}
    """
    if not shared_data:
        return ""

    """Steal a short phrase (2–5 words) from another pillar’s output."""
    others = [v for k, v in shared_data.items() if k != exclude_name and v]
    if not others:
        return ""

    line = random.choice(others)
    words = line.split()
    if not words:
        return ""
    frag = random.choice(words)
    return frag
