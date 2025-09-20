import random

def steal_fragment(shared_data, exclude_name):
    # collect all lines from other characters
    others = [v for k, v in shared_data.items() if k != exclude_name and v]

    if not others:
        return ""

    # choose a random list (pillar output) and flatten to a single line
    chosen_list = random.choice(others)
    if isinstance(chosen_list, list):
        # pick a random line from that list
        line = random.choice(chosen_list)
    else:
        line = chosen_list

    # ensure line is a string
    if isinstance(line, list):
        line = " ".join(line)

    # now safe to split into words
    words = line.split()
    if not words:
        return ""

    # pick a random fragment length
    frag_len = min(len(words), random.randint(1, 5))
    start = random.randint(0, len(words) - frag_len)
    fragment = " ".join(words[start:start + frag_len])
    return fragment
