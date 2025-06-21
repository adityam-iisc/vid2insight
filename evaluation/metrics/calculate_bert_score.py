"""Calculating BERT Score between ground truth and model generated text."""

import os
import argparse
import json
from bert_score import score
from agent.config.initialize_logger import setup_logger
from evaluation.constants.paths import DEFAULT_REFERENCE_PATH, DEFAULT_PREDICTION_PATH, BERT_RESULTS_PATH
from evaluation.config.model_config import BERT_CONFIG

# Set up logger
logger = setup_logger()

def read_file(file_path):
    """Reading from txt file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        raise

def calculate_bert_score(reference_path=DEFAULT_REFERENCE_PATH, prediction_path=DEFAULT_PREDICTION_PATH):
    """Calculate BERT score between reference and prediction texts."""
    try:
        reference = read_file(reference_path)
        prediction = read_file(prediction_path)
        
        # Print the first 100 characters of each file for verification
        logger.info("Reference text (first 100 chars): %s", reference[:100])
        logger.info("Prediction text (first 100 chars): %s", prediction[:100])
        
        # Calculate BERT score using config
        P, R, F1 = score([prediction], [reference], 
                         lang=BERT_CONFIG['language'],
                         model_type=BERT_CONFIG['model_type'],
                         num_layers=BERT_CONFIG['num_layers'],
                         batch_size=BERT_CONFIG['batch_size'],
                         verbose=True)
        
        precision = P.mean().item()
        recall = R.mean().item()
        f1 = F1.mean().item()
        
        logger.info("\nBERT Score Results:")
        logger.info(f"Precision: {precision:.4f}")
        logger.info(f"Recall: {recall:.4f}")
        logger.info(f"F1: {f1:.4f}")
        
        # Save results to JSON file
        results = {
            "precision": precision,
            "recall": recall,
            "f1": f1
        }
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(BERT_RESULTS_PATH), exist_ok=True)
        
        with open(BERT_RESULTS_PATH, 'w') as f:
            json.dump(results, f, indent=4)
            
        logger.info(f"BERT score results saved to {BERT_RESULTS_PATH}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error calculating BERT score: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Calculate BERT score between reference and prediction texts.')
    parser.add_argument('--reference', type=str, default=DEFAULT_REFERENCE_PATH,
                        help=f'Path to the reference text file (default: {DEFAULT_REFERENCE_PATH})')
    parser.add_argument('--prediction', type=str, default=DEFAULT_PREDICTION_PATH,
                        help=f'Path to the prediction text file (default: {DEFAULT_PREDICTION_PATH})')
    args = parser.parse_args()
    
    calculate_bert_score(args.reference, args.prediction)

if __name__ == "__main__":
    main()
