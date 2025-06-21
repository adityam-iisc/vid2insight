#!/usr/bin/env python
"""
Direct evaluation script for the transcript against ground truth.
This script skips the generation step and directly compares existing files.
"""

import sys
import os
import json
from pathlib import Path
import shutil

# Add the parent directory to sys.path to allow imports from the root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from evaluation.calculate_all_metrics import calculate_all_metrics
from agent.config.initialize_logger import setup_logger

# Set up logger
logger = setup_logger()

def extract_transcript():
    """Extract transcript from JSON and save to a text file."""
    transcript_file = "/Users/ankitku5/Desktop/vid2insight/docs/transcript.json"
    output_file = "/Users/ankitku5/Desktop/vid2insight/evaluation/model_outputs/model_generated_transcript.txt"
    
    print(f"Loading transcript from {transcript_file}")
    try:
        with open(transcript_file, 'r') as f:
            transcript_data = json.load(f)
        
        # Extract combined transcript
        combined_transcript = transcript_data.get('combined_transcript', [{}])[0].get('combined_transcript', '')
        
        # If the combined_transcript is empty or not found, try to construct it from audio_transcript segments
        if not combined_transcript:
            print("Combined transcript not found directly, attempting to extract from segments...")
            combined_transcript = ""
            # Iterate through all segments (000, 001, etc.)
            segment_keys = sorted([k for k in transcript_data.keys() if k.isdigit()])
            
            for segment_key in segment_keys:
                segment = transcript_data[segment_key]
                if 'audio_transcript' in segment and 'transcript' in segment['audio_transcript']:
                    for transcript_item in segment['audio_transcript']['transcript']:
                        combined_transcript += transcript_item.get('text', '') + " "
            
            combined_transcript = combined_transcript.strip()
        
        # Save to output file
        with open(output_file, 'w') as f:
            f.write(combined_transcript)
        
        print(f"Transcript extracted and saved to {output_file}")
        return True
    except Exception as e:
        print(f"Error extracting transcript: {e}")
        return False

def evaluate_transcript():
    """
    Compare the saved transcript against ground truth using all metrics.
    """
    # Define paths
    ground_truth_path = "/Users/ankitku5/Desktop/vid2insight/evaluation/ground_truth/ground_truth.txt"
    generated_path = "/Users/ankitku5/Desktop/vid2insight/evaluation/model_outputs/model_generated_transcript.txt"
    output_dir = "/Users/ankitku5/Desktop/vid2insight/evaluation/reports"
    
    # Make sure files exist
    if not os.path.exists(ground_truth_path):
        print(f"Ground truth file not found: {ground_truth_path}")
        return False
    
    if not os.path.exists(generated_path):
        print(f"Generated transcript file not found: {generated_path}")
        return False
    
    print("Running evaluation metrics...")
    
    # Run evaluation using the calculate_all_metrics function
    results = calculate_all_metrics(ground_truth_path, generated_path)
    
    # Generate report
    report_path = os.path.join(output_dir, "transcript_evaluation_report.md")
    with open(report_path, 'w') as f:
        f.write("# Transcript Evaluation Report\n\n")
        
        # BERT Score section
        f.write("## BERT Score\n")
        bert = results.get('bert', {})
        f.write(f"- Precision: {bert.get('precision', 0.0):.4f}\n")
        f.write(f"- Recall: {bert.get('recall', 0.0):.4f}\n")
        f.write(f"- F1: {bert.get('f1', 0.0):.4f}\n\n")
        
        # BLEU Score section
        f.write("## BLEU Score\n")
        bleu = results.get('bleu', {})
        f.write(f"- BLEU-1: {bleu.get('bleu_1', 0.0):.4f}\n")
        f.write(f"- BLEU-2: {bleu.get('bleu_2', 0.0):.4f}\n")
        f.write(f"- BLEU-3: {bleu.get('bleu_3', 0.0):.4f}\n")
        f.write(f"- BLEU-4: {bleu.get('bleu_4', 0.0):.4f}\n\n")
        
        # ROUGE Score section
        f.write("## ROUGE Score\n")
        rouge = results.get('rouge', {})
        for rouge_type, values in rouge.items():
            f.write(f"### {rouge_type.upper()}\n")
            f.write(f"- Precision: {values.get('precision', 0.0):.4f}\n")
            f.write(f"- Recall: {values.get('recall', 0.0):.4f}\n")
            f.write(f"- F1: {values.get('f1', 0.0):.4f}\n\n")
        
        # LLM Evaluation section
        f.write("## LLM Evaluation\n")
        llm = results.get('llm', {})
        for key, value in llm.items():
            if isinstance(value, (int, float)):
                f.write(f"- {key.capitalize()}: {value:.4f}\n")
            else:
                f.write(f"- {key.capitalize()}: {value}\n")
    
    print(f"Evaluation report saved to {report_path}")
    
    # Print simplified results in requested format
    print("\nBERT score:    Precision:   {:.4f}".format(bert.get('precision', 0.0)))
    print("  Recall:      {:.4f}".format(bert.get('recall', 0.0)))
    print("  F1:          {:.4f}".format(bert.get('f1', 0.0)))
    
    # BLEU Score section with simplified formatting
    print("\nBLEU score:")
    print("\n  BLEU-1:      {:.4f}".format(bleu.get('bleu_1', 0.0)))
    print("  BLEU-2:      {:.4f}".format(bleu.get('bleu_2', 0.0)))
    print("  BLEU-3:      {:.4f}".format(bleu.get('bleu_3', 0.0)))
    print("  BLEU-4:      {:.4f}".format(bleu.get('bleu_4', 0.0)))
    
    # ROUGE Score section with simplified formatting
    print("\nrouge:")
    for rouge_type, values in rouge.items():
        print("  {}".format(rouge_type.upper()))
        print("    Precision: {:.4f}".format(values.get('precision', 0.0)))
        print("    Recall:    {:.4f}".format(values.get('recall', 0.0)))
        print("    F1:        {:.4f}".format(values.get('f1', 0.0)))
        print("")
    
    # LLM Evaluation section with simplified formatting
    print("")
    llm = results.get('llm', {})
    
    # Get all LLM values first
    llm_values = {}
    for key, value in llm.items():
        if isinstance(value, (int, float)):
            llm_values[key] = value
        elif isinstance(value, dict) and 'average_score' in value:
            llm_values[key] = value['average_score']
    
    # Print in a specific format with correct spacing
    print("Correctness:{:.4f}".format(llm_values.get('correctness', 0.0)))
    print("Relevance: {:.4f}".format(llm_values.get('relevance', 0.0)))
    print("Coherence : {:.4f}".format(llm_values.get('coherence', 0.0)))
    print("Fluency: {:.4f}Helpfulness : {:.4f}".format(
        llm_values.get('fluency', 0.0), 
        llm_values.get('helpfulness', 0.0)
    ))
    print("Harmlessness: {:.4f}".format(llm_values.get('harmlessness', 0.0)))
    
    return results

def main():
    """Main function to extract and evaluate transcripts."""
    print("Starting transcript evaluation...")
    
    # First extract the transcript
    if not extract_transcript():
        print("Failed to extract transcript. Exiting.")
        return 1
    
    # Then evaluate it
    try:
        evaluate_transcript()
    except Exception as e:
        print(f"Error: Evaluation failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
