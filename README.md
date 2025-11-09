# AI Projects Repository

This repository contains **two separate AI projects**, each solving different real-world problems.

---

## 📂 Projects

### 1. Mental Wellness Q&A Agent 🧠
**Location**: [`mental-wellness-agent/`](mental-wellness-agent/)

An AI agent that provides empathetic mental wellness support using LangGraph and RAG.

**Tech Stack**: LangGraph, LangChain, ChromaDB, OpenAI, Streamlit

**Quick Start**:
```bash
cd mental-wellness-agent
pip install -r requirements.txt
export OPENAI_API_KEY='your-key'
streamlit run streamlit_app.py
```

[**→ Full Documentation**](mental-wellness-agent/PROJECT_SUMMARY.md)

---

### 2. Proof-of-Work Hiring Platform 💼
**Location**: [`hiring-platform/`](hiring-platform/)

A hiring platform where both candidates and HR prove themselves through actual work.

**Tech Stack**: FastAPI, PostgreSQL, Redis, OpenAI GPT-4, SQLAlchemy, Docker

**Quick Start**:
```bash
cd hiring-platform
docker-compose up -d
# Access: http://localhost:8000/docs
```

[**→ Full Documentation**](hiring-platform/PLATFORM_SUMMARY.md)

---

## 🎯 Project Comparison

| Aspect | Mental Wellness Agent | Hiring Platform |
|--------|----------------------|-----------------|
| **Domain** | Mental health support | Technical hiring |
| **Architecture** | LangGraph workflow | FastAPI + microservices |
| **AI Role** | Conversational assistant | Code reviewer + evaluator |
| **Database** | ChromaDB (vectors) | PostgreSQL + Redis |
| **UI** | Streamlit | API-first |
| **Innovation** | RAG-powered empathy | Mutual accountability |

---

## 📁 Repository Structure

```
ASSIGNMENT_NOV_1/
│
├── mental-wellness-agent/     # Project 1
│   ├── agent.py
│   ├── rag_system.py
│   ├── streamlit_app.py
│   ├── knowledge_base/
│   └── requirements.txt
│
├── hiring-platform/           # Project 2
│   ├── app/
│   │   ├── core/
│   │   ├── models/
│   │   └── services/
│   ├── docker-compose.yml
│   └── requirements-platform.txt
│
└── README.md                  # This file
```

---

## 📚 Documentation

### Mental Wellness Agent
- [README](mental-wellness-agent/README.md)
- [PROJECT_SUMMARY](mental-wellness-agent/PROJECT_SUMMARY.md)
- [QUICKSTART](mental-wellness-agent/QUICKSTART.md)

### Hiring Platform
- [README](hiring-platform/README.md)
- [PLATFORM_SUMMARY](hiring-platform/PLATFORM_SUMMARY.md)
- [ARCHITECTURE](hiring-platform/ARCHITECTURE.md)
- [DATABASE_SCHEMA](hiring-platform/DATABASE_SCHEMA.md)
- [CODEBASE_STRUCTURE](hiring-platform/CODEBASE_STRUCTURE.md)

---

**Two different problems. Two AI-powered solutions. One repository.**
