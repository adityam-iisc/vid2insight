#!/usr/bin/env python3
"""
Direct Executive Summary Generator for Evaluation
================================================

This script generates an executive summary by directly calling the agent
without going through the UI layer to avoid evaluation feedback conflicts.

Usage:
    python generate_exec_summary_direct.py

Output:
    - model_generated_exec_summary.txt: Generated executive summary
"""

import sys
import os
import json
import asyncio

# Add the parent directory to path to import from agent modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.vid2_insight_graph import app
from agent.doc_agent.constants import Intent as DocIntent
from agent.constants import AgentType
from agent.config.initialize_logger import setup_logger

# Set up logger
logger = setup_logger()

def load_transcript():
    """Load the transcript data from docs/transcript.json"""
    transcript_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'transcript.json')
    
    if not os.path.exists(transcript_path):
        raise FileNotFoundError(f"Transcript file not found at: {transcript_path}")
    
    with open(transcript_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_executive_summary_direct():
    """Generate executive summary by directly calling the agent"""
    print("Loading transcript data...")
    transcript_data = load_transcript()
    
    print("Generating executive summary using agent directly...")
    try:
        # Extract video context from transcript
        video_context = transcript_data['combined_transcript'][0]['combined_transcript']
        
        # Configure the agent for executive summary generation
        config = {"configurable": {"thread_id": "eval_session", 'agent_choice': AgentType.doc_agent.value}}
        
        # Create the payload with the correct intent for executive summary
        payload = {
            "messages": [{"role": "human", "content": 'generate an executive summary for the video content.'}],
            'expert_preference': AgentType.doc_agent.value,
            'video_context': video_context,
            'intent': DocIntent.GENERATE_EXEC_SUMMARY.value  # Use the correct intent
        }
        
        # Call the agent directly
        raw = asyncio.run(app.ainvoke(payload, config))
        
        print("✅ Executive summary generated successfully!")
        
        # Get the generated content
        # For executive summary, the content should be in the answer field
        generated_content = raw.get('answer', '') or raw.get('exec_summary', '') or raw.get('doc_content', '') or raw.get('chat_content', '')
        
        if not generated_content or not generated_content.strip():
            raise ValueError("Generated executive summary is empty")
        
        print(f"Content length: {len(generated_content)} characters")
        return generated_content
        
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
    print("🚀 Starting Direct Executive Summary Generation for Evaluation")
    print("=" * 60)
    
    try:
        # Generate executive summary
        generated_summary = generate_executive_summary_direct()
        
        # Save to file
        output_path = save_generated_summary(generated_summary)
        
        print("\n✅ Executive Summary Generation Complete!")
        print(f"Generated file: {output_path}")
        print(f"Content length: {len(generated_summary)} characters")
        
        # Show preview
        print("\n📋 Preview (first 300 characters):")
        print("-" * 40)
        print(generated_summary[:300] + "..." if len(generated_summary) > 300 else generated_summary)
        
    except Exception as e:
        print(f"\n❌ Executive summary generation failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
