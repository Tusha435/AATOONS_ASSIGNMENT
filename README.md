# Mental Wellness Q&A Agent with LangGraph and RAG

A conversational AI agent built with LangGraph that helps users with mental wellness queries using Retrieval-Augmented Generation (RAG). The agent provides empathetic, context-aware responses about daily emotional wellness, coping strategies, and reflection practices.

## How It Works

### Agent Architecture

The agent implements a **4-node LangGraph workflow** that processes queries through distinct stages:

```
User Question → PLAN → RETRIEVE → ANSWER → REFLECT → Final Answer
```

1. **PLAN Node**: Analyzes the user's question using an LLM to determine if retrieval from the knowledge base is necessary. This prevents unnecessary database queries for out-of-scope questions.

2. **RETRIEVE Node**: If retrieval is needed, performs semantic search on the ChromaDB vector database to find the top-3 most relevant document chunks using OpenAI embeddings (text-embedding-3-small).

3. **ANSWER Node**: Generates a compassionate, contextually-aware response using GPT-4o-mini, incorporating the retrieved context and maintaining an empathetic tone suitable for mental wellness discussions.

4. **REFLECT Node**: Acts as a quality control layer, evaluating whether the generated answer is relevant, appropriate, helpful, and complete. This self-validation step ensures response quality.

### RAG System

The RAG (Retrieval-Augmented Generation) system consists of:

- **Knowledge Base**: Text files containing mental wellness information about daily reflection, emotional support, and coping strategies
- **Vector Storage**: ChromaDB for efficient similarity search with persistence
- **Embeddings**: OpenAI's text-embedding-3-small model for semantic understanding
- **Retrieval**: Similarity search with configurable top-k results

### Evaluation

The system includes comprehensive evaluation using the **RAGAs framework**, measuring:

- **Faithfulness**: Factual consistency with retrieved context
- **Answer Relevancy**: How well the answer addresses the question
- **Context Precision**: Accuracy of retrieved documents
- **Context Recall**: Completeness of retrieved information
- **Answer Similarity**: Semantic similarity to ground truth
- **Answer Correctness**: Overall quality combining multiple factors

## Project Structure

```
AATOONS_ASSIGNMENT/
├── knowledge_base/              # Mental wellness knowledge base
│   ├── daily_wellness.txt
│   ├── emotional_support.txt
│   └── coping_strategies.txt
├── chroma_db/                   # Vector database (auto-created)
├── agent.py                     # Main LangGraph agent
├── rag_system.py               # RAG implementation
├── streamlit_app.py            # Interactive UI
├── evaluation.py               # Evaluation script
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- OpenAI API key
- (Optional) LangSmith API key for tracing

### Installation

1. **Clone or download this repository**

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

   Or export directly:
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

5. **(Optional) Enable LangSmith tracing**:
   ```bash
   export LANGCHAIN_TRACING_V2=true
   export LANGCHAIN_API_KEY='your-langsmith-api-key'
   export LANGCHAIN_PROJECT='mental-wellness-agent'
   ```

## Usage

### 1. Run the Agent (Command Line)

Test the agent with example questions:

```bash
python agent.py
```

This will run the agent on three test questions and show the complete workflow through all four nodes.

### 2. Run the Streamlit UI (Interactive)

Launch the interactive web interface:

```bash
streamlit run streamlit_app.py
```

Then open your browser to `http://localhost:8501`

Features:
- Interactive question input
- Sample questions sidebar
- Workflow visualization
- Conversation history
- Retrieved documents viewer

### 3. Run Evaluation

Evaluate the agent's performance:

```bash
python evaluation.py
```

This will:
- Run the agent on 6 test cases
- Calculate RAGAs metrics
- Generate evaluation reports (CSV and TXT files)
- Display comprehensive scores

## Example Queries

- "How is your day, tell me all about it?"
- "I'm having a stressful day at work, what should I do?"
- "What are healthy ways to process my emotions?"
- "How can I reflect on my daily experiences?"
- "I'm feeling anxious today"

## Technical Implementation Details

### LangGraph Workflow

The agent uses LangGraph's `StateGraph` to define a stateful workflow. Each node receives the current state, performs its operation, and returns an updated state. This enables:

- **State persistence** across nodes
- **Conditional routing** (planned but not yet implemented)
- **Debugging and visualization** of the workflow
- **Easy modification** and extension

### RAG Pipeline

1. **Document Loading**: Uses LangChain's DirectoryLoader to load .txt files
2. **Text Splitting**: RecursiveCharacterTextSplitter creates 500-character chunks with 50-character overlap
3. **Embedding**: OpenAI's text-embedding-3-small generates 1536-dimensional vectors
4. **Storage**: ChromaDB stores embeddings with automatic persistence
5. **Retrieval**: Similarity search returns top-k most relevant chunks
6. **Context Formatting**: Retrieved chunks are formatted for LLM consumption

### Key Features

- ✅ **LangGraph orchestration** with 4-node workflow
- ✅ **RAG implementation** using ChromaDB and OpenAI
- ✅ **Streamlit UI** for interactive Q&A
- ✅ **RAGAs evaluation** for comprehensive metrics
- ✅ **LangSmith integration** (optional) for tracing
- ✅ **Detailed logging** at each workflow step
- ✅ **Self-reflection** for answer validation

## Challenges Faced

### 1. State Management in LangGraph
**Challenge**: Properly structuring the state to pass through all nodes while maintaining type safety.

**Solution**: Used TypedDict to define a clear state schema that includes all necessary fields (question, retrieved_docs, context, answer, reflection, etc.). This ensures type consistency across nodes.

### 2. Balancing Context Window Size
**Challenge**: Retrieved documents can be lengthy, potentially exceeding LLM context limits or degrading response quality.

**Solution**: Implemented chunk size of 500 characters with 50-character overlap, and limited retrieval to top-3 most relevant chunks. This balances information richness with context efficiency.

### 3. Evaluation Metric Selection
**Challenge**: Determining which metrics best evaluate mental wellness responses, where empathy and appropriateness matter as much as factual accuracy.

**Solution**: Selected RAGAs framework which includes multiple complementary metrics (faithfulness, relevancy, precision, recall, similarity, correctness) providing a holistic evaluation rather than a single score.

### 4. Knowledge Base Curation
**Challenge**: Creating a knowledge base that's comprehensive enough for meaningful responses but focused enough for accurate retrieval.

**Solution**: Developed three targeted documents covering daily wellness practices, emotional support, and coping strategies. This provides sufficient coverage while maintaining retrieval precision.

## Future Enhancements

- Add conditional routing based on question type or complexity
- Implement conversation memory for multi-turn dialogues
- Expand knowledge base with more mental wellness topics
- Add user feedback collection for continuous improvement
- Implement caching for frequently asked questions
- Add support for PDF documents in knowledge base

## Requirements

See `requirements.txt` for complete list. Key dependencies:

- `langgraph==0.2.58` - Agent orchestration
- `langchain==0.3.13` - RAG components
- `langchain-openai==0.2.14` - OpenAI integration
- `chromadb==0.5.23` - Vector database
- `streamlit==1.41.1` - Web UI
- `ragas==0.2.9` - Evaluation framework
- `openai==1.59.3` - OpenAI API client

## License

This project is created for educational and demonstration purposes.

## Author

Created as part of the AATOONS AI Agent Development Assignment.

---

**Note**: This agent is designed for educational purposes and should not replace professional mental health services. If you're experiencing a mental health crisis, please contact a qualified mental health professional or crisis helpline.
