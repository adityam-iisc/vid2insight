#!/usr/bin/env python
"""Script to generate product chat responses and save them to a file.

This script loads the transcript, generates product chat responses using 
the same method as the UI's send_chat_docG function, and saves them to 
model_generated_product_chat.txt
"""

import sys
import os
import json
import asyncio

# Add the parent directory to sys.path to allow imports from the root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.vid2_insight_graph import app
from agent.doc_agent.constants import Intent as DocIntent
from agent.constants import AgentType
from agent.config.initialize_logger import setup_logger

# Set up logger
logger = setup_logger()

# Define sample chat queries based on ground truth document about LangChain
SAMPLE_QUERIES = [
    "What is LangChain?",
    "What are the key features of LangChain?",
    "How does LangChain support prompt engineering?",
    "What is Retrieval-Augmented Generation (RAG) in LangChain?",
    "Is LangChain compatible with different language models?",
    "How does LangChain compare to other frameworks?",
    "How do I use LangChain with OpenAI models?",
    "What is the RunnablePassthrough feature in LangChain?",
    "How can I implement batch processing in LangChain?",
    "What is the LCEL (LangChain Expression Language)?"
]

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

def generate_product_chat_responses(transcript_data: dict, 
                                   session_id: str = "chat_generation_session",
                                   queries: list = None):
    """Generate product chat responses using the agent."""
    try:
        logger.info("Generating product chat responses...")
        
        # Extract video context from transcript
        video_context = transcript_data['combined_transcript'][0]['combined_transcript']
        
        # Use provided queries or default to sample queries
        chat_queries = queries or SAMPLE_QUERIES
        
        # Generate responses for each query
        responses = []
        doc_content = ""  # Initial doc content is empty
        
        for query in chat_queries:
            logger.info(f"Processing query: {query}")
            
            # Configure the agent (same as in ui.py's send_chat_docG)
            config = {"configurable": {"thread_id": session_id, 'agent_choice': AgentType.doc_agent.value}}
            
            # Create message with reference to current doc if available
            message = f"Answer my query: {query}" + (
                f" with reference to my current version of document: {doc_content}" if doc_content else '')
            
            # Create the payload (same as in ui.py's send_chat_docG)
            payload = {
                "messages": [{"role": "human", "content": message}],
                'expert_preference': AgentType.doc_agent.value,
                'video_context': video_context,
                'intent': DocIntent.DOC_CHAT.value,
            }
            
            # Invoke the agent
            raw = asyncio.run(app.ainvoke(payload, config))
            
            # Extract chat content and update doc content
            chat_content = raw.get('chat_content', '')
            doc_content = raw.get('doc_content', doc_content)
            
            # Store query and response
            responses.append({
                "query": query,
                "response": chat_content
            })
            
            logger.info(f"Response generated for query: {query}")
        
        return responses
        
    except Exception as e:
        logger.error(f"Error generating product chat responses: {e}")
        import traceback
        traceback.print_exc()
        return []

def save_responses_to_file(responses: list, output_path: str = '/Users/ankitku5/Desktop/vid2insight/evaluation/model_outputs/model_generated_product_chat.txt'):
    """Save the generated responses to a file."""
    try:
        with open(output_path, 'w') as f:
            for item in responses:
                f.write(f"Q: {item['query']}\n\n")
                f.write(f"A: {item['response']}\n\n")
                f.write("-" * 80 + "\n\n")
        
        logger.info(f"Generated chat responses saved to {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving responses: {e}")
        return False

def main():
    """Main function to run the script."""
    # Load transcript
    transcript_data = load_transcript()
    if not transcript_data:
        logger.error("Failed to load transcript. Exiting.")
        return False
    
    # Generate product chat responses
    responses = generate_product_chat_responses(transcript_data)
    if not responses:
        logger.error("Failed to generate product chat responses. Exiting.")
        return False
    
    # Save responses to file
    success = save_responses_to_file(responses)
    if not success:
        logger.error("Failed to save responses to file. Exiting.")
        return False
    
    logger.info("Product chat response generation completed successfully!")
    return True

if __name__ == "__main__":
    main()
