#!/usr/bin/env python
"""Test script to check if the generate_study_summary function works."""

import sys
import os
import json

# Add the parent directory to sys.path to allow imports from the root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock Streamlit
import importlib.util
import sys

class MockStreamlit:
    class SessionState:
        def __init__(self):
            self.context = {
                'combined_transcript': [{
                    'combined_transcript': "This is a test transcript for LangChain documentation."
                }]
            }

    def __init__(self):
        self.session_state = self.SessionState()

# Install mock
sys.modules['streamlit'] = MockStreamlit()
import streamlit as st

# Now import the Facilitator
from agent.ui.ui import Facilitator

# Print the session state to verify it's set correctly
print("Session state:", st.session_state.context)

# Try to generate a summary
try:
    print("Trying to generate summary...")
    summary, _ = Facilitator.generate_study_summary()
    print("Generated summary:", summary[:100] + "..." if len(summary) > 100 else summary)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
