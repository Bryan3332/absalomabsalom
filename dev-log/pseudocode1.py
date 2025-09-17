# Function: elongate_text
# Takes user input and stretches it into Faulknerian nightmare sentences

function elongate_text(input_text, depth=1, max_depth=3):
    if depth > max_depth:
        return input_text
    
    # Step 1: Split into words
    words = split(input_text)

    # Step 2: Mutation operations
    # a) Repetition
    repeated = randomly_repeat(words)

    # b) Insertion
    inserted = randomly_insert(repeated, fragments_from_corpus)

    # c) Conjunction chaining
    chained = glue_with_conjunctions(inserted, ["and", "but", "yet", "because"])

    # Step 3: Recurse
    mutated = elongate_text(chained, depth + 1, max_depth)

    return mutated

Key Helper Functions
randomly_repeat(words) → pick random words, repeat them multiple times. (“old old old house”)
randomly_insert(words, corpus) → sprinkle in random phrases from your Faulkner snippets or your own bank.
glue_with_conjunctions(words, conj_list) → chain clauses together with endless “and/but/because” so it feels breathless.