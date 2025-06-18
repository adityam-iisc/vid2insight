import hashlib

import streamlit as st
import os
import asyncio
import json
from agent.vid2_insight_graph import app
from streamlit.runtime.scriptrunner import get_script_run_ctx
from ingestion.combined_text_transcriptor import create_ingestion_data
from agent.student_agent.constants import Intent as StudIntent
from agent.doc_agent.constants import Intent as DocIntent
from agent.constants import AgentType



class Facilitator:

    @staticmethod
    def compute_video_id(video_hash: str, length: int) -> str:
        """
        Compute a unique fingerprint for a video by hashing together:
          1. The video's content hash (SHA-256 hex digest)
          2. The video's length in bytes

        Args:
            video_hash (str): SHA-256 hex digest of the video content.
            length (int): Length of the video file in bytes.

        Returns:
            str: SHA-256 hex digest of the concatenated input.
        """
        # Combine the two pieces of data in a canonical way
        payload = f"{video_hash}:{length}"
        # Compute and return the SHA-256 of that payload
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()

    @staticmethod
    def process_video(video_input, consider_audio, consider_video, interval):
        uuid = Facilitator.compute_video_id(
            hashlib.sha256(video_input.read()).hexdigest(),
            video_input.size
        )
        video_input.seek(0)
        input_path = '../docs/input'
        output_path = os.path.join('../docs/', uuid)
        if video_input is not None:
            if os.path.exists(os.path.join(output_path, 'transcript.json')):
                st.info('Video already processed. Loading existing data...')
                transcript = json.load(open(os.path.join(output_path, 'transcript.json')))
                st.session_state.context = transcript
                return True
            os.makedirs(input_path, exist_ok=True)
            os.makedirs(output_path, exist_ok=True)
            with open(os.path.join(input_path,f'{uuid}.mp4'), 'wb') as f:
                f.write(video_input.read())
            pload, output_dir = create_ingestion_data(os.path.join(input_path,f'{uuid}.mp4'), output_path, interval)
            st.session_state.context = json.loads(pload)
        return True

    @staticmethod
    def generate_mcqs(session_id:str = '1'):
        config = {"configurable": {"thread_id": session_id, 'agent_choice': AgentType.student_agent.value}}
        payload = {
            "messages": [{"role": "human", "content": 'generate a set of mcq questions covering all key concepts for the video content.'}],
            'expert_preference': AgentType.student_agent.value,
            'video_context': st.session_state.context['combined_transcript'][0]['combined_transcript'],
            'intent': StudIntent.GENERATE_MCQ.value,
        }
        raw = asyncio.run(app.ainvoke(payload, config))
        return json.loads(raw['answer'].replace('```json','').replace('```',''))

    @staticmethod
    def generate_study_summary(session_id:str = '1') -> tuple[str, str]:
        # invoke student_agent graph for Summary
        config = {"configurable": {"thread_id": session_id, 'agent_choice': AgentType.student_agent.value}}
        payload = {
            "messages": [{"role": "human", "content": 'generate a comprehensive study summary for the video content.'}],
            'expert_preference': AgentType.student_agent.value,
            'video_context': st.session_state.context['combined_transcript'][0]['combined_transcript'],
            'intent': StudIntent.GENERATE_SUMMARY.value
        }
        raw = asyncio.run(app.ainvoke(payload, config))
        return json.loads(raw['answer'].replace('```json','').replace('```',''))

    @staticmethod
    def send_chat_studentG(session_id: str, results: list[dict], chat_input: str):
        """
        Send the MCQ evaluation results (correct/incorrect per question) back to the app.
        """
        if chat_input.strip() == '':
            st.warning("Please enter a message to send.")
            return '', ''
        config = {"configurable": {"thread_id": session_id, 'agent_choice': AgentType.student_agent.value}}
        messages = f"Answer my query: {chat_input}" + (f"And some additional context if necessary: {json.dumps(results)}" if results else '')
        payload = {
            "messages": [{"role": "human", "content": messages}],
            'expert_preference': AgentType.student_agent.value,
            'video_context': st.session_state.context['combined_transcript'][0]['combined_transcript'],
            'intent': StudIntent.DOC_CHAT.value,
        }
        raw = asyncio.run(app.ainvoke(payload, config))
        return raw['chat_content'], raw['doc_content']

    @staticmethod
    def generate_product_doc(session_id: str = 1, doc_choice: str = "Product Doc") -> str:
        """
        Generate a product document based on the selected mode and video.
        """
        intent = DocIntent.GENERATE_DOCS.value if doc_choice == "Product Doc" else DocIntent.GENERATE_EXEC_SUMMARY.value

        config = {"configurable": {"thread_id": session_id, 'agent_choice': AgentType.doc_agent.value}}
        payload = {
            "messages": [{"role": "human", "content": 'generate a product documentation for the video content.'}],
            'expert_preference': AgentType.doc_agent.value,
            'video_context': st.session_state.context['combined_transcript'][0]['combined_transcript'],
            'intent': DocIntent.GENERATE_DOCS.value
        }
        raw = asyncio.run(app.ainvoke(payload, config))
        return raw['answer']

    @staticmethod
    def send_chat_docG(session_id: str = 1, results: str= '', chat_input: str = '') -> str:
        """
        Generate a product document based on the selected mode and video.
        """
        if not chat_input:
            return '', ''
        config = {"configurable": {"thread_id": session_id, 'agent_choice': AgentType.doc_agent.value}}
        messages = f"Answer my query: {chat_input}" + (
            f"with reference to my current version of document: {results}" if results else '')
        payload = {
            "messages": [{"role": "human", "content": messages}],
            'expert_preference': AgentType.doc_agent.value,
            'video_context': st.session_state.context['combined_transcript'][0]['combined_transcript'],
            'intent': DocIntent.DOC_CHAT.value,
        }
        raw = asyncio.run(app.ainvoke(payload, config))
        return raw['chat_content'], raw['doc_content']

    def send_gen_chat(session_id: str = 1, chat_input: str = '') -> str:
        """
        Send a chat message to the general chat agent.
        """
        if not chat_input:
            return ''
        config = {"configurable": {"thread_id": session_id, 'agent_choice': AgentType.chat.value}}
        payload = {
            "messages": [{"role": "human", "content": chat_input}],
            'expert_preference': AgentType.chat.value,
            'video_context': st.session_state.context['combined_transcript'][0]['combined_transcript'],
            'intent': DocIntent.DOC_CHAT.value,
        }
        raw = asyncio.run(app.ainvoke(payload, config))
        return raw['chat_content']


class MultiScreenApp:
    def __init__(self):
        self.screen = st.session_state.get("screen", 1)
        st.session_state.session_id = get_script_run_ctx().session_id
        st.set_page_config(page_title="Video Insight App", layout="wide")

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
            self.show_screen_5()

    def show_screen_1(self):
        st.title("Upload or Link a Video")

        st.file_uploader("Upload a video file", type=["mp4", "mov", "avi"], key="video_file")
        st.text_input("Or enter YouTube link", key="youtube_link")

        st.checkbox("Consider Audio", value=True, key="consider_audio")
        st.checkbox("Consider Video", value=True, key="consider_video")
        st.slider("Process every X seconds", 1, 60, 15, key="interval")

        if st.button("Submit"):
            result = ()
            with st.spinner("Processing video… Please do not refresh the page."):
                st.info('This process can take upto 20min depending on the video length and your system performance.')
                result = st.session_state.video_name = Facilitator.process_video(
                    st.session_state.get("video_file"),
                    st.session_state.get("consider_audio"),
                    st.session_state.get("consider_video"),
                    st.session_state.get("interval")
                )
            if result:
                st.session_state.screen = 2
                st.rerun()
            else:
                st.session_state = 1
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
                elif option == "Simple Chat":
                    st.session_state.screen = 5
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
        specialist = st.radio("Choose your desired output format: ", ["Product Doc", "Executive Summary"], key="doc_choice", horizontal=True)

        col_response, col_chat = st.columns([5, 2])
        with col_response:
            editable = st.checkbox("Enable editing", value=True, key="output_editable")
            st.subheader(f"Generated Response" + (f" (Editable)" if editable else ""))
            if st.session_state.get("last_specialist",'') != specialist:
                response = Facilitator.generate_product_doc(st.session_state.session_id, doc_choice=specialist)

            if "output" not in st.session_state or st.session_state.get("last_specialist") != specialist:
                st.session_state.output = response
                st.session_state.last_specialist = specialist
            # st.session_state.output = st.text_area("Edit your response:", value=st.session_state.get("output", ""),
            #                                            height=400)
            if editable:
                st.session_state.output = st.text_area(
                    "Edit your response:",
                    value=st.session_state.output,
                    height=400,
                    key="output_textarea"
                )
            else:
                st.markdown(st.session_state.output)
        with col_chat:
            st.subheader("Chat Interface")
            for turn in st.session_state.get("chat_history", []):
                st.chat_message(turn["role"]).write(turn["content"])

            chat_input = st.text_area(
                "Type your message",
                key="chat_input",
                height=80
            )
            if st.button("Send", key="chat_send"):
                if not chat_input.strip():
                    st.warning("Please enter a message to send.")
                else:
                    response, output = Facilitator.send_chat_docG(
                        session_id=st.session_state.session_id,
                        results=st.session_state.output,
                        chat_input=chat_input
                    )
                    st.session_state.output = output
                    st.session_state.chat_history = (
                            st.session_state.get("chat_history", []) +
                            [
                                {"role": "user", "content": chat_input},
                                {"role": "assistant", "content": response}
                            ]
                    )
                    st.rerun()

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("Submit"):
                st.session_state.output = (
                    f"Processed output for: {st.session_state.get('doc_choice')}"
                )
                st.rerun()
        with col2:
            st.download_button(
                "Download as Markdown",
                st.session_state.output,
                "output.md"
            )
        with col3:
            if st.button("Reset"):
                st.session_state.output = ""
                st.session_state.chat_history = []
                st.session_state.screen = 2
                st.session_state.last_specialist = ''
                st.rerun()

    def show_screen_4(self):
        st.title("Student Tutor")

        tutor_mode = st.radio("Choose Action", ["Generate MCQ", "Summary"], horizontal=True, key="tutor_choice")
        col_left, col_right = st.columns([4, 2])
        with col_left:
            if tutor_mode == "Generate MCQ":
                if "mcq_data" not in st.session_state:
                    st.session_state.mcq_data = Facilitator.generate_mcqs(st.session_state.session_id)
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
                        # mark evaluated
                        st.session_state.mcq_evaluated = True
                        # compile first-try results list
                        results = []
                        for i, q in enumerate(st.session_state.mcq_data["questions"]):
                            sel_idx = st.session_state.mcq_answers.get(i)
                            is_correct = (q["options"][sel_idx] == q["correct_option"])
                            results.append({"question_index": i, "correct": is_correct})
                        st.session_state.mcq_eval = results
                        st.rerun()
            else:  # Summary
                if "summary_data" not in st.session_state:
                    st.session_state.summary_data = Facilitator.generate_study_summary(st.session_state.session_id)

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
            chat_input = st.text_area("Message", key="tutor_chat_input", placeholder=st.session_state.get("chat_input", "Type your message here..."))
            additional_info = st.session_state.get('mcq_eval', []) if tutor_mode == "Generate MCQ" else json.dumps(st.session_state.get('summary_data', {}))
            if st.button("Send", key="tutor_chat_send"):
                response, mcq_questions = Facilitator.send_chat_studentG(session_id=st.session_state.session_id, results= additional_info, chat_input=chat_input)
                if st.session_state.get("tutor_chat_history", []):
                    st.session_state.tutor_chat_history.extend([
                        {"role": "user", "content": chat_input},
                        {"role": "assistant", "content": response}
                    ])
                else:
                    st.session_state.tutor_chat_history = [
                        {"role": "user", "content": chat_input},
                        {"role": "assistant", "content": response}
                    ]
                if tutor_mode == "Generate MCQ" and mcq_questions:
                    st.session_state.mcq_data = mcq_questions
                    st.session_state.mcq_answers = {}
                    st.session_state.mcq_evaluated = False
                st.session_state.chat_input = ""  # clear input
            for turn in st.session_state.get('tutor_chat_history', []):
                st.chat_message(turn["role"]).write(turn["content"])
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Submit", key="tutor_submit"):
                st.rerun()
        with col2:
            if st.button("Reset", key="tutor_reset"):
                st.session_state.mcq_data = []
                st.session_state.mcq_answers = {}
                st.session_state.mcq_evaluated = False
                st.session_state.summary_data = []
                st.session_state.screen = 2
                st.rerun()

    def show_screen_5(self):
        st.title("Chat")

        # Chat history window
        for turn in st.session_state.get("screen5_chat_history", []):
            st.chat_message(turn["role"]).write(turn["content"])

        # Input box at bottom
        chat_input = st.text_area(
            "Message",
            key="screen5_chat_input",
            placeholder="Type your message here...",
            height=80
        )

        send_col, reset_col = st.columns([1, 1])
        with send_col:
            if st.button("Send", key="screen5_send"):
                if chat_input.strip():
                    history = st.session_state.get("screen5_chat_history", [])

                    history.append({"role": "user", "content": chat_input})

                    response = Facilitator.send_gen_chat(
                        session_id=st.session_state.session_id,
                        chat_input=chat_input
                    )
                    history.append({"role": "assistant", "content": response})

                    st.session_state.screen5_chat_history = history
                    st.rerun()
        with reset_col:
            if st.button("Reset", key="screen5_reset"):
                st.session_state.screen5_chat_history = []
                st.rerun()


if __name__ == "__main__":
    if "screen" not in st.session_state:
        st.session_state.screen = 1
    ui_app = MultiScreenApp()
    ui_app.run()

