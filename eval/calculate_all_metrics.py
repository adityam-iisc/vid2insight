# filepath: /Users/ankitku5/Desktop/Data_seicene_college_project/eval/metrics/calculate_all_metrics.py
"""Calculate all evaluation metrics (BERT, BLEU, ROUGE, LLM) between ground truth and model generated text."""

import os
import importlib.util
import argparse
import json
import time
from agent.config.initialize_logger import setup_logger
from eval.constants.paths import (
    DEFAULT_REFERENCE_PATH, DEFAULT_PREDICTION_PATH, 
    ALL_RESULTS_PATH, BERT_RESULTS_PATH, BLEU_RESULTS_PATH, ROUGE_RESULTS_PATH, LLM_RESULTS_JSON_PATH
)
from eval.constants.criteria import DEFAULT_AUTO_METRICS, DEFAULT_LLM_METRICS, DEFAULT_ALL_METRICS

# Set up logger
logger = setup_logger()

def check_module_installed(module_name):
    """Check if a Python module is installed."""
    return importlib.util.find_spec(module_name) is not None

def run_bert_score_evaluation(reference_path, prediction_path):
    """Run BERT score evaluation."""
    try:
        logger.info("Running BERT score evaluation...")
        
        if not check_module_installed('bert_score'):
            logger.error("bert-score package not installed. Please install it with 'pip install bert-score'")
            return None
        
        # Import the calculate_bert_score function from our metrics module
        from eval.metrics.calculate_bert_score import calculate_bert_score
        
        # Calculate BERT score
        results = calculate_bert_score(reference_path, prediction_path)
        return results
        
    except Exception as e:
        logger.error(f"Error running BERT score evaluation: {e}")
        return None

def run_bleu_score_evaluation(reference_path, prediction_path):
    """Run BLEU score evaluation."""
    try:
        logger.info("Running BLEU score evaluation...")
        
        if not check_module_installed('nltk'):
            logger.error("nltk package not installed. Please install it with 'pip install nltk'")
            return None
        
        # Import the calculate_bleu_score function from our metrics module
        from eval.metrics.calculate_bleu_score import calculate_bleu_score
        
        # Calculate BLEU score
        results = calculate_bleu_score(reference_path, prediction_path)
        return results
        
    except Exception as e:
        logger.error(f"Error running BLEU score evaluation: {e}")
        return None

def run_rouge_score_evaluation(reference_path, prediction_path):
    """Run ROUGE score evaluation."""
    try:
        logger.info("Running ROUGE score evaluation...")
        
        if not check_module_installed('rouge'):
            logger.error("rouge package not installed. Please install it with 'pip install rouge'")
            return None
        
        # Import the calculate_rouge_score function from our metrics module
        from eval.metrics.calculate_rouge_score import calculate_rouge_score
        
        # Calculate ROUGE score
        results = calculate_rouge_score(reference_path, prediction_path)
        return results
        
    except Exception as e:
        logger.error(f"Error running ROUGE score evaluation: {e}")
        return None

def run_llm_evaluation(reference_path, prediction_path):
    """Run LLM-based evaluation."""
    try:
        logger.info("Running LLM-based evaluation...")
        
        # Import the run function from llm_evaluation.py
        from eval.llm_evaluation import run as run_llm_eval
        
        # Run LLM evaluation
        results = run_llm_eval(reference_path, prediction_path)
        return results
        
    except Exception as e:
        logger.error(f"Error running LLM evaluation: {e}")
        return None

def calculate_all_metrics(reference_path=DEFAULT_REFERENCE_PATH, prediction_path=DEFAULT_PREDICTION_PATH, metrics=None):
    """Calculate all evaluation metrics."""
    try:
        if metrics is None:
            metrics = DEFAULT_ALL_METRICS
        
        logger.info(f"Calculating metrics: {', '.join(metrics)}")
        
        all_results = {}
        
        # Run automatic metrics
        if 'bert' in metrics:
            logger.info("=== Running BERT Score Evaluation ===")
            bert_results = run_bert_score_evaluation(reference_path, prediction_path)
            if bert_results:
                all_results['bert'] = bert_results
        
        if 'bleu' in metrics:
            logger.info("=== Running BLEU Score Evaluation ===")
            bleu_results = run_bleu_score_evaluation(reference_path, prediction_path)
            if bleu_results:
                all_results['bleu'] = bleu_results
        
        if 'rouge' in metrics:
            logger.info("=== Running ROUGE Score Evaluation ===")
            rouge_results = run_rouge_score_evaluation(reference_path, prediction_path)
            if rouge_results:
                all_results['rouge'] = rouge_results
        
        # Run LLM-based evaluation
        if 'llm' in metrics:
            logger.info("=== Running LLM Evaluation ===")
            llm_results = run_llm_evaluation(reference_path, prediction_path)
            if llm_results:
                all_results['llm'] = llm_results
        
        # Save combined results
        if all_results:
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(ALL_RESULTS_PATH), exist_ok=True)
            
            with open(ALL_RESULTS_PATH, 'w') as f:
                json.dump(all_results, f, indent=4)
                
            logger.info(f"All evaluation results saved to {ALL_RESULTS_PATH}")
        
        return all_results
        
    except Exception as e:
        logger.error(f"Error calculating all metrics: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Calculate evaluation metrics between reference and prediction texts.')
    parser.add_argument('--reference', type=str, default=DEFAULT_REFERENCE_PATH,
                        help=f'Path to the reference text file (default: {DEFAULT_REFERENCE_PATH})')
    parser.add_argument('--prediction', type=str, default=DEFAULT_PREDICTION_PATH,
                        help=f'Path to the prediction text file (default: {DEFAULT_PREDICTION_PATH})')
    parser.add_argument('--metrics', type=str, nargs='+', default=DEFAULT_ALL_METRICS,
                        help=f'Metrics to calculate (default: {" ".join(DEFAULT_ALL_METRICS)})')
    args = parser.parse_args()
    
    calculate_all_metrics(args.reference, args.prediction, args.metrics)

if __name__ == "__main__":
    main()
