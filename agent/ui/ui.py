import streamlit as st
import os
import tempfile
import asyncio
import json
from agent.student_agent.student_graph import app as student_app
from streamlit.runtime import get_instance
from streamlit.runtime.scriptrunner import get_script_run_ctx



class PlaceholderFunctions:
    @staticmethod
    def process_video(video_input, consider_audio, consider_video, interval):
        if video_input is not None:
            suffix = os.path.splitext(video_input.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                tmp_file.write(video_input.read())
                return tmp_file.name
        return None

    @staticmethod
    def generate_mcqs(session_id:str = '1'):
        # invoke student_agent graph for MCQ
        video_path = st.session_state.get("video_name")
        config = {
            "configurable": {
                "thread_id": session_id,
                "user_id": "streamlit_user",
                "intent": "generate_mcq",
                "file_path": video_path
            }
        }
        input_data = {
            "messages": [
                {"role": "human", "content": "Generate multiple-choice questions for the provided video."}
            ]
        }
        raw = asyncio.run(student_app.ainvoke(input_data, config))
        # raw['mcq'] is a JSON string; parse it into a dict and return
        mcq_json = json.loads(raw['answer'].content.replace("```json", "").replace("```", ""))
        return mcq_json

    @staticmethod
    def generate_study_summary(session_id:str = '1'):
        # invoke student_agent graph for Summary
        video_path = st.session_state.get("video_name")
        config = {
            "configurable": {
                "thread_id": session_id,
                "user_id": "streamlit_user",
                "intent": "generate_summary",
                "file_path": video_path
            }
        }
        input_data = {
            "messages": [
                {"role": "human", "content": "Generate a student-focused summary for the provided video."}
            ]
        }
        raw = asyncio.run(student_app.ainvoke(input_data, config))
        # parse the JSON string response
        return json.loads(raw['answer'].content.replace("```json", "").replace("```", ""))


class MultiScreenApp:
    def __init__(self):
        self.screen = st.session_state.get("screen", 1)
        runtime = get_instance()
        st.session_state.session_id = get_script_run_ctx().session_id


    def run(self):
        if self.screen == 1:
            self.show_screen_1()
        elif self.screen == 2:
            self.show_screen_2()
        elif self.screen == 3:
            self.show_screen_3()
        elif self.screen == 4:
            self.show_screen_4()
        elif self.screen == 5:
            st.write("This is the fifth screen, which is currently not implemented.")

    def show_screen_1(self):
        st.title("Upload or Link a Video")

        st.file_uploader("Upload a video file", type=["mp4", "mov", "avi"], key="video_file")
        st.text_input("Or enter YouTube link", key="youtube_link")

        st.checkbox("Consider Audio", value=True, key="consider_audio")
        st.checkbox("Consider Video", value=True, key="consider_video")
        st.slider("Process every X seconds", 1, 10, 3, key="interval")

        if st.button("Submit"):
            st.session_state.video_name = PlaceholderFunctions.process_video(
                st.session_state.get("video_file"),
                st.session_state.get("consider_audio"),
                st.session_state.get("consider_video"),
                st.session_state.get("interval")
            )
            st.session_state.screen = 2
            st.rerun()

    def show_screen_2(self):
        st.title(f"Choose your preferred Agent for")
        st.write(f'{st.session_state.get('video_name', '')}')
        option = st.radio("Select Mode", ["Product Document Generator", "Student Tutor", "Simple Chat"], key="mode")

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Submit"):
                if option == "Student Tutor":
                    st.session_state.screen = 4
                else:
                    st.session_state.screen = 3
                st.session_state.selected_mode = option
                st.rerun()

        with col2:
            if st.button("Reset"):
                st.session_state.clear()
                st.session_state.screen = 1
                st.rerun()

    def show_screen_3(self):
        st.title("Product Document Generator")
        st.video(st.session_state.get("video_name", ""))

        st.radio("Choose your desired output format: ", ["Product Doc", "Executive Summary"], key="doc_choice")

        col_response, col_chat = st.columns([5, 2])
        with col_response:
            st.subheader("Generated Response (Editable)")
            st.session_state.output = st.text_area("Edit your response:", value=st.session_state.get("output", ""), height=400)

        with col_chat:
            st.subheader("Chat Interface")
            chat_input = st.text_area("Type your message", key="chat_input")
            if st.button("Send", key="chat_send"):
                st.session_state.chat_history = st.session_state.get("chat_history", []) + [chat_input]
            for msg in reversed(st.session_state.get("chat_history", [])):
                st.markdown(f"**You:** {msg}")

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("Submit"):
                st.session_state.output = f"Processed output for: {st.session_state.get('doc_choice')}"
                st.rerun()
        with col2:
            st.download_button("Download as Markdown", st.session_state.output, "output.md")
        with col3:
            if st.button("Reset"):
                st.session_state.output = ""
                st.session_state.chat_history = []
                st.session_state.screen = 2
                st.rerun()

    def show_screen_4(self):
        st.title("Student Tutor")

        tutor_mode = st.radio("Choose Action", ["Generate MCQ", "Summary"], horizontal=True, key="tutor_choice")
        col_left, col_right = st.columns([4, 2])
        with col_left:
            if tutor_mode == "Generate MCQ":
                if "mcq_data" not in st.session_state:
                    st.session_state.mcq_data = PlaceholderFunctions.generate_mcqs(st.session_state.get("thread_id", "1"))
                    st.session_state.mcq_answers = {}
                    st.session_state.mcq_evaluated = False

                for i, q in enumerate(st.session_state.mcq_data["questions"]):
                    st.markdown(f"### Q{i + 1}: {q['question']}")

                    # Topics covered with tag-style display
                    topic_tags = " ".join([f"`{topic}`" for topic in q["topics_covered"]])
                    st.markdown(f"**Topics Covered:** {topic_tags}")

                    selected_option = st.radio(
                        label="Choose your answer",
                        options=q["options"],
                        key=f"mcq_answer_{i}",
                        index=st.session_state.mcq_answers.get(i, -1) if st.session_state.mcq_answers.get(i,
                                                                                                          -1) != -1 else 0
                    )
                    st.session_state.mcq_answers[i] = q["options"].index(selected_option)

                    if st.session_state.mcq_evaluated:
                        if selected_option == q["correct_option"]:
                            st.success("✅ Correct!")
                        else:
                            st.error(f"❌ Incorrect. Correct answer: {q['correct_option']}")

                if not st.session_state.mcq_evaluated:
                    if st.button("Evaluate"):
                        st.session_state.mcq_evaluated = True
                        st.rerun()
            else:  # Summary
                if "summary_data" not in st.session_state:
                    st.session_state.summary_data = PlaceholderFunctions.generate_study_summary(st.session_state.get("thread_id", "1"))

                data = st.session_state.summary_data
                # Topics
                st.subheader("Topics Covered")
                for topic in data["topics"]:
                    st.markdown(f"- {topic}")

                # Summary text
                st.subheader("Summary")
                st.write(data["summary"])

                # Study plan
                st.subheader("Study Plan")
                for day in data["study_plan"]:
                    st.markdown(f"**Day {day['day']}: {day['focus']}**")
                    for act in day["activities"]:
                        st.markdown(f"- {act}")

                # Prerequisites
                st.subheader("Prerequisites")
                if isinstance(data['prerequisites'], str):
                    st.markdown(f"- {data['prerequisites']}")
                else:
                    for prereq in data["prerequisites"]:
                        st.markdown(f"- {prereq}")
        with col_right:
            st.subheader("Chat Interface")
            chat_input = st.text_area("Message", key="tutor_chat_input")
            if st.button("Send", key="tutor_chat_send"):
                st.session_state.tutor_chat_history = st.session_state.get("tutor_chat_history", []) + [chat_input]
            for msg in reversed(st.session_state.get("tutor_chat_history", [])):
                st.markdown(f"**You:** {msg}")

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Submit", key="tutor_submit"):
                st.rerun()
        with col2:
            if st.button("Reset", key="tutor_reset"):
                st.session_state.screen = 2
                st.rerun()

    def show_screen_5(self):
        st.title("Screen 5")
        st.write("This is the fifth screen, which is currently not implemented.")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Submit", key="tutor_submit"):
                st.rerun()
        with col2:
            if st.button("Reset", key="tutor_reset"):
                st.session_state.screen = 2
                st.rerun()


if __name__ == "__main__":
    if "screen" not in st.session_state:
        st.session_state.screen = 1
    ui_app = MultiScreenApp()
    ui_app.run()

