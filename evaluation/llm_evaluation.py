"""LLM-based evaluation of text quality comparing generated text to reference."""

import os
import argparse
import json
import sys
from typing import Dict, List, Any
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from agent.config.base_config import BaseConfiguration
from agent.config.initialize_logger import setup_logger
from evaluation.constants.criteria import CRITERIA_DESCRIPTIONS, DEFAULT_LLM_METRICS, MAX_TEXT_LENGTH, CHART_COLORS
from evaluation.constants.paths import (
    DEFAULT_REFERENCE_PATH, DEFAULT_PREDICTION_PATH, 
    LLM_RESULTS_JSON_PATH, LLM_RESULTS_CSV_PATH, LLM_RESULTS_IMG_PATH
)
from evaluation.config.model_config import DEFAULT_LLM_MODEL

# Import for fallback method, only used if BaseConfiguration approach fails
try:
    import google.generativeai as genai_fallback
except ImportError:
    genai_fallback = None

# Set up logger
logger = setup_logger()

try:
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))
except Exception as e:
    logger.error(f"Error loading environment variables: {e}")
    raise

def read_file(file_path):
    """Read text from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        raise

def evaluate_with_llm(reference_text, prediction_text, criterion, criterion_description, llm_model=None):
    """Evaluate text using LLM."""
    try:
        # Create prompt for evaluation
        prompt = f"""
        You are an expert evaluator assessing the quality of generated text.
        
        You need to evaluate the generated text on the criterion of {criterion}:
        {criterion_description}
        
        Reference (Ground Truth) Text:
        ```
        {reference_text[:MAX_TEXT_LENGTH]}  # Limiting text length to avoid token limits
        ```
        
        Generated Text:
        ```
        {prediction_text[:MAX_TEXT_LENGTH]}  # Limiting text length to avoid token limits
        ```
        
        Based on the criterion of {criterion}, evaluate the generated text on a scale from 0.0 to 1.0, where:
        - 0.0 means it completely fails to meet the criterion
        - 0.25 means it poorly meets the criterion
        - 0.5 means it somewhat meets the criterion
        - 0.75 means it largely meets the criterion
        - 1.0 means it perfectly meets the criterion
        
        You can use any decimal value between 0.0 and 1.0 for fine-grained assessment.
        
        Provide your detailed reasoning first, then provide your final score on a new line as 'Score: X.XX' (a decimal number between 0.0 and 1.0, rounded to 2 decimal places).
        """
        
        result = ""
        
        # Get model configuration
        if llm_model is None:
            llm_model = DEFAULT_LLM_MODEL
        
        # Create model configuration dictionary for BaseConfiguration
        model_config = {
            'provider': 'google_genai',
            'model_name': 'gemini-1.5-flash-latest', 
        }
        
        logger.info(f"Using model: {llm_model} (mapped to {model_config['model_name']})")
        
        # Try the standard approach using BaseConfiguration first
        try:
            # Initialize the model using BaseConfiguration
            llm = BaseConfiguration.get_model(model_config)
            
            # Create a human message for the LLM
            message = HumanMessage(content=prompt)
            
            # Call the LLM
            response = llm.invoke([message])
            
            # Extract the content from the response
            result = response.content
            logger.info("Successfully used BaseConfiguration approach")
            
        # If the standard approach fails, fall back to direct Google Generative AI usage
        except Exception as e:
            logger.warning(f"BaseConfiguration approach failed: {e}. Trying fallback method...")
            
            if genai_fallback is None:
                try:
                    # Import here to avoid conflicts if not needed
                    import google.generativeai as genai_local
                except ImportError:
                    raise ImportError("Neither the BaseConfiguration approach nor the fallback method are available. Please install langchain and google-generativeai.")
            else:
                genai_local = genai_fallback
            
            # Configure the API key
            genai_local.configure(api_key=os.environ.get("GEMINI_API_KEY"))
            
            # Create a generative model instance
            model = genai_local.GenerativeModel(model_config['model_name'])
            
            # Generate content
            response = model.generate_content(prompt)
            
            # Extract text from response
            result = response.text
            logger.info("Successfully used fallback approach with direct Google API")
        
        # Extract score and reasoning
        lines = result.strip().split('\n')
        score_line = next((line for line in lines if "Score:" in line), "Score: 0.0")
        
        # Extract numeric score from the score line
        try:
            # Look for decimal number in the score line
            import re
            score_match = re.search(r'Score:\s*(\d+\.\d+|\d+)', score_line)
            if score_match:
                score = float(score_match.group(1))
                # Ensure score is between 0.0 and 1.0
                score = max(0.0, min(score, 1.0))
            else:
                # Fallback if no numeric score found
                score = 0.0
        except Exception:
            # If parsing fails, default to 0.0
            score = 0.0
        
        # Everything except the score line is reasoning
        reasoning = '\n'.join([line for line in lines if "Score:" not in line])
        
        return {
            "score": score,
            "reasoning": reasoning.strip()
        }
    except Exception as e:
        logger.error(f"Error evaluating with LLM for criterion '{criterion}': {e}")
        raise

def run_evaluations(reference_path, prediction_path, eval_metrics, llm_model=None):
    """Run evaluations for all specified metrics."""
    try:
        reference = read_file(reference_path)
        prediction = read_file(prediction_path)
        
        # Print the first 100 characters of each file for verification
        logger.info("Reference text (first 100 chars): %s", reference[:100])
        logger.info("Prediction text (first 100 chars): %s", prediction[:100])
        
        logger.info(f"\nRunning evaluations for metrics: {', '.join(eval_metrics)}")
        
        # Results 
        results = {}
        
        # Run evaluations for each criterion
        for criterion in eval_metrics:
            logger.info(f"Evaluating {criterion}...")
            
            try:
                # Run evaluation
                result = evaluate_with_llm(
                    reference, 
                    prediction, 
                    criterion, 
                    CRITERIA_DESCRIPTIONS[criterion],
                    llm_model
                )
                
                # Store result
                results[criterion] = {
                    "average_score": result["score"],
                    "details": [{"score": result["score"], "explanation": result["reasoning"]}]
                }
                
                logger.info(f"  {criterion}: {result['score']:.2f}")
                
                # Save individual evaluation to file
                eval_dir = os.path.dirname(LLM_RESULTS_JSON_PATH)
                os.makedirs(eval_dir, exist_ok=True)
                
                with open(os.path.join(eval_dir, f"eval_{criterion}.json"), "w") as f:
                    json.dump({
                        "criterion": criterion,
                        "score": result["score"],
                        "reasoning": result["reasoning"]
                    }, f, indent=2)
                
            except Exception as e:
                logger.error(f"Error evaluating criterion '{criterion}': {e}")
                # Continue with other criteria even if one fails
                results[criterion] = {
                    "average_score": 0.0,
                    "details": [{"score": 0.0, "explanation": f"Error during evaluation: {str(e)}"}]
                }
        
        return results
    
    except Exception as e:
        logger.error(f"Error in run_evaluations: {e}")
        raise

def visualize_results(results):
    """Create a visualization of evaluation results."""
    try:
        criteria = list(results.keys())
        scores = [results[c]["average_score"] for c in criteria]
        
        plt.figure(figsize=(12, 8))
        bars = plt.bar(criteria, scores, color=CHART_COLORS['primary'])
        plt.ylim(0, 1.0)
        plt.xlabel('Evaluation Criteria')
        plt.ylabel('Score (0-1)')
        plt.title('LLM-as-Judge Evaluation Results')
        plt.xticks(rotation=45)
        
        # Add score labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{height:.2f}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(LLM_RESULTS_IMG_PATH), exist_ok=True)
        plt.savefig(LLM_RESULTS_IMG_PATH)
        logger.info(f"Visualization saved to '{LLM_RESULTS_IMG_PATH}'")
    
    except Exception as e:
        logger.error(f"Error visualizing results: {e}")
        # Don't raise here to allow saving the results in JSON/CSV even if visualization fails

def main():
    """Parse arguments and run LLM evaluation."""
    try:
        parser = argparse.ArgumentParser(description='Evaluate text using LLM')
        parser.add_argument('--reference', default=DEFAULT_REFERENCE_PATH, 
                            help='Path to the reference/ground truth text file')
        parser.add_argument('--prediction', default=DEFAULT_PREDICTION_PATH, 
                            help='Path to the prediction/model generated text file')
        parser.add_argument('--metrics', nargs='+', 
                            default=DEFAULT_LLM_METRICS,
                            help='Evaluation metrics to use')
        parser.add_argument('--model', default=DEFAULT_LLM_MODEL,
                            help='LLM model to use for evaluation (uses models defined in project config)')
        
        args = parser.parse_args()
        
        # Get absolute paths if only filenames are provided
        reference_path = args.reference
        if not os.path.isabs(reference_path):
            reference_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), reference_path)
            
        prediction_path = args.prediction
        if not os.path.isabs(prediction_path):
            prediction_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), prediction_path)
        
        # Check if files exist
        if not os.path.exists(reference_path):
            logger.error(f"Error: Reference file not found: {reference_path}")
            return
            
        if not os.path.exists(prediction_path):
            logger.error(f"Error: Prediction file not found: {prediction_path}")
            return
        
        logger.info(f"Evaluating text with LLM:")
        logger.info(f"  Reference: {reference_path}")
        logger.info(f"  Prediction: {prediction_path}")
        logger.info(f"  Model: {args.model}")
        logger.info("-" * 50)
        
        # Run evaluation
        results = run_evaluations(reference_path, prediction_path, args.metrics, args.model)
        
        # Visualize results
        visualize_results(results)
        
        logger.info("\nEvaluation complete.")
        
        try:
            # Save detailed results to CSV
            os.makedirs(os.path.dirname(LLM_RESULTS_CSV_PATH), exist_ok=True)
            df_results = pd.DataFrame({
                'Criterion': list(results.keys()),
                'Score': [results[c]["average_score"] for c in results.keys()],
                'Explanation': [results[c]["details"][0]["explanation"] for c in results.keys()]
            })
            df_results.to_csv(LLM_RESULTS_CSV_PATH, index=False)
            logger.info(f"Detailed results saved to '{LLM_RESULTS_CSV_PATH}'")
        except Exception as e:
            logger.error(f"Error saving results to CSV: {e}")
        
        try:
            # Save all results to a single JSON file
            os.makedirs(os.path.dirname(LLM_RESULTS_JSON_PATH), exist_ok=True)
            with open(LLM_RESULTS_JSON_PATH, "w") as f:
                json.dump(results, f, indent=2)
            logger.info(f"Complete results saved to '{LLM_RESULTS_JSON_PATH}'")
        except Exception as e:
            logger.error(f"Error saving results to JSON: {e}")
    
    except Exception as e:
        logger.error(f"An error occurred in the main function: {e}")
        sys.exit(1)
        
def run(reference_path=DEFAULT_REFERENCE_PATH, prediction_path=DEFAULT_PREDICTION_PATH, metrics=None, model=None):
    """Run LLM evaluation (function that can be imported from other modules)."""
    try:
        if not metrics:
            metrics = DEFAULT_LLM_METRICS
        
        # Get absolute paths if only filenames are provided
        if not os.path.isabs(reference_path):
            reference_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), reference_path)
            
        if not os.path.isabs(prediction_path):
            prediction_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), prediction_path)
        
        # Check if files exist
        if not os.path.exists(reference_path):
            logger.error(f"Error: Reference file not found: {reference_path}")
            return None
            
        if not os.path.exists(prediction_path):
            logger.error(f"Error: Prediction file not found: {prediction_path}")
            return None
        
        logger.info(f"Evaluating text with LLM:")
        logger.info(f"  Reference: {reference_path}")
        logger.info(f"  Prediction: {prediction_path}")
        logger.info(f"  Model: {model}")
        logger.info("-" * 50)
        
        # Run evaluation
        results = run_evaluations(reference_path, prediction_path, metrics, model)
        
        # Visualize results
        visualize_results(results)
        
        try:
            # Save detailed results to CSV
            os.makedirs(os.path.dirname(LLM_RESULTS_CSV_PATH), exist_ok=True)
            df_results = pd.DataFrame({
                'Criterion': list(results.keys()),
                'Score': [results[c]["average_score"] for c in results.keys()],
                'Explanation': [results[c]["details"][0]["explanation"] for c in results.keys()]
            })
            df_results.to_csv(LLM_RESULTS_CSV_PATH, index=False)
            logger.info(f"Detailed results saved to '{LLM_RESULTS_CSV_PATH}'")
        except Exception as e:
            logger.error(f"Error saving results to CSV: {e}")
        
        try:
            # Save all results to a single JSON file
            os.makedirs(os.path.dirname(LLM_RESULTS_JSON_PATH), exist_ok=True)
            with open(LLM_RESULTS_JSON_PATH, "w") as f:
                json.dump(results, f, indent=2)
            logger.info(f"Complete results saved to '{LLM_RESULTS_JSON_PATH}'")
        except Exception as e:
            logger.error(f"Error saving results to JSON: {e}")
        
        return results
        
    except Exception as e:
        logger.error(f"An error occurred in the run function: {e}")
        return None

if __name__ == '__main__':
    main()
