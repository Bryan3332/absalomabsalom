# faulkner_machine.py
"""
Faulkner Machine v3 — Phase 3

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

from voices import mrcompson_echo, rosa_rhetorical, quentin_decay, shreve_speculation
from ground import ground_devour
from corpus_loader import load_corpus
from incest import steal_fragment

# -------- CONFIG ----------
PILLAR_CHAR_CAP = 1288
GROUND_CHAR_CAP = 1288
CYCLES = 24            # how many full rounds of 4 voices
DELAY = 0.18           # seconds between each voice output (for display)
COL_WIDTH = 28         # column width for terminal UI
CORPUS_FILENAME = "absalom-clean.txt"  # expect this in same folder as script
# ---------------------------

SCRIPT_DIR = os.path.dirname(__file__)  # folder of faulkner_machine.py
CORPUS_PATH = os.path.join(SCRIPT_DIR, "absalom-clean.txt")
CORPUS = load_corpus(CORPUS_PATH)

class Character:
    def __init__(self, name, style_rules):
        self.name = name
        self.style_rules = style_rules
        self.output = []

    def generate_text(self, input_text, shared_data, depth=0):
        words = input_text.split()

        # Core manipulations
        words = self.randomly_repeat(words)
        words = self.randomly_insert(words, shared_data)
        # Convert words to text
        text = " ".join(words)

        # Apply voice-specific helpers (externalized in voices.py)
        if self.name == "Mr Compson":
	        text = mrcompson_echo(text, shared_data, self.name)
        elif self.name == "Rosa":
            text = rosa_rhetorical(text)
        elif self.name == "Quentin":
            text = quentin_decay(text, depth) #depth only applies to Quentin
        elif self.name == "Shreve":
            text = shreve_speculation(text)

        # Save output (this column)
        self.output.append(text)

         # Enforce 1288 character cap on pillar
        joined = " ".join(self.output)
        if len(joined) > 1288:
            truncated = joined[:1288]  # cut off at 1288 characters
            self.output = [truncated]  # reset output to a single truncated string


    def randomly_repeat(self, words):
        repeated_words = []
        for word in words:
            repeated_words.append(word)
            if random.random() < self.style_rules.get("repetition_prob", 0.1):
                repeated_words.append(word)
        return repeated_words

    def randomly_insert(self, words, shared_data):
        inserted_words = words[:]  # copy

        # Hallucination: misinterpret a word
        if random.random() < self.style_rules.get("hallucination_prob", 0.05) and inserted_words:
            word_to_misinterpret = random.choice(inserted_words)
            misinterpretations = {
                "house": "horse",
                "silence": "violence",
                "earth": "birth",
                "ghost": "guilt",
                "curse": "caress"
            }
            lower = word_to_misinterpret.lower()
            if lower in misinterpretations:
                inserted_words[inserted_words.index(word_to_misinterpret)] = misinterpretations[lower]
            else:
                if CORPUS:
                    # use first token of a random fragment as a small misinterpretation
                    misinterpretation = random.choice(CORPUS).split()[0]
                    inserted_words[inserted_words.index(word_to_misinterpret)] = misinterpretation

        # Insert from corpus
        if random.random() < self.style_rules.get("corpus_insert_prob", 0.2) and CORPUS:
            fragment = random.choice(CORPUS).split()
            insertion_point = random.randint(0, max(0, len(inserted_words)))
            inserted_words[insertion_point:insertion_point] = fragment

        # Referencing other columns (steal phrases)
        if random.random() < self.style_rules.get("reference_prob", 0.1):
            other_outputs = [val for key, val in shared_data.items() if key != self.name and val]
            if other_outputs:
                random_output_list = random.choice(other_outputs)
                if random_output_list:
                    phrase_to_reference = random.choice(random_output_list).split()
                    insertion_point = random.randint(0, max(0, len(inserted_words)))
                    inserted_words[insertion_point:insertion_point] = phrase_to_reference

        return inserted_words


class StoryGenerator:
    def __init__(self):
        self.shared_data = {
            "Mr Compson": [],
            "Rosa": [],
            "Quentin": [],
            "Shreve": []
        }
        self.ground = [] #holds the earth's fragments

        self.characters = [
            Character("Mr Compson", {
                "max_depth": 4, "repetition_prob": 0.05, "corpus_insert_prob": 0.05,
                "hallucination_prob": 0.05, "reference_prob": 0.3,
            }),
            Character("Rosa", {
                "max_depth": 5, "repetition_prob": 0.2, "corpus_insert_prob": 0.3,
                "hallucination_prob": 0.1, "reference_prob": 0.15,
            }),
            Character("Quentin", {
                "max_depth": 6, "repetition_prob": 0.4, "corpus_insert_prob": 0.25,
                "hallucination_prob": 0.2, "reference_prob": 0.2,
            }),
            Character("Shreve", {
                "max_depth": 5, "repetition_prob": 0.1, "corpus_insert_prob": 0.1,
                "hallucination_prob": 0.05, "reference_prob": 0.1,
            }),
        ]


    async def generate_story(self, user_input, cycles=10, delay=0.2):
        depth = 0
        for _ in range(cycles):
            for char in self.characters:
                # grow this pillar
                char.generate_text(user_input, self.shared_data, depth)
                self.shared_data[char.name] = char.output

                # ground devours whatever just grew
                if char.output:
                    fragment = char.output[-1]  # latest line
                    devoured = ground_devour(fragment)
                    self.ground.append(devoured)

                    # Enforce 1288 character cap on ground
                    joined_ground = " ".join(self.ground)
                    if len(joined_ground) > 1288:
                        truncated_ground = joined_ground[:1288]
                        self.ground = [truncated_ground]

                # show scene as it builds
                self.format_output()
                await asyncio.sleep(delay)
            
            depth += 1  # increase after each full round of characters


    def format_output(self, col_width=30):
        """
        Print pillars rising upward with the ground swallowing lines.
        """
        height = max(len(char.output) for char in self.characters)
        names = [char.name for char in self.characters]

        # Wrap ground into lines (downward growth)
        ground_text = " ".join(self.ground)
        ground_lines = textwrap.wrap(ground_text, width=col_width)

        max_rows = max(height, len(ground_lines))

        print("\n" + "-" * (col_width * len(names) + len(names) - 1 + 4))
        for row in range(max_rows):
            row_cells = []
            for char in self.characters:
                if row < len(char.output):
                    row_cells.append(char.output[row][:col_width].ljust(col_width))
                else:
                    row_cells.append("".ljust(col_width))

            g_line = ground_lines[row] if row < len(ground_lines) else ""
            print(" | ".join(row_cells) + " || " + g_line)
        print("-" * (col_width * len(names) + len(names) - 1 + 4))


if __name__ == "__main__":
    generator = StoryGenerator()
    user_input = input("Enter a question, thought, memory, or dream: ")
    asyncio.run(generator.generate_story(user_input))
