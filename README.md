# 💼 AI Interview Preparation Platform

A beginner-friendly web app that helps you practice job interviews with a local AI coach.
Choose a role, answer by typing or speaking, and get instant scores and feedback.
Everything runs on your own computer, so it is free and your answers stay private.

**Tech stack:** Python • Streamlit • LangChain • Ollama (Llama 3.2) • OpenAI Whisper

---

## ✨ Features

- AI-generated interview questions for any job role, level and interview type
- Answer by **typing** or **speaking** (Whisper converts voice to text)
- Instant feedback: score out of 10, strengths, improvements and a sample answer
- Progress bar, performance chart and a final summary with answer review
- Custom CSS styling for a clean, modern look

---

## 📁 Project Structure

```
ai_interview_prep/
├── app.py             # Main Streamlit application
├── style.css          # Custom styling
├── requirements.txt   # Python packages
└── README.md          # Project documentation
```

---

## ⚙️ Prerequisites

| Tool | Why it is needed | Download |
|---|---|---|
| Python 3.10+ | Runs the app | https://www.python.org |
| Ollama | Runs the AI model locally | https://ollama.com/download |
| ffmpeg | Lets Whisper read audio | https://ffmpeg.org |

---

## 🚀 Installation

**1. Clone the repository**
```bash
git clone https://github.com/<your-username>/ai-interview-prep.git
cd ai-interview-prep
```

**2. (Optional) Create a virtual environment**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux
```

**3. Install the packages**
```bash
pip install -r requirements.txt
```

**4. Download the AI model**
```bash
ollama pull llama3.2
```
Check it is installed with `ollama list`.

**5. Run the app**
```bash
streamlit run app.py
```
The app opens at http://localhost:8501

---

## 🧭 How to Use

1. Enter your **job role** (for example, Data Analyst).
2. Pick your **experience level**, **interview type** and **number of questions**.
3. Click **Start Interview**.
4. Answer each question by typing or recording your voice.
5. Read the AI feedback, then move to the next question.
6. See your final score and review all answers at the end.

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---|---|
| `model 'llama3.2' not found` | Run `ollama pull llama3.2` |
| `Could not reach Ollama` | Make sure Ollama is installed and running |
| Voice transcription fails | Install **ffmpeg** and restart the terminal |
| App is slow | Use a smaller model: `ollama pull llama3.2:1b`, then type `llama3.2:1b` in the sidebar |
| Styling not updating | Refresh the browser page |

---

## 🔮 Future Improvements

- Save interview history and track progress over time
- Upload a resume to get personalised questions
- Add a timer for each question
- Export the final report as PDF
- Support more languages

---

## 📚 What You Learn

- Building web apps with Streamlit and session state
- Writing prompts and using LangChain with a local LLM
- Adding speech-to-text with Whisper
- Parsing and displaying AI responses

---

## 📄 License

This project is open source and free to use for learning purposes.
