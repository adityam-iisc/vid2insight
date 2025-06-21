#!/usr/bin/env python
# filepath: /Users/ankitku5/Desktop/Data_seicene_college_project/evaluation/extract_transcript.py
"""Extract the combined transcript from transcript.json and save to a text file for evaluation."""

import json
import os
import sys
import argparse
import logging

# Add the parent directory to sys.path to allow imports from the root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up a basic logger instead of using the one from agent module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_combined_transcript(transcript_file_path, output_file_path):
    """
    Extract the combined transcript from a JSON file and save it to a text file.

    Args:
        transcript_file_path (str): Path to the transcript JSON file
        output_file_path (str): Path to save the extracted transcript

    Returns:
        str: Path to the extracted transcript file
    """
    try:
        # Read the transcript JSON
        logger.info(f"Reading transcript from {transcript_file_path}")
        with open(transcript_file_path, 'r', encoding='utf-8') as f:
            transcript_data = json.load(f)
        
        # Extract the combined transcript
        if 'combined_transcript' in transcript_data and isinstance(transcript_data['combined_transcript'], list):
            combined_transcript = transcript_data['combined_transcript'][0]['combined_transcript']
            logger.info(f"Successfully extracted combined transcript of length {len(combined_transcript)} chars")
        else:
            logger.error("Failed to extract combined transcript. Expected structure not found.")
            return None
        
        # Save to output file
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(combined_transcript)
        
        logger.info(f"Saved combined transcript to {output_file_path}")
        return output_file_path
    
    except Exception as e:
        logger.error(f"Error extracting transcript: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Extract combined transcript from JSON file')
    # Use absolute path
    default_input = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs', 'transcript.json')
    parser.add_argument('--input', type=str, default=default_input,
                        help='Path to the transcript JSON file')
    parser.add_argument('--output', type=str, default='model_generated.txt',
                        help='Path to save the extracted transcript')
    args = parser.parse_args()
    
    extract_combined_transcript(args.input, args.output)

if __name__ == "__main__":
    main()
