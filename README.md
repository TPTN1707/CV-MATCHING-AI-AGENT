# CV-MATCHING-AI-AGENT

An AI-powered Resume Matching System that automatically analyzes a candidate's resume, retrieves relevant job postings from a vector database, and recommends the most suitable positions using an AI Agent built with LangChain and Google Gemini.

---

## Overview

Searching for a suitable job among hundreds of job postings can be time-consuming.

This project automates the process by combining:

- Resume understanding
- Semantic search (Vector Database)
- AI Agent reasoning
- Structured job recommendations

A user simply uploads a PDF resume, and the system:

1. Extracts the candidate's skills and experience.
2. Searches a vector database of job postings.
3. Compares the resume against relevant positions.
4. Returns the Top 3 best matching jobs.
5. Explains why each job is recommended.
6. Suggests missing skills and improvement tips.

---

## Demo Workflow

```text
                   Google Careers
                          │
                          ▼
                 Job Crawling Pipeline
                          │
                          ▼
                Gemini Embedding Model
                          │
                          ▼
                     ChromaDB
                          │
────────────────────────────────────────────────────────

                  Upload Resume (PDF)
                          │
                          ▼
                 Streamlit Frontend
                          │
                          ▼
                  FastAPI Backend
                          │
                          ▼
                  LangChain Agent
                          │
                          ▼
                  search_jobs Tool
                          │
                          ▼
                     ChromaDB Search
                          │
                          ▼
              Gemini 2.5 Flash Reasoning
                          │
                          ▼
             Structured Job Recommendations
                          │
                          ▼
                     Streamlit UI
```

---

# Features

## Resume Analysis

- Upload PDF resumes
- Automatic resume understanding using Gemini
- Extract candidate skills and experience

---

## AI Agent

Built with LangChain Agent.

The agent is capable of:

- understanding resumes
- calling tools autonomously
- performing semantic job search
- ranking matching jobs
- explaining recommendations

---

## Semantic Search

Job postings are stored inside ChromaDB.

Instead of keyword matching, the system performs semantic similarity search using embeddings.

Embedding model:

```
models/gemini-embedding-2
```

---

## Job Recommendation

For every recommended job, the AI returns:

- Job title
- Job URL
- Match score
- Candidate strengths
- Missing skills
- Recommendation reasoning
- Improvement suggestions

---

## Real-time Streaming

The backend streams progress to the frontend using Server-Sent Events (SSE).

Example progress:

```
Receiving resume...

Searching jobs...

Analyzing candidate...

Generating recommendations...

Completed.
```

---

# Tech Stack

## AI

- Google Gemini 2.5 Flash
- Gemini Embedding 2
- LangChain
- LangGraph

---

## Backend

- FastAPI
- Uvicorn
- Server-Sent Events (SSE)

---

## Frontend

- Streamlit

---

## Vector Database

- ChromaDB

---

## Web Crawling

- httpx
- BeautifulSoup4
- asyncio

---

# Project Structure

```
CV-MATCHING-AI-AGENT
│
├── chroma_db/
│
├── hr_agent/
│   ├── hr_agent.py
│   ├── hr_agent_tools.py
│   ├── hr_agent_format.py
│   ├── hr_agent_be.py
│   └── hr_agent_fe.py
│
├── job_craws.py
│
├── requirements.txt
├── .env
└── README.md
```

---

# Components

## job_craws.py

Responsible for building the vector database.

Functions:

- Crawl Google Careers
- Extract job descriptions
- Clean HTML
- Generate embeddings
- Store vectors in ChromaDB

---

## hr_agent_tools.py

Contains LangChain tools.

Current tool:

```
search_jobs()
```

Responsibilities:

- Query ChromaDB
- Perform semantic search
- Return structured job documents

---

## hr_agent_format.py

Defines structured outputs using Pydantic.

Models include:

- JobMatch
- MatchResponse

---

## hr_agent.py

Core AI Agent.

Responsibilities:

- Configure Gemini model
- Register tools
- Build LangChain Agent
- Define system prompt
- Produce structured outputs

---

## hr_agent_be.py

FastAPI backend.

Responsibilities:

- Receive uploaded resumes
- Send resume to the AI Agent
- Stream execution progress
- Return structured recommendations

---

## hr_agent_fe.py

Streamlit frontend.

Features:

- Dark UI
- PDF upload
- Live progress
- Recommendation cards
- Expandable details

---

# AI Agent Workflow

```
Resume
   │
   ▼
Gemini understands resume
   │
   ▼
search_jobs()
   │
   ▼
Vector Search
   │
   ▼
Relevant Jobs
   │
   ▼
Gemini compares
   │
   ▼
Top 3 Matches
```

---

# Installation

## Clone repository

```bash
git clone https://github.com/your_username/CV-MATCHING-AI-AGENT.git

cd CV-MATCHING-AI-AGENT
```

---

## Create virtual environment

```bash
uv venv

source .venv/bin/activate
```

Windows

```bash
.venv\Scripts\activate
```

---

## Install dependencies

```bash
uv pip install -r requirements.txt
```

---

## Configure environment variables

Create a `.env` file.

```env
GOOGLE_API_KEY=YOUR_API_KEY
```

---

# Build the Vector Database

Run

```bash
python job_craws.py
```

The script will:

- Crawl Google Careers
- Generate embeddings
- Build ChromaDB

---

# Start Backend

```bash
python hr_agent/hr_agent_be.py
```

or

```bash
uvicorn hr_agent.hr_agent_be:app --reload
```

---

# Start Frontend

```bash
streamlit run hr_agent/hr_agent_fe.py
```

---

# API

## Health Check

```
GET /health
```

Response

```json
{
  "status": "ok",
  "message": "System is running normally"
}
```

---

## Find Jobs

```
POST /find_jobs
```

Form Data

```
resume
```

Type

```
application/pdf
```

Returns

Server-Sent Events (SSE)

---

# Example Output

```json
{
  "matches": [
    {
      "job_title": "...",
      "match_score": 91,
      "reasoning": "...",
      "strengths": [],
      "missing_skills": [],
      "improvement_tips": "...",
      "job_url": "..."
    }
  ]
}
```

---

# Future Improvements

- Support multiple job websites (LinkedIn, Indeed, VietnamWorks, TopCV, etc.)
- Hybrid search (semantic + keyword search)
- Automatic daily job crawling
- Resume parsing with OCR
- User authentication
- Docker deployment
- Kubernetes deployment
- Redis caching
- PostgreSQL integration
- Job bookmarking
- Match history
- Multi-language support
- Email notifications

---

# Author

**Tran Pham Trong Nhan**

AI / Machine Learning Enthusiast

GitHub:
https://github.com/TPTN1707

---

# License

This project is intended for educational and portfolio purposes.