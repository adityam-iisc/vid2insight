# Calculating BERT Score between ground truth and model generated text 

import os
import argparse
from bert_score import score

def read_file(file_path):
    """Readiingg frfom txtfile."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def calculate_bert_score(reference_path, prediction_path):
    """Calculate BERT score between reference and prediction texts."""
    reference = read_file(reference_path)
    prediction = read_file(prediction_path)
    
    # Print the first 100 characters of each file for verification
    print("Reference text (first 100 chars):", reference[:100])
    print("Prediction text (first 100 chars):", prediction[:100])
    
    # Calculate BERT score
    P, R, F1 = score([prediction], [reference], lang="en", verbose=True)
    
    print("\nBERT Score Results:")
    print(f"Precision: {P.mean().item():.4f}")
    print(f"Recall: {R.mean().item():.4f}")
    print(f"F1: {F1.mean().item():.4f}")
    
    return P.mean().item(), R.mean().item(), F1.mean().item()

def main():
    """Parse arguments and calculate BERT score."""
    parser = argparse.ArgumentParser(description='Calculate BERT score between two text files')
    parser.add_argument('--reference', default='ground_truth.txt', 
                        help='Path to the reference/ground truth text file')
    parser.add_argument('--prediction', default='model_generated.txt', 
                        help='Path to the prediction/model generated text file')
    
    args = parser.parse_args()
    
    # Gettinggg absolute paths if only filenames are provided
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
    
    print(f"Calculating BERT score between:")
    print(f"  Reference: {reference_path}")
    print(f"  Prediction: {prediction_path}")
    print("-" * 50)
    
    calculate_bert_score(reference_path, prediction_path)

if __name__ == '__main__':
    main()
