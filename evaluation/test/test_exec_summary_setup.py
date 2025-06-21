#!/usr/bin/env python3
"""
Test Executive Summary Evaluation Setup
======================================

This script tests the executive summary evaluation setup by:
1. Validating imports
2. Testing transcript loading
3. Testing the evaluation metrics

Usage:
    python test_exec_summary_setup.py
"""

import sys
import os
import json
import unittest

# Add the parent directory to path to import from agent modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_imports():
    """Test if all required imports work."""
    try:
        from agent.vid2_insight_graph import app
        from agent.doc_agent.constants import Intent as DocIntent
        from agent.constants import AgentType
        from evaluation.calculate_all_metrics import calculate_all_metrics
        print("✓ All required agent and evaluation imports work")
        
        # Test other required imports
        import numpy as np
        import pandas as pd
        from rouge_score import rouge_scorer
        
        try:
            import bert_score
            print("✓ BERT Score package is installed")
        except ImportError:
            print("⚠ BERT Score package is not installed. Install with: pip install bert-score")
            
        try:
            import nltk
            print("✓ NLTK package is installed")
            # Check if necessary NLTK data is downloaded
            try:
                nltk.data.find('tokenizers/punkt')
                print("✓ NLTK punkt tokenizer is installed")
            except LookupError:
                print("⚠ NLTK punkt tokenizer is not installed. Run: nltk.download('punkt')")
        except ImportError:
            print("⚠ NLTK package is not installed. Install with: pip install nltk")
        
        print("✓ All required external packages are available")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_transcript_loading():
    """Test if transcript can be loaded."""
    transcript_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'transcript.json')
    try:
        if not os.path.exists(transcript_path):
            print(f"✗ Transcript file not found at: {transcript_path}")
            return False
        
        with open(transcript_path, 'r') as f:
            transcript_data = json.load(f)
        
        if 'combined_transcript' in transcript_data and len(transcript_data['combined_transcript']) > 0:
            print("✓ Transcript loaded successfully")
            print(f"  - Combined transcript length: {len(transcript_data['combined_transcript'][0]['combined_transcript'])} characters")
            return True
        else:
            print("✗ Transcript format is invalid (missing 'combined_transcript' field)")
            return False
    except Exception as e:
        print(f"✗ Error loading transcript: {e}")
        return False

def test_reference_file():
    """Test if reference executive summary file exists."""
    exec_summary_path = os.path.join(os.path.dirname(__file__), '..', 'executive_summary.txt')
    try:
        if not os.path.exists(exec_summary_path):
            print(f"✗ Executive summary reference file not found at: {exec_summary_path}")
            return False
        
        with open(exec_summary_path, 'r') as f:
            content = f.read()
        
        if content and len(content) > 100:  # Basic sanity check
            print("✓ Executive summary reference file exists and has content")
            print(f"  - File size: {len(content)} characters")
            return True
        else:
            print("✗ Executive summary reference file is empty or too small")
            return False
    except Exception as e:
        print(f"✗ Error checking executive summary reference file: {e}")
        return False

def test_metrics_calculation():
    """Test if metrics calculation works with sample data."""
    try:
        from evaluation.metrics.calculate_rouge_score import calculate_rouge_score
        
        # Create temporary test files
        test_dir = os.path.join(os.path.dirname(__file__), 'test_tmp')
        os.makedirs(test_dir, exist_ok=True)
        
        ref_path = os.path.join(test_dir, 'test_ref.txt')
        pred_path = os.path.join(test_dir, 'test_pred.txt')
        
        with open(ref_path, 'w') as f:
            f.write("This is a test reference text for executive summary evaluation. It contains multiple sentences and should be used to verify metric calculation.")
        
        with open(pred_path, 'w') as f:
            f.write("Test executive summary. Contains sentences to verify metrics.")
        
        # Test ROUGE calculation
        results = calculate_rouge_score(ref_path, pred_path)
        
        if results and 'rouge_1' in results and 'f1' in results['rouge_1']:
            print("✓ ROUGE metrics calculation works")
            print(f"  - Test ROUGE-1 F1: {results['rouge_1']['f1']:.4f}")
            
            # Clean up test files
            os.remove(ref_path)
            os.remove(pred_path)
            os.rmdir(test_dir)
            return True
        else:
            print("✗ ROUGE metrics calculation failed")
            return False
    except Exception as e:
        print(f"✗ Error testing metrics calculation: {e}")
        return False

def main():
    """Run all tests."""
    print("=== Executive Summary Evaluation Test ===")
    
    print("\n1. Testing imports...")
    if not test_imports():
        print("FAIL: Import test failed")
        sys.exit(1)
    
    print("\n2. Testing transcript loading...")
    if not test_transcript_loading():
        print("FAIL: Transcript loading test failed")
        sys.exit(1)
    
    print("\n3. Testing reference file...")
    if not test_reference_file():
        print("FAIL: Reference file test failed")
        sys.exit(1)
    
    print("\n4. Testing metrics calculation...")
    if not test_metrics_calculation():
        print("FAIL: Metrics calculation test failed")
        sys.exit(1)
    
    print("\n✓ All tests passed!")
    print("Ready to evaluate executive summaries.")

if __name__ == "__main__":
    main()
