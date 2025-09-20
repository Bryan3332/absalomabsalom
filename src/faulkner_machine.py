# faulkner_machine.py
"""
Phase-3 (fixed UI): four pillars (bottom->top), single ground block UNDER pillars,
one printed frame per cycle, voices mutate their last line, Quentin keeps depth.
Modular: uses voices.py, ground.py, incest.py, corpus_loader.py
"""

import os
import random
import textwrap
import asyncio

from corpus_loader import load_corpus
from voices import mrcompson_echo, rosa_rhetorical, quentin_decay, shreve_speculation
from ground import ground_devour
from incest import steal_fragment

# ---------- CONFIG ----------
PILLAR_CHAR_CAP = 1288
GROUND_CHAR_CAP = 1288
CYCLES = 24
DELAY = 0.2
COL_WIDTH = 30
CORPUS_FILE = "corpus.txt"
# ----------------------------

# load corpus (corpus_loader.load_corpus expected)
SCRIPT_DIR = os.path.dirname(__file__)
CORPUS_PATH = os.path.join(SCRIPT_DIR, CORPUS_FILE)
CORPUS = load_corpus(CORPUS_PATH)


class Character:
    def __init__(self, name, style_rules):
        self.name = name
        self.style_rules = style_rules
        self.output = []          # list of lines (oldest -> newest)
        self.saturated = False    # true when char has hit its cap

    def generate_text(self, seed_text, shared_snapshot, depth):
        """Generate a single line for this character (no recursion)."""
        if self.saturated:
            return None

        base = (seed_text or "").strip()
        words = base.split() if base else []

        # small local mutations
        # repetition
        if words and random.random() < self.style_rules.get("repetition_prob", 0.1):
            idx = random.randrange(len(words))
            words.insert(idx, words[idx])

        # hallucination: occasionally replace a token with corpus-first-token
        if words and random.random() < self.style_rules.get("hallucination_prob", 0.07) and CORPUS:
            idx = random.randrange(len(words))
            words[idx] = random.choice(CORPUS).split()[0]

        candidate = " ".join(words) if words else (random.choice(CORPUS) if CORPUS and random.random() < 0.25 else base)

        # voice-specific transformation
        if self.name == "Mr Compson":
            line = mrcompson_echo(candidate, shared_snapshot, self.name, CORPUS)
        elif self.name == "Rosa":
            line = rosa_rhetorical(candidate, shared_snapshot, self.name, CORPUS)
        elif self.name == "Quentin":
            line = quentin_decay(candidate, depth, CORPUS)
        elif self.name == "Shreve":
            line = shreve_speculation(candidate, shared_snapshot, self.name, CORPUS)
        else:
            line = candidate

        # mild incest: sometimes insert a tiny stolen fragment at the start
        if random.random() < self.style_rules.get("reference_prob", 0.15):
            frag = steal_fragment(shared_snapshot, self.name)
            if frag:
                line = f"{frag} {line}"

        line = " ".join(line.split())  # tidy spaces

        # append as newest line (pillar grows upward visually)
        self.output.append(line)

        # enforce pillar cap: if exceeded, collapse to single truncated line and mark saturated
        total_chars = len(" ".join(self.output))
        if total_chars >= PILLAR_CHAR_CAP:
            merged = " ".join(self.output)[:PILLAR_CHAR_CAP]
            self.output = [merged]
            self.saturated = True

        return line


class StoryGenerator:
    def __init__(self):
        self.characters = [
            Character("Mr Compson", {"repetition_prob": 0.05, "hallucination_prob": 0.05, "reference_prob": 0.18}),
            Character("Rosa",       {"repetition_prob": 0.18, "hallucination_prob": 0.12, "reference_prob": 0.30}),
            Character("Quentin",    {"repetition_prob": 0.30, "hallucination_prob": 0.22, "reference_prob": 0.22}),
            Character("Shreve",     {"repetition_prob": 0.08, "hallucination_prob": 0.06, "reference_prob": 0.40}),
        ]
        # shared snapshot for incest helpers: name -> list(lines)
        self.shared = {c.name: [] for c in self.characters}
        self.ground = []  # ground lines top -> down

    def snapshot(self):
        return {c.name: c.output[:] for c in self.characters}

    async def generate_story(self, user_input, cycles=CYCLES, delay=DELAY):
        """
        Outer loop controls depth.
        Each cycle: sequentially generate one line per character (in order),
        ground devours the freshly emitted line into one ground row,
        then at end of full cycle we print ONE frame that shows current pillars and ground.
        """
        # initial seeds: each pillar starts with the user input as first seed
        last_lines = {c.name: user_input for c in self.characters}
        depth = 0

        for cycle in range(cycles):
            for char in self.characters:
                if char.saturated:
                    # update shared snapshot but skip generating
                    self.shared[char.name] = char.output
                    continue

                # choose seed: prefer pillar's last line (so pillar mutates itself)
                seed = last_lines.get(char.name) or user_input

                # small chance to seed from another pillar to encourage incest forward momentum
                if random.random() < 0.22:
                    frag = steal_fragment(self.snapshot(), char.name)
                    if frag:
                        seed = f"{frag} {seed}"

                # generate single line for this character
                line = char.generate_text(seed, self.snapshot(), depth)
                if line is None:
                    # saturated or no output
                    continue

                # update last line for this pillar
                last_lines[char.name] = line
                # update shared data for incest
                self.shared[char.name] = char.output

                # ground devours a bite of the line -> produce one ground row (top -> down)
                dev_line = ground_devour(line)
                self.ground.append(dev_line)

                # enforce ground cap: if exceeded, collapse to single truncated line and stop further ground growth
                total_ground_chars = len(" ".join(self.ground))
                if total_ground_chars >= GROUND_CHAR_CAP:
                    merged = " ".join(self.ground)[:GROUND_CHAR_CAP]
                    self.ground = [merged]
                    # mark ground saturated by setting a flag: we won't append more but pillars still generate
                    # We simply won't append further devours (we check length below)
                # small pause for display effect (optional)
                await asyncio.sleep(delay)

            # after all four voices produced a line this cycle, print a single frame
            self.format_output(col_width=COL_WIDTH)
            depth += 1

            # If every pillar is saturated and ground saturated, we can early exit
            if all(c.saturated for c in self.characters) and len(" ".join(self.ground)) >= GROUND_CHAR_CAP:
                print("\n[halt] all pillars and ground saturated.")
                break

        print("\n[done] final frame. (Interrupt earlier with Ctrl-C)\n")

    def format_output(self, col_width=COL_WIDTH):
        """
        Print the pillars block (4 columns) with new lines filling bottom->top,
        then print the ground block UNDER the pillars (not as a separate right column).
        """
        # pillar heights (oldest -> newest)
        heights = [len(c.output) for c in self.characters]
        max_height = max(heights) if heights else 0

        # compute header and separator
        names = [c.name.center(col_width) for c in self.characters]
        header = " | ".join(names)
        sep = "-" * len(header)
        print("\n" + sep)
        print(header)
        print(sep)

        # print rows bottom -> top so that new lines appear at the top of the block visually
        # row index r corresponds to pillar index = r (0 = bottom/oldest)
        # but we render from top (max_height - 1) down to 0
        for row in range(max_height - 1, -1, -1):
            cells = []
            for c in self.characters:
                if row < len(c.output):
                    # row index corresponds to that element (oldest at index 0)
                    cell = c.output[row][:col_width].ljust(col_width)
                else:
                    cell = "".ljust(col_width)
                cells.append(cell)
            print(" | ".join(cells))

        # base separator between pillars and ground
        print(sep)
        # Now render ground as lines top -> down UNDER the pillars
        ground_lines = textwrap.wrap(" ".join(self.ground), width=col_width)
        if not ground_lines:
            print("(the earth is quiet...)\n")
            return
        print("GROUND".center(len(header)))
        print("-" * len(header))
        for g in ground_lines:
            print(g[:col_width].center(len(header)))
        print(sep)

# entry point
if __name__ == "__main__":
    gen = StoryGenerator()
    seed = input("Enter a question, thought, memory, or dream: ").strip()
    try:
        asyncio.run(gen.generate_story(seed, cycles=CYCLES, delay=DELAY))
    except KeyboardInterrupt:
        print("\n[interrupted] stopped by user")
