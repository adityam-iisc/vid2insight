#!/usr/bin/env python
"""Simple script to generate product documentation and save it to a file.

This script loads the transcript and generates product documentation
using the same method as the UI, then saves it to model_generated_product_doc.txt
"""

import sys
import os
import json
import asyncio

# Add the parent directory to sys.path to allow imports from the root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agent.vid2_insight_graph import app
from agent.doc_agent.constants import Intent as DocIntent
from agent.constants import AgentType
from agent.config.initialize_logger import setup_logger

# Set up logger
logger = setup_logger()

def load_transcript(transcript_path: str = '/Users/ankitku5/Desktop/vid2insight/docs/transcript.json'):
    """Load transcript data from JSON file."""
    try:
        with open(transcript_path, 'r') as f:
            transcript_data = json.load(f)
        logger.info(f"Loaded transcript from {transcript_path}")
        return transcript_data
    except Exception as e:
        logger.error(f"Error loading transcript: {e}")
        return None

def generate_product_documentation(transcript_data: dict, session_id: str = "generation_session"):
    """Generate product documentation using the agent."""
    try:
        logger.info("Generating product documentation...")
        
        # Extract video context from transcript
        video_context = transcript_data['combined_transcript'][0]['combined_transcript']
        
        # Configure the agent (same as in ui.py)
        config = {"configurable": {"thread_id": session_id, 'agent_choice': AgentType.doc_agent.value}}
        
        # Create the payload (same as in ui.py)
        payload = {
            "messages": [{"role": "human", "content": 'generate a product documentation for the video content.'}],
            'expert_preference': AgentType.doc_agent.value,
            'video_context': video_context,
            'intent': DocIntent.GENERATE_DOCS.value
        }
        
        # Call the agent
        raw = asyncio.run(app.ainvoke(payload, config))
        
        logger.info("Product documentation generated successfully")
        logger.info(f"Raw response keys: {raw.keys()}")
        logger.info(f"Chat content length: {len(raw.get('chat_content', ''))}")
        logger.info(f"Doc content length: {len(raw.get('doc_content', ''))}")
        
        return raw['chat_content'], raw['doc_content']
        
    except Exception as e:
        logger.error(f"Error generating product documentation: {e}")
        return None, None

def save_documentation(doc_content: str, output_path: str = '/Users/ankitku5/Desktop/vid2insight/model_generated_product_doc.txt'):
    """Save the generated documentation to file."""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(doc_content)
        logger.info(f"Generated documentation saved to {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving documentation: {e}")
        return False

def main():
    """Main function."""
    import argparse
    
    try:
        parser = argparse.ArgumentParser(description='Generate Product Documentation')
        parser.add_argument('--transcript', type=str, 
                           default='/Users/ankitku5/Desktop/vid2insight/docs/transcript.json',
                           help='Path to the transcript JSON file')
        parser.add_argument('--output', type=str,
                           default='/Users/ankitku5/Desktop/vid2insight/evaluation/model_outputs/model_generated_product_doc.txt',
                           help='Path to save the generated documentation')
        parser.add_argument('--session-id', type=str, default='generation_session',
                           help='Session ID for the agent')
        
        args = parser.parse_args()
        
        print("=== Product Documentation Generator ===")
        
        # Step 1: Load transcript
        print("Loading transcript...")
        transcript_data = load_transcript(args.transcript)
        if not transcript_data:
            print("ERROR: Failed to load transcript data")
            sys.exit(1)
        
        # Step 2: Generate documentation
        print("Generating product documentation...")
        chat_content, doc_content = generate_product_documentation(transcript_data, args.session_id)
        
        # Use chat_content if doc_content is empty (based on the logs, content is in chat_content)
        final_content = doc_content if doc_content and doc_content.strip() else chat_content
        
        if not final_content or not final_content.strip():
            print("ERROR: Failed to generate product documentation")
            sys.exit(1)
        
        # Step 3: Save documentation
        print("Saving generated documentation...")
        if save_documentation(final_content, args.output):
            print(f"SUCCESS: Documentation saved to {args.output}")
            
            # Show preview
            print("\n" + "="*60)
            print("GENERATED DOCUMENTATION PREVIEW")
            print("="*60)
            print(final_content[:500] + "..." if len(final_content) > 500 else final_content)
            print("="*60)
        else:
            print("ERROR: Failed to save documentation")
            sys.exit(1)
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
