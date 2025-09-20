# faulkner_engine.py
import random
import textwrap
import time
from voices import mrcompson_echo, rosa_rhetorical, quentin_decay, shreve_speculation
from ground import ground_devour
from incest import steal_fragment

PILLAR_WIDTH = 28
PILLAR_HEIGHT = 20   # adjust to fit terminal if needed
GROUND_HEIGHT = 10
CAP = 1288           # character cap for pillars and ground
DELAY = 0.15         # seconds per line fill

class Character:
    def __init__(self, name, voice_fn, use_depth=False):
        self.name = name
        self.voice_fn = voice_fn
        self.use_depth = use_depth
        self.output = []

    def speak(self, text, shared_data, corpus, depth=0):
        if self.use_depth:
            line = self.voice_fn(text, shared_data, self.name, corpus, depth)
        else:
            line = self.voice_fn(text, shared_data, self.name, corpus)
        self.output.insert(0, line)  # bottom-up growth
        # enforce cap
        combined = " ".join(self.output)
        if len(combined) > CAP:
            self.output = [" ".join(combined[:CAP].split())]
        return line

class StoryGenerator:
    def __init__(self, corpus):
        self.corpus = corpus
        self.shared_data = {}
        self.ground = []

        # initialize characters
        self.characters = [
            Character("Mr Compson", mrcompson_echo),
            Character("Rosa", rosa_rhetorical),
            Character("Quentin", quentin_decay, use_depth=True),
            Character("Shreve", shreve_speculation)
        ]
        for c in self.characters:
            self.shared_data[c.name] = []

    def format_pillars(self):
        # Build pillar lines
        lines = []
        for i in range(PILLAR_HEIGHT):
            row = []
            for char in self.characters:
                text = char.output[i] if i < len(char.output) else ""
                wrapped = textwrap.wrap(text, width=PILLAR_WIDTH)
                line_text = wrapped[0] if wrapped else ""
                row.append(line_text.ljust(PILLAR_WIDTH))
            lines.append(row)
        return lines

    def format_ground(self):
        # bottom-up growth of ground
        ground_text = " ".join(self.ground)
        wrapped = textwrap.wrap(ground_text, width=PILLAR_WIDTH*4 + 3*3)
        return wrapped[-GROUND_HEIGHT:]  # last lines fit ground

    def render(self):
        # headers
        headers = [c.name.center(PILLAR_WIDTH) for c in self.characters]
        sep_line = "-" * (PILLAR_WIDTH*4 + 3*3)
        print(sep_line)
        print(" | ".join(headers))
        print(sep_line)

        # pillar content
        pillar_lines = self.format_pillars()
        ground_lines = self.format_ground()
        max_rows = max(len(pillar_lines), len(ground_lines))
        for i in range(max_rows):
            row_cells = []
            if i < len(pillar_lines):
                row_cells = pillar_lines[i]
            else:
                row_cells = ["".ljust(PILLAR_WIDTH) for _ in self.characters]
            g_line = ground_lines[i] if i < len(ground_lines) else ""
            print(" | ".join(row_cells) + " || " + g_line)
        print(sep_line)

    def generate_story(self, user_input, cycles=20):
        for depth in range(cycles):
            for char in self.characters:
                # character speaks
                line = char.speak(user_input, self.shared_data, self.corpus, depth)
                self.shared_data[char.name].append(line)

                # ground randomly devours fragments
                if random.random() < 0.5:
                    frag = ground_devour(line)
                    self.ground.append(frag)
                    # cap ground
                    combined = " ".join(self.ground)
                    if len(combined) > CAP:
                        self.ground = [" ".join(combined[:CAP].split())]

                # slight delay to simulate slow fill
                time.sleep(DELAY)

            # render single frame
            print("\033c", end="")  # clear terminal for animation effect
            self.render()

if __name__ == "__main__":
    from corpus_loader import load_corpus
    corpus = load_corpus("absalom-clean.txt")
    generator = StoryGenerator(corpus)
    seed = input("Enter a thought, memory, or dream: ")
    generator.generate_story(seed)
