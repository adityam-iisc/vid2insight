#!/usr/bin/env python
"""Evaluation script for Product Documentation generation.

This script:
1. Loads the transcript data 
2. Calls the product document generation function from the UI
3. Saves the generated product documentation 
4. Runs evaluation metrics comparing generated vs ground truth
"""

import sys
import os
import json
import asyncio

# Add the parent directory to sys.path to allow imports from the root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.ui.ui import Facilitator
from agent.vid2_insight_graph import app
from agent.doc_agent.constants import Intent as DocIntent
from agent.constants import AgentType
from evaluation.calculate_all_metrics import calculate_all_metrics
from agent.config.initialize_logger import setup_logger

# Set up logger
logger = setup_logger()

class ProductDocEvaluator:
    """Evaluator for Product Documentation generation."""
    
    def __init__(self, transcript_path: str = None, ground_truth_path: str = None):
        """Initialize the evaluator.
        
        Args:
            transcript_path: Path to the transcript.json file
            ground_truth_path: Path to the ground truth product documentation
        """
        self.transcript_path = transcript_path or '/Users/ankitku5/Desktop/vid2insight/docs/transcript.json'
        self.ground_truth_path = ground_truth_path or '/Users/ankitku5/Desktop/vid2insight/evaluation/ground_truth/detailed_product_Doc.txt'
        self.output_path = '/Users/ankitku5/Desktop/vid2insight/evaluation/model_outputs/model_generated_product_doc.txt'
        self.report_path = '/Users/ankitku5/Desktop/vid2insight/evaluation/reports/product_doc_evaluation_report.md'
        
    def load_transcript(self):
        """Load transcript data from JSON file."""
        try:
            with open(self.transcript_path, 'r') as f:
                transcript_data = json.load(f)
            logger.info(f"Loaded transcript from {self.transcript_path}")
            return transcript_data
        except Exception as e:
            logger.error(f"Error loading transcript: {e}")
            return None
    
    def generate_product_doc(self, transcript_data: dict, session_id: str = "eval_session"):
        """Generate product documentation using the agent.
        
        Args:
            transcript_data: The loaded transcript data
            session_id: Session ID for the agent
            
        Returns:
            tuple: (chat_content, doc_content) from the agent
        """
        try:
            logger.info("Generating product documentation using agent...")
            
            # Set up the context similar to how it's done in the UI
            video_context = transcript_data['combined_transcript'][0]['combined_transcript']
            
            # Configure the agent
            config = {"configurable": {"thread_id": session_id, 'agent_choice': AgentType.doc_agent.value}}
            
            # Create the payload
            payload = {
                "messages": [{"role": "human", "content": 'generate a product documentation for the video content.'}],
                'expert_preference': AgentType.doc_agent.value,
                'video_context': video_context,
                'intent': DocIntent.GENERATE_DOCS.value
            }
            
            # Call the agent
            raw = asyncio.run(app.ainvoke(payload, config))
            
            logger.info("Product documentation generated successfully")
            return raw['chat_content'], raw['doc_content']
            
        except Exception as e:
            logger.error(f"Error generating product documentation: {e}")
            return None, None
    
    def save_generated_doc(self, doc_content: str):
        """Save the generated documentation to file.
        
        Args:
            doc_content: The generated documentation content
        """
        try:
            with open(self.output_path, 'w', encoding='utf-8') as f:
                f.write(doc_content)
            logger.info(f"Generated documentation saved to {self.output_path}")
        except Exception as e:
            logger.error(f"Error saving generated documentation: {e}")
    
    def run_evaluation(self, metrics: list = None):
        """Run evaluation metrics comparing generated vs ground truth.
        
        Args:
            metrics: List of metrics to run (default: all metrics)
            
        Returns:
            dict: Evaluation results
        """
        try:
            logger.info("Running evaluation metrics...")
            
            # Check if files exist
            if not os.path.exists(self.ground_truth_path):
                logger.error(f"Ground truth file not found: {self.ground_truth_path}")
                return None
                
            if not os.path.exists(self.output_path):
                logger.error(f"Generated documentation file not found: {self.output_path}")
                return None
            
            # Run evaluation
            results = calculate_all_metrics(
                reference_path=self.ground_truth_path,
                prediction_path=self.output_path,
                metrics=metrics
            )
            
            logger.info("Evaluation completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error running evaluation: {e}")
            return None
    
    def create_eval_report(self, results):
        """Create an evaluation report markdown file.
        
        Args:
            results: Evaluation results dict
        """
        import datetime
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.report_path), exist_ok=True)
            
            with open(self.report_path, 'w', encoding='utf-8') as f:
                f.write("# Product Documentation Evaluation Report\n\n")
                f.write(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write("## Summary\n\n")
                
                # BERT Score
                f.write("### BERT Metrics\n\n")
                bert = results.get('bert', {})
                f.write("| Metric | Score |\n")
                f.write("|--------|-------|\n")
                f.write(f"| bert_precision | {bert.get('precision', 0.0):.4f} |\n")
                f.write(f"| bert_recall | {bert.get('recall', 0.0):.4f} |\n")
                f.write(f"| bert_f1 | {bert.get('f1', 0.0):.4f} |\n\n")
                
                # BLEU Score
                f.write("### BLEU Metrics\n\n")
                bleu = results.get('bleu', {})
                f.write("| Metric | Score |\n")
                f.write("|--------|-------|\n")
                f.write(f"| bleu_1 | {bleu.get('bleu_1', 0.0):.4f} |\n")
                f.write(f"| bleu_2 | {bleu.get('bleu_2', 0.0):.4f} |\n")
                f.write(f"| bleu_3 | {bleu.get('bleu_3', 0.0):.4f} |\n")
                f.write(f"| bleu_4 | {bleu.get('bleu_4', 0.0):.4f} |\n\n")
                
                # ROUGE Score
                f.write("### ROUGE Metrics\n\n")
                rouge = results.get('rouge', {})
                f.write("| Metric | Score |\n")
                f.write("|--------|-------|\n")
                
                for rouge_type, values in rouge.items():
                    if isinstance(values, dict):
                        f.write(f"| {rouge_type}_precision | {values.get('precision', 0.0):.4f} |\n")
                        f.write(f"| {rouge_type}_recall | {values.get('recall', 0.0):.4f} |\n")
                        f.write(f"| {rouge_type}_f1 | {values.get('f1', 0.0):.4f} |\n")
                
                # LLM Evaluation
                if 'llm' in results:
                    f.write("\n### LLM Evaluation Metrics\n\n")
                    f.write("| Metric | Score |\n")
                    f.write("|--------|-------|\n")
                    
                    llm = results['llm']
                    for key, value in llm.items():
                        if isinstance(value, (int, float)):
                            f.write(f"| {key.capitalize()} | {value:.4f} |\n")
                
                # Content comparison
                f.write("\n## Content Comparison\n\n")
                
                # Read first 300 chars of ground truth
                try:
                    with open(self.ground_truth_path, 'r', encoding='utf-8') as gt_file:
                        ground_truth = gt_file.read(300)
                    
                    with open(self.output_path, 'r', encoding='utf-8') as gen_file:
                        generated = gen_file.read(300)
                    
                    f.write("### Ground Truth (first 300 chars)\n\n")
                    f.write("```\n")
                    f.write(f"{ground_truth}...\n")
                    f.write("```\n\n")
                    
                    f.write("### Generated (first 300 chars)\n\n")
                    f.write("```\n")
                    f.write(f"{generated}...\n")
                    f.write("```\n")
                except Exception as e:
                    f.write(f"Error reading comparison files: {e}\n")
            
            logger.info(f"Evaluation report saved to {self.report_path}")
            
        except Exception as e:
            logger.error(f"Error creating evaluation report: {e}")
    
    def evaluate(self, metrics: list = None):
        """Complete evaluation pipeline.
        
        Args:
            metrics: List of metrics to run (default: all metrics)
            
        Returns:
            dict: Evaluation results
        """
        logger.info("=== Starting Product Documentation Evaluation ===")
        
        # Step 1: Load transcript
        transcript_data = self.load_transcript()
        if not transcript_data:
            logger.error("Failed to load transcript data")
            return None
        
        # Step 2: Generate product documentation
        chat_content, doc_content = self.generate_product_doc(transcript_data)
        if not doc_content:
            logger.error("Failed to generate product documentation")
            return None
        
        # Step 3: Save generated documentation
        self.save_generated_doc(doc_content)
        
        # Step 4: Run evaluation
        results = self.run_evaluation(metrics)
        
        if results:
            logger.info("=== Product Documentation Evaluation Completed ===")
            
            # Generate report
            self.create_eval_report(results)
            
            # Print summary
            print("\n" + "="*60)
            print("PRODUCT DOCUMENTATION EVALUATION RESULTS")
            print("="*60)
            
            for metric_type, metric_results in results.items():
                print(f"\n{metric_type.upper()} Results:")
                if isinstance(metric_results, dict):
                    for key, value in metric_results.items():
                        if isinstance(value, (int, float)):
                            print(f"  {key}: {value:.4f}")
                        else:
                            print(f"  {key}: {value}")
                else:
                    print(f"  {metric_results}")
            
            print("="*60)
            print(f"\nEvaluation report saved to: {self.report_path}")
        
        # Step 5: Create evaluation report
        self.create_eval_report(results)
        
        return results


def main():
    """Main function for command line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Evaluate Product Documentation Generation')
    parser.add_argument('--transcript', type=str, 
                       default='/Users/ankitku5/Desktop/vid2insight/docs/transcript.json',
                       help='Path to the transcript JSON file')
    parser.add_argument('--ground-truth', type=str,
                       default='/Users/ankitku5/Desktop/vid2insight/evaluation/ground_truth/detailed_product_Doc.txt', 
                       help='Path to the ground truth product documentation')
    parser.add_argument('--metrics', type=str, nargs='+', 
                       default=['bert', 'bleu', 'rouge', 'llm'],
                       help='Metrics to calculate (bert, bleu, rouge, llm)')
    parser.add_argument('--session-id', type=str, default='eval_session',
                       help='Session ID for the agent')
    
    args = parser.parse_args()
    
    # Create evaluator
    evaluator = ProductDocEvaluator(
        transcript_path=args.transcript,
        ground_truth_path=args.ground_truth
    )
    
    # Run evaluation
    results = evaluator.evaluate(metrics=args.metrics)
    
    if results:
        print("\nEvaluation completed successfully!")
        print(f"Generated documentation saved to: {evaluator.output_path}")
        print(f"Evaluation report saved to: {evaluator.report_path}")
        print("Detailed metrics saved to eval_results/ directory")
    else:
        print("\nEvaluation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
