"""Constants for file paths used in evaluation."""

import os

# Default file paths
DEFAULT_REFERENCE_PATH = 'ground_truth.txt'
DEFAULT_PREDICTION_PATH = 'model_generated.txt'

# Output file paths
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'eval_results')
os.makedirs(OUTPUT_DIR, exist_ok=True)

BERT_RESULTS_PATH = os.path.join(OUTPUT_DIR, 'bert_score_results.json')
BLEU_RESULTS_PATH = os.path.join(OUTPUT_DIR, 'bleu_score_results.json')
ROUGE_RESULTS_PATH = os.path.join(OUTPUT_DIR, 'rouge_score_results.json')
LLM_RESULTS_JSON_PATH = os.path.join(OUTPUT_DIR, 'llm_evaluation_results.json')
LLM_RESULTS_CSV_PATH = os.path.join(OUTPUT_DIR, 'llm_evaluation_results.csv')
LLM_RESULTS_IMG_PATH = os.path.join(OUTPUT_DIR, 'llm_evaluation_results.png')
ALL_RESULTS_PATH = os.path.join(OUTPUT_DIR, 'all_evaluation_results.json')
