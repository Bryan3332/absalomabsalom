import asyncio
import random
import textwrap

# A small, handcrafted corpus of Faulkner-esque fragments for "hallucination"
# This can be expanded significantly.
CORPUS = [
    "as if the past were not a thing but a place",
    "the old, haunted silence of the South",
    "a monstrous, unholy betrayal",
    "like a ghost returning to a house long dead",
    "it was not memory but a fever dream",
    "the weight of blood and dirt and dust",
    "as if the sound itself had been silenced by the sun",
    "the ceaseless, buzzing murmur of time",
    "and the past is never dead it's not even past",
    "a cold and terrible truth",
    "an inherited curse",
]

class Character:
    """
    Represents a single character's voice and text generation logic.
    Each character has a name and unique stylistic tendencies.
    """
    def __init__(self, name, style_rules):
        self.name = name
        self.style_rules = style_rules
        self.output = []

    def generate_text(self, input_text, shared_data, depth=0):
        """
        The core recursive function for a character's text generation.
        This function will be customized for each character's voice.
        """
        if depth >= self.style_rules.get("max_depth", 3):
            return ""

        words = input_text.split()
        
        # 1. Repetition
        words = self.randomly_repeat(words)

        # 2. Insertion & "Hallucination"
        words = self.randomly_insert(words, shared_data)

        # 3. Conjunction Chaining
        text = self.glue_with_conjunctions(words)
        
        # Add Quentin's special reversal logic
        if self.name == "Quentin" and depth >= self.style_rules.get("reversal_depth", 4):
            text = self.reverse_text(text)
        
        # Add Father's specific echoing logic
        if self.name == "Father":
            text = self.echo_text(text, shared_data)

        # Append to this character's output column
        self.output.append(text)

        # Recurse
        return self.generate_text(text, shared_data, depth + 1)

    def randomly_repeat(self, words):
        """Randomly repeats words based on character's style."""
        repeated_words = []
        for word in words:
            repeated_words.append(word)
            if random.random() < self.style_rules.get("repetition_prob", 0.1):
                repeated_words.append(word)
        return repeated_words

    def randomly_insert(self, words, shared_data):
        """
        Sprinkles in fragments from the corpus and other characters' outputs.
        Includes the "hallucination" feature.
        """
        inserted_words = words[:] # A copy to avoid modifying in-place
        
        # Hallucination: Misinterpret a word
        if random.random() < self.style_rules.get("hallucination_prob", 0.05) and inserted_words:
            word_to_misinterpret = random.choice(inserted_words)
            misinterpretations = {
                "house": "horse",
                "silence": "violence",
                "earth": "birth",
                "ghost": "guilt", # Another theme-specific hallucination
                "curse": "caress" # A more poetic, sinister one
            }
            if word_to_misinterpret.lower() in misinterpretations:
                misinterpretation = misinterpretations[word_to_misinterpret.lower()]
                inserted_words[inserted_words.index(word_to_misinterpret)] = misinterpretation
            else:
                if CORPUS:
                    misinterpretation = random.choice(CORPUS).split()[0]
                    inserted_words[inserted_words.index(word_to_misinterpret)] = misinterpretation

        # Insert from corpus
        if random.random() < self.style_rules.get("corpus_insert_prob", 0.2) and CORPUS:
            fragment = random.choice(CORPUS).split()
            insertion_point = random.randint(0, len(inserted_words))
            inserted_words[insertion_point:insertion_point] = fragment

        # Referencing other columns
        if random.random() < self.style_rules.get("reference_prob", 0.1):
            other_outputs = [val for key, val in shared_data.items() if key != self.name and val]
            if other_outputs:
                random_output_list = random.choice(other_outputs)
                if random_output_list:
                    phrase_to_reference = random.choice(random_output_list).split()
                    insertion_point = random.randint(0, len(inserted_words))
                    inserted_words[insertion_point:insertion_point] = phrase_to_reference
        
        return inserted_words

    def glue_with_conjunctions(self, words):
        """Chains clauses with endless conjunctions."""
        conjunctions = self.style_rules.get("conjunctions", ["and", "but", "yet", "because"])
        text = " ".join(words)
        
        num_chains = random.randint(0, self.style_rules.get("max_chains", 2))
        for _ in range(num_chains):
            text += f" {random.choice(conjunctions)} {random.choice(words)}"
        
        return text

    def reverse_text(self, text):
        """Special method for Quentin: reverses the order of words or phrases."""
        words = text.split()
        if len(words) > 1:
            reversed_words = words[::-1] # A simple reversal
            return " ".join(reversed_words)
        return text
    
    def echo_text(self, text, shared_data):
        """Special method for Father: echoes a random phrase from other characters."""
        if random.random() < self.style_rules.get("echo_prob", 0.5):
            other_outputs = [val for key, val in shared_data.items() if key != self.name and val]
            if other_outputs:
                random_output_list = random.choice(other_outputs)
                if random_output_list:
                    phrase_to_echo = random.choice(random_output_list)
                    return f"{text} ... {phrase_to_echo}"
        return text

class StoryGenerator:
    """
    Main class to manage the story generation and asynchronous loops.
    """
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
        """Asynchronous wrapper for a character's generation loop."""
        
        # Run the generation
        character.generate_text(input_text, self.shared_data)

        # Update the shared data with the current character's output
        self.shared_data[character.name] = character.output

        # Pause to simulate async work and allow other tasks to run
        await asyncio.sleep(0.1)

    async def generate_story(self, user_input):
        """
        Runs the four character loops concurrently and combines their output.
        """
        tasks = [self.run_loop(char, user_input) for char in self.characters]

        # Use asyncio.gather to run all tasks concurrently
        await asyncio.gather(*tasks)

        # Format and combine the output
        self.format_output()

    def format_output(self):
        """
        Formats the final output into a single, cohesive story.
        This is where we'll implement the "pillars" and "ground" visual.
        """
        # Determine the maximum height of any column
        max_height = max(len(char.output) for char in self.characters)
        
        # Print the columns with a header
        header = f"{'Rosa':^30} | {'Father':^30} | {'Quentin':^30} | {'Shreve':^30}"
        print(header)
        print("=" * 128)
        
        # Print the columns
        for i in range(max_height):
            line = []
            for char in self.characters:
                text = char.output[i] if i < len(char.output) else ""
                wrapped_text = textwrap.fill(text, width=30)
                line.append(wrapped_text)
            
            print(" | ".join(line))
            print("-" * 128) # Separator

        # Final "ground" text
        final_text = ""
        for char in self.characters:
            final_text += " ".join(char.output) + " "
        
        # Elongate the final text for the "ground" effect
        final_ground = self.characters[0].glue_with_conjunctions(final_text.split())
        
        print("\n\n")
        print("THE GROUND")
        print("=" * 128)
        print(textwrap.fill(final_ground, width=120))


# Main entry point to run the program
if __name__ == "__main__":
    generator = StoryGenerator()
    user_input = input("Enter a question, thought, memory, or dream: ")
    asyncio.run(generator.generate_story(user_input))