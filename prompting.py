#!/usr/bin/env python3
"""
Google AI Studio model prompting script for adjective hypernymy research.
Uses Google's Gemini models via API instead of local models.
"""

import os
import json
import time
import google.generativeai as genai
from datetime import datetime

# === Configuration ===
# Available models:
# - "gemini-1.5-flash" (fast, efficient)
# - "gemini-1.5-pro" (high quality, slower)
# - "gemini-1.0-pro" (standard quality)

MODEL_NAME = "gemini-1.5-flash"
INPUT_DIR = "prompts"
OUTPUT_DIR = "outputs_2.0"

# Generation parameters
MAX_OUTPUT_TOKENS = 2048
TEMPERATURE = 0.7
TOP_P = 0.9

# Rate limiting (to avoid hitting API limits)
REQUEST_DELAY = 1  # seconds between requests

def setup_api():
    """Initialize the Google AI Studio API."""
    # Option 1: Set API key directly in script (less secure)
    # Uncomment the line below and replace with your actual API key
    # api_key = ""

    # Option 2: Get API key from environment variable (recommended)
    api_key = os.getenv('GOOGLE_AI_STUDIO_API_KEY')

    if not api_key:
        print("Error: GOOGLE_AI_STUDIO_API_KEY environment variable not set")
        print("\nTo set up your API key:")
        print("1. Go to https://makersuite.google.com/app/apikey")
        print("2. Create a new API key")
        print("3. Either:")
        print("   Option A - Set environment variable:")
        print("   export GOOGLE_AI_STUDIO_API_KEY='your-api-key-here'")
        print("   (or add it to your .bashrc/.zshrc)")
        print("   Option B - Edit this script and uncomment the api_key line")
        return None

    try:
        # Configure the API
        genai.configure(api_key=api_key)

        # Create model instance
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=MAX_OUTPUT_TOKENS,
                temperature=TEMPERATURE,
                top_p=TOP_P,
            )
        )

        print(f"Successfully initialized Google AI Studio API with model: {MODEL_NAME}")
        return model

    except Exception as e:
        print(f"Error setting up Google AI Studio API: {e}")
        return None

def generate_response(model, prompt):
    """Generate response for a given prompt using Google AI Studio."""
    try:
        # Generate response
        response = model.generate_content(prompt)

        # Check if response was blocked
        if response.candidates[0].finish_reason.name == "SAFETY":
            return "Response blocked due to safety filters"

        if response.candidates[0].finish_reason.name == "RECITATION":
            return "Response blocked due to recitation concerns"

        # Extract the text response
        if response.text:
            return response.text.strip()
        else:
            return "No response generated"

    except Exception as e:
        return f"Error generating response: {str(e)}"

def process_prompts():
    """Main function to process all prompts."""
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Check if input directory exists
    if not os.path.exists(INPUT_DIR):
        print(f"Input directory '{INPUT_DIR}' not found. Creating it...")
        os.makedirs(INPUT_DIR, exist_ok=True)
        print(f"Please add your prompt files (.txt) to the '{INPUT_DIR}' directory")
        return

    # Setup API
    model = setup_api()
    if not model:
        return

    # Get all text files in input directory
    txt_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.txt')]

    if not txt_files:
        print(f"No .txt files found in '{INPUT_DIR}' directory")
        return

    print(f"Found {len(txt_files)} prompt files to process")

    if REQUEST_DELAY > 0:
        print(f"Rate limiting enabled: {REQUEST_DELAY} second delay between requests")

    # Process each file
    results_summary = []

    for i, filename in enumerate(txt_files, 1):
        print(f"\nProcessing {i}/{len(txt_files)}: {filename}")

        input_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)

        try:
            # Read prompt
            with open(input_path, 'r', encoding='utf-8') as f:
                prompt = f.read().strip()

            if not prompt:
                print(f"Warning: {filename} is empty, skipping...")
                continue

            print(f"Generating response for: {filename[:50]}...")

            # Generate response
            response = generate_response(model, prompt)

            # Save only the response (no prompt, no metadata)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(response)

            # Add to summary
            results_summary.append({
                'filename': filename,
                'status': 'success',
                'prompt_length': len(prompt),
                'response_length': len(response)
            })

            print(f"✓ Saved response to: {output_path}")

            # Rate limiting delay
            if REQUEST_DELAY > 0 and i < len(txt_files):
                print(f"Waiting {REQUEST_DELAY} seconds before next request...")
                time.sleep(REQUEST_DELAY)

        except Exception as e:
            error_msg = f"Error processing {filename}: {str(e)}"
            print(f"✗ {error_msg}")

            # Save error to output file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"ERROR: {error_msg}\n\nPrompt file: {filename}\nModel: {MODEL_NAME}\nTime: {datetime.now().isoformat()}")

            results_summary.append({
                'filename': filename,
                'status': 'error',
                'error': str(e)
            })

    # Save summary
    summary_path = os.path.join(OUTPUT_DIR, 'processing_summary.json')
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump({
            'model': MODEL_NAME,
            'timestamp': datetime.now().isoformat(),
            'total_files': len(txt_files),
            'successful': len([r for r in results_summary if r['status'] == 'success']),
            'failed': len([r for r in results_summary if r['status'] == 'error']),
            'generation_config': {
                'max_output_tokens': MAX_OUTPUT_TOKENS,
                'temperature': TEMPERATURE,
                'top_p': TOP_P
            },
            'results': results_summary
        }, f, indent=2)

    print(f"\n=== Processing Complete ===")
    print(f"Total files: {len(txt_files)}")
    print(f"Successful: {len([r for r in results_summary if r['status'] == 'success'])}")
    print(f"Failed: {len([r for r in results_summary if r['status'] == 'error'])}")
    print(f"Summary saved to: {summary_path}")

def test_api_connection():
    """Test the API connection with a simple prompt."""
    print("Testing API connection...")

    model = setup_api()
    if not model:
        return False

    try:
        test_prompt = "Say 'Hello, this is a test of the Google AI Studio API connection.'"
        response = generate_response(model, test_prompt)

        if "Error" in response:
            print(f"API test failed: {response}")
            return False
        else:
            print(f"✓ API test successful: {response[:100]}...")
            return True

    except Exception as e:
        print(f"API test failed: {e}")
        return False

def main():
    """Main entry point."""
    print("=== Google AI Studio Model Prompting Script ===")
    print(f"Using model: {MODEL_NAME}")
    print(f"Input directory: {INPUT_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print()

    # Test API connection first
    if not test_api_connection():
        print("\nAPI connection test failed. Please check your API key and try again.")
        return

    print()

    try:
        process_prompts()
    except KeyboardInterrupt:
        print("\n\nProcessing interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

if __name__ == "__main__":
    main()
