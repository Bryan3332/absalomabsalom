# voices.py
import random

def mrcompson_echo(text, shared_data, self_name):
    other_outputs = [val for key, val in shared_data.items() if key != self_name and val]
    if other_outputs and random.random() < 0.5:
        phrase = random.choice(random.choice(other_outputs))
        return text + " ... " + phrase
    return text

def rosa_rhetorical(text):
    tics = [
        "what else could it have been",
        "unthinkable",
        "terrible",
        "lo behold",
        "demon",
        "strong enough to cope",
        "amoral evil's undeviating absolute",
        "never a child",
        "never a woman",
        "no interval for reply"
    ]
    if random.random() < 0.3:
        text += " " + random.choice(tics)
    return text

def quentin_decay(text, depth):
    # Add ellipses and self-contradiction with recursion depth
    if random.random() < 0.4:
        text = text.replace(" ", " ... ", 1)
    if depth > 2 and random.random() < 0.3:
        text += " yes no yes no"
    return text

def shreve_speculation(text):
    prefixes = ["perhaps", "surely he thought", "it must have been", "was it not", "could it have been", "and now", "lets go to bed"]
    if random.random() < 0.3:
        text = random.choice(prefixes) + " " + text
    if random.random() < 0.2:
        text += "?"
    return text
