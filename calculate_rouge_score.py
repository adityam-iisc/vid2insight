# Calculating  ROUGE Score between ground truth and model generated text files

import os
import argparse
from rouge import Rouge

def read_file(file_path):
    """Read text from a file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def calculate_rouge_score(reference_path, prediction_path):
    """Calculate ROUGE score between reference and prediction texts."""
    reference = read_file(reference_path)
    prediction = read_file(prediction_path)
    
    # Print the first 100 characters of each file for verification
    print("Reference text (first 100 chars):", reference[:100])
    print("Prediction text (first 100 chars):", prediction[:100])
    
    # Initialize Rouge
    rouge = Rouge()
    
    # Calculate ROUGE scores
    # ROUGE expects non-empty strings
    if not reference.strip() or not prediction.strip():
        print("Error: One of the files is empty or contains only whitespace")
        return None
    
    try:
        scores = rouge.get_scores(prediction, reference)
        
        # Extract scores
        rouge_1 = scores[0]['rouge-1']
        rouge_2 = scores[0]['rouge-2']
        rouge_l = scores[0]['rouge-l']
        
        # Print results
        print("\nROUGE Score Results:")
        print(f"ROUGE-1:")
        print(f"  Precision: {rouge_1['p']:.4f}")
        print(f"  Recall: {rouge_1['r']:.4f}")
        print(f"  F1: {rouge_1['f']:.4f}")
        
        print(f"\nROUGE-2:")
        print(f"  Precision: {rouge_2['p']:.4f}")
        print(f"  Recall: {rouge_2['r']:.4f}")
        print(f"  F1: {rouge_2['f']:.4f}")
        
        print(f"\nROUGE-L:")
        print(f"  Precision: {rouge_l['p']:.4f}")
        print(f"  Recall: {rouge_l['r']:.4f}")
        print(f"  F1: {rouge_l['f']:.4f}")
        
        return rouge_1, rouge_2, rouge_l
    
    except Exception as e:
        print(f"Error calculating ROUGE scores: {e}")
        return None

def main():
    """Parse arguments and calculate ROUGE score."""
    parser = argparse.ArgumentParser(description='Calculate ROUGE score between two text files')
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
    
    print(f"Calculating ROUGE score between:")
    print(f"  Reference: {reference_path}")
    print(f"  Prediction: {prediction_path}")
    print("-" * 50)
    
    calculate_rouge_score(reference_path, prediction_path)

if __name__ == '__main__':
    main()
