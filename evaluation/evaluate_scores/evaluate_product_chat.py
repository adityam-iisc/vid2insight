#!/usr/bin/env python
"""Evaluation script for Product Chat responses.

This script:
1. Loads the transcript data 
2. Calls the product chat generation function
3. Saves the generated product chat responses
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
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.ui.ui import Facilitator
from agent.vid2_insight_graph import app
from agent.doc_agent.constants import Intent as DocIntent
from agent.constants import AgentType
from evaluation.generate_output.generate_product_chat import generate_product_chat_responses, load_transcript, SAMPLE_QUERIES
from evaluation.calculate_all_metrics import calculate_all_metrics
from agent.config.initialize_logger import setup_logger

# Set up logger
logger = setup_logger()

class ProductChatEvaluator:
    """Evaluator for Product Chat responses."""
    
    def __init__(self, transcript_path: str = None, ground_truth_path: str = None):
        """Initialize the evaluator.
        
        Args:
            transcript_path: Path to the transcript.json file
            ground_truth_path: Path to the ground truth product chat responses
        """
        self.transcript_path = transcript_path or '/Users/ankitku5/Desktop/vid2insight/docs/transcript.json'
        self.ground_truth_path = ground_truth_path or '/Users/ankitku5/Desktop/vid2insight/evaluation/ground_truth/Product_chat.txt'
        self.output_path = '/Users/ankitku5/Desktop/vid2insight/evaluation/model_outputs/model_generated_product_chat.txt'
        self.results_dir = '/Users/ankitku5/Desktop/vid2insight/evaluation/reports'
        
        # Create results directory if it doesn't exist
        os.makedirs(self.results_dir, exist_ok=True)
        
    def load_transcript(self):
        """Load transcript data from JSON file."""
        return load_transcript(self.transcript_path)
    
    def load_ground_truth(self):
        """Load ground truth chat responses."""
        try:
            with open(self.ground_truth_path, 'r') as f:
                content = f.read()
            logger.info(f"Loaded ground truth from {self.ground_truth_path}")
            return content
        except Exception as e:
            logger.error(f"Error loading ground truth: {e}")
            return None
    
    def generate_responses(self):
        """Generate product chat responses and save to file."""
        try:
            # Load transcript
            transcript_data = self.load_transcript()
            if not transcript_data:
                return False
            
            # Generate responses
            responses = generate_product_chat_responses(transcript_data)
            if not responses:
                return False
            
            # Save responses to file
            with open(self.output_path, 'w') as f:
                for item in responses:
                    f.write(f"Q: {item['query']}\n\n")
                    f.write(f"A: {item['response']}\n\n")
                    f.write("-" * 80 + "\n\n")
            
            logger.info(f"Generated chat responses saved to {self.output_path}")
            return True
        except Exception as e:
            logger.error(f"Error generating responses: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def extract_sections_from_ground_truth(self, content):
        """Extract sections from ground truth document in Q&A format."""
        sections = []
        # Split by the section separator "---"
        qa_sections = content.split("---")
        
        for section in qa_sections:
            section = section.strip()
            if not section or section.startswith('//'):  # Skip empty or comment sections
                continue
                
            # Extract only the answer part (after "A: ")
            if "A:" in section:
                answer_part = section.split("A:")[1].strip()
                sections.append(answer_part)
        
        return sections
    
    def extract_responses_from_generated(self, content):
        """Extract responses from generated output."""
        responses = []
        # Split by the delimiter line
        sections = content.split("-" * 80)
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
                
            # Extract only the answer part (after "A: ")
            if "A:" in section:
                answer_part = section.split("A:")[1].strip()
                responses.append(answer_part)
            
        return responses
    
    def evaluate(self):
        """Run evaluation metrics on the generated chat responses."""
        try:
            # Load generated and ground truth content
            with open(self.output_path, 'r') as f:
                generated_content = f.read()
            
            ground_truth_content = self.load_ground_truth()
            if not ground_truth_content:
                return False
            
            # Extract sections for comparison
            ground_truth_sections = self.extract_sections_from_ground_truth(ground_truth_content)
            generated_responses = self.extract_responses_from_generated(generated_content)
            
            # Evaluate metrics
            metrics_results = {}
            
            # Compare responses to corresponding sections in ground truth
            # We take the minimum length in case there are different numbers of items
            for i in range(min(len(SAMPLE_QUERIES), len(ground_truth_sections), len(generated_responses))):
                query = SAMPLE_QUERIES[i]
                reference = ground_truth_sections[i]
                candidate = generated_responses[i]
                
                # Calculate metrics for this response - using temporary files since calculate_all_metrics works with files
                import tempfile
                import os
                
                # Create temporary files
                ref_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
                ref_file.write(reference)
                ref_file.close()
                
                cand_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
                cand_file.write(candidate)
                cand_file.close()
                
                # Calculate metrics using file paths
                metrics = calculate_all_metrics(ref_file.name, cand_file.name)
                
                # Clean up temporary files
                os.unlink(ref_file.name)
                os.unlink(cand_file.name)
                
                metrics_results[f"query_{i+1}"] = {
                    "query": query,
                    "metrics": metrics or {}
                }
            
            # Calculate average metrics across all responses
            # Initialize with structure matching the metrics format
            avg_metrics = {
                "bert": {"precision": 0, "recall": 0, "f1": 0},
                "bleu": {"bleu_1": 0, "bleu_2": 0, "bleu_3": 0, "bleu_4": 0},
                "rouge": {
                    "rouge_1": {"precision": 0, "recall": 0, "f1": 0},
                    "rouge_2": {"precision": 0, "recall": 0, "f1": 0},
                    "rouge_l": {"precision": 0, "recall": 0, "f1": 0}
                },
                "llm_fluency": 0,
                "llm_relevance": 0,
                "llm_correctness": 0,
                "llm_coherence": 0,
                "llm_helpfulness": 0,
                "llm_harmlessness": 0
            }
            
            # Sum all metrics
            num_responses = 0
            for query_id, response_data in metrics_results.items():
                if not isinstance(response_data, dict) or "metrics" not in response_data:
                    continue
                
                num_responses += 1
                metrics = response_data["metrics"]
                
                # Process BERT scores
                if "bert" in metrics and isinstance(metrics["bert"], dict):
                    for key in ["precision", "recall", "f1"]:
                        if key in metrics["bert"] and isinstance(metrics["bert"][key], (int, float)):
                            avg_metrics["bert"][key] += metrics["bert"][key]
                
                # Process BLEU scores
                if "bleu" in metrics and isinstance(metrics["bleu"], dict):
                    for key in ["bleu_1", "bleu_2", "bleu_3", "bleu_4"]:
                        if key in metrics["bleu"] and isinstance(metrics["bleu"][key], (int, float)):
                            avg_metrics["bleu"][key] += metrics["bleu"][key]
                
                # Process ROUGE scores
                if "rouge" in metrics and isinstance(metrics["rouge"], dict):
                    for rouge_type in ["rouge_1", "rouge_2", "rouge_l"]:
                        if rouge_type in metrics["rouge"] and isinstance(metrics["rouge"][rouge_type], dict):
                            for metric in ["precision", "recall", "f1"]:
                                if metric in metrics["rouge"][rouge_type] and isinstance(metrics["rouge"][rouge_type][metric], (int, float)):
                                    avg_metrics["rouge"][rouge_type][metric] += metrics["rouge"][rouge_type][metric]
                
                # Process LLM metrics
                if "llm" in metrics and isinstance(metrics["llm"], dict):
                    for llm_metric in ["correctness", "relevance", "coherence", "fluency", "helpfulness", "harmlessness"]:
                        if llm_metric in metrics["llm"] and isinstance(metrics["llm"][llm_metric], dict):
                            avg_key = f"llm_{llm_metric}"
                            if "average_score" in metrics["llm"][llm_metric] and isinstance(metrics["llm"][llm_metric]["average_score"], (int, float)):
                                avg_metrics[avg_key] += metrics["llm"][llm_metric]["average_score"]
            
            # Calculate averages
            if num_responses > 0:
                # Average BERT scores
                for key in avg_metrics["bert"]:
                    avg_metrics["bert"][key] /= num_responses
                
                # Average BLEU scores
                for key in avg_metrics["bleu"]:
                    avg_metrics["bleu"][key] /= num_responses
                
                # Average ROUGE scores
                for rouge_type in avg_metrics["rouge"]:
                    for metric in avg_metrics["rouge"][rouge_type]:
                        avg_metrics["rouge"][rouge_type][metric] /= num_responses
                
                # Average LLM metrics
                for key in [k for k in avg_metrics if k.startswith("llm_")]:
                    avg_metrics[key] /= num_responses
            
            metrics_results["average"] = avg_metrics
            
            # Save results to file
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = os.path.join(self.results_dir, f"product_chat_evaluation_{timestamp}.json")
            
            with open(results_file, 'w') as f:
                json.dump(metrics_results, f, indent=2)
            
            logger.info(f"Evaluation results saved to {results_file}")
            
            # Generate markdown report
            self.generate_report(metrics_results)
            
            return True
            
        except Exception as e:
            logger.error(f"Error during evaluation: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def generate_report(self, metrics_results):
        """Generate a comprehensive markdown report."""
        try:
            report_path = "/Users/ankitku5/Desktop/vid2insight/evaluation/reports/product_chat_evaluation_report.md"
            
            with open(report_path, 'w') as f:
                f.write("# Product Chat Evaluation Report\n\n")
                
                # Add timestamp
                f.write(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Add summary section
                f.write("## Summary\n\n")
                
                # Add average metrics table - Organized by metric categories
                f.write("### Average Metrics\n\n")
                
                avg_metrics = metrics_results.get("average", {})
                
                # BERT metrics section
                f.write("#### BERT Metrics\n\n")
                f.write("| Metric | Score |\n")
                f.write("|--------|-------|\n")
                if "bert" in avg_metrics and isinstance(avg_metrics["bert"], dict):
                    for key, value in avg_metrics["bert"].items():
                        if isinstance(value, (int, float)):
                            f.write(f"| bert_{key} | {value:.4f} |\n")
                        else:
                            f.write(f"| bert_{key} | {value} |\n")
                f.write("\n")
                
                # BLEU metrics section
                f.write("#### BLEU Metrics\n\n")
                f.write("| Metric | Score |\n")
                f.write("|--------|-------|\n")
                if "bleu" in avg_metrics and isinstance(avg_metrics["bleu"], dict):
                    for key, value in avg_metrics["bleu"].items():
                        if isinstance(value, (int, float)):
                            f.write(f"| {key} | {value:.4f} |\n")
                        else:
                            f.write(f"| {key} | {value} |\n")
                f.write("\n")
                
                # ROUGE metrics section
                f.write("#### ROUGE Metrics\n\n")
                f.write("| Metric | Score |\n")
                f.write("|--------|-------|\n")
                if "rouge" in avg_metrics and isinstance(avg_metrics["rouge"], dict):
                    for rouge_type in sorted(avg_metrics["rouge"].keys()):
                        if isinstance(avg_metrics["rouge"][rouge_type], dict):
                            for metric, value in avg_metrics["rouge"][rouge_type].items():
                                if isinstance(value, (int, float)):
                                    f.write(f"| {rouge_type}_{metric} | {value:.4f} |\n")
                                else:
                                    f.write(f"| {rouge_type}_{metric} | {value} |\n")
                f.write("\n")
                
                # LLM metrics section
                f.write("#### LLM Evaluation Metrics\n\n")
                f.write("| Metric | Score |\n")
                f.write("|--------|-------|\n")
                llm_metrics = [key for key in avg_metrics if key.startswith("llm_")]
                for key in sorted(llm_metrics):
                    # Format the metric name for better readability
                    metric_name = key.replace("llm_", "").capitalize()
                    value = avg_metrics[key]
                    if isinstance(value, (int, float)):
                        f.write(f"| {metric_name} | {value:.4f} |\n")
                    else:
                        f.write(f"| {metric_name} | {value} |\n")
                f.write("\n")
                
                # Add individual query results
                f.write("\n## Individual Query Results\n\n")
                
                # Filter out the "average" key
                query_results = {k: v for k, v in metrics_results.items() if k != "average"}
                
                for idx, (query_id, data) in enumerate(query_results.items()):
                    try:
                        f.write(f"### Query {idx+1}: {data['query']}\n\n")
                        
                        metrics = data["metrics"]
                        
                        # Group metrics by category
                        bert_metrics = {k: v for k, v in metrics.items() if k.startswith("bert")}
                        bleu_metrics = {k: v for k, v in metrics.items() if k == "bleu"}
                        rouge_metrics = {k: v for k, v in metrics.items() if k.startswith("rouge")}
                        llm_metrics = {k: v for k, v in metrics.items() if k.startswith("llm_")}
                    except (KeyError, TypeError) as e:
                        logger.error(f"Error processing query {idx+1} ({query_id}): {e}")
                        continue
                    
                    try:
                        # BERT metrics
                        if bert_metrics:
                            f.write("#### BERT Metrics\n\n")
                            f.write("| Metric | Score |\n")
                            f.write("|--------|-------|\n")
                            if isinstance(bert_metrics.get("bert"), dict):
                                for key, value in bert_metrics["bert"].items():
                                    if isinstance(value, (int, float)):
                                        f.write(f"| bert_{key} | {value:.4f} |\n")
                                    else:
                                        f.write(f"| bert_{key} | {str(value)} |\n")
                            else:
                                for key, value in bert_metrics.items():
                                    if isinstance(value, (int, float)):
                                        f.write(f"| {key} | {value:.4f} |\n")
                                    else:
                                        f.write(f"| {key} | {str(value)} |\n")
                            f.write("\n")
                        
                        # BLEU metrics
                        if bleu_metrics:
                            f.write("#### BLEU Metrics\n\n")
                            f.write("| Metric | Score |\n")
                            f.write("|--------|-------|\n")
                            if isinstance(bleu_metrics.get("bleu"), dict):
                                for key, value in bleu_metrics["bleu"].items():
                                    if isinstance(value, (int, float)):
                                        f.write(f"| {key} | {value:.4f} |\n")
                                    else:
                                        f.write(f"| {key} | {str(value)} |\n")
                            else:
                                for key, value in bleu_metrics.items():
                                    if isinstance(value, (int, float)):
                                        f.write(f"| {key} | {value:.4f} |\n")
                                    else:
                                        f.write(f"| {key} | {str(value)} |\n")
                            f.write("\n")
                        
                        # ROUGE metrics
                        if rouge_metrics:
                            f.write("#### ROUGE Metrics\n\n")
                            f.write("| Metric | Score |\n")
                            f.write("|--------|-------|\n")
                            if isinstance(rouge_metrics.get("rouge"), dict):
                                for rouge_type in sorted(rouge_metrics["rouge"].keys()):
                                    if isinstance(rouge_metrics["rouge"][rouge_type], dict):
                                        for metric, value in rouge_metrics["rouge"][rouge_type].items():
                                            if isinstance(value, (int, float)):
                                                f.write(f"| {rouge_type}_{metric} | {value:.4f} |\n")
                                            else:
                                                f.write(f"| {rouge_type}_{metric} | {str(value)} |\n")
                            else:
                                for key in sorted(rouge_metrics.keys()):
                                    value = rouge_metrics[key]
                                    if isinstance(value, (int, float)):
                                        f.write(f"| {key} | {value:.4f} |\n")
                                    else:
                                        f.write(f"| {key} | {str(value)} |\n")
                            f.write("\n")
                        
                        # LLM metrics
                        if llm_metrics:
                            f.write("#### LLM Evaluation Metrics\n\n")
                            f.write("| Metric | Score |\n")
                            f.write("|--------|-------|\n")
                            if isinstance(llm_metrics.get("llm"), dict):
                                for metric_name, metric_data in sorted(llm_metrics["llm"].items()):
                                    if isinstance(metric_data, dict) and "average_score" in metric_data:
                                        value = metric_data["average_score"]
                                        capitalized_name = metric_name.capitalize()
                                        if isinstance(value, (int, float)):
                                            f.write(f"| {capitalized_name} | {value:.4f} |\n")
                                        else:
                                            f.write(f"| {capitalized_name} | {str(value)} |\n")
                            else:
                                for key in sorted(llm_metrics.keys()):
                                    # Format the metric name for better readability
                                    metric_name = key.replace("llm_", "").capitalize()
                                    value = llm_metrics[key]
                                    if isinstance(value, (int, float)):
                                        f.write(f"| {metric_name} | {value:.4f} |\n")
                                    else:
                                        f.write(f"| {metric_name} | {str(value)} |\n")
                            f.write("\n")
                    except Exception as e:
                        logger.error(f"Error writing metrics for query {idx+1}: {e}")
                        continue
                
                # Add methodology section
                f.write("\n## Evaluation Methodology\n\n")
                f.write("The evaluation uses the following metrics:\n\n")
                f.write("- **BERT Score**: Measures semantic similarity using BERT embeddings\n")
                f.write("- **BLEU**: Measures the precision of n-grams between generated and reference text\n")
                f.write("- **ROUGE**: Measures the overlap of n-grams between generated and reference text\n")
                f.write("  - ROUGE-1: Unigram overlap\n")
                f.write("  - ROUGE-2: Bigram overlap\n")
                f.write("  - ROUGE-L: Longest common subsequence\n")
                f.write("- **LLM-based metrics**: Using an LLM to evaluate on a continuous scale (0.0-1.0):\n")
                f.write("  - **Fluency**: How natural and readable the generated text is\n")
                f.write("  - **Relevance**: How well the response answers the query\n")
                f.write("  - **Correctness**: How factually accurate the response is\n")
                f.write("  - **Coherence**: How logically structured and consistent the response is\n")
                f.write("  - **Helpfulness**: How useful the information is for the intended purpose\n")
                f.write("  - **Harmlessness**: Whether the content is free from harmful elements\n\n")
                
                f.write("## Next Steps\n\n")
                f.write("Based on these evaluation results, consider the following next steps:\n\n")
                f.write("1. Analyze queries with low performance scores to identify patterns of weakness\n")
                f.write("2. Refine the product chat generation process to improve areas with low scores\n")
                f.write("3. Expand the set of test queries to cover more diverse scenarios\n")
                f.write("4. Conduct human evaluation to complement automated metrics\n")
            
            logger.info(f"Evaluation report generated at {report_path}")
            
            # Print a summary of the metrics to the console
            self.print_metrics_summary(metrics_results)
            return True
                
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def print_metrics_summary(self, metrics_results):
        """Print a formatted summary of evaluation metrics to the console."""
        try:
            avg_metrics = metrics_results.get("average", {})
            
            if not avg_metrics:
                logger.warning("No average metrics available to display")
                return
            
            print("\n" + "="*80)
            print(" "*30 + "EVALUATION METRICS SUMMARY")
            print("="*80 + "\n")
            
            # Format metrics by category
            print("\033[1m" + "BERT Metrics:" + "\033[0m")
            if "bert" in avg_metrics and isinstance(avg_metrics["bert"], dict):
                for key, value in avg_metrics["bert"].items():
                    if isinstance(value, (int, float)):
                        print(f"  bert_{key:<11}: {value:.4f}")
                    else:
                        print(f"  bert_{key:<11}: {value}")
            else:
                print("  No BERT metrics available")
            print()
            
            print("\033[1m" + "BLEU Metric:" + "\033[0m")
            if "bleu" in avg_metrics and isinstance(avg_metrics["bleu"], dict):
                for key, value in avg_metrics["bleu"].items():
                    if isinstance(value, (int, float)):
                        print(f"  {key:<15}: {value:.4f}")
                    else:
                        print(f"  {key:<15}: {value}")
            else:
                print("  No BLEU metric available")
            print()
            
            print("\033[1m" + "ROUGE Metrics:" + "\033[0m")
            if "rouge" in avg_metrics and isinstance(avg_metrics["rouge"], dict):
                for rouge_type in sorted(avg_metrics["rouge"].keys()):
                    if isinstance(avg_metrics["rouge"][rouge_type], dict):
                        for metric, value in avg_metrics["rouge"][rouge_type].items():
                            metric_name = f"{rouge_type}_{metric}"
                            if isinstance(value, (int, float)):
                                print(f"  {metric_name:<15}: {value:.4f}")
                            else:
                                print(f"  {metric_name:<15}: {value}")
            else:
                print("  No ROUGE metrics available")
            print()
            
            print("\033[1m" + "LLM Evaluation Metrics:" + "\033[0m")
            llm_metrics = {k: v for k, v in avg_metrics.items() if k.startswith("llm_")}
            if llm_metrics:
                for key in sorted(llm_metrics.keys()):
                    # Format the metric name for better readability
                    metric_name = key.replace("llm_", "").capitalize()
                    value = llm_metrics[key]
                    if isinstance(value, (int, float)):
                        print(f"  {metric_name:<15}: {value:.4f}")
                    else:
                        print(f"  {metric_name:<15}: {value}")
            else:
                print("  No LLM metrics available")
                
            print("\n" + "="*80)
            
        except Exception as e:
            logger.error(f"Error printing metrics summary: {e}")

def main():
    """Main function to run the evaluation."""
    print("\n" + "="*80)
    print(" "*25 + "PRODUCT CHAT EVALUATION SYSTEM")
    print("="*80 + "\n")
    
    evaluator = ProductChatEvaluator()
    
    # Generate responses
    print("\033[1m" + "Step 1: Generating product chat responses...\033[0m")
    success = evaluator.generate_responses()
    if not success:
        print("\033[91mFailed to generate product chat responses. Exiting.\033[0m")
        return
    print("\033[92mProduct chat responses generated successfully!\033[0m\n")
    
    # Evaluate responses
    print("\033[1m" + "Step 2: Evaluating product chat responses...\033[0m")
    print("This will calculate BERT, BLEU, ROUGE, and LLM evaluation metrics.")
    print("Please wait, this may take a few minutes...")
    
    success = evaluator.evaluate()
    if not success:
        print("\033[91mFailed to evaluate product chat responses. Exiting.\033[0m")
        return
    
    # Report location
    report_path = "/Users/ankitku5/Desktop/vid2insight/evaluation/reports/product_chat_evaluation_report.md"
    print("\n\033[92mProduct chat evaluation completed successfully!\033[0m")
    print(f"\nDetailed report saved to: {report_path}")
    print("Run 'open " + report_path + "' to view the full markdown report.")

if __name__ == "__main__":
    main()
