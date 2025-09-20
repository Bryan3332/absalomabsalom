# faulkner_engine_single.py
import time
import textwrap
import random

from voices import mrcompson_echo, rosa_rhetorical, quentin_decay, shreve_speculation
from ground import ground_devour
from incest import steal_fragment
from corpus_loader import load_corpus

# CONFIG
CORPUS = load_corpus("absalom-clean.txt")
PILLAR_WIDTH = 30
PILLAR_CHAR_CAP = 1288
GROUND_CHAR_CAP = 1288
SLEEP_DELAY = 0.15
CYCLES = 20

class Character:
    def __init__(self, name, voice_fn):
        self.name = name
        self.voice_fn = voice_fn
        self.output = []

    def generate_line(self, user_input, shared_data, depth=0):
        line = self.voice_fn(user_input, shared_data, self.name, CORPUS, depth)
        # Insert at top to grow upward
        self.output.insert(0, line)
        # Enforce hard cap
        joined = " ".join(self.output)
        if len(joined) > PILLAR_CHAR_CAP:
            truncated = joined[:PILLAR_CHAR_CAP]
            self.output = textwrap.wrap(truncated, width=PILLAR_WIDTH)
        return line

class StoryMachine:
    def __init__(self, user_input):
        self.user_input = user_input
        self.shared_data = {}
        self.pillars = [
            Character("Mr Compson", mrcompson_echo),
            Character("Rosa", rosa_rhetorical),
            Character("Quentin", quentin_decay),
            Character("Shreve", shreve_speculation),
        ]
        self.ground = []

    def build_ground(self):
        # Randomly select bits from pillars
        for char in self.pillars:
            if char.output and random.random() < 0.5:
                fragment = random.choice(char.output)
                mutated = ground_devour(fragment)
                self.ground.append(mutated)
        # Cap ground
        joined = " ".join(self.ground)
        if len(joined) > GROUND_CHAR_CAP:
            truncated = joined[:GROUND_CHAR_CAP]
            self.ground = textwrap.wrap(truncated, width=PILLAR_WIDTH*4 + 3*3)

    def render_canvas(self):
        # Wrap pillars
        wrapped_pillars = []
        max_height = 0
        for char in self.pillars:
            wrapped = [line[:PILLAR_WIDTH].ljust(PILLAR_WIDTH) for line in char.output]
            wrapped_pillars.append(wrapped)
            max_height = max(max_height, len(wrapped))

        # Wrap ground
        wrapped_ground = self.ground

        # Print pillar headers
        headers = [c.name.center(PILLAR_WIDTH) for c in self.pillars]
        sep_line = "-" * (PILLAR_WIDTH * len(self.pillars) + 3 * (len(self.pillars)-1))
        print(" | ".join(headers))
        print(sep_line)

        # Print pillars (bottom to top)
        for i in range(max_height-1, -1, -1):
            row = []
            for col in wrapped_pillars:
                if i < len(col):
                    row.append(col[i])
                else:
                    row.append(" " * PILLAR_WIDTH)
            print(" | ".join(row))

        # Print ground
        print("\nGROUND".center(PILLAR_WIDTH*len(self.pillars)+3*3))
        print("-" * (PILLAR_WIDTH * len(self.pillars) + 3 * (len(self.pillars)-1)))
        for line in wrapped_ground:
            print(line.ljust(PILLAR_WIDTH*len(self.pillars)+3*3))

    def run(self):
        for depth in range(CYCLES):
            for char in self.pillars:
                char.generate_line(self.user_input, self.shared_data, depth)
                self.shared_data[char.name] = char.output
                # Grow ground slowly
                self.build_ground()
                self.render_canvas()
                time.sleep(SLEEP_DELAY)

if __name__ == "__main__":
    user_input = input("Enter a thought, memory, dream, or quote: ")
    machine = StoryMachine(user_input)
    machine.run()
