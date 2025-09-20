# engine4.py
import asyncio
import os
import random
import textwrap

from voices import mrcompson_echo, rosa_rhetorical, quentin_decay, shreve_speculation
from ground import ground_devour
from incest import steal_fragment
from corpus_loader import load_corpus

COL_WIDTH = 28
PILLAR_HEIGHT = 20  # visible lines per pillar
GROUND_HEIGHT = 10  # visible lines for ground
PILLAR_CHAR_CAP = 1288
GROUND_CHAR_CAP = 1288
CORPUS = load_corpus("absalom-clean.txt")

class Character:
    def __init__(self, name, voice_fn, corpus=None):
        self.name = name
        self.voice_fn = voice_fn
        self.corpus = corpus
        self.output = []

    def generate_line(self, shared_data, depth=0):
        # choose seed text (for demo purposes)
        seed = random.choice(self.corpus) if self.corpus else "..."
        # generate new line using voice
        if self.name == "Quentin":
            line = self.voice_fn(seed, shared_data, self.name, self.corpus, depth)
        else:
            line = self.voice_fn(seed, shared_data, self.name, self.corpus)
        # insert at start → bottom-up growth
        self.output.insert(0, line)
        # enforce pillar char cap
        joined = " ".join(self.output)
        if len(joined) > PILLAR_CHAR_CAP:
            truncated = joined[:PILLAR_CHAR_CAP]
            self.output = [truncated]

        return line


class StoryGenerator:
    def __init__(self):
        self.characters = [
            Character("Mr Compson", mrcompson_echo, CORPUS),
            Character("Rosa", rosa_rhetorical),
            Character("Quentin", quentin_decay, CORPUS),
            Character("Shreve", shreve_speculation)
        ]
        self.ground = []

    async def generate_story(self, cycles=20, delay=0.3):
        for depth in range(cycles):
            for char in self.characters:
                # generate a new line
                line = char.generate_line(self.snapshot(), depth)
                # ground reacts at random
                if random.random() < 0.7:
                    devoured = ground_devour(line)
                    self.ground.append(devoured)
                    # enforce ground char cap
                    joined_ground = " ".join(self.ground)
                    if len(joined_ground) > GROUND_CHAR_CAP:
                        self.ground = [joined_ground[:GROUND_CHAR_CAP]]
            # render one frame per cycle
            self.render()
            await asyncio.sleep(delay)

    def snapshot(self):
        # snapshot for voices to reference others
        return {c.name: " ".join(c.output) for c in self.characters}

    def render(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        # prepare pillar lines
        pillar_lines = []
        for i in range(PILLAR_HEIGHT):
            row = []
            for c in self.characters:
                idx = PILLAR_HEIGHT - i - 1
                if idx < len(c.output):
                    line = c.output[idx][:COL_WIDTH].ljust(COL_WIDTH)
                else:
                    line = " " * COL_WIDTH
                row.append(line)
            pillar_lines.append(row)

        # print pillar header
        headers = [c.name.center(COL_WIDTH) for c in self.characters]
        sep = "-" * (COL_WIDTH * len(self.characters) + 3 * (len(self.characters) - 1))
        print(" | ".join(headers))
        print(sep)

        # print pillar lines (bottom-up)
        for row in pillar_lines:
            print(" | ".join(row))

        # print ground
        print(sep)
        ground_lines = textwrap.wrap(" ".join(self.ground), width=COL_WIDTH * len(self.characters) + 3 * (len(self.characters) - 1))
        for gline in ground_lines[-GROUND_HEIGHT:]:
            print(gline)
        print(sep)


if __name__ == "__main__":
    generator = StoryGenerator()
    asyncio.run(generator.generate_story())
