# getting-hypernyms

Script that sends .txt prompts to a local Ollama model and saves only the model responses.

## Setup
```bash
python -m venv .venv
source .venv/bin/activate   # Windows PowerShell: . .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run
```bash
python main.py
# or with overrides:
python main.py --model llama2 --input-dir prompts_directory --output-dir output_directory --host http://localhost:11434
```

Default directories:
- prompts_directory/  
- output_directory/  

Environment variables accepted:
- MODEL_NAME, INPUT_DIR, OUTPUT_DIR, OLLAMA_HOST, REQUEST_DELAY
