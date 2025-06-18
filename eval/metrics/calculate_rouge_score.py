"""Calculating ROUGE Score between ground truth and model generated text files."""

import os
import argparse
import json
from rouge import Rouge
from agent.config.initialize_logger import setup_logger
from eval.constants.paths import DEFAULT_REFERENCE_PATH, DEFAULT_PREDICTION_PATH, ROUGE_RESULTS_PATH

# Set up logger
logger = setup_logger()

def read_file(file_path):
    """Read text from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        raise

def calculate_rouge_score(reference_path=DEFAULT_REFERENCE_PATH, prediction_path=DEFAULT_PREDICTION_PATH):
    """Calculate ROUGE score between reference and prediction texts."""
    try:
        reference = read_file(reference_path)
        prediction = read_file(prediction_path)
        
        # Print the first 100 characters of each file for verification
        logger.info("Reference text (first 100 chars): %s", reference[:100])
        logger.info("Prediction text (first 100 chars): %s", prediction[:100])
        
        # Initialize Rouge
        rouge = Rouge()
        
        # Calculate ROUGE scores
        # ROUGE expects non-empty strings
        if not reference.strip() or not prediction.strip():
            logger.error("Error: One of the files is empty or contains only whitespace")
            return None
        
        try:
            scores = rouge.get_scores(prediction, reference)
            
            # Extract scores
            rouge_1 = scores[0]['rouge-1']
            rouge_2 = scores[0]['rouge-2']
            rouge_l = scores[0]['rouge-l']
            
            # Log results
            logger.info("\nROUGE Score Results:")
            logger.info(f"ROUGE-1: P={rouge_1['p']:.4f}, R={rouge_1['r']:.4f}, F={rouge_1['f']:.4f}")
            logger.info(f"ROUGE-2: P={rouge_2['p']:.4f}, R={rouge_2['r']:.4f}, F={rouge_2['f']:.4f}")
            logger.info(f"ROUGE-L: P={rouge_l['p']:.4f}, R={rouge_l['r']:.4f}, F={rouge_l['f']:.4f}")
            
            # Save results to JSON file
            results = {
                "rouge_1": {
                    "precision": rouge_1['p'],
                    "recall": rouge_1['r'],
                    "f1": rouge_1['f']
                },
                "rouge_2": {
                    "precision": rouge_2['p'],
                    "recall": rouge_2['r'],
                    "f1": rouge_2['f']
                },
                "rouge_l": {
                    "precision": rouge_l['p'],
                    "recall": rouge_l['r'],
                    "f1": rouge_l['f']
                }
            }
            
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(ROUGE_RESULTS_PATH), exist_ok=True)
            
            with open(ROUGE_RESULTS_PATH, 'w') as f:
                json.dump(results, f, indent=4)
                
            logger.info(f"ROUGE score results saved to {ROUGE_RESULTS_PATH}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in Rouge scoring: {e}")
            return None
            
    except Exception as e:
        logger.error(f"Error calculating ROUGE score: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Calculate ROUGE score between reference and prediction texts.')
    parser.add_argument('--reference', type=str, default=DEFAULT_REFERENCE_PATH,
                        help=f'Path to the reference text file (default: {DEFAULT_REFERENCE_PATH})')
    parser.add_argument('--prediction', type=str, default=DEFAULT_PREDICTION_PATH,
                        help=f'Path to the prediction text file (default: {DEFAULT_PREDICTION_PATH})')
    args = parser.parse_args()
    
    calculate_rouge_score(args.reference, args.prediction)

if __name__ == "__main__":
    main()
