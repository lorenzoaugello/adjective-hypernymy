import pandas as pd
import os

# === Configuration ===
input_csv = "./data/adj_def_disambig.csv"   # input file
output_dir = "output_directory"        # output directory

# Create output directory if not already existing
os.makedirs(output_dir, exist_ok=True)

# Read CSV
df = pd.read_csv(input_csv)

# Cycle each row and generate a txt file
for idx, row in df.iterrows():
    hyponym = str(row["hyponym"]).strip()
    definition = str(row["definition"]).strip()

    prompt = f"""Given the hyponym adjective "{hyponym}" with definition "{definition}", generate a list of related adjective hypernyms. Only a list of adjective hypernyms must be in the output, nothing else more. Do not re-generate the input hyponym. Respect the following guidelines:

    - The hyponym and the hypernym must be different.
    - The hyponym and the hypernym must not pertain to the same synset in the Open English WordNet.
    - Adjectives that are in the same synset need to have the same hypernym. There are many adjectives that are very similar (e.g., 'Eurasian', 'Eurasiatic', oewn-03035646-a, relating to, or coming from, Europe and Asia) and should have the same hypernym.
    - Principle of substitution: if you substitute the hyponym with the hypernym, the meaning of the phrase should not change much. There could necessarily be some loss of specificity, but the difference should only concern a broader meaning. Vice-versa, if you substitute the hypernym with the hyponym, there could be loss of meaning because the scope of the hyponym is littler that the hypernym one.
    - Inclusion of meaning principle: the meaning of the hyponym is narrower and should be included in the meaning of the hypernym, which is broader. Vice-versa, the meaning of the hypernym is not completely included in the hyponym one.
    - Hyponym and hypernym must not pertain to the same synset, because this would mean that there is a synonymy relation between them, rather than hypernymy.
    - A hyponym could have more than one hypernym.
    - Always output an adjective/s. The hypernym must be an adjective. The relation must hold between two lemmas that have the same part of speech. You cannot output a different part of speech than adjective.
    - If the input hyponym lemma could have multiple parts of speech (e.g., 'clean' could be an adjective and a verb), always consider the adjective one, as you are dealing with adjectival hypernymy.
    - For input adjectives that are polysemous (e.g., 'hard'), always consider the provided definition to disambiguate.
    - The concept should be distinct from other concepts in the wordnet. For example, "happy" and "felicitous" are synonyms, ewn-01052105-s and the examples can be substituted, e.g., "a happy life"/"a felicitous outcome". This does not mean that they can be substituted in every sense, e.g., "happy to help" but not *"felicitous to help". This is valid for synonyms, but the substitution check must always hold for hypernymy.
    - Well-defined principle: it should be possible to easily write a definition for this concept that is distinct from other concepts in Open English Wordnet.

"""

    # File name: hyponym.txt
    safe_filename = "".join(c if c.isalnum() or c in (" ", "_", "-") else "_" for c in hyponym)
    output_path = os.path.join(output_dir, f"{safe_filename}_{idx}.txt")

    # ...
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(prompt)

print(f"Prompts generati nella cartella: {output_dir}")
