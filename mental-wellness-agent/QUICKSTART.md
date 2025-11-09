# Quick Start Guide

Get up and running with the Mental Wellness Q&A Agent in 5 minutes!

## Prerequisites

- Python 3.9+
- OpenAI API Key ([Get one here](https://platform.openai.com/api-keys))

## Setup (Option 1: Automated)

```bash
# Run the setup script
./setup.sh

# Activate virtual environment
source venv/bin/activate

# Set your API key
export OPENAI_API_KEY='your-api-key-here'
```

## Setup (Option 2: Manual)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set API key
export OPENAI_API_KEY='your-api-key-here'
```

## Run the Agent

### 1. Command Line Demo

```bash
python agent.py
```

This will run the agent on example questions and show the complete workflow.

### 2. Interactive UI (Recommended)

```bash
streamlit run streamlit_app.py
```

Then open http://localhost:8501 in your browser.

### 3. Run Evaluation

```bash
python evaluation.py
```

This evaluates the agent using RAGAs metrics and generates detailed reports.

## Example Questions to Try

1. "How is your day, tell me all about it?"
2. "I'm feeling stressed today, what can I do?"
3. "What are healthy ways to process emotions?"
4. "How can I reflect on my daily experiences?"

## Troubleshooting

### "OPENAI_API_KEY not found"
Make sure you've exported the environment variable:
```bash
export OPENAI_API_KEY='your-key-here'
```

### Import errors
Make sure you've activated the virtual environment:
```bash
source venv/bin/activate
```

### ChromaDB errors
Delete the chroma_db folder and let it recreate:
```bash
rm -rf chroma_db
python agent.py
```

## Project Structure

```
├── agent.py              # Main LangGraph agent
├── rag_system.py        # RAG with ChromaDB
├── streamlit_app.py     # Interactive UI
├── evaluation.py        # Evaluation script
├── knowledge_base/      # Mental wellness docs
└── requirements.txt     # Dependencies
```

## What Happens on First Run?

1. The RAG system loads documents from `knowledge_base/`
2. Creates embeddings using OpenAI
3. Stores vectors in ChromaDB (in `chroma_db/` folder)
4. On subsequent runs, it loads the existing database

## Optional: Enable LangSmith Tracing

Track and debug your agent runs:

```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY='your-langsmith-key'
export LANGCHAIN_PROJECT='mental-wellness-agent'
```

View traces at https://smith.langchain.com/

## Need Help?

Check the full README.md for detailed documentation and architecture explanation.

---

**Ready to go!** Start with the Streamlit UI for the best experience:
```bash
streamlit run streamlit_app.py
```
