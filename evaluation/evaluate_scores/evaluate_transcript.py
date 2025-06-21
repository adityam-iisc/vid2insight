#!/usr/bin/env python
"""
Evaluation script for comparing the transcript against ground truth.
"""

import sys
import os
import json
from pathlib import Path
import datetime

# Add the parent directory to sys.path to allow imports from the root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from evaluation.calculate_all_metrics import calculate_all_metrics
from agent.config.initialize_logger import setup_logger

# Set up logger
logger = setup_logger()

def evaluate_transcript():
    """
    Evaluate the transcript against ground truth.
    """
    # Load the transcript
    transcript_file = "/Users/ankitku5/Desktop/vid2insight/docs/transcript.json"
    ground_truth_file = "/Users/ankitku5/Desktop/vid2insight/evaluation/ground_truth/ground_truth.txt"
    output_file = "/Users/ankitku5/Desktop/vid2insight/evaluation/model_outputs/model_generated_transcript.txt"
    
    print(f"Loading transcript from {transcript_file}")
    with open(transcript_file, 'r', encoding='utf-8') as f:
        transcript_data = json.load(f)
    
    # Extract combined transcript
    combined_transcript = transcript_data['combined_transcript'][0]['combined_transcript']
    
    # Save combined transcript to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(combined_transcript)
    
    # Run evaluation
    print(f"Comparing with ground truth: {ground_truth_file}")
    eval_results = calculate_all_metrics(
        ground_truth_file,
        output_file
    )
    
    # Create evaluation report
    create_eval_report(eval_results)
    
    return eval_results

def create_eval_report(results):
    """
    Create an evaluation report markdown file.
    """
    output_dir = Path("/Users/ankitku5/Desktop/vid2insight/evaluation")
    
    report_file = output_dir / "transcript_evaluation_report.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Transcript Evaluation Report\n\n")
        f.write(f"**Evaluation Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Evaluation Metrics\n\n")
        
        # BERT Score
        f.write("### BERT Score\n")
        bert = results.get('bert', {})
        f.write(f"- Precision: {bert.get('precision', 0.0):.4f}\n")
        f.write(f"- Recall: {bert.get('recall', 0.0):.4f}\n")
        f.write(f"- F1: {bert.get('f1', 0.0):.4f}\n\n")
        
        # BLEU Score
        f.write("### BLEU Score\n")
        bleu = results.get('bleu', {})
        f.write(f"- BLEU-1: {bleu.get('bleu_1', 0.0):.4f}\n")
        f.write(f"- BLEU-2: {bleu.get('bleu_2', 0.0):.4f}\n")
        f.write(f"- BLEU-3: {bleu.get('bleu_3', 0.0):.4f}\n")
        f.write(f"- BLEU-4: {bleu.get('bleu_4', 0.0):.4f}\n\n")
        
        # ROUGE Score
        f.write("### ROUGE Score\n")
        rouge = results.get('rouge', {})
        for rouge_type, values in rouge.items():
            f.write(f"#### {rouge_type.upper()}\n")
            f.write(f"- Precision: {values.get('precision', 0.0):.4f}\n")
            f.write(f"- Recall: {values.get('recall', 0.0):.4f}\n")
            f.write(f"- F1: {values.get('f1', 0.0):.4f}\n\n")
        
        # LLM Evaluation
        f.write("### LLM Evaluation\n")
        llm = results.get('llm', {})
        for key, value in llm.items():
            if isinstance(value, (int, float)):
                f.write(f"- {key.capitalize()}: {value:.4f}\n")
            else:
                f.write(f"- {key.capitalize()}: {value}\n")
        f.write("\n")
        
        # Sample comparison
        f.write("## Sample Comparison\n")
        f.write("### Generated Transcript vs. Ground Truth\n")
        f.write("*First 500 characters of each:*\n\n")
        
        # Read first 500 chars of generated transcript
        with open("/Users/ankitku5/Desktop/vid2insight/evaluation/model_outputs/model_generated_transcript.txt", 'r', encoding='utf-8') as gen_file:
            generated = gen_file.read(500)
        
        # Read first 500 chars of ground truth
        with open("/Users/ankitku5/Desktop/vid2insight/evaluation/ground_truth/ground_truth.txt", 'r', encoding='utf-8') as ref_file:
            reference = ref_file.read(500)
        
        f.write("**Generated Transcript:**\n```\n")
        f.write(f"{generated}...\n")
        f.write("```\n\n")
        
        f.write("**Ground Truth:**\n```\n")
        f.write(f"{reference}...\n")
        f.write("```\n")
    
    print(f"Evaluation report saved to {report_file}")

if __name__ == "__main__":
    print("Starting transcript evaluation...")
    results = evaluate_transcript()
    print("Evaluation complete!")
    print(f"BERT Score F1: {results.get('bert', {}).get('f1', 0.0):.4f}")
    print(f"BLEU-4 Score: {results.get('bleu', {}).get('bleu_4', 0.0):.4f}")
    print(f"ROUGE-L F1: {results.get('rouge', {}).get('rouge_l', {}).get('f1', 0.0):.4f}")
    if 'llm' in results:
        print(f"LLM Evaluation:")
        for key, value in results['llm'].items():
            print(f"- {key.capitalize()}: {value:.4f}")
