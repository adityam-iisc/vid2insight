#!/usr/bin/env python
# filepath: /Users/ankitku5/Desktop/Data_seicene_college_project/evaluation/run_evaluation.py
"""Command-line interface for running all evaluation metrics."""

import argparse
import os
import sys

# Add the parent directory to sys.path to allow imports from the root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import from the evaluation package
from evaluation.constants.paths import DEFAULT_REFERENCE_PATH, DEFAULT_PREDICTION_PATH
from evaluation.constants.criteria import DEFAULT_AUTO_METRICS, DEFAULT_LLM_METRICS, DEFAULT_ALL_METRICS
from evaluation.metrics.calculate_bert_score import calculate_bert_score
from evaluation.metrics.calculate_bleu_score import calculate_bleu_score
from evaluation.metrics.calculate_rouge_score import calculate_rouge_score
from evaluation.llm_evaluation import run as run_llm_evaluation
from evaluation.calculate_all_metrics import calculate_all_metrics
from agent.config.initialize_logger import setup_logger

# Set up logger
logger = setup_logger()

def main():
    parser = argparse.ArgumentParser(description='Text Quality Evaluation Suite')
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Evaluation command to run')
    
    # Common arguments for all parsers
    common_args = {
        '--reference': {
            'type': str,
            'default': DEFAULT_REFERENCE_PATH,
            'help': f'Path to the reference/ground truth text file (default: {DEFAULT_REFERENCE_PATH})'
        },
        '--prediction': {
            'type': str,
            'default': DEFAULT_PREDICTION_PATH,
            'help': f'Path to the prediction/model-generated text file (default: {DEFAULT_PREDICTION_PATH})'
        }
    }
    
    # BERT score parser
    bert_parser = subparsers.add_parser('bert', help='Calculate BERT score')
    bert_parser.add_argument('--reference', **common_args['--reference'])
    bert_parser.add_argument('--prediction', **common_args['--prediction'])
    
    # BLEU score parser
    bleu_parser = subparsers.add_parser('bleu', help='Calculate BLEU score')
    bleu_parser.add_argument('--reference', **common_args['--reference'])
    bleu_parser.add_argument('--prediction', **common_args['--prediction'])
    
    # ROUGE score parser
    rouge_parser = subparsers.add_parser('rouge', help='Calculate ROUGE score')
    rouge_parser.add_argument('--reference', **common_args['--reference'])
    rouge_parser.add_argument('--prediction', **common_args['--prediction'])
    
    # LLM evaluation parser
    llm_parser = subparsers.add_parser('llm', help='Run LLM-based evaluation')
    llm_parser.add_argument('--reference', **common_args['--reference'])
    llm_parser.add_argument('--prediction', **common_args['--prediction'])
    llm_parser.add_argument('--metrics', type=str, nargs='+', default=DEFAULT_LLM_METRICS,
                           help=f'LLM evaluation criteria (default: {" ".join(DEFAULT_LLM_METRICS)})')
    llm_parser.add_argument('--model', type=str, default=None,
                           help='LLM model to use for evaluation (default: from config)')
    
    # All metrics parser
    all_parser = subparsers.add_parser('all', help='Calculate all evaluation metrics')
    all_parser.add_argument('--reference', **common_args['--reference'])
    all_parser.add_argument('--prediction', **common_args['--prediction'])
    all_parser.add_argument('--metrics', type=str, nargs='+', default=DEFAULT_ALL_METRICS,
                          help=f'Metrics to calculate (default: {" ".join(DEFAULT_ALL_METRICS)})')
    
    # Parse arguments
    args = parser.parse_args()
    
    # If no command is specified, print help and exit
    if args.command is None:
        parser.print_help()
        return
        
    # Check if files exist
    if hasattr(args, 'reference') and not os.path.isfile(args.reference):
        logger.error(f"Reference file not found: {args.reference}")
        return
    
    if hasattr(args, 'prediction') and not os.path.isfile(args.prediction):
        logger.error(f"Prediction file not found: {args.prediction}")
        return
    
    # Run the selected command
    if args.command == 'bert':
        logger.info("Running BERT score evaluation...")
        calculate_bert_score(args.reference, args.prediction)
        
    elif args.command == 'bleu':
        logger.info("Running BLEU score evaluation...")
        calculate_bleu_score(args.reference, args.prediction)
        
    elif args.command == 'rouge':
        logger.info("Running ROUGE score evaluation...")
        calculate_rouge_score(args.reference, args.prediction)
        
    elif args.command == 'llm':
        logger.info("Running LLM-based evaluation...")
        run_llm_evaluation(args.reference, args.prediction, args.metrics, args.model)
        
    elif args.command == 'all':
        logger.info("Running all evaluation metrics...")
        calculate_all_metrics(args.reference, args.prediction, args.metrics)
        
    else:
        # No command specified, show help
        parser.print_help()

if __name__ == "__main__":
    main()
