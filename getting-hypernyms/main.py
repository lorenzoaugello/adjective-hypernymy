#!/usr/bin/env python3
"""
main.py

"""

import os
import time
import argparse
import logging
from pathlib  import Path
from ollama import Client


DEFAULT_MODEL = os.getenv("MODEL_NAME", "llama2")
DEFAULT_INPUT_DIR = os.getenv("INPUT_DIR", "prompts_directory")
DEFAULT_OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output_directory")
DEFAULT_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_DELAY = float(os.getenv("REQUEST_DELAY", "1"))

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("clean-responses")

def setup_client(host: str) -> Client:
    try:
        client = Client(host=host)
        return client
    except Exception as e:
        logger.error(f"Failed to create Ollama client: {e}")
        raise

def generate_response(client: Client, model: str, prompt: str) -> str:
    try:
        resp = client.generate(model=model, prompt=prompt)
        text = getattr(resp, "response", None) or getattr(resp, "text", None) or getattr(resp, "content", None) or str(resp)
        return text.strip() if text else "[No response generated]"
    except Exception as e:
        return f"[Error: {e}]"

def process_files(client: Client, model: str, input_dir: Path, output_dir: Path, delay: float):
    output_dir.mkdir(parents=True, exist_ok=True)
    txt_files = sorted([p for p in input_dir.iterdir() if p.suffix == ".txt"])
    if not txt_files:
        logger.info(f"No .txt files found in {input_dir}")
        return
    logger.info(f"Processing {len(txt_files)} files (model={model})...")
    for i, src_path in enumerate(txt_files, start=1):
        dst_path = output_dir / src_path.name
        logger.info(f"[{i}/{len(txt_files)}] {src_path.name}")
        try:
            prompt = src_path.read_text(encoding="utf-8").strip()
            if not prompt:
                logger.info("  (empty prompt, skipping)")
                continue
            response = generate_response(client, model, prompt)
            dst_path.write_text(response, encoding="utf-8")
            logger.info("  Response saved")
        except Exception as e:
            logger.error(f"  Error processing {src_path.name}: {e}")
            dst_path.write_text(f"[Processing Error: {e}]", encoding="utf-8")
        if delay > 0 and i < len(txt_files):
            time.sleep(delay)
    logger.info(f"\nComplete! Clean responses saved to {output_dir}/")

def main():
    parser = argparse.ArgumentParser(description="Generate model responses with Ollama and save outputs.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model name hosted on Ollama")
    parser.add_argument("--input-dir", default=DEFAULT_INPUT_DIR, help="Directory with .txt prompt files")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="Directory to save responses")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Ollama host (e.g. http://localhost:11434)")
    parser.add_argument("--delay", type=float, default=DEFAULT_DELAY, help="Seconds to wait between requests")
    args = parser.parse_args()
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    if not input_dir.exists():
        input_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created {input_dir}. Add .txt prompt files there and re-run.")
        return
    client = setup_client(args.host)
    process_files(client, args.model, input_dir, output_dir, args.delay)

if __name__ == "__main__":
    main()
