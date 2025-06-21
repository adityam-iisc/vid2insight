#!/usr/bin/env python
"""Test script to verify product documentation generation works."""

import sys
import os

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
        
        print(f"Testing transcript loading from: {transcript_path}")
        
        if not os.path.exists(transcript_path):
            print(f"ERROR: Transcript file not found at {transcript_path}")
            return False
            
        with open(transcript_path, 'r') as f:
            transcript_data = json.load(f)
            
        print("✓ Transcript loaded successfully")
        
        # Check structure
        if 'combined_transcript' in transcript_data:
            print("✓ Combined transcript found")
            
            if len(transcript_data['combined_transcript']) > 0:
                content = transcript_data['combined_transcript'][0]['combined_transcript']
                print(f"✓ Content length: {len(content)} characters")
                print(f"Content preview: {content[:100]}...")
                return True
            else:
                print("ERROR: No combined transcript content found")
                return False
        else:
            print("ERROR: No combined_transcript key found")
            return False
            
    except Exception as e:
        print(f"Transcript loading error: {e}")
        return False

def main():
    """Run all tests."""
    print("=== Product Documentation Generation Test ===")
    
    print("\n1. Testing imports...")
    if not test_imports():
        print("FAIL: Import test failed")
        sys.exit(1)
    
    print("\n2. Testing transcript loading...")
    if not test_transcript_loading():
        print("FAIL: Transcript loading test failed")
        sys.exit(1)
    
    print("\n✓ All tests passed!")
    print("Ready to generate product documentation.")

if __name__ == "__main__":
    main()
