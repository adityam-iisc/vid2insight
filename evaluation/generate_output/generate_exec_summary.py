#!/usr/bin/env python3
"""
Executive Summary Generator for Evaluation
===========================================

This script generates an executive summary using the UI agent's generate_product_doc() method
with doc_choice="Executive Summary" and saves it for evaluation.

Usage:
    python generate_exec_summary.py

Output:
    - model_generated_exec_summary.txt: Generated executive summary
"""

import sys
import os
import json

# Add the parent directory to path to import from agent modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.ui.ui import Facilitator

class MockSessionState:
    """Mock Streamlit session state for testing"""
    def __init__(self, transcript_data):
        self.context = transcript_data

def load_transcript():
    """Load the transcript data from docs/transcript.json"""
    transcript_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'transcript.json')
    
    if not os.path.exists(transcript_path):
        raise FileNotFoundError(f"Transcript file not found at: {transcript_path}")
    
    with open(transcript_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_executive_summary():
    """Generate executive summary using the UI agent"""
    print("Loading transcript data...")
    transcript_data = load_transcript()
    
    # Mock streamlit session state
    import streamlit as st
    if not hasattr(st, 'session_state'):
        st.session_state = MockSessionState(transcript_data)
    else:
        st.session_state.context = transcript_data
    
    print("Generating executive summary using UI agent...")
    try:
        # Use the Facilitator class to generate executive summary
        chat_content, doc_content = Facilitator.generate_product_doc(
            session_id="eval_session", 
            doc_choice="Executive Summary"  # This triggers executive summary generation
        )
        
        # Use doc_content if available, otherwise use chat_content (similar to product doc handling)
        final_content = doc_content if doc_content and doc_content.strip() else chat_content
        
        if not final_content or not final_content.strip():
            raise ValueError("Generated executive summary is empty")
        
        print("✅ Executive summary generated successfully!")
        print(f"Content length: {len(final_content)} characters")
        return final_content
        
    except Exception as e:
        print(f"❌ Error generating executive summary: {e}")
        import traceback
        traceback.print_exc()
        raise

def save_generated_summary(content):
    """Save the generated executive summary to a file"""
    output_path = os.path.join(os.path.dirname(__file__), '..', 'model_generated_exec_summary.txt')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"📄 Generated executive summary saved to: {output_path}")
    return output_path

def main():
    """Main execution function"""
    print("🚀 Starting Executive Summary Generation for Evaluation")
    print("=" * 60)
    
    try:
        # Generate executive summary
        generated_summary = generate_executive_summary()
        
        # Save to file
        output_path = save_generated_summary(generated_summary)
        
        print("\n✅ Executive Summary Generation Complete!")
        print(f"Generated file: {output_path}")
        print(f"Content length: {len(generated_summary)} characters")
        
        # Show preview
        print("\n📋 Preview (first 200 characters):")
        print("-" * 40)
        print(generated_summary[:200] + "..." if len(generated_summary) > 200 else generated_summary)
        
    except Exception as e:
        print(f"\n❌ Executive summary generation failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
