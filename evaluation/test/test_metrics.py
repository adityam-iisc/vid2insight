#!/usr/bin/env python

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Simple test script for calculating metrics")
print(f"Current directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

try:
    # Import the metrics calculation function
    print("Attempting to import calculate_all_metrics...")
    from evaluation.calculate_all_metrics import calculate_all_metrics
    print("Successfully imported calculate_all_metrics")
    
    # Define paths
    ground_truth = "/Users/ankitku5/Desktop/vid2insight/ground_truth.txt"
    generated = "/Users/ankitku5/Desktop/vid2insight/model_generated_transcript.txt"
    
    # Check if files exist
    print(f"Ground truth exists: {os.path.exists(ground_truth)}")
    
    # Create generated transcript if it doesn't exist
    if not os.path.exists(generated):
        print("Creating a simple generated transcript...")
        with open("/Users/ankitku5/Desktop/vid2insight/docs/transcript.json", 'r') as f:
            import json
            data = json.load(f)
            transcript = data['combined_transcript'][0]['combined_transcript']
            
        with open(generated, 'w') as f:
            f.write(transcript)
        print(f"Created generated transcript at {generated}")
    else:
        print(f"Generated transcript exists at {generated}")
    
    # Calculate metrics
    print("Calculating metrics...")
    metrics = calculate_all_metrics(ground_truth, generated)
    
    # Print results
    print("\nResults:")
    print(f"BERT Score: {metrics.get('bert', {})}")
    print(f"BLEU Score: {metrics.get('bleu', {})}")
    print(f"ROUGE Score: {metrics.get('rouge', {})}")
    print(f"LLM Evaluation: {metrics.get('llm', {})}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
