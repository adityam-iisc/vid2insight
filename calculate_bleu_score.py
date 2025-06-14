# CalculatimngBLEU Score between ground truth and model generated text files

import os
import argparse
import nltk
from nltk.translate.bleu_score import sentence_bleu, corpus_bleu, SmoothingFunction

def read_file(file_path):
    """Read text from a file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def calculate_bleu_score(reference_path, prediction_path):
    """Calculate BLEU score between reference and prediction texts."""
    reference = read_file(reference_path)
    prediction = read_file(prediction_path)
    
    # Print the first 100 characters of each file for verification
    print("Reference text (first 100 chars):", reference[:100])
    print("Prediction text (first 100 chars):", prediction[:100])
    
    # Download necessary NLTK data
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    
    # Tokenize the whole text (not by sentences)
    reference_tokens = nltk.word_tokenize(reference)
    prediction_tokens = nltk.word_tokenize(prediction)
    
    # Calculate BLEU score at different n-gram levels
    smoothie = SmoothingFunction().method1
    
    # Calculate sentence BLEU (treating the whole text as one sentence)
    bleu_1 = sentence_bleu([reference_tokens], prediction_tokens, 
                        weights=(1, 0, 0, 0),
                        smoothing_function=smoothie)
    
    bleu_2 = sentence_bleu([reference_tokens], prediction_tokens, 
                        weights=(0.5, 0.5, 0, 0),
                        smoothing_function=smoothie)
    
    bleu_3 = sentence_bleu([reference_tokens], prediction_tokens, 
                        weights=(0.33, 0.33, 0.33, 0),
                        smoothing_function=smoothie)
    
    bleu_4 = sentence_bleu([reference_tokens], prediction_tokens, 
                        weights=(0.25, 0.25, 0.25, 0.25),
                        smoothing_function=smoothie)
    
    # Print results
    print("\nBLEU Score Results:")
    print(f"BLEU-1 (unigrams only): {bleu_1:.4f}")
    print(f"BLEU-2 (unigrams and bigrams): {bleu_2:.4f}")
    print(f"BLEU-3 (1-3 grams): {bleu_3:.4f}")
    print(f"BLEU-4 (1-4 grams): {bleu_4:.4f}")
    
    return bleu_1, bleu_2, bleu_3, bleu_4

def main():
    """Parse arguments and calculate BLEU score."""
    parser = argparse.ArgumentParser(description='Calculate BLEU score between two text files')
    parser.add_argument('--reference', default='ground_truth.txt', 
                        help='Path to the reference/ground truth text file')
    parser.add_argument('--prediction', default='model_generated.txt', 
                        help='Path to the prediction/model generated text file')
    
    args = parser.parse_args()
    
    # Get absolute paths if only filenames are provided
    reference_path = args.reference
    if not os.path.isabs(reference_path):
        reference_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), reference_path)
        
    prediction_path = args.prediction
    if not os.path.isabs(prediction_path):
        prediction_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), prediction_path)
    
    # # Check if files exist
    # if not os.path.exists(reference_path):
    #     print(f"Error: Reference file not found: {reference_path}")
    #     return
        
    # if not os.path.exists(prediction_path):
    #     print(f"Error: Prediction file not found: {prediction_path}")
    #     return
    
    print(f"Calculating BLEU score between:")
    print(f"  Reference: {reference_path}")
    print(f"  Prediction: {prediction_path}")
    print("-" * 50)
    
    calculate_bleu_score(reference_path, prediction_path)

if __name__ == '__main__':
    main()
