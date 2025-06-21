#!/usr/bin/env python
"""Script to generate student summary responses and save them to a file.

This script loads the transcript, generates a student summary directly 
without using UI functions, and saves it to model_generated_student_summary.txt
"""

import sys
import os
import json

# Add the parent directory to sys.path to allow imports from the root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.config.initialize_logger import setup_logger
import asyncio
from agent.vid2_insight_graph import app
from agent.constants import AgentType
from agent.student_agent.constants import Intent as StudIntent

# Set up logger
logger = setup_logger()

def format_summary_for_output(summary_data: dict) -> str:
    """Format summary data into a readable text format.
    
    Args:
        summary_data: Dictionary containing summary data
        
    Returns:
        Formatted summary as a string
    """
    if not summary_data:
        return "No summary was generated."
    
    formatted_output = []
    
    # Add title
    formatted_output.append("# STUDY SUMMARY\n")
    
    # Add topics if available
    if summary_data.get("topics"):
        formatted_output.append("## Topics Covered")
        for topic in summary_data["topics"]:
            formatted_output.append(f"- {topic}")
        formatted_output.append("")
    
    # Add summary content
    if summary_data.get("summary"):
        formatted_output.append("## Summary")
        formatted_output.append(summary_data["summary"])
        formatted_output.append("")
    
    # Add study plan if available
    if summary_data.get("study_plan"):
        formatted_output.append("## Study Plan")
        for day in summary_data["study_plan"]:
            formatted_output.append(f"### Day {day['day']}: {day['focus']}")
            for activity in day['activities']:
                formatted_output.append(f"- {activity}")
            formatted_output.append("")
    
    # Add prerequisites if available
    if summary_data.get("prerequisites"):
        formatted_output.append("## Prerequisites")
        if isinstance(summary_data["prerequisites"], list):
            for prereq in summary_data["prerequisites"]:
                formatted_output.append(f"- {prereq}")
        else:
            formatted_output.append(f"- {summary_data['prerequisites']}")
    
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

def generate_student_summary(transcript_data,
                          session_id: str = "student_summary_generation_session",
                          output_file: str = '/Users/ankitku5/Desktop/vid2insight/evaluation/model_outputs/model_generated_student_summary.txt'):
    """Generate student summary from transcript data using the student agent.
    
    Args:
        transcript_data: The transcript data
        session_id: Session ID for the agent
        output_file: Path to save the generated summary
        
    Returns:
        The generated summary as a dictionary
    """
    if not transcript_data:
        logger.error("No transcript data provided. Can't generate summary.")
        return None

    logger.info("Generating student summary...")
    
    try:
        # Create the output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Extract video context from transcript
        video_context = transcript_data['combined_transcript'][0]['combined_transcript']
        
        # Configure the agent (similar to ui.py's generate_study_summary)
        config = {"configurable": {"thread_id": session_id, 'agent_choice': AgentType.student_agent.value}}
        
        # Create the payload (similar to ui.py's generate_study_summary)
        payload = {
            "messages": [{"role": "human", "content": 'generate a comprehensive study summary for the video content.'}],
            'expert_preference': AgentType.student_agent.value,
            'video_context': video_context,
            'intent': StudIntent.GENERATE_SUMMARY.value,
        }
        
        # Invoke the agent asynchronously
        logger.info("Invoking student agent to generate summary...")
        raw = asyncio.run(app.ainvoke(payload, config))
        
        # Process the response
        summary_data = json.loads(raw['answer'].replace('```json','').replace('```',''))
        
        # Format summary for output file
        formatted_summary = format_summary_for_output(summary_data)
        
        # Save to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(formatted_summary)
        
        logger.info(f"Saved generated student summary to {output_file}")
        return summary_data
        
    except Exception as e:
        logger.error(f"Error generating student summary: {e}")
        # Save error message to file
        error_msg = f"ERROR: Failed to generate student summary: {str(e)}"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(error_msg)
        return error_msg

if __name__ == "__main__":
    print("\n" + "="*80)
    print(" "*25 + "STUDENT SUMMARY GENERATION")
    print("="*80 + "\n")
    
    print("Loading transcript data...")
    transcript_data = load_transcript()
    
    if transcript_data:
        session_id = "student_summary_generation_session"
        output_file = '/Users/ankitku5/Desktop/vid2insight/evaluation/model_outputs/model_generated_student_summary.txt'
        
        print("\nGenerating study summary for the video transcript...")
        print("This may take a minute or two...\n")
        
        summary = generate_student_summary(transcript_data, session_id, output_file)
        
        if isinstance(summary, dict):
            print("\nSuccessfully generated study summary!")
            print(f"Topics covered: {len(summary.get('topics', []))}")
            if summary.get('study_plan'):
                print(f"Study plan days: {len(summary.get('study_plan', []))}")
            print(f"\nFull study summary saved to: {output_file}")
        else:
            print("\nFailed to generate study summary.")
    else:
        print("Failed to load transcript data. Exiting.")
