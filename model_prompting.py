import os
from transformers import AutoTokenizer, AutoModelForCausalLM

# === Config ===
model_name = "HuggingFaceTB/SmolLM-360M-Instruct"  # adjust as needed
input_dir = "prompts"    # folder with txt files
output_dir = "outputs"   # folder to save generated outputs

os.makedirs(output_dir, exist_ok=True)

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
model.eval()  # set model to evaluation mode

# Optional: move to GPU if available
import torch
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

# Iterate over txt files
for filename in os.listdir(input_dir):
    if not filename.endswith(".txt"):
        continue

    input_path = os.path.join(input_dir, filename)
    with open(input_path, "r", encoding="utf-8") as f:
        prompt = f.read()

    # Tokenize and generate
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=150,   # adjust output length
        do_sample=True,       # enable sampling for more natural outputs
        temperature=0.7       # creativity parameter
    )

    text_out = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Save output
    output_path = os.path.join(output_dir, filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text_out)

    print(f"Processed {filename} → {output_path}")
