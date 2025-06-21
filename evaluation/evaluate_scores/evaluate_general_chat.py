#!/usr/bin/env python
"""Evaluation script for General Purpose Chat responses.

This script:
1. Loads the transcript data 
2. Calls the general chat generation function
3. Saves the generated general chat responses
4. Runs evaluation metrics comparing generated vs ground truth
"""

import sys
import os
import json
import re
from pathlib import Path
import asyncio
import datetime

# Add the parent directory to sys.path to allow imports from the root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agent.ui.ui import Facilitator
from agent.vid2_insight_graph import app
from agent.doc_agent.constants import Intent as DocIntent
from agent.constants import AgentType
from evaluation.generate_output.generate_general_chat import generate_general_chat_responses, load_transcript, SAMPLE_QUERIES
from evaluation.calculate_all_metrics import calculate_all_metrics
from agent.config.initialize_logger import setup_logger

# Set up logger
logger = setup_logger()

class GeneralChatEvaluator:
    """Evaluator for General Purpose Chat responses."""
    
    def __init__(self, transcript_path: str = None, ground_truth_path: str = None):
        """Initialize the evaluator.
        
        Args:
            transcript_path: Path to the transcript.json file
            ground_truth_path: Path to the ground truth general chat responses
        """
        # Set default paths if not provided
        self.transcript_path = transcript_path or '/Users/ankitku5/Desktop/vid2insight/docs/transcript.json'
        self.ground_truth_path = ground_truth_path or '/Users/ankitku5/Desktop/vid2insight/evaluation/ground_truth/General_purpose_chat.txt'
        self.output_path = '/Users/ankitku5/Desktop/vid2insight/evaluation/model_outputs/model_generated_general_chat.txt'
        self.eval_results_dir = '/Users/ankitku5/Desktop/vid2insight/eval_results'
        self.report_path = '/Users/ankitku5/Desktop/vid2insight/evaluation/reports/general_chat_evaluation_report.md'
        
        # Ensure eval_results_dir exists
        os.makedirs(self.eval_results_dir, exist_ok=True)
    
    def generate_responses(self):
        """Generate model responses for general chat queries."""
        logger.info("Loading transcript data...")
        transcript_data = load_transcript(self.transcript_path)
        if not transcript_data:
            logger.error("Failed to load transcript data.")
            return False

        logger.info("Generating general chat responses...")
        responses = generate_general_chat_responses(transcript_data, self.output_path)
        if not responses:
            logger.error("Failed to generate general chat responses.")
            return False
            
        return True
    
    def load_generated_responses(self):
        """Load generated responses from output file."""
        try:
            with open(self.output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse the Q&A format
            qa_pairs = re.split(r'Q: ', content)
            responses = []
            
            # Skip the first empty element if exists
            for qa in qa_pairs:
                if not qa.strip():
                    continue
                    
                parts = re.split(r'\nA: ', qa, maxsplit=1)
                if len(parts) == 2:
                    response = parts[1].strip()
                    responses.append(response)
            
            return responses
        except Exception as e:
            logger.error(f"Error loading generated responses: {e}")
            return []
    
    def load_ground_truth(self):
        """Load ground truth responses."""
        try:
            with open(self.ground_truth_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            logger.error(f"Error loading ground truth: {e}")
            return ""
    
    def run_evaluation(self):
        """Run the full evaluation workflow."""
        logger.info("Starting general chat evaluation...")

        # Generate model responses
        success = self.generate_responses()
        if not success:
            logger.error("Failed to generate responses. Stopping evaluation.")
            return False
        
        # Load generated responses and ground truth
        generated_responses = self.load_generated_responses()
        ground_truth = self.load_ground_truth()
        
        if not generated_responses:
            logger.error("No generated responses to evaluate.")
            return False
            
        if not ground_truth:
            logger.error("No ground truth available for comparison.")
            return False
        
        # Run evaluation metrics
        logger.info("Calculating evaluation metrics...")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create temporary files for metrics calculation
        import tempfile
        import os
        
        # Create temporary files
        ref_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        ref_file.write(ground_truth)
        ref_file.close()
        
        cand_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        cand_file.write("\n".join(generated_responses))
        cand_file.close()
        
        # Calculate metrics using file paths
        # Note: output_path param is not used, results are saved to DEFAULT_ALL_RESULTS_PATH
        metrics_results = calculate_all_metrics(
            reference_path=ref_file.name,
            prediction_path=cand_file.name
        )
        
        # Clean up temporary files
        os.unlink(ref_file.name)
        os.unlink(cand_file.name)
        
        # Print results to terminal
        print("\n===== EVALUATION RESULTS FOR GENERAL CHAT =====")
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
        self._generate_report(metrics_results, generated_responses)
        
        return True
    
    def _generate_report(self, metrics_results, generated_responses):
        """Generate an evaluation report in markdown format."""
        try:
            ground_truth = self.load_ground_truth()
            
            # Create markdown report
            report = [
                "# General Chat Evaluation Report\n",
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
            
            # Add Sample Comparison section
            report.append("\n## Sample Comparison\n")
            
            # Show first 3 generated responses compared to ground truth
            for i, (query, response) in enumerate(zip(SAMPLE_QUERIES, generated_responses[:3])):
                report.append(f"\n### Query {i+1}: {query}\n")
                report.append(f"**Model Response:**\n```\n{response}\n```\n")
            
            report.append(f"\n**Ground Truth (full text):**\n```\n{ground_truth[:1000]}...\n```\n")
            
            # Write report to file
            with open(self.report_path, 'w', encoding='utf-8') as f:
                f.write(''.join(report))
                
            logger.info(f"Evaluation report saved to {self.report_path}")
            
        except Exception as e:
            logger.error(f"Error generating evaluation report: {e}")


if __name__ == "__main__":
    evaluator = GeneralChatEvaluator()
    evaluator.run_evaluation()
