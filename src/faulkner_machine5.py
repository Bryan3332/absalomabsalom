# faulkner_machine.py
"""
Faulkner Machine — Clean Modular Engine
- Four pillars grow upward from bottom to top
- Ground grows downward from the bottom
- Voices are idiosyncratic and can interact
- One frame printed; text fills pillars slowly
- Caps applied for pillars and ground
"""

import asyncio
import os
import random
import textwrap

from voices import mrcompson_echo, rosa_rhetorical, quentin_decay, shreve_speculation
from ground import ground_devour
from incest import steal_fragment
from corpus_loader import load_corpus

# -------- CONFIG ----------
PILLAR_CHAR_CAP = 1288
GROUND_CHAR_CAP = 1288
COL_WIDTH = 30
CYCLES = 20
DELAY = 0.3  # delay between lines
CORPUS_FILENAME = "absalom-clean.txt"
# ---------------------------

SCRIPT_DIR = os.path.dirname(__file__)
CORPUS_PATH = os.path.join(SCRIPT_DIR, CORPUS_FILENAME)
CORPUS = load_corpus(CORPUS_PATH)

class Character:
    def __init__(self, name, voice_fn, corpus=None):
        self.name = name
        self.voice_fn = voice_fn
        self.output = []
        self.corpus = corpus

    def generate_line(self, input_text, shared_data, depth=0):
        # Core text manipulations can be added here
        line = self.voice_fn(input_text, shared_data, self.name, self.corpus, depth)
        # Insert new line at top for bottom-up growth
        self.output.insert(0, line)
        # Cap pillar
        joined = " ".join(self.output)
        if len(joined) > PILLAR_CHAR_CAP:
            truncated = joined[:PILLAR_CHAR_CAP]
            self.output = [truncated]
        return line

class StoryGenerator:
    def __init__(self, user_input):
        self.user_input = user_input
        self.shared_data = {}
        self.ground = []
        self.characters = [
            Character("Mr Compson", mrcompson_echo, CORPUS),
            Character("Rosa", rosa_rhetorical, CORPUS),
            Character("Quentin", quentin_decay, CORPUS),
            Character("Shreve", shreve_speculation, CORPUS),
        ]
        for char in self.characters:
            self.shared_data[char.name] = []

    async def generate_story(self, cycles=CYCLES, delay=DELAY):
        for depth in range(cycles):
            for char in self.characters:
                # Generate line and add to pillar
                line = char.generate_line(self.user_input, self.shared_data, depth)
                self.shared_data[char.name].append(line)

                # Ground randomly devours fragments
                if random.random() < 0.5:
                    devoured = ground_devour(line)
                    self.ground.append(devoured)
                    # Cap ground
                    joined_ground = " ".join(self.ground)
                    if len(joined_ground) > GROUND_CHAR_CAP:
                        truncated_ground = joined_ground[:GROUND_CHAR_CAP]
                        self.ground = [truncated_ground]

                # Wait to emulate slow filling
                await asyncio.sleep(delay)

            # Update one single frame (clear + redraw)
            self.render_frame()

    def render_frame(self):
        # Clear terminal for animation
        print("\033[2J\033[H", end="")

        # Prepare pillars
        height = max(len(c.output) for c in self.characters)
        pillar_lines = []
        for row in range(height):
            row_cells = []
            for char in self.characters:
                if row < len(char.output):
                    cell = char.output[row][:COL_WIDTH].ljust(COL_WIDTH)
                else:
                    cell = " " * COL_WIDTH
                row_cells.append(cell)
            pillar_lines.append(" | ".join(row_cells))

        # Prepare ground
        ground_text = " ".join(self.ground)
        ground_lines = textwrap.wrap(ground_text, width=COL_WIDTH * 4 + 3 * 3)

        # Print headers
        headers = [c.name.center(COL_WIDTH) for c in self.characters]
        print(" | ".join(headers))
        print("-" * (COL_WIDTH * 4 + 3 * 3))

        # Print pillar lines bottom-up
        for line in reversed(pillar_lines):
            print(line)

        # Print separator for ground
        print("-" * (COL_WIDTH * 4 + 3 * 3))
        print("GROUND".center(COL_WIDTH * 4 + 3 * 3))
        print("-" * (COL_WIDTH * 4 + 3 * 3))

        # Print ground
        for line in ground_lines:
            print(line)

if __name__ == "__main__":
    seed_input = input("Enter a thought, memory, idea, or quote: ")
    generator = StoryGenerator(seed_input)
    asyncio.run(generator.generate_story())
