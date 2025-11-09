# Mental Wellness Q&A Agent with LangGraph and RAG

A conversational AI agent built with LangGraph that helps users with mental wellness queries using Retrieval-Augmented Generation (RAG).

## 🎯 Overview

This project implements a **4-node LangGraph workflow**:

```
User Question → PLAN → RETRIEVE → ANSWER → REFLECT → Final Answer
```

## 🚀 Quick Start

```bash
cd mental-wellness-agent

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set API key
export OPENAI_API_KEY='your-key-here'

# Run
streamlit run streamlit_app.py
```

## 📁 Project Files

- `agent.py` - Main LangGraph agent
- `rag_system.py` - RAG with ChromaDB
- `streamlit_app.py` - Interactive UI
- `evaluation.py` - RAGAs evaluation
- `knowledge_base/` - Mental wellness documents

## 📚 Full Documentation

See **PROJECT_SUMMARY.md** for complete details.

---

**AATOONS AI Agent Development Assignment**
