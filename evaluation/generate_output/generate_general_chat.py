#!/usr/bin/env python
"""Script to generate general purpose chat responses and save them to a file.

This script loads the transcript, generates general chat responses using 
the same method as the UI's send_gen_chat function, and saves them to 
model_generated_general_chat.txt
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

# Define sample chat queries based on ground truth document (LangChain content)
SAMPLE_QUERIES = [
    "What is LangChain and what problem does it solve?",
    "How do I load environment variables in the LangChain notebook?",
    "What are the core components of LangChain mentioned in the video?",
    "What is LangChain Expression Language (LCEL)?",
    "How is the OpenAI API used in the LangChain example?",
    "What is batch processing in LangChain and why is it useful?",
    "What is RAG and how does it relate to LangChain?",
    "What are some alternatives to LangChain mentioned in the presentation?",
    "How do you create a chat completion using LangChain?",
    "What's the purpose of RunnablePassthrough in LangChain?"
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

def generate_general_chat_responses(transcript_data, 
                            session_id: str = "general_chat_generation_session",
                            output_file: str = '/Users/ankitku5/Desktop/vid2insight/evaluation/model_outputs/model_generated_general_chat.txt',
                            queries: list = None):
    """Generate general chat responses for a set of predefined queries.
    
    Args:
        transcript_data: The transcript data
        session_id: Session ID for the agent
        output_file: Path to save the generated responses
        queries: List of queries to process (defaults to SAMPLE_QUERIES)
        
    Returns:
        List of formatted responses
    """
    if not transcript_data:
        logger.error("No transcript data provided. Can't generate responses.")
        return None

    try:
        logger.info("Initializing general chat response generation")
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
                # Configure the agent (similar to ui.py's send_gen_chat)
                config = {"configurable": {"thread_id": session_id, 'agent_choice': AgentType.chat.value}}
                
                # Create the payload (same as in ui.py's send_gen_chat)
                payload = {
                    "messages": [{"role": "user", "content": query}],
                    'expert_preference': AgentType.chat.value,
                    'video_context': video_context,
                    'intent': DocIntent.DOC_CHAT.value,
                }
                
                # Invoke the agent asynchronously
                raw = asyncio.run(app.ainvoke(payload, config))
                
                # Extract chat content
                chat_content = raw.get('chat_content', '')
                
                all_responses.append(f"Q: {query}\nA: {chat_content}\n\n")
                logger.info(f"Generated response of length {len(chat_content)}")
            except Exception as e:
                logger.error(f"Error generating response for query: {query}, Error: {e}")
                import traceback
                traceback.print_exc()
                all_responses.append(f"Q: {query}\nA: ERROR: Failed to generate response: {str(e)}\n\n")
        
        # Save all responses to file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("".join(all_responses))
            logger.info(f"Saved generated general chat responses to {output_file}")
        except Exception as e:
            logger.error(f"Error saving responses to file: {e}")
        
        return all_responses
        
    except Exception as e:
        logger.error(f"Error in generate_general_chat_responses: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("\n" + "="*80)
    print(" "*25 + "GENERAL CHAT RESPONSE GENERATION")
    print("="*80 + "\n")
    
    print("Loading transcript data...")
    transcript_data = load_transcript()
    
    if transcript_data:
        session_id = "general_chat_generation_session"
        output_file = '/Users/ankitku5/Desktop/vid2insight/evaluation/model_outputs/model_generated_general_chat.txt'
        
        print("\nGenerating general chat responses for the following queries:")
        for i, query in enumerate(SAMPLE_QUERIES, 1):
            print(f"  {i}. {query}")
        
        print("\nThis may take a few minutes...\n")
        
        responses = generate_general_chat_responses(
            transcript_data, 
            session_id=session_id,
            output_file=output_file,
            queries=SAMPLE_QUERIES
        )
        
        if responses:
            print("\n\033[92mSuccessfully generated general chat responses!\033[0m")
            print(f"Results saved to: {output_file}")
        else:
            print("\n\033[91mFailed to generate general chat responses.\033[0m")
    else:
        print("Failed to load transcript data. Exiting.")
