# faulkner_machine.py
import asyncio
import random
import textwrap
import os

from voices import mrcompson_echo, rosa_rhetorical, quentin_decay, shreve_speculation
from ground import ground_devour
from corpus_loader import load_corpus

SCRIPT_DIR = os.path.dirname(__file__)  # folder of faulkner_machine.py
CORPUS_PATH = os.path.join(SCRIPT_DIR, "absalom-clean.txt")
CORPUS = load_corpus(CORPUS_PATH)

class Character:
    def __init__(self, name, style_rules):
        self.name = name
        self.style_rules = style_rules
        self.output = []

    def generate_text(self, input_text, shared_data, depth=0):
        if depth >= self.style_rules.get("max_depth", 3):
            return ""

        words = input_text.split()

        # Core manipulations
        words = self.randomly_repeat(words)
        words = self.randomly_insert(words, shared_data)

        # Apply voice-specific helpers (externalized in voices.py)
        if self.name == "Mr Compson":
	        text = mrcompson_echo(text, shared_data, self.name)
        elif self.name == "Rosa":
            text = rosa_rhetorical(text)
        elif self.name == "Quentin":
            text = quentin_decay(text, depth)
        elif self.name == "Shreve":
            text = shreve_speculation(text)

        # Save output (this column)
        self.output.append(text)


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
                "conjunctions": ["and then"], "max_chains": 1, "echo_prob": 0.5,
            }),
            Character("Rosa", {
                "max_depth": 5, "repetition_prob": 0.2, "corpus_insert_prob": 0.3,
                "hallucination_prob": 0.1, "reference_prob": 0.15,
                "conjunctions": ["and", "but", "so"], "max_chains": 3,
            }),
            Character("Quentin", {
                "max_depth": 6, "repetition_prob": 0.4, "corpus_insert_prob": 0.25,
                "hallucination_prob": 0.2, "reference_prob": 0.2,
                "conjunctions": ["and", "or", "for"], "max_chains": 4, "reversal_depth": 4,
            }),
            Character("Shreve", {
                "max_depth": 5, "repetition_prob": 0.1, "corpus_insert_prob": 0.1,
                "hallucination_prob": 0.05, "reference_prob": 0.1,
                "conjunctions": ["if", "so that"], "max_chains": 2,
            }),
        ]


    async def generate_story(self, user_input, cycles=10, delay=0.2):
        for _ in range(cycles):
            for char in self.characters:
                # grow this pillar
                char.generate_text(user_input, self.shared_data)
                self.shared_data[char.name] = char.output

                # ground devours whatever just grew
                if char.output:
                    fragment = char.output[-1]  # latest line
                    devoured = ground_devour(fragment)
                    self.ground.append(devoured)

                # show scene as it builds
                self.format_output()
                await asyncio.sleep(delay)


    def format_output(self, col_width=30):
        """
        Print pillars rising upward with the ground swallowing lines.
        """
        height = max(len(char.output) for char in self.characters)
        names = [char.name for char in self.characters]

        print("\n" + "-" * (col_width * len(names) + len(names) - 1 + 4))
        for row in range(height):
            row_cells = []
            for char in self.characters:
                if row < len(char.output):
                    row_cells.append(char.output[row][:col_width].ljust(col_width))
                else:
                    row_cells.append("".ljust(col_width))
            ground_text = self.ground[row] if row < len(self.ground) else ""
            print(" | ".join(row_cells) + " || " + ground_text)
        print("-" * (col_width * len(names) + len(names) - 1 + 4))


if __name__ == "__main__":
    generator = StoryGenerator()
    user_input = input("Enter a question, thought, memory, or dream: ")
    asyncio.run(generator.generate_story(user_input))
