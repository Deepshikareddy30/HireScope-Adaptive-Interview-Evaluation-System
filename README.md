# HireScope – AI-Powered Interview Simulation Platform

HireScope is an AI-powered interview simulation platform that conducts personalized, multi-round mock interviews based on a candidate's resume, role, and responses.

Unlike traditional mock interview platforms that rely on fixed question banks, HireScope dynamically generates questions, evaluates responses, and asks context-aware follow-up questions to create a more realistic interview experience.

---

## 🚀 Features

- 📄 **Resume-Based Interviewing**
  - Extracts relevant information from a candidate's resume.
  - Uses skills, projects, technologies, and experience to personalize questions.

- 🤖 **AI-Powered Question Generation**
  - Generates interview questions dynamically based on the candidate's profile and selected role.
  - Supports multiple interview rounds.

- 🔄 **Adaptive Follow-Up Questions**
  - Evaluates candidate responses.
  - Generates follow-up questions when additional clarification or deeper explanation is required.

- 🎯 **Multi-Round Interviews**
  - Resume Round
  - Technical Round
  - HR Round

- 🧠 **AI Answer Evaluation**
  - Evaluates responses based on factors such as correctness, depth, relevance, and clarity.

- 📊 **Interview Session Management**
  - Tracks questions, responses, follow-ups, rounds, and session progress.

- 💬 **Conversational Interview Experience**
  - Provides an interactive chat-based interview interface.

---

## 🏗️ System Architecture

```text
Candidate
    │
    ▼
Frontend
(HTML / CSS / JavaScript)
    │
    ▼
FastAPI Backend
    │
    ├── Resume Processing
    │
    ├── Interview Session Management
    │
    ├── Question Generation
    │
    └── Answer Evaluation
    │
    ▼
LLM API
    │
    ▼
AI Response
    │
    ▼
Frontend Interview Chat
