# ground.py
import random

def ground_devour(line):
    words = line.split()
    if not words:
        return ""

    # Take a random bite out of the line
    bite_size = random.randint(1, max(2, len(words)//3))
    fragment = " ".join(random.sample(words, bite_size))

    # Distort the fragment
    fragment = distort(fragment)

    return fragment

def distort(text):
    # Corrupt words a little
    text = text.replace("a", "aa").replace("e", "ee")
    if random.random() < 0.3:
        text = text[::-1]  # occasional reversal
    if random.random() < 0.2:
        text = text.upper()
    return text
