#!/usr/bin/env python
"""Evaluation script for Student Summary responses.

This script:
1. Loads the transcript data 
2. Calls the student summary generation function
3. Saves the generated student summary
4. Runs evaluation metrics comparing generated vs ground truth
"""

import sys
import os
import json
import re
from pathlib import Path
import datetime
import tempfile

# Add the project root directory to sys.path to allow imports from the root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from evaluation.generate_output.generate_student_summary import generate_student_summary, load_transcript
from evaluation.calculate_all_metrics import calculate_all_metrics
from agent.config.initialize_logger import setup_logger

# Set up logger
logger = setup_logger()

class StudentSummaryEvaluator:
    """Evaluator for Student Summary responses."""
    
    def __init__(self, transcript_path: str = None, ground_truth_path: str = None):
        """Initialize the evaluator.
        
        Args:
            transcript_path: Path to the transcript.json file
            ground_truth_path: Path to the ground truth student summary
        """
        # Set default paths if not provided
        self.transcript_path = transcript_path or '/Users/ankitku5/Desktop/vid2insight/docs/transcript.json'
        self.ground_truth_path = ground_truth_path or '/Users/ankitku5/Desktop/vid2insight/evaluation/ground_truth/student_summary.txt'
        self.output_path = '/Users/ankitku5/Desktop/vid2insight/evaluation/model_outputs/model_generated_student_summary.txt'
        self.eval_results_dir = '/Users/ankitku5/Desktop/vid2insight/eval_results'
        self.report_path = '/Users/ankitku5/Desktop/vid2insight/evaluation/reports/student_summary_evaluation_report.md'
        
        # Ensure eval_results_dir exists
        os.makedirs(self.eval_results_dir, exist_ok=True)
    
    def generate_summary(self):
        """Generate model summary for student mode."""
        logger.info("Loading transcript data...")
        transcript_data = load_transcript(self.transcript_path)
        if not transcript_data:
            logger.error("Failed to load transcript data.")
            return False

        logger.info("Generating student summary...")
        summary = generate_student_summary(transcript_data, self.output_path)
        if not summary:
            logger.error("Failed to generate student summary.")
            return False
            
        return True
    
    def load_generated_summary(self):
        """Load generated summary from output file."""
        try:
            with open(self.output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            logger.error(f"Error loading generated summary: {e}")
            return ""
    
    def load_ground_truth(self):
        """Load ground truth summary."""
        try:
            with open(self.ground_truth_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            logger.error(f"Error loading ground truth: {e}")
            return ""
    
    def run_evaluation(self):
        """Run the full evaluation workflow."""
        logger.info("Starting student summary evaluation...")

        # Generate model summary
        success = self.generate_summary()
        if not success:
            logger.error("Failed to generate summary. Stopping evaluation.")
            return False
        
        # Load generated summary and ground truth
        generated_summary = self.load_generated_summary()
        ground_truth = self.load_ground_truth()
        
        if not generated_summary:
            logger.error("No generated summary to evaluate.")
            return False
            
        if not ground_truth:
            logger.error("No ground truth available for comparison.")
            return False
        
        # Run evaluation metrics
        logger.info("Calculating evaluation metrics...")
        
        # Create temporary files for metrics calculation
        ref_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        ref_file.write(ground_truth)
        ref_file.close()
        
        cand_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        cand_file.write(generated_summary)
        cand_file.close()
        
        # Calculate metrics using file paths
        metrics_results = calculate_all_metrics(
            reference_path=ref_file.name,
            prediction_path=cand_file.name
        )
        
        # Clean up temporary files
        os.unlink(ref_file.name)
        os.unlink(cand_file.name)
        
        # Print results to terminal
        print("\n===== EVALUATION RESULTS FOR STUDENT SUMMARY =====")
        # Print BERT Score
        bert_scores = metrics_results.get('bert', {})
        print(f"\nBERT Score:")
        print(f"Precision: {bert_scores.get('precision', 0):.4f}")
        print(f"Recall: {bert_scores.get('recall', 0):.4f}")
        print(f"F1: {bert_scores.get('f1', 0):.4f}")
        
        # Print BLEU Score
        bleu_scores = metrics_results.get('bleu', {})
        print(f"\nBLEU Score:")
        for k, v in bleu_scores.items():
            print(f"{k}: {v:.4f}")
        
        # Print ROUGE Score
        rouge_scores = metrics_results.get('rouge', {})
        print(f"\nROUGE Score:")
        for k, v in rouge_scores.items():
            if isinstance(v, dict):
                print(f"{k} Precision: {v.get('precision', 0):.4f}, Recall: {v.get('recall', 0):.4f}, F1: {v.get('f1', 0):.4f}")
        
        # Print LLM Evaluation
        print(f"\nLLM Evaluation:")
        llm_scores = metrics_results.get('llm', {})
        for metric, score in llm_scores.items():
            if isinstance(score, dict) and 'average_score' in score:
                print(f"{metric}: {score['average_score']:.4f}")
        
        # Generate evaluation report in markdown
        self._generate_report(metrics_results, generated_summary)
        
        return True
    
    def _generate_report(self, metrics_results, generated_summary):
        """Generate an evaluation report in markdown format."""
        try:
            ground_truth = self.load_ground_truth()
            
            # Create markdown report
            report = [
                "# Student Summary Evaluation Report\n",
                f"**Evaluation Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
                "\n## Evaluation Metrics\n",
            ]
            
            # Add BERT Score section
            bert_scores = metrics_results.get('bert', {})
            report.append("### BERT Score\n")
            report.append(f"- Precision: {bert_scores.get('precision', 0):.4f}\n")
            report.append(f"- Recall: {bert_scores.get('recall', 0):.4f}\n")
            report.append(f"- F1: {bert_scores.get('f1', 0):.4f}\n")
            
            # Add BLEU Score section
            bleu_scores = metrics_results.get('bleu', {})
            report.append("\n### BLEU Score\n")
            for k, v in bleu_scores.items():
                report.append(f"- {k}: {v:.4f}\n")
            
            # Add ROUGE Score section
            rouge_scores = metrics_results.get('rouge', {})
            report.append("\n### ROUGE Score\n")
            for k, v in rouge_scores.items():
                if isinstance(v, dict):
                    report.append(f"- {k}\n  - Precision: {v.get('precision', 0):.4f}\n  - Recall: {v.get('recall', 0):.4f}\n  - F1: {v.get('f1', 0):.4f}\n")
            
            # Add LLM Evaluation section
            report.append("\n### LLM Evaluation\n")
            llm_scores = metrics_results.get('llm', {})
            for metric, score in llm_scores.items():
                if isinstance(score, dict) and 'average_score' in score:
                    report.append(f"- {metric}: {score['average_score']:.4f}\n")
            
            # Add Content Comparison section
            report.append("\n## Content Comparison\n")
            
            max_display_length = 1000  # Limit display length for readability
            
            report.append(f"\n### Model Generated Summary\n")
            summary_preview = generated_summary[:max_display_length]
            if len(generated_summary) > max_display_length:
                summary_preview += "..."
            report.append(f"```\n{summary_preview}\n```\n")
            
            report.append(f"\n### Ground Truth Summary\n")
            truth_preview = ground_truth[:max_display_length]
            if len(ground_truth) > max_display_length:
                truth_preview += "..."
            report.append(f"```\n{truth_preview}\n```\n")
            
            # Write report to file
            with open(self.report_path, 'w', encoding='utf-8') as f:
                f.write(''.join(report))
                
            logger.info(f"Evaluation report saved to {self.report_path}")
            
        except Exception as e:
            logger.error(f"Error generating evaluation report: {e}")


if __name__ == "__main__":
    evaluator = StudentSummaryEvaluator()
    evaluator.run_evaluation()
