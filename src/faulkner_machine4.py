# engine4.py
import os
import random
import textwrap
import asyncio

from itertools import zip_longest

from voices import mrcompson_echo, rosa_rhetorical, quentin_decay, shreve_speculation
from ground import ground_devour
from corpus_loader import load_corpus
from incest import steal_fragment

# ---------------- CONFIG ----------------
PILLAR_CHAR_CAP = 1288
GROUND_CHAR_CAP = 1288
CYCLES = 20           # total cycles
DELAY = 0.2           # delay between lines (for visual effect)
COL_WIDTH = 28        # width of each pillar
CORPUS_FILE = "absalom-clean.txt"
# ----------------------------------------

CORPUS_PATH = os.path.join(os.path.dirname(__file__), CORPUS_FILE)
CORPUS = load_corpus(CORPUS_PATH)

# ---------------- Characters ----------------
class Character:
    def __init__(self, name, voice_fn):
        self.name = name
        self.voice_fn = voice_fn
        self.output = []

    def generate_line(self, user_input, shared_data, corpus, depth=0):
        """Generate a single line of output"""
        line = self.voice_fn(user_input, shared_data, self.name, corpus, depth)
        # Insert at top to grow upward
        self.output.insert(0, line)
        # Enforce character cap
        total_text = " ".join(self.output)
        if len(total_text) > PILLAR_CHAR_CAP:
            truncated = total_text[:PILLAR_CHAR_CAP]
            self.output = truncated.split("\n")  # keep as list of lines
        return line

# ---------------- Story Engine ----------------
class FaulknerMachine:
    def __init__(self):
        self.characters = [
            Character("Mr Compson", mrcompson_echo),
            Character("Rosa", rosa_rhetorical),
            Character("Quentin", quentin_decay),
            Character("Shreve", shreve_speculation),
        ]
        self.ground = []

    def snapshot(self):
        """Shared data snapshot for inter-pillar references (flattened strings)"""
        return {c.name: " ".join(c.output) for c in self.characters}

    async def generate_story(self, user_input, cycles=CYCLES, delay=DELAY):
        depth = 0
        for _ in range(cycles):
            for c in self.characters:
                # Generate new line
                line = c.generate_line(user_input, self.snapshot(), CORPUS, depth if c.name=="Quentin" else 0)

                # Ground reacts randomly
                if random.random() < 0.7:  # 70% chance ground will devour something
                    fragment = random.choice(c.output)  # pick a random line from this pillar
                    devoured = ground_devour(fragment)
                    self.ground.append(devoured)
                    # Enforce ground cap
                    total_ground = " ".join(self.ground)
                    if len(total_ground) > GROUND_CHAR_CAP:
                        self.ground = total_ground[:GROUND_CHAR_CAP].split("\n")

                # Render one frame (pillars bottom→top, ground downward)
                self.render()

                await asyncio.sleep(delay)

            depth += 1

    def render(self):
        """Render all pillars and ground as a single frame"""
        max_height = max(len(c.output) for c in self.characters)
        # Prepare pillar lines
        pillar_lines = []
        for i in range(max_height):
            row = []
            for c in self.characters:
                line = c.output[i] if i < len(c.output) else ""
                # wrap or pad to COL_WIDTH
                wrapped = textwrap.wrap(line, COL_WIDTH) or [""]
                row.append(wrapped)
            # Transpose wrapped lines for row-by-row printing
            for wrapped_row in zip_longest(*row, fillvalue=" " * COL_WIDTH):
                pillar_lines.append([w.ljust(COL_WIDTH) for w in wrapped_row])

        # Then join with " | " to preserve distinct pillar boundaries
        for row in reversed(pillar_lines):
            print(" | ".join(row))


        # Print header
        headers = [c.name.center(COL_WIDTH) for c in self.characters]
        sep_line = "-" * (COL_WIDTH * len(self.characters) + 3 * (len(self.characters)-1))
        print("\n" + sep_line)
        print(" | ".join(headers))
        print(sep_line)

        # Print pillars line by line (bottom → top)
        for row_idx in reversed(range(max_height)):
            print(" | ".join(pillar_lines[row_idx]))
        print(sep_line)

        # Print ground (full width)
        ground_text = " ".join(self.ground)
        wrapped_ground = textwrap.wrap(ground_text, width=COL_WIDTH * len(self.characters) + 3 * (len(self.characters)-1))
        print("GROUND".center(COL_WIDTH * len(self.characters) + 3 * (len(self.characters)-1)))
        print("-" * (COL_WIDTH * len(self.characters) + 3 * (len(self.characters)-1)))
        for line in wrapped_ground:
            print(line.center(COL_WIDTH * len(self.characters) + 3 * (len(self.characters)-1)))
        print(sep_line)

# ---------------- Main ----------------
if __name__ == "__main__":
    seed = input("Enter a thought, memory, idea, or quote: ")
    machine = FaulknerMachine()
    asyncio.run(machine.generate_story(seed))
