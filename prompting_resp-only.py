#!/usr/bin/env python3
"""
Script that saves only the model responses without prompts or metadata.
"""

import os
import json
import time
import google.generativeai as genai
from datetime import datetime

# === Configuration ===
MODEL_NAME = "model_name"
INPUT_DIR = "prompts_directory"
OUTPUT_DIR = "output_directory"

# Generation parameters
MAX_OUTPUT_TOKENS = 2048
TEMPERATURE = 0.7
TOP_P = 0.9
REQUEST_DELAY = 1  # seconds between requests

def setup_api():
    """Initialize the Google AI Studio API."""
    # Option 1: 
    # api_key = ""

    # Option 2: 
    api_key = os.getenv('GOOGLE_AI_STUDIO_API_KEY')

    if not api_key:
        print("Error: API key not found")
        return None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=MAX_OUTPUT_TOKENS,
                temperature=TEMPERATURE,
                top_p=TOP_P,
            )
        )
        return model
    except Exception as e:
        print(f"Error setting up API: {e}")
        return None

def generate_response(model, prompt):
    """Generate clean response."""
    try:
        response = model.generate_content(prompt)

        if response.candidates[0].finish_reason.name == "SAFETY":
            return "[Response blocked by safety filters]"

        if response.candidates[0].finish_reason.name == "RECITATION":
            return "[Response blocked due to recitation concerns]"

        return response.text.strip() if response.text else "[No response generated]"

    except Exception as e:
        return f"[Error: {str(e)}]"

def main():
    """Main processing function."""
    # Setup
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if not os.path.exists(INPUT_DIR):
        print(f"Creating {INPUT_DIR} directory...")
        os.makedirs(INPUT_DIR, exist_ok=True)
        print(f"Add your .txt prompt files to {INPUT_DIR}/")
        return

    model = setup_api()
    if not model:
        return

    # Get prompt files
    txt_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.txt')]

    if not txt_files:
        print(f"No .txt files found in {INPUT_DIR}/")
        return

    print(f"Processing {len(txt_files)} files...")

    # Process each file
    for i, filename in enumerate(txt_files, 1):
        print(f"[{i}/{len(txt_files)}] {filename}")

        input_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)

        try:
            # Read prompt
            with open(input_path, 'r', encoding='utf-8') as f:
                prompt = f.read().strip()

            if not prompt:
                continue

            # Generate and save clean response
            response = generate_response(model, prompt)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(response)

            print(f"  ✓ Response saved")

            # Rate limiting
            if REQUEST_DELAY > 0 and i < len(txt_files):
                time.sleep(REQUEST_DELAY)

        except Exception as e:
            print(f"  ✗ Error: {e}")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"[Processing Error: {str(e)}]")

    print(f"\nComplete! Clean responses saved to {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
