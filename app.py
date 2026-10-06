"""
AI Interview Preparation Platform  (beginner level)
---------------------------------------------------
Stack : Python + Streamlit + LangChain + Ollama (local LLM) + Whisper (speech-to-text)

How it works
1. You pick a job role, level and interview type.
2. The AI (running locally in Ollama) generates interview questions.
3. You answer by typing OR speaking (Whisper turns your voice into text).
4. The AI gives a score, strengths, improvements and a sample answer.
5. At the end you see a summary of your performance.
"""

import os
import re
import tempfile

import streamlit as st
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------
st.set_page_config(page_title="AI Interview Prep", page_icon="🎯", layout="centered")


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def get_llm(model_name: str) -> ChatOllama:
    """Create the connection to the local Ollama model."""
    return ChatOllama(model=model_name, temperature=0.7)


def generate_questions(model_name, role, level, interview_type, count):
    """Ask the AI to create interview questions and return them as a list."""
    prompt = ChatPromptTemplate.from_template(
        "You are an expert interviewer.\n"
        "Create {count} {interview_type} interview questions for a {level} "
        "{role} position.\n"
        "Rules: write ONE question per line, number them 1., 2., 3. ... "
        "and write nothing else (no intro, no answers)."
    )
    chain = prompt | get_llm(model_name) | StrOutputParser()
    text = chain.invoke(
        {"count": count, "interview_type": interview_type, "level": level, "role": role}
    )

    questions = []
    for line in text.split("\n"):
        line = line.strip()
        # Keep only lines that start with a number like "1." or "2)"
        if re.match(r"^\d+[\.\)]", line):
            questions.append(re.sub(r"^\d+[\.\)]\s*", "", line))
    return questions[:count]


def get_feedback(model_name, role, level, question, answer):
    """Ask the AI to evaluate the candidate's answer."""
    prompt = ChatPromptTemplate.from_template(
        "You are a friendly but honest interview coach.\n"
        "Role: {level} {role}\n"
        "Question: {question}\n"
        "Candidate's answer: {answer}\n\n"
        "Evaluate the answer using EXACTLY this format:\n"
        "Score: <number from 1 to 10>/10\n"
        "Strengths:\n- ...\n"
        "Improvements:\n- ...\n"
        "Sample better answer: <a short model answer>"
    )
    chain = prompt | get_llm(model_name) | StrOutputParser()
    return chain.invoke(
        {"role": role, "level": level, "question": question, "answer": answer}
    )


def extract_score(feedback_text):
    """Pull the number out of 'Score: 7/10'. Returns 0 if not found."""
    match = re.search(r"Score:\s*(\d+)", feedback_text)
    return min(int(match.group(1)), 10) if match else 0


@st.cache_resource(show_spinner="Loading Whisper model (first time only)...")
def load_whisper():
    """Load Whisper once and reuse it. 'base' is small and fast."""
    import whisper  # imported here so the app starts quickly

    return whisper.load_model("base")


def transcribe_audio(audio_file) -> str:
    """Convert recorded/uploaded audio into text using Whisper.
    (Whisper needs ffmpeg installed on your computer.)"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_file.getvalue())
        tmp_path = tmp.name
    try:
        result = load_whisper().transcribe(tmp_path)
        return result["text"].strip()
    finally:
        os.remove(tmp_path)  # clean up the temporary file


# ---------------------------------------------------------------------------
# Session state (Streamlit forgets variables on every click, so we store them)
# ---------------------------------------------------------------------------
defaults = {
    "stage": "setup",      # setup -> interview -> summary
    "questions": [],
    "current": 0,
    "results": [],         # list of dicts: question, answer, feedback, score
    "feedback": None,      # feedback for the question currently on screen
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def reset_all():
    for key, value in defaults.items():
        st.session_state[key] = value


# ---------------------------------------------------------------------------
# Sidebar settings
# ---------------------------------------------------------------------------
st.sidebar.header("⚙️ Settings")
model_name = st.sidebar.text_input("Ollama model", value="llama3.2")
st.sidebar.caption("Install it first:  `ollama pull llama3.2`")
if st.sidebar.button("🔄 Start over"):
    reset_all()
    st.rerun()

st.title("🎯 AI Interview Preparation")
st.caption("Practice interviews with a local AI coach — type or speak your answers.")

# ---------------------------------------------------------------------------
# STAGE 1: Setup
# ---------------------------------------------------------------------------
if st.session_state.stage == "setup":
    st.subheader("1. Tell us about your interview")

    role = st.text_input("Job role", placeholder="e.g. Python Developer, Data Analyst")
    level = st.selectbox("Experience level", ["Fresher", "Junior", "Mid-level", "Senior"])
    interview_type = st.selectbox(
        "Interview type", ["Technical", "HR / Behavioral", "Mixed"]
    )
    count = st.slider("Number of questions", 3, 10, 5)

    if st.button("🚀 Start Interview", type="primary"):
        if not role.strip():
            st.warning("Please enter a job role.")
        else:
            with st.spinner("AI is preparing your questions..."):
                try:
                    questions = generate_questions(
                        model_name, role, level, interview_type, count
                    )
                except Exception as e:
                    st.error(
                        f"Could not reach Ollama. Is it running? ({e})"
                    )
                    st.stop()

            if not questions:
                st.error("The AI did not return any questions. Try again.")
            else:
                st.session_state.update(
                    questions=questions,
                    role=role,
                    level=level,
                    stage="interview",
                    current=0,
                    results=[],
                    feedback=None,
                )
                st.rerun()

# ---------------------------------------------------------------------------
# STAGE 2: Interview
# ---------------------------------------------------------------------------
elif st.session_state.stage == "interview":
    idx = st.session_state.current
    total = len(st.session_state.questions)
    question = st.session_state.questions[idx]

    st.progress(idx / total, text=f"Question {idx + 1} of {total}")
    st.subheader(f"Q{idx + 1}. {question}")

    # --- Step A: collect the answer (only before feedback is shown) ---
    if st.session_state.feedback is None:
        mode = st.radio("How do you want to answer?", ["⌨️ Type", "🎤 Speak"], horizontal=True)
        answer = ""

        if mode == "⌨️ Type":
            answer = st.text_area("Your answer", height=180)
        else:
            # st.audio_input exists in newer Streamlit; otherwise fall back to upload
            if hasattr(st, "audio_input"):
                audio = st.audio_input("Record your answer")
            else:
                audio = st.file_uploader("Upload your answer", type=["wav", "mp3", "m4a"])

            if audio is not None:
                with st.spinner("Transcribing your voice..."):
                    try:
                        answer = transcribe_audio(audio)
                    except Exception as e:
                        st.error(f"Transcription failed. Is ffmpeg installed? ({e})")
                st.text_area("What Whisper heard (you can edit it)", value=answer, key=f"t{idx}")
                answer = st.session_state.get(f"t{idx}", answer)

        if st.button("✅ Submit answer", type="primary"):
            if not answer.strip():
                st.warning("Please give an answer first.")
            else:
                with st.spinner("AI coach is reviewing your answer..."):
                    feedback = get_feedback(
                        model_name,
                        st.session_state.role,
                        st.session_state.level,
                        question,
                        answer,
                    )
                st.session_state.feedback = feedback
                st.session_state.results.append(
                    {
                        "question": question,
                        "answer": answer,
                        "feedback": feedback,
                        "score": extract_score(feedback),
                    }
                )
                st.rerun()

    # --- Step B: show feedback and move on ---
    else:
        last = st.session_state.results[-1]
        st.info(f"**Your answer:** {last['answer']}")
        st.markdown("### 🧠 AI Feedback")
        st.markdown(st.session_state.feedback)

        is_last = idx + 1 >= total
        if st.button("🏁 Finish" if is_last else "➡️ Next question", type="primary"):
            st.session_state.feedback = None
            if is_last:
                st.session_state.stage = "summary"
            else:
                st.session_state.current += 1
            st.rerun()

# ---------------------------------------------------------------------------
# STAGE 3: Summary
# ---------------------------------------------------------------------------
elif st.session_state.stage == "summary":
    results = st.session_state.results
    scores = [r["score"] for r in results]
    average = sum(scores) / len(scores) if scores else 0

    st.subheader("🎉 Interview complete!")
    col1, col2 = st.columns(2)
    col1.metric("Average score", f"{average:.1f} / 10")
    col2.metric("Questions answered", len(results))

    if average >= 8:
        st.success("Excellent! You look interview-ready.")
    elif average >= 5:
        st.info("Good effort. Review the feedback and practice again.")
    else:
        st.warning("Keep practicing — you'll improve quickly with repetition.")

    st.bar_chart({f"Q{i + 1}": s for i, s in enumerate(scores)})

    st.markdown("### Review your answers")
    for i, r in enumerate(results, start=1):
        with st.expander(f"Q{i}: {r['question']}  —  {r['score']}/10"):
            st.markdown(f"**Your answer:** {r['answer']}")
            st.markdown(r["feedback"])

    if st.button("🔁 Practice again", type="primary"):
        reset_all()
        st.rerun()