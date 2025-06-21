#!/usr/bin/env python
"""Script to generate student chat responses and save them to a file.

This script loads the transcript, generates student chat responses using the
student agent, and saves them to model_generated_student_chat.txt
"""

import sys
import os
import json
import re
import asyncio
from pathlib import Path

# Add the parent directory to sys.path to allow imports from the root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agent.student_agent.constants import Intent as StudentIntent
from agent.vid2_insight_graph import app
from agent.constants import AgentType
from agent.config.initialize_logger import setup_logger

# Set up logger
logger = setup_logger()

# Define sample chat queries based on ground truth document
SAMPLE_QUERIES = [
    "What are the key capabilities of LangChain?",
    "How does routing work in LangChain?",
    "What is RAG and how does it improve model responses?",
    "How do I create intelligent agents in LangChain?",
    "How can I integrate OpenAI models with LangChain?",
    "What is the LangChain Expression Language used for?",
    "Can you explain how batch processing works in LangChain?",
    "What's the benefit of using LangChain over direct API calls?"
]

def load_transcript(transcript_path: str = '/Users/ankitku5/Desktop/vid2insight/docs/transcript.json'):
    """Load transcript data from JSON file."""
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript_data = json.load(f)
        return transcript_data
    except Exception as e:
        logger.error(f"Error loading transcript: {e}")
        return None

def generate_student_chat_responses(transcript_data, 
                                  session_id: str = "student_chat_generation_session",
                                  output_file: str = '/Users/ankitku5/Desktop/vid2insight/evaluation/model_outputs/model_generated_student_chat.txt',
                                  queries: list = None):
    """Generate student chat responses for a set of predefined queries using the student agent.
    
    Args:
        transcript_data: The transcript data
        session_id: Session ID for the agent
        output_file: Path to save the generated responses
        queries: List of queries to process (defaults to SAMPLE_QUERIES)
    
    Returns:
        List of dictionaries containing queries and responses
    """
    if not transcript_data:
        logger.error("No transcript data provided. Can't generate responses.")
        return None

    try:
        logger.info("Initializing student chat response generation")
        all_responses = []
        
        # Create the output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Extract video context from transcript
        video_context = transcript_data['combined_transcript'][0]['combined_transcript']
        
        # Use provided queries or default to sample queries
        chat_queries = queries or SAMPLE_QUERIES
        
        for query in chat_queries:
            logger.info(f"Generating response for: {query}")
            try:
                # Configure the agent (similar to ui.py's send_chat_studentG)
                config = {"configurable": {"thread_id": session_id, 'agent_choice': AgentType.student_agent.value}}
                
                # Create the message
                message = f"Answer my query: {query}"
                
                # Create the payload (similar to ui.py's send_chat_studentG)
                payload = {
                    "messages": [{"role": "human", "content": message}],
                    'expert_preference': AgentType.student_agent.value,
                    'video_context': video_context,
                    'intent': StudentIntent.DOC_CHAT.value,
                }
                
                # Invoke the agent asynchronously
                raw = asyncio.run(app.ainvoke(payload, config))
                
                # Extract chat content 
                chat_content = raw.get('chat_content', '')
                
                all_responses.append({
                    "query": query,
                    "response": chat_content
                })
                
                logger.info(f"Generated response of length {len(chat_content)}")
            except Exception as e:
                logger.error(f"Error generating response for query: {query}, Error: {e}")
                import traceback
                traceback.print_exc()
                all_responses.append({
                    "query": query,
                    "response": f"ERROR: Failed to generate response: {str(e)}"
                })
        
        # Save all responses to file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for item in all_responses:
                    f.write(f"Q: {item['query']}\n\n")
                    f.write(f"A: {item['response']}\n\n")
                    f.write("-" * 80 + "\n\n")
            logger.info(f"Saved generated student chat responses to {output_file}")
        except Exception as e:
            logger.error(f"Error saving responses to file: {e}")
        
        return all_responses
    
    except Exception as e:
        logger.error(f"Error in generate_student_chat_responses: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function to run the script."""
    print("\n" + "="*80)
    print(" "*25 + "STUDENT CHAT RESPONSE GENERATION")
    print("="*80 + "\n")
    
    print("Loading transcript data...")
    transcript_data = load_transcript()
    
    if not transcript_data:
        print("\033[91mFailed to load transcript data. Exiting.\033[0m")
        return
    
    print("\nGenerating student chat responses for the following queries:")
    for i, query in enumerate(SAMPLE_QUERIES, 1):
        print(f"  {i}. {query}")
    
    print("\nThis may take a few minutes...\n")
    
    output_file = '/Users/ankitku5/Desktop/vid2insight/evaluation/model_outputs/model_generated_student_chat.txt'
    session_id = "student_chat_generation_session"
    
    responses = generate_student_chat_responses(
        transcript_data, 
        session_id=session_id,
        output_file=output_file,
        queries=SAMPLE_QUERIES
    )
    
    if responses:
        print("\n\033[92mSuccessfully generated student chat responses!\033[0m")
        print(f"Results saved to: {output_file}")
    else:
        print("\n\033[91mFailed to generate student chat responses.\033[0m")

if __name__ == "__main__":
    main()
