# 🤖 CV-MATCHING-AI-AGENT

<p align="center">

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF4B4B?logo=streamlit)
![LangChain](https://img.shields.io/badge/LangChain-Agent-green)
![Gemini](https://img.shields.io/badge/Google-Gemini-orange?logo=google)
![ChromaDB](https://img.shields.io/badge/Chroma-VectorDB-purple)

</p>

<p align="center">
An AI-powered Resume Matching System built with <b>FastAPI</b>, <b>Streamlit</b>, <b>LangChain Agent</b>, <b>Google Gemini</b>, and <b>ChromaDB</b>.
</p>

---

# 📖 Overview

CV-MATCHING-AI-AGENT is an end-to-end AI application that automatically analyzes a candidate's resume, retrieves relevant Google Careers job postings from a vector database, and recommends the Top 3 most suitable jobs with explanations, missing skills, and actionable improvement suggestions.

---

# ✨ Features

- 📄 PDF Resume Upload
- 🤖 AI Resume Analysis
- 🔍 Semantic Job Search
- 🧠 LangChain Tool Calling Agent
- 📊 Structured Output (Pydantic)
- ⚡ FastAPI Backend
- 🌐 Streamlit Frontend
- 📡 Server-Sent Events (Realtime Streaming)
- 🗄️ Chroma Vector Database
- 🔗 Google Careers Web Crawler

---

# 🏗️ Architecture

```text
               Resume (PDF)

                     │
                     ▼
          Streamlit Frontend
                     │
          HTTP + Streaming (SSE)
                     │
                     ▼
             FastAPI Backend
                     │
                     ▼
          LangChain AI Agent
                     │
         ┌───────────┴────────────┐
         │                        │
         ▼                        ▼
 search_jobs()              Gemini 2.5 Flash
         │                        │
         ▼                        │
   Chroma VectorDB                │
         ▲                        │
         │                        │
 Google Embedding-2               │
         ▲                        │
         │                        │
 Google Careers Crawler ──────────┘
```

---

# 🛠️ Tech Stack

| Layer | Technology |
|--------|------------|
| Language | Python |
| Backend | FastAPI |
| Frontend | Streamlit |
| AI | Google Gemini 2.5 Flash |
| Agent | LangChain |
| Embeddings | Gemini Embedding 2 |
| Vector DB | ChromaDB |
| Crawling | HTTPX + BeautifulSoup |
| Streaming | Server-Sent Events |

---

# 📂 Project Structure

```text
CV-MATCHING-AI-AGENT/
│
├── hr_agent/
│   ├── hr_agent.py
│   ├── hr_agent_tools.py
│   ├── hr_agent_format.py
│   ├── hr_agent_be.py
│   └── hr_agent_fe.py
│
├── job_craws.py
├── chroma_db/
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

# ⚙️ Installation

```bash
git clone https://github.com/<TPTN1707>/CV-MATCHING-AI-AGENT.git

cd CV-MATCHING-AI-AGENT

uv sync
```

or

```bash
pip install -r requirements.txt
```

---

# 🔑 Environment Variables

Create a `.env`

```env
GOOGLE_API_KEY=YOUR_API_KEY
```

---

# 🕸️ Crawl Jobs

```bash
python job_craws.py
```

This will

- Crawl Google Careers
- Extract job descriptions
- Generate embeddings
- Store them into ChromaDB

---

# 🚀 Run Backend

```bash
python hr_agent/hr_agent_be.py
```

or

```bash
uvicorn hr_agent.hr_agent_be:app --reload
```

Backend:

```
http://localhost:8000
```

Swagger:

```
http://localhost:8000/docs
```

---

# 💻 Run Frontend

```bash
streamlit run hr_agent/hr_agent_fe.py
```

Frontend:

```
http://localhost:8501
```

---

# 🔄 Workflow

1. Upload Resume PDF
2. Backend receives file
3. Agent analyzes resume
4. Agent calls `search_jobs`
5. Chroma retrieves relevant jobs
6. Gemini compares candidate vs jobs
7. Returns Top 3 matches
8. Stream results to UI

---

# 🤖 Agent Responsibilities

The AI Agent:

- Analyze resume
- Search vector database
- Compare qualifications
- Calculate match score
- Explain reasoning
- Identify missing skills
- Suggest improvements

---

# 📦 API

## GET /health

```json
{
  "status":"ok",
  "message":"System is running normally"
}
```

## POST /find_jobs

Input:

- multipart/form-data
- PDF Resume

Output:

- Server-Sent Events

---

# 📊 Returned Result

```json
{
  "matches":[
    {
      "job_title":"Software Engineer",
      "match_score":88,
      "reasoning":"...",
      "strengths":["Python","FastAPI"],
      "missing_skills":["GCP"],
      "improvement_tips":"Learn Google Cloud."
    }
  ]
}
```

---

# 🌟 Highlights

- Modular architecture
- Async crawling
- Async FastAPI
- Streaming responses
- Structured AI output
- Vector search
- Tool Calling
- Production-friendly separation of concerns

---

# 🛣️ Roadmap

- [x] Job crawler
- [x] Vector database
- [x] LangChain Agent
- [x] Resume matching
- [x] FastAPI backend
- [x] Streamlit frontend
- [ ] Authentication
- [ ] Docker
- [ ] CI/CD
- [ ] Cloud deployment
- [ ] Multi-job websites
- [ ] Resume history
- [ ] User accounts

---

# 📜 License

MIT License

---

# 👨‍💻 Author

Developed as an AI Engineering portfolio project demonstrating:

- AI Agents
- Retrieval-Augmented Generation (RAG)
- Semantic Search
- LLM Tool Calling
- FastAPI
- Streamlit
- Vector Databases
- Production-oriented Python engineering

If you find this project useful, consider giving it a ⭐ on GitHub.

---

# 📄 License

This project is licensed under the **MIT License**.

You are free to use, modify, and distribute this project in accordance with the terms of the MIT License.

This project was developed primarily for **educational purposes**, **learning**, and **portfolio demonstration**.

See the [LICENSE](LICENSE) file for more details.