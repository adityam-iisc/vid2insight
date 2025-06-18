"""Calculating BLEU Score between ground truth and model generated text files."""

import os
import argparse
import json
import nltk
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from agent.config.initialize_logger import setup_logger
from eval.constants.paths import DEFAULT_REFERENCE_PATH, DEFAULT_PREDICTION_PATH, BLEU_RESULTS_PATH
from eval.config.model_config import BLEU_CONFIG

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

def calculate_bleu_score(reference_path=DEFAULT_REFERENCE_PATH, prediction_path=DEFAULT_PREDICTION_PATH):
    """Calculate BLEU score between reference and prediction texts."""
    try:
        reference = read_file(reference_path)
        prediction = read_file(prediction_path)
        
        # Print the first 100 characters of each file for verification
        logger.info("Reference text (first 100 chars): %s", reference[:100])
        logger.info("Prediction text (first 100 chars): %s", prediction[:100])
        
        # Download necessary NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            logger.info("Downloading NLTK punkt data...")
            nltk.download('punkt')
        
        # Tokenize the whole text (not by sentences)
        reference_tokens = nltk.word_tokenize(reference)
        prediction_tokens = nltk.word_tokenize(prediction)
        
        # Calculate BLEU score at different n-gram levels
        smoothie = SmoothingFunction().method1
        
        # Calculate sentence BLEU (treating the whole text as one sentence)
        bleu_1 = sentence_bleu([reference_tokens], prediction_tokens, 
                             weights=BLEU_CONFIG['weights_1gram'], smoothing_function=smoothie)
        bleu_2 = sentence_bleu([reference_tokens], prediction_tokens, 
                             weights=BLEU_CONFIG['weights_2gram'], smoothing_function=smoothie)
        bleu_3 = sentence_bleu([reference_tokens], prediction_tokens, 
                             weights=BLEU_CONFIG['weights_3gram'], smoothing_function=smoothie)
        bleu_4 = sentence_bleu([reference_tokens], prediction_tokens, 
                             weights=BLEU_CONFIG['weights_4gram'], smoothing_function=smoothie)
        
        # Log results
        logger.info("\nBLEU Score Results:")
        logger.info(f"BLEU-1: {bleu_1:.4f}")
        logger.info(f"BLEU-2: {bleu_2:.4f}")
        logger.info(f"BLEU-3: {bleu_3:.4f}")
        logger.info(f"BLEU-4: {bleu_4:.4f}")
        
        # Save results to JSON file
        results = {
            "bleu_1": bleu_1,
            "bleu_2": bleu_2,
            "bleu_3": bleu_3,
            "bleu_4": bleu_4
        }
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(BLEU_RESULTS_PATH), exist_ok=True)
        
        with open(BLEU_RESULTS_PATH, 'w') as f:
            json.dump(results, f, indent=4)
            
        logger.info(f"BLEU score results saved to {BLEU_RESULTS_PATH}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error calculating BLEU score: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Calculate BLEU score between reference and prediction texts.')
    parser.add_argument('--reference', type=str, default=DEFAULT_REFERENCE_PATH,
                        help=f'Path to the reference text file (default: {DEFAULT_REFERENCE_PATH})')
    parser.add_argument('--prediction', type=str, default=DEFAULT_PREDICTION_PATH,
                        help=f'Path to the prediction text file (default: {DEFAULT_PREDICTION_PATH})')
    args = parser.parse_args()
    
    calculate_bleu_score(args.reference, args.prediction)

if __name__ == "__main__":
    main()
