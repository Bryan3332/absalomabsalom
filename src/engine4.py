import asyncio
import random
import os
from corpus_loader import load_corpus
from voices import mrcompson_echo, rosa_rhetorical, quentin_decay, shreve_speculation, ground_voice

WORD_CAP = 1288  # hard cap for both pillars and ground


class Pillar:
    def __init__(self, name, voice_fn, corpus):
        self.name = name
        self.voice_fn = voice_fn
        self.lines = []
        self.corpus = corpus



    def generate_text(self, seed, shared_data, depth=1):
        if self.name == "Quentin":
            text = self.voice_fn(seed, depth)
        else:
            text = self.voice_fn(seed, shared_data, self.name, self.corpus)
       
        self.lines.insert(0, text)  # newest line at the top
        self.enforce_cap()
        return text



    def enforce_cap(self):
        # Count total words across pillar
        all_words = " ".join(self.lines).split()
        if len(all_words) > WORD_CAP:
            # trim oldest lines until under cap
            while len(" ".join(self.lines).split()) > WORD_CAP and self.lines:
                self.lines.pop()  # remove bottom line


class Ground:
    def __init__(self):
        self.lines = []

    def digest(self, text):
        digested = ground_voice(text)
        self.lines.append(digested)
        self.enforce_cap()
        return digested

    def enforce_cap(self):
        all_words = " ".join(self.lines).split()
        if len(all_words) > WORD_CAP:
            while len(" ".join(self.lines).split()) > WORD_CAP and self.lines:
                self.lines.pop(0)  # remove earliest ground lines (top)


class FaulknerMachine:
    def __init__(self, corpus):
        self.pillars = [
            Pillar("Mr Compson", mrcompson_echo, corpus),
            Pillar("Rosa", rosa_rhetorical, corpus),
            Pillar("Quentin", quentin_decay, corpus),
            Pillar("Shreve", shreve_speculation, corpus),
        ]
        self.ground = Ground()
        self.shared_data = {p.name: [] for p in self.pillars}

    def snapshot(self):
        return self.shared_data

    async def generate_story(self, seed, cycles=10, delay=0.5):
        for depth in range(cycles):
            for p in self.pillars:
                line = p.generate_text(seed, self.snapshot(), depth)
                self.shared_data[p.name].append(line)
                self.ground.digest(line)

                # redraw single-screen animation
                self.render()
                await asyncio.sleep(delay)

    def render(self):
        os.system("clear")  # clears the terminal before printing
        print("-" * 130)
        header = " | ".join(f"{p.name:^30}" for p in self.pillars)
        print(header)
        print("-" * 130)

        # --- pillar content (bottom up)
        max_height = max(len(p.lines) for p in self.pillars)
        for row in range(max_height):
            cols = []
            for p in self.pillars:
                idx = max_height - row - 1
                if idx < len(p.lines):
                    cols.append(f"{p.lines[idx]:30.30}")
                else:
                    cols.append(" " * 30)
            print(" | ".join(cols))

        print("-" * 130)
        print(f"{'THE EARTH SWALLOWED EVERYTHING':^130}")
        print("-" * 130)

        for g in self.ground.lines[-10:]:
            print(f"{g:^130}")


if __name__ == "__main__":
    corpus = load_corpus("corpus.txt")
    machine = FaulknerMachine(corpus)
    seed = "long still hot weary dead September afternoon"
    asyncio.run(machine.generate_story(seed, cycles=20, delay=0.5))
