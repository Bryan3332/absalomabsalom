# faulkner_machine.py
"""
Faulkner Machine v3 — Phase 3 (clean, single-script version)

Behavior summary:
- Four sequential voices (Mr Compson, Rosa, Quentin, Shreve)
- Pillars grow upward line-by-line; ground grows downward line-by-line
- Incest = small fragment-stealing between pillars
- Pillars & ground hard-capped at 1288 characters
- Quentin uses outer-loop depth for decay
- Ground devours pieces of pillar output (bite-size) and outputs distorted fragments
"""

import os
import random
import textwrap
import asyncio
import time

# -------- CONFIG ----------
PILLAR_CHAR_CAP = 1288
GROUND_CHAR_CAP = 1288
CYCLES = 24            # how many full rounds of 4 voices
DELAY = 0.18           # seconds between each voice output (for display)
COL_WIDTH = 28         # column width for terminal UI
CORPUS_FILENAME = "absalom-clean.txt"  # expect this in same folder as script
# ---------------------------

# helper: load corpus lines
def load_corpus(path):
    if not os.path.isabs(path):
        base = os.path.dirname(__file__)
        path = os.path.join(base, path)
    if not os.path.exists(path):
        print(f"[!] Corpus file not found: {path} — continuing with small fallback corpus.")
        return [
            "as if the past were not a thing but a place",
            "the old haunted silence of the south",
            "a monstrous unholy betrayal",
            "like a ghost returning to a house long dead",
            "an inherited curse",
        ]
    with open(path, "r", encoding="utf-8") as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    return lines

CORPUS = load_corpus(CORPUS_FILENAME)


# small helper: steal a small fragment (2-5 words) from shared_data (other pillars)
def steal_fragment(shared_data, exclude_name):
    others = [v for k, v in shared_data.items() if k != exclude_name and v]
    if not others:
        return ""
    chosen_list = random.choice(others)
    # chosen_list is list of lines (each element is a pillar row)
    if not chosen_list:
        return ""
    chosen_line = random.choice(chosen_list)
    words = chosen_line.split()
    if len(words) < 2:
        return chosen_line if words else ""
    # take a short window
    w = random.randint(2, min(5, len(words)))
    start = random.randint(0, len(words) - w)
    frag = " ".join(words[start:start + w])
    return frag


# voice helpers --------------------------------------------------------------
def mrcompson_echo(text, shared_data, self_name):
    # Mr Compson is the most "faithful", but still echoes and borrows a tiny phrase
    # Insert a short corpus quote sometimes
    if random.random() < 0.25 and CORPUS:
        quote = random.choice(CORPUS).split()
        snippet = " ".join(quote[: min(6, len(quote))])
        text = f"{text} {snippet}"
    # occasionally echo a tiny fragment from other pillars
    frag = steal_fragment(shared_data, self_name)
    if frag:
        text = f"{text} {frag}"
    return text


def rosa_rhetorical(text, shared_data=None, self_name="Rosa"):
    # Rosa: accusatory, rhetorical flourishes; always adds a judgment tic
    tics = ["unthinkable", "terrible", "monstrous", "damned", "an inherited shame"]
    # always drop at least one tic to mark voice distinctiveness
    if text:
        text = f"{text} {random.choice(tics)}"
    # sometimes steal a small phrase (mild incest)
    if shared_data and random.random() < 0.4:
        frag = steal_fragment(shared_data, self_name)
        if frag:
            text = f"{frag} {text}"
    return text


def quentin_decay(text, depth):
    # Quentin degrades with depth: elliptical breaks and contradictions
    # Always add an ellipsis somewhere early
    if " " in text:
        # replace first space to create an ellipsis break
        parts = text.split(" ", 1)
        text = f"{parts[0]} ... {parts[1]}" if len(parts) > 1 else parts[0]
    # depth-driven degradation
    if depth >= 2:
        # add circular negation more frequently as depth increases
        if random.random() < min(0.9, 0.2 + depth * 0.12):
            text += " yes no yes no"
    # sometimes reverse a short phrase
    if random.random() < 0.18:
        words = text.split()
        if len(words) >= 4:
            a = words[:3]
            rest = words[3:]
            text = " ".join(rest + a[::-1])
    return text


def shreve_speculation(text, shared_data=None, self_name="Shreve"):
    # Shreve: speculative, asks questions, inserts qualifiers
    prefixes = ["perhaps", "it must have been", "surely he thought", "maybe"]
    if random.random() < 0.6:
        text = f"{random.choice(prefixes)} {text}"
    # sometimes append a question fragment
    if random.random() < 0.35:
        text = f"{text} ?"
    # steal heavy fragments (more incest) but as questions
    if shared_data and random.random() < 0.5:
        frag = steal_fragment(shared_data, self_name)
        if frag:
            text = f"{text} {frag}?"
    return text


# ground devourer ------------------------------------------------------------
def ground_devour(fragment, bite_size=4, drop_prob=0.28):
    """
    Simulates the ground chewing a fragment and returning a small devoured line.
    - bite_size: how many words are considered per bite chunk
    - drop_prob: probability that a particular word is dropped (rotting away)
    The function returns a short string (one line) to append to ground.
    """
    words = fragment.split()
    if not words:
        return ""
    devoured = []
    i = 0
    while i < len(words) and len(devoured) < bite_size:
        chunk = words[i:i + bite_size]
        # drop some words
        kept = [w for w in chunk if random.random() > drop_prob]
        # randomly mutate a word (reverse or trim)
        if kept and random.random() < 0.22:
            idx = random.randrange(len(kept))
            w = kept[idx]
            # small mutation: reverse or cut half
            if random.random() < 0.5:
                kept[idx] = w[::-1]
            else:
                kept[idx] = w[: max(1, len(w)//2)]
        devoured.extend(kept)
        i += bite_size
    # if nothing survived the bite, return a short earthy token occasionally
    if not devoured:
        return random.choice(["dirt", "root", "bone", "rot"])
    return " ".join(devoured)


# Character class (single-line-per-cycle generator) -------------------------
class Character:
    def __init__(self, name, style_rules):
        self.name = name
        self.style_rules = style_rules
        # store pillar lines in bottom->top order; append() adds new top line
        self.output = []

    def generate_text(self, seed_text, shared_data, depth):
        """
        Generate a single line for this character, using:
        - seed_text: usually last pillar line or the original user input for the first pass
        - shared_data: dict of other pillars (for stealing)
        - depth: outer-loop depth for Quentin
        """
        # Base: start with seed_text trimmed
        base = seed_text.strip() if seed_text else ""
        # Mix in a short corpus quote randomly (so book text appears)
        corpus_injection = ""
        if CORPUS and random.random() < self.style_rules.get("corpus_insert_prob", 0.25):
            c = random.choice(CORPUS).split()
            corpus_injection = " ".join(c[: random.randint(3, min(10, len(c)))])
        # Small local mutations (repetition/hallucination)
        words = base.split() if base else []
        # repetition: sometimes repeat a word
        if words and random.random() < self.style_rules.get("repetition_prob", 0.10):
            idx = random.randrange(len(words))
            words.insert(idx, words[idx])
        # hallucinate by replacing a simple token with corpus-first-token occasionally
        if words and random.random() < self.style_rules.get("hallucination_prob", 0.14):
            idx = random.randrange(len(words))
            replacement = random.choice(CORPUS).split()[0]
            words[idx] = replacement

        # reassemble a working text candidate
        candidate = " ".join(words) if words else corpus_injection or base

        # voice-specific processing
        if self.name == "Mr Compson":
            line = mrcompson_echo(candidate, shared_data, self.name)
        elif self.name == "Rosa":
            line = rosa_rhetorical(candidate, shared_data, self.name)
        elif self.name == "Quentin":
            line = quentin_decay(candidate, depth)
        elif self.name == "Shreve":
            line = shreve_speculation(candidate, shared_data, self.name)
        else:
            line = candidate

        # mild trim
        line = " ".join(line.split())

        # small chance to forcibly inject a tiny stolen fragment (incest)
        if random.random() < self.style_rules.get("reference_prob", 0.22):
            frag = steal_fragment(shared_data, self.name)
            if frag:
                # insert it near the start
                line = f"{frag} {line}"

        # append to pillar (top)
        self.output.append(line)

        # enforce pillar character cap (hard)
        total = len(" ".join(self.output))
        if total > PILLAR_CHAR_CAP:
            # truncate combined text to cap and keep as single top line (stop growth)
            all_text = " ".join(self.output)
            truncated = all_text[:PILLAR_CHAR_CAP]
            self.output = [truncated]
        return line


# StoryGenerator: orchestrates sequential growth + ground devouring -------------
class StoryGenerator:
    def __init__(self):
        self.shared_data = {
            "Mr Compson": [],
            "Rosa": [],
            "Quentin": [],
            "Shreve": []
        }
        self.ground = []  # ground lines in top->down order (append adds next downward line)
        # characters in the order you wanted
        self.characters = [
            Character("Mr Compson", {"repetition_prob": 0.05, "corpus_insert_prob": 0.2, "hallucination_prob": 0.05, "reference_prob": 0.18}),
            Character("Rosa",       {"repetition_prob": 0.18, "corpus_insert_prob": 0.25, "hallucination_prob": 0.12, "reference_prob": 0.30}),
            Character("Quentin",    {"repetition_prob": 0.3,  "corpus_insert_prob": 0.20, "hallucination_prob": 0.22, "reference_prob": 0.22}),
            Character("Shreve",     {"repetition_prob": 0.08, "corpus_insert_prob": 0.15, "hallucination_prob": 0.06, "reference_prob": 0.40}),
        ]

    def current_shared_snapshot(self):
        # returns a simple dict name -> list-of-lines to share with voice helpers
        return {c.name: c.output[:] for c in self.characters}

    async def generate_story(self, user_input, cycles=CYCLES, delay=DELAY):
        """
        Sequential rounds. depth increases after each full cycle (of 4 voices).
        Each voice uses its last line as seed for next round; first round seeds use user_input.
        After each voice emits a line, ground chews a bite and appends one ground line.
        """
        depth = 0
        # initial seeds map — start with user input for all
        last_lines = {c.name: user_input for c in self.characters}

        for cycle in range(cycles):
            for char in self.characters:
                # if the pillar is already saturated (cap reached and collapsed to a single truncated line), skip growth
                combined_len = len(" ".join(char.output))
                if combined_len >= PILLAR_CHAR_CAP:
                    # keep shared snapshot up-to-date but do not grow further
                    self.shared_data[char.name] = char.output
                    continue

                # choose a seed: prefer last line from this pillar (so pillar mutates itself),
                # but occasionally start from a stolen fragment or corpus to encourage cross-contamination
                seed = last_lines.get(char.name) or user_input
                if random.random() < 0.25:
                    # small chance to seed from another pillar fragment to encourage incest forward momentum
                    frag = steal_fragment(self.current_shared_snapshot(), char.name)
                    if frag:
                        seed = f"{frag} {seed}"

                # generate one line for the character
                # pass shared_data snapshot so helpers can steal
                line = char.generate_text(seed, self.current_shared_snapshot(), depth)
                # update last_lines so next cycle the pillar will use its own most recent line as seed
                last_lines[char.name] = line
                # update shared_data for others to reference
                self.shared_data[char.name] = char.output

                # ground devours a bite of the freshly produced line
                dev_line = ground_devour(line)
                # append the devoured fragment as the next ground row (top -> down)
                self.ground.append(dev_line)

                # enforce ground cap: truncate joined ground to GROUND_CHAR_CAP and collapse to single line if exceeded
                total_ground = len(" ".join(self.ground))
                if total_ground > GROUND_CHAR_CAP:
                    joined = " ".join(self.gound)
                    truncated = joined[:GROUND_CHAR_CAP]
                    self.ground = [truncated]
                    # once ground is saturated, we stop appending further devours (but pillars can still produce)
                # display the current scene
                self.format_output()
                await asyncio.sleep(delay)
            depth += 1  # increase depth per full round

        # final frame (no additional ground chorus — ground is the single earth)
        print("\n[done] final state (pillars halted when capped, ground halted when capped).")

    def format_output(self, col_width=COL_WIDTH):
        """
        Print pillars (top-down) and ground (left to right: 4 pillars then '||' then ground).
        Pillars are printed so their latest appended lines appear at the top.
        Ground lines are printed top-to-down in the final column.
        """
        # heights for pillars
        heights = [len(c.output) for c in self.characters]
        max_pillar_h = max(heights) if heights else 0
        ground_lines = self.ground[:]  # top-to-down lines
        total_rows = max(max_pillar_h, len(ground_lines))

        # compute header and separators
        names = [c.name.center(col_width) for c in self.characters]
        header = " | ".join(names) + " || " + "ground".center(col_width)
        sep = "-" * (len(header))
        print("\n" + sep)
        print(header)
        print(sep)

        # print row by row from top -> down
        for row in range(total_rows):
            row_cells = []
            # pillar cell: compute index for this row (top row = latest element)
            for c in self.characters:
                h = len(c.output)
                idx = h - 1 - row  # top row -> index = last element
                if idx >= 0:
                    cell = c.output[idx][:col_width].ljust(col_width)
                else:
                    cell = "".ljust(col_width)
                row_cells.append(cell)
            # ground cell: straightforward top->down indexing
            gcell = ground_lines[row] if row < len(ground_lines) else ""
            gcell = gcell[: col_width].ljust(col_width)
            print(" | ".join(row_cells) + " || " + gcell)
        print(sep)


# Entry point ---------------------------------------------------------------
if __name__ == "__main__":
    gen = StoryGenerator()
    ui = input("Enter a question, thought, memory, or dream (seed): ").strip()
    try:
        asyncio.run(gen.generate_story(ui, cycles=CYCLES, delay=DELAY))
    except KeyboardInterrupt:
        print("\n[interrupted] stopped by user")
