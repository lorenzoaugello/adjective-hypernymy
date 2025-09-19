import pandas as pd
import os
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# === Configuration ===
input_csv = "./data/adjectives_def.csv"   # your input file
output_dir = "prompts"                    # output folder for prompts
responses_dir = "responses"               # output folder for model responses

# Create output directories if they don't exist
os.makedirs(output_dir, exist_ok=True)
os.makedirs(responses_dir, exist_ok=True)

# Load SmolLM-360M model
print("Loading SmolLM-360M model...")
model_name = "HuggingFaceTB/SmolLM-360M"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Set pad token if not already set
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

# Move model to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
print(f"Model loaded on device: {device}")

# Read the CSV
print("Reading CSV file...")
df = pd.read_csv(input_csv)

# Generation parameters
max_new_tokens = 150
temperature = 0.7
do_sample = True

print(f"Processing {len(df)} adjectives...")

# Loop through each row and generate prompt + response
for idx, row in df.iterrows():
    hyponym = str(row["hyponym"]).strip()
    definition = str(row["definition"]).strip()

    print(f"Processing {idx+1}/{len(df)}: {hyponym}")

    prompt = f"""Given the hyponym adjective "{hyponym}" with definition "{definition}", generate a list of related adjective hypernyms, respecting the following guidelines:
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

Hypernyms for "{hyponym}":"""

    # Clean filename (remove special characters)
    safe_filename = "".join(c if c.isalnum() or c in (" ", "_", "-") else "_" for c in hyponym)

    # Save prompt
    prompt_path = os.path.join(output_dir, f"{safe_filename}.txt")
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt)

    # Generate response using SmolLM-360M
    try:
        # Tokenize input
        inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True, max_length=2048)
        inputs = {k: v.to(device) for k, v in inputs.items()}

        # Generate response
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=do_sample,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id
            )

        # Decode response
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract only the generated part (remove the original prompt)
        generated_text = response[len(prompt):].strip()

        # Save response
        response_path = os.path.join(responses_dir, f"{safe_filename}_response.txt")
        with open(response_path, "w", encoding="utf-8") as f:
            f.write(f"Hyponym: {hyponym}\n")
            f.write(f"Definition: {definition}\n")
            f.write(f"Generated Hypernyms:\n{generated_text}\n")

        print(f"  ✓ Generated response saved")

    except Exception as e:
        print(f"  ✗ Error generating response for {hyponym}: {str(e)}")

        # Save error log
        error_path = os.path.join(responses_dir, f"{safe_filename}_error.txt")
        with open(error_path, "w", encoding="utf-8") as f:
            f.write(f"Hyponym: {hyponym}\n")
            f.write(f"Definition: {definition}\n")
            f.write(f"Error: {str(e)}\n")

print(f"\nProcessing completed!")
print(f"Prompts generated in folder: {output_dir}")
print(f"Responses generated in folder: {responses_dir}")
