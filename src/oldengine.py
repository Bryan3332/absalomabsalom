# faulkner_machine.py
import asyncio
import random
import textwrap

from voices import rosa_rhetorical, quentin_decay, shreve_speculation, father_echo
from corpus_loader import load_corpus

# Load Faulkner fragments from txt (adjust filename if yours differs)
CORPUS = load_corpus("absalom-clean.txt")


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
        text = self.glue_with_conjunctions(words)

        # Apply voice-specific helpers (externalized in voices.py)
        if self.name == "Rosa":
            text = rosa_rhetorical(text)
        elif self.name == "Quentin":
            text = quentin_decay(text, depth)
        elif self.name == "Shreve":
            text = shreve_speculation(text)
        elif self.name == "Father":
            text = father_echo(text, shared_data, self.name)

        # Save output (this column)
        self.output.append(text)

        # Recurse
        return self.generate_text(text, shared_data, depth + 1)

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

    def glue_with_conjunctions(self, words):
        conjunctions = self.style_rules.get("conjunctions", ["and", "but", "yet", "because"])
        text = " ".join(words)

        num_chains = random.randint(0, self.style_rules.get("max_chains", 2))
        for _ in range(num_chains):
            # choose a random word to chain with
            if words:
                text += f" {random.choice(conjunctions)} {random.choice(words)}"
        return text


class StoryGenerator:
    def __init__(self):
        self.shared_data = {
            "Rosa": [],
            "Father": [],
            "Quentin": [],
            "Shreve": []
        }

        self.characters = [
            Character("Rosa", {
                "max_depth": 5, "repetition_prob": 0.2, "corpus_insert_prob": 0.3,
                "hallucination_prob": 0.1, "reference_prob": 0.15,
                "conjunctions": ["and", "but", "so"], "max_chains": 3,
            }),
            Character("Father", {
                "max_depth": 4, "repetition_prob": 0.05, "corpus_insert_prob": 0.05,
                "hallucination_prob": 0.05, "reference_prob": 0.3,
                "conjunctions": ["and then"], "max_chains": 1, "echo_prob": 0.5,
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

    async def run_loop(self, character, input_text):
        # run the generation
        character.generate_text(input_text, self.shared_data)

        # update shared data
        self.shared_data[character.name] = character.output

        # small pause so other tasks can run
        await asyncio.sleep(0.05)

    async def generate_story(self, user_input):
        tasks = [self.run_loop(char, user_input) for char in self.characters]
        await asyncio.gather(*tasks)
        # after generation, format output (pillars + ground)
        self.format_output()

    def format_output(self, col_width=30):
        """
        Print side-by-side columns (pillars) and then a Ground chorus that has
        been passed deterministically through all four voice helpers.
        """
        # prepare wrapped lines for each cell per depth
        # determine number of rows (depth levels)
        max_height = max(len(char.output) for char in self.characters)

        # header
        headers = [char.name for char in self.characters]
        header_line = " | ".join(h.center(col_width) for h in headers)
        sep_line = "-" * len(header_line)
        print(header_line)
        print(sep_line)

        # for each depth row, print each column with proper wrapping/padding
        for i in range(max_height):
            # get wrapped lines per column for this depth
            wrapped_columns = []
            for char in self.characters:
                text = char.output[i] if i < len(char.output) else ""
                wrapped = textwrap.wrap(text, width=col_width) or [""]
                wrapped_columns.append(wrapped)

            # compute max lines needed for this row (because columns may wrap differently)
            max_lines = max(len(w) for w in wrapped_columns)

            # print line-by-line for this row
            for line_idx in range(max_lines):
                row_cells = []
                for col_wrapped in wrapped_columns:
                    cell_line = col_wrapped[line_idx] if line_idx < len(col_wrapped) else ""
                    row_cells.append(cell_line.ljust(col_width))
                print(" | ".join(row_cells))
            print(sep_line)

        # --- Build the Ground (true chorus) ---
        all_text = []
        for char in self.characters:
            all_text.extend(char.output)

        combined = " ".join(all_text).strip()

        # Force a deeper decay value based on configured max depths
        max_depth_val = max(c.style_rules.get("max_depth", 3) for c in self.characters)
        decay_depth = max_depth_val + 2

        # deterministically pass through each helper (in sequence)
        combined = rosa_rhetorical(combined)
        combined = quentin_decay(combined, decay_depth)
        combined = shreve_speculation(combined)
        combined = father_echo(combined, self.shared_data, "Ground")

        # glue to make the run-on swamp effect
        ground = self.characters[0].glue_with_conjunctions(combined.split())

        print("\n\nTHE GROUND")
        print("=" * (col_width * 4 + 3 * 3))
        print(textwrap.fill(ground, width=col_width * 4 + 3 * 3))


if __name__ == "__main__":
    generator = StoryGenerator()
    user_input = input("Enter a question, thought, memory, or dream: ")
    asyncio.run(generator.generate_story(user_input))
