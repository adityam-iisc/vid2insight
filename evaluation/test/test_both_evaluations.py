#!/usr/bin/env python3
"""
Comprehensive Test Script for Both Evaluation Systems
====================================================

This script tests both the product documentation and executive summary
evaluation systems to ensure they work correctly.

Usage:
    python test_both_evaluations.py

Tests:
    1. Product documentation generation and evaluation
    2. Executive summary generation and evaluation
    3. File integrity checks
    4. Results validation
"""

import sys
import os
import json
import subprocess
import time

# Add the parent directory to path to import from agent modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def check_file_exists(filepath, description):
    """Check if a file exists and report."""
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {filepath}")
    return exists

def run_command(command, description, timeout=60):
    """Run a command and report success/failure."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd='/Users/ankitku5/Desktop/vid2insight'
        )
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed:")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏱️ {description} timed out after {timeout} seconds")
        return False
    except Exception as e:
        print(f"❌ {description} failed with error: {e}")
        return False

def check_evaluation_results(results_file, evaluation_type):
    """Check if evaluation results are valid."""
    try:
        if not os.path.exists(results_file):
            print(f"❌ {evaluation_type} results file not found: {results_file}")
            return False
        
        with open(results_file, 'r') as f:
            results = json.load(f)
        
        required_metrics = ['bert', 'bleu', 'rouge', 'llm']
        missing_metrics = [metric for metric in required_metrics if metric not in results]
        
        if missing_metrics:
            print(f"❌ {evaluation_type} missing metrics: {missing_metrics}")
            return False
        
        print(f"✅ {evaluation_type} results are complete with all metrics")
        
        # Check BERT scores
        if 'bert' in results and 'f1' in results['bert']:
            bert_f1 = results['bert']['f1']
            print(f"📊 {evaluation_type} BERT F1: {bert_f1:.4f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking {evaluation_type} results: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Comprehensive Evaluation System Test")
    print("=" * 60)
    
    success_count = 0
    total_tests = 0
    
    # Test 1: Check prerequisite files
    print("\n📋 Test 1: Checking prerequisite files...")
    total_tests += 1
    
    prerequisite_files = [
        ('/Users/ankitku5/Desktop/vid2insight/docs/transcript.json', 'Transcript data'),
        ('/Users/ankitku5/Desktop/vid2insight/detailed_product_Doc.txt', 'Product doc ground truth'),
        ('/Users/ankitku5/Desktop/vid2insight/executive_summary.txt', 'Executive summary ground truth'),
    ]
    
    prereq_success = True
    for filepath, description in prerequisite_files:
        if not check_file_exists(filepath, description):
            prereq_success = False
    
    if prereq_success:
        print("✅ All prerequisite files found")
        success_count += 1
    else:
        print("❌ Some prerequisite files missing")
    
    # Test 2: Product Documentation Generation
    print("\n📋 Test 2: Product Documentation Generation...")
    total_tests += 1
    
    if run_command(
        'python evaluation/generate_product_doc.py',
        'Product documentation generation',
        timeout=120
    ):
        if check_file_exists(
            '/Users/ankitku5/Desktop/vid2insight/model_generated_product_doc.txt',
            'Generated product documentation'
        ):
            success_count += 1
        else:
            print("❌ Product documentation file not generated")
    
    # Test 3: Executive Summary Generation
    print("\n📋 Test 3: Executive Summary Generation...")
    total_tests += 1
    
    if run_command(
        'python evaluation/generate_exec_summary_direct.py',
        'Executive summary generation',
        timeout=120
    ):
        if check_file_exists(
            '/Users/ankitku5/Desktop/vid2insight/model_generated_exec_summary.txt',
            'Generated executive summary'
        ):
            success_count += 1
        else:
            print("❌ Executive summary file not generated")
    
    # Test 4: Product Documentation Evaluation
    print("\n📋 Test 4: Product Documentation Evaluation...")
    total_tests += 1
    
    if run_command(
        'python -c "from evaluation.calculate_all_metrics import calculate_all_metrics; calculate_all_metrics(\'/Users/ankitku5/Desktop/vid2insight/detailed_product_Doc.txt\', \'/Users/ankitku5/Desktop/vid2insight/model_generated_product_doc.txt\')"',
        'Product documentation evaluation',
        timeout=180
    ):
        if check_evaluation_results(
            '/Users/ankitku5/Desktop/vid2insight/eval_results/all_evaluation_results.json',
            'Product documentation'
        ):
            success_count += 1
    
    # Test 5: Executive Summary Evaluation
    print("\n📋 Test 5: Executive Summary Evaluation...")
    total_tests += 1
    
    if run_command(
        'python -c "from evaluation.calculate_all_metrics import calculate_all_metrics; calculate_all_metrics(\'/Users/ankitku5/Desktop/vid2insight/executive_summary.txt\', \'/Users/ankitku5/Desktop/vid2insight/model_generated_exec_summary.txt\')"',
        'Executive summary evaluation',
        timeout=180
    ):
        if check_evaluation_results(
            '/Users/ankitku5/Desktop/vid2insight/eval_results/all_evaluation_results.json',
            'Executive summary'
        ):
            success_count += 1
    
    # Test 6: Check evaluation reports
    print("\n📋 Test 6: Checking evaluation reports...")
    total_tests += 1
    
    report_files = [
        ('/Users/ankitku5/Desktop/vid2insight/evaluation/product_doc_evaluation_report.md', 'Product doc report'),
        ('/Users/ankitku5/Desktop/vid2insight/evaluation/exec_summary_evaluation_report.md', 'Executive summary report'),
    ]
    
    report_success = True
    for filepath, description in report_files:
        if not check_file_exists(filepath, description):
            report_success = False
    
    if report_success:
        success_count += 1
    
    # Test 7: Check evaluation results directory
    print("\n📋 Test 7: Checking evaluation results directory...")
    total_tests += 1
    
    eval_dir = '/Users/ankitku5/Desktop/vid2insight/eval_results'
    if os.path.exists(eval_dir):
        result_files = os.listdir(eval_dir)
        expected_files = [
            'bert_score_results.json',
            'bleu_score_results.json',
            'rouge_score_results.json',
            'llm_evaluation_results.json',
            'all_evaluation_results.json'
        ]
        
        missing_files = [f for f in expected_files if f not in result_files]
        if not missing_files:
            print(f"✅ All expected result files found in {eval_dir}")
            success_count += 1
        else:
            print(f"❌ Missing result files: {missing_files}")
    else:
        print(f"❌ Evaluation results directory not found: {eval_dir}")
    
    # Final Summary
    print("\n" + "=" * 60)
    print("🏁 TEST SUMMARY")
    print("=" * 60)
    print(f"Tests Passed: {success_count}/{total_tests}")
    print(f"Success Rate: {(success_count/total_tests)*100:.1f}%")
    
    if success_count == total_tests:
        print("\n🎉 ALL TESTS PASSED! Both evaluation systems are working correctly.")
        print("\n📋 Available outputs:")
        print("- Product Documentation: model_generated_product_doc.txt")
        print("- Executive Summary: model_generated_exec_summary.txt")
        print("- Product Doc Report: evaluation/product_doc_evaluation_report.md")
        print("- Exec Summary Report: evaluation/exec_summary_evaluation_report.md")
        print("- Detailed Results: eval_results/ directory")
        return True
    else:
        print(f"\n⚠️ {total_tests - success_count} tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
