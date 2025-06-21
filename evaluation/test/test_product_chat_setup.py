#!/usr/bin/env python
"""Test script to verify product chat evaluation setup works."""

import sys
import os
import json
from pathlib import Path

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test if all required imports work."""
    try:
        print("Testing imports...")
        
        from agent.vid2_insight_graph import app
        print("✓ agent.vid2_insight_graph imported")
        
        from agent.doc_agent.constants import Intent as DocIntent
        print("✓ agent.doc_agent.constants imported")
        
        from agent.constants import AgentType
        print("✓ agent.constants imported")
        
        from agent.config.initialize_logger import setup_logger
        print("✓ agent.config.initialize_logger imported")
        
        from evaluation.calculate_all_metrics import calculate_all_metrics
        print("✓ evaluation.calculate_all_metrics imported")
        
        print("All imports successful!")
        return True
        
    except Exception as e:
        print(f"Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_transcript_loading():
    """Test if transcript can be loaded."""
    try:
        import json
        transcript_path = '/Users/ankitku5/Desktop/vid2insight/docs/transcript.json'
        
        print(f"Testing transcript loading from {transcript_path}...")
        
        with open(transcript_path, 'r') as f:
            transcript_data = json.load(f)
        
        print(f"✓ Successfully loaded transcript from {transcript_path}")
        
        # Check if transcript contains required fields
        assert 'combined_transcript' in transcript_data, "combined_transcript field missing"
        assert len(transcript_data['combined_transcript']) > 0, "combined_transcript is empty"
        assert 'combined_transcript' in transcript_data['combined_transcript'][0], "transcript format incorrect"
        
        print("✓ Transcript format is correct")
        return True
        
    except FileNotFoundError:
        print(f"Error: Transcript file not found at {transcript_path}")
        return False
    except json.JSONDecodeError:
        print(f"Error: Transcript file is not valid JSON")
        return False
    except Exception as e:
        print(f"Error loading transcript: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ground_truth_loading():
    """Test if ground truth file can be loaded."""
    try:
        ground_truth_path = '/Users/ankitku5/Desktop/vid2insight/Product_chat.txt'
        
        print(f"Testing ground truth loading from {ground_truth_path}...")
        
        with open(ground_truth_path, 'r') as f:
            content = f.read()
        
        print(f"✓ Successfully loaded ground truth from {ground_truth_path}")
        
        # Check if file contains content
        assert len(content.strip()) > 0, "Ground truth file is empty"
        
        print("✓ Ground truth file contains content")
        return True
        
    except FileNotFoundError:
        print(f"Error: Ground truth file not found at {ground_truth_path}")
        return False
    except Exception as e:
        print(f"Error loading ground truth: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_metrics_calculation():
    """Test if metrics calculation works."""
    try:
        print("Testing metrics calculation...")
        
        # For testing purposes, we'll create temporary files with the test content
        import tempfile
        import os
        
        # Sample text for testing metrics
        reference = "The product chat system should be thoroughly evaluated."
        candidate = "We need to evaluate the product chat system thoroughly."
        query = "How should we test the product chat system?"
        
        # Create temporary files
        ref_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        ref_file.write(reference)
        ref_file.close()
        
        cand_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        cand_file.write(candidate)
        cand_file.close()
        
        # Import the full file-based metrics function
        from evaluation.calculate_all_metrics import calculate_all_metrics
        
        # Calculate metrics using file paths
        metrics = calculate_all_metrics(ref_file.name, cand_file.name)
        
        print("✓ Successfully calculated metrics")
        print(f"Sample metrics: {metrics}")
        
        # Check if metrics object is a dictionary
        assert isinstance(metrics, dict), "Metrics should be a dictionary"
        
        # Clean up temporary files
        os.unlink(ref_file.name)
        os.unlink(cand_file.name)
        
        print("✓ Metrics calculation is correct")
        return True
        
    except Exception as e:
        print(f"Error calculating metrics: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_output_directories():
    """Test if output directories exist or can be created."""
    try:
        print("Testing output directories...")
        
        # Define directories to check
        dirs_to_check = [
            '/Users/ankitku5/Desktop/vid2insight/eval_results',
            '/Users/ankitku5/Desktop/vid2insight/evaluation',
        ]
        
        for dir_path in dirs_to_check:
            if os.path.exists(dir_path):
                print(f"✓ Directory exists: {dir_path}")
            else:
                print(f"Creating directory: {dir_path}")
                os.makedirs(dir_path, exist_ok=True)
                print(f"✓ Created directory: {dir_path}")
        
        print("✓ Output directories check complete")
        return True
        
    except Exception as e:
        print(f"Error checking/creating directories: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests and return overall status."""
    tests = [
        ("Import tests", test_imports),
        ("Transcript loading test", test_transcript_loading),
        ("Ground truth loading test", test_ground_truth_loading),
        ("Metrics calculation test", test_metrics_calculation),
        ("Output directories test", test_output_directories),
    ]
    
    all_passed = True
    
    print("=" * 60)
    print("PRODUCT CHAT EVALUATION SETUP TEST")
    print("=" * 60)
    
    for test_name, test_func in tests:
        print("\n" + "-" * 40)
        print(f"Running {test_name}...")
        print("-" * 40)
        
        success = test_func()
        
        if success:
            print(f"\n✅ {test_name} PASSED")
        else:
            print(f"\n❌ {test_name} FAILED")
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 ALL TESTS PASSED - Product chat evaluation setup is ready!")
    else:
        print("⚠️ SOME TESTS FAILED - Fix the issues before proceeding")
    
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    main()
