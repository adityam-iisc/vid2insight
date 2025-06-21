#!/usr/bin/env python

import json
import os
import sys
from pathlib import Path

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import the calculate_all_metrics function
try:
    from evaluation.calculate_all_metrics import calculate_all_metrics
    print("Successfully imported calculate_all_metrics")
except ImportError as e:
    print(f"Error importing calculate_all_metrics: {e}")
    sys.exit(1)

def main():
    print("Starting transcript evaluation...")
    
    # Define file paths
    transcript_path = "/Users/ankitku5/Desktop/vid2insight/docs/transcript.json"
    ground_truth_path = "/Users/ankitku5/Desktop/vid2insight/ground_truth.txt"
    output_path = "/Users/ankitku5/Desktop/vid2insight/model_generated_transcript.txt"
    
    try:
        # Load transcript
        print(f"Loading transcript from {transcript_path}")
        with open(transcript_path, 'r') as f:
            transcript_data = json.load(f)
        
        # Extract combined transcript
        combined_transcript = transcript_data['combined_transcript'][0]['combined_transcript']
        
        # Save to output file
        print(f"Saving transcript to {output_path}")
        with open(output_path, 'w') as f:
            f.write(combined_transcript)
        
        # Run evaluation
        print(f"Running evaluation...")
        metrics = calculate_all_metrics(
            ground_truth_path,
            output_path
        )
        
        # Print results
        print("\nEvaluation Results:")
        print(f"BERT Score: {metrics.get('bert', {}).get('f1', 0):.4f}")
        print(f"BLEU-4 Score: {metrics.get('bleu', {}).get('bleu_4', 0):.4f}")
        print(f"ROUGE-L F1: {metrics.get('rouge', {}).get('rouge_l', {}).get('f1', 0):.4f}")
        
        if 'llm' in metrics:
            print("\nLLM Evaluation:")
            for key, val in metrics['llm'].items():
                print(f"- {key}: {val:.4f}")
        
    except Exception as e:
        print(f"Error during evaluation: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
