#!/usr/bin/env python
"""Script to generate student MCQs and save them to a file.

This script loads the transcript, generates student MCQs without 
using UI functions, and saves them to model_generated_student_mcq.txt
"""

import sys
import os
import json
import re

# Add the parent directory to sys.path to allow imports from the root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.config.initialize_logger import setup_logger
import asyncio
from agent.vid2_insight_graph import app
from agent.constants import AgentType
from agent.student_agent.constants import Intent as StudIntent

# Set up logger
logger = setup_logger()

def format_mcqs_for_output(mcq_data: dict) -> str:
    """Format MCQ data into a readable text format.
    
    Args:
        mcq_data: Dictionary containing MCQ data with questions and options
        
    Returns:
        Formatted MCQs as a string
    """
    if not mcq_data or not mcq_data.get("questions"):
        return "No MCQs were generated."
    
    formatted_output = []
    
    # Add topics if available
    if mcq_data.get("topics"):
        formatted_output.append("Topics covered in the video:")
        for i, topic in enumerate(mcq_data["topics"], 1):
            formatted_output.append(f"{i}. {topic}")
        formatted_output.append("\n")
    
    # Format each question
    for i, q in enumerate(mcq_data["questions"], 1):
        formatted_output.append(f"Question {i}: {q['question']}")
        
        # Format options
        for j, option in enumerate(q["options"]):
            option_letter = chr(97 + j)  # Convert 0 -> a, 1 -> b, etc.
            formatted_output.append(f"   {option_letter}) {option}")
        
        # Mark correct answer
        formatted_output.append(f"\nCorrect answer: {q['correct_option']}")
        
        # Add topics covered by this question if available
        if q.get("topics_covered"):
            topic_list = ", ".join(q["topics_covered"])
            formatted_output.append(f"Topics: {topic_list}")
        
        formatted_output.append("\n")
    
    return "\n".join(formatted_output)

def load_transcript(transcript_path: str = '/Users/ankitku5/Desktop/vid2insight/docs/transcript.json'):
    """Load transcript data from JSON file."""
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript_data = json.load(f)
        return transcript_data
    except Exception as e:
        logger.error(f"Error loading transcript: {e}")
        return None

def generate_student_mcqs(transcript_data, 
                      session_id: str = "student_mcq_generation_session",
                      output_file: str = '/Users/ankitku5/Desktop/vid2insight/evaluation/model_outputs/model_generated_student_mcq.txt'):
    """Generate student MCQs from transcript data using the student agent.
    
    Args:
        transcript_data: The transcript data
        session_id: Session ID for the agent
        output_file: Path to save the generated MCQs
        
    Returns:
        The generated MCQs as a dictionary
    """
    if not transcript_data:
        logger.error("No transcript data provided. Can't generate MCQs.")
        return None

    logger.info("Generating student MCQs...")
    
    try:
        # Create the output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Extract video context from transcript
        video_context = transcript_data['combined_transcript'][0]['combined_transcript']
        
        # Configure the agent (similar to ui.py's generate_mcqs)
        config = {"configurable": {"thread_id": session_id, 'agent_choice': AgentType.student_agent.value}}
        
        # Create the payload (similar to ui.py's generate_mcqs)
        payload = {
            "messages": [{"role": "human", "content": 'generate a set of mcq questions covering all key concepts for the video content.'}],
            'expert_preference': AgentType.student_agent.value,
            'video_context': video_context,
            'intent': StudIntent.GENERATE_MCQ.value,
        }
        
        # Invoke the agent asynchronously
        logger.info("Invoking student agent to generate MCQs...")
        raw = asyncio.run(app.ainvoke(payload, config))
        
        # Process the response
        try:
            # Try to parse JSON from answer field
            answer_text = raw['answer'].replace('```json','').replace('```','').strip()
            mcq_data = json.loads(answer_text)
        except json.JSONDecodeError as e:
            # If there's an error, try to use the doc content instead
            logger.warning(f"Failed to parse MCQ data from answer: {str(e)}. Trying doc_content.")
            mcq_data = {"questions": [], "topics": []}
            
            # Extract MCQ data from doc_content if available
            if "doc_content" in raw:
                # For now, just use the doc content as is
                doc_content = raw["doc_content"]
                
                # Save the doc content to the output file
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(doc_content)
                
                logger.info(f"Saved doc content to {output_file}")
                return {"raw_doc_content": doc_content}
        
        # Format MCQs for output file if we have valid MCQ data
        formatted_mcqs = format_mcqs_for_output(mcq_data)
        
        # Save to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(formatted_mcqs)
        
        logger.info(f"Saved generated student MCQs to {output_file}")
        return mcq_data
        
    except Exception as e:
        logger.error(f"Error generating student MCQs: {e}")
        # Save error message to file
        error_msg = f"ERROR: Failed to generate student MCQs: {str(e)}"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(error_msg)
        return error_msg

if __name__ == "__main__":
    print("\n" + "="*80)
    print(" "*25 + "STUDENT MCQ GENERATION")
    print("="*80 + "\n")
    
    print("Loading transcript data...")
    transcript_data = load_transcript()
    
    if transcript_data:
        session_id = "student_mcq_generation_session"
        output_file = '/Users/ankitku5/Desktop/vid2insight/evaluation/model_outputs/model_generated_student_mcq.txt'
        
        print("\nGenerating MCQs for the video transcript...")
        print("This may take a minute or two...\n")
        
        mcqs = generate_student_mcqs(transcript_data, session_id, output_file)
        
        if isinstance(mcqs, dict) and 'questions' in mcqs:
            print("\nSuccessfully generated MCQs!")
            print(f"Number of questions: {len(mcqs.get('questions', []))}")
            print(f"Topics covered: {len(mcqs.get('topics', []))}")
            print(f"\nFull MCQs saved to: {output_file}")
        else:
            print("\nFailed to generate MCQs.")
    else:
        print("Failed to load transcript data. Exiting.")
