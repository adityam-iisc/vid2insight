#!/usr/bin/env python
"""Evaluation script for Executive Summary generation.

This script:
1. Loads the transcript data 
2. Calls the executive summary generation function from the agent
3. Saves the generated executive summary 
4. Runs evaluation metrics comparing generated vs ground truth
"""

import sys
import os
import json
import asyncio

# Add the project root directory to sys.path to allow imports from the root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agent.vid2_insight_graph import app
from agent.doc_agent.constants import Intent as DocIntent
from agent.constants import AgentType
from evaluation.calculate_all_metrics import calculate_all_metrics
from agent.config.initialize_logger import setup_logger

# Set up logger
logger = setup_logger()

class ExecSummaryEvaluator:
    """Evaluator for Executive Summary generation."""
    
    def __init__(self, transcript_path: str = None, ground_truth_path: str = None):
        """Initialize the evaluator.
        
        Args:
            transcript_path: Path to the transcript.json file
            ground_truth_path: Path to the ground truth executive summary
        """
        self.transcript_path = transcript_path or '/Users/ankitku5/Desktop/vid2insight/docs/transcript.json'
        self.ground_truth_path = ground_truth_path or '/Users/ankitku5/Desktop/vid2insight/evaluation/ground_truth/executive_summary.txt'
        self.output_path = '/Users/ankitku5/Desktop/vid2insight/evaluation/model_outputs/model_generated_exec_summary.txt'
        self.report_path = '/Users/ankitku5/Desktop/vid2insight/evaluation/reports/exec_summary_evaluation_report.md'

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

    def generate_exec_summary(self, transcript_data: dict, session_id: str = "eval_session"):
        """Generate executive summary using the agent.
        
        Args:
            transcript_data: The loaded transcript data
            session_id: Session ID for the agent
            
        Returns:
            str: Generated executive summary content
        """
        try:
            logger.info("Generating executive summary using agent...")
            
            # Set up the context similar to how it's done in the UI
            video_context = transcript_data['combined_transcript'][0]['combined_transcript']
            
            # Configure the agent
            config = {"configurable": {"thread_id": session_id, 'agent_choice': AgentType.doc_agent.value}}
            
            # Create the payload for executive summary generation
            payload = {
                "messages": [{"role": "human", "content": 'generate an executive summary for the video content.'}],
                'expert_preference': AgentType.doc_agent.value,
                'video_context': video_context,
                'intent': DocIntent.GENERATE_EXEC_SUMMARY.value
            }
            
            # Call the agent
            raw = asyncio.run(app.ainvoke(payload, config))
            
            # Get the generated content - for executive summary it should be in doc_content
            generated_content = raw.get('doc_content', '') or raw.get('answer', '') or raw.get('exec_summary', '') or raw.get('chat_content', '')
            
            if not generated_content or not generated_content.strip():
                logger.error("Generated executive summary is empty")
                return None
            
            logger.info("Executive summary generated successfully")
            return generated_content
            
        except Exception as e:
            logger.error(f"Error generating executive summary: {e}")
            return None

    def save_generated_summary(self, summary_content: str):
        """Save the generated executive summary to file.
        
        Args:
            summary_content: The generated executive summary content
        """
        try:
            with open(self.output_path, 'w', encoding='utf-8') as f:
                f.write(summary_content)
            logger.info(f"Generated executive summary saved to {self.output_path}")
        except Exception as e:
            logger.error(f"Error saving generated executive summary: {e}")

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
                logger.error(f"Generated executive summary file not found: {self.output_path}")
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

    def evaluate(self, metrics: list = None):
        """Complete evaluation pipeline.
        
        Args:
            metrics: List of metrics to run (default: all metrics)
            
        Returns:
            dict: Evaluation results
        """
        logger.info("=== Starting Executive Summary Evaluation ===")
        
        # Step 1: Load transcript
        transcript_data = self.load_transcript()
        if not transcript_data:
            logger.error("Failed to load transcript data")
            return None
        
        # Step 2: Generate executive summary
        summary_content = self.generate_exec_summary(transcript_data)
        if not summary_content:
            logger.error("Failed to generate executive summary")
            return None
        
        # Step 3: Save generated summary
        self.save_generated_summary(summary_content)
        
        # Step 4: Run evaluation
        results = self.run_evaluation(metrics)
        
        if results:
            logger.info("=== Executive Summary Evaluation Completed ===")
            
            # Print summary
            print("\n" + "="*60)
            print("EXECUTIVE SUMMARY EVALUATION RESULTS")
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
        
        return results

def main():
    """Main function for command line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Evaluate Executive Summary Generation')
    parser.add_argument('--transcript', type=str, 
                       default='/Users/ankitku5/Desktop/vid2insight/docs/transcript.json',
                       help='Path to the transcript JSON file')
    parser.add_argument('--ground-truth', type=str,
                       default='/Users/ankitku5/Desktop/vid2insight/evaluation/ground_truth/executive_summary.txt', 
                       help='Path to the ground truth executive summary')
    parser.add_argument('--metrics', type=str, nargs='+', 
                       default=['bert', 'bleu', 'rouge', 'llm'],
                       help='Metrics to calculate (bert, bleu, rouge, llm)')
    parser.add_argument('--session-id', type=str, default='eval_session',
                       help='Session ID for the agent')
    
    args = parser.parse_args()
    
    # Create evaluator
    evaluator = ExecSummaryEvaluator(
        transcript_path=args.transcript,
        ground_truth_path=args.ground_truth
    )
    
    # Run evaluation
    results = evaluator.evaluate(metrics=args.metrics)
    
    if results:
        print("\nEvaluation completed successfully!")
        print(f"Generated executive summary saved to: {evaluator.output_path}")
        print("Detailed results saved to eval_results/ directory")
    else:
        print("\nEvaluation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
