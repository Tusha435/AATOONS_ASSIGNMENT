"""
Streamlit UI for Mental Wellness Q&A Agent
Interactive interface for asking questions to the agent
"""

import streamlit as st
import os
from agent import MentalWellnessAgent
import time


# Page configuration
st.set_page_config(
    page_title="Mental Wellness Q&A Bot",
    page_icon="🧠",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #4A90E2;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4A90E2;
        color: white;
    }
    .step-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)


@st.cache_resource
def initialize_agent():
    """Initialize and cache the agent instance."""
    agent = MentalWellnessAgent()
    agent.initialize_rag(force_reload=False)
    agent.build_graph()
    return agent


def display_workflow_step(step_name: str, content: str, icon: str):
    """Display a workflow step in a nice format."""
    with st.expander(f"{icon} {step_name}", expanded=False):
        st.write(content)


def main():
    # Header
    st.markdown('<h1 class="main-header">🧠 Mental Wellness Q&A Bot</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Ask me about your day, emotional wellness, or coping strategies</p>', unsafe_allow_html=True)

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        st.error("⚠️ OPENAI_API_KEY not found in environment variables")
        st.info("Please set your OpenAI API key as an environment variable before running the app.")
        st.code("export OPENAI_API_KEY='your-key-here'")
        st.stop()

    # Initialize agent
    with st.spinner("Initializing agent..."):
        try:
            agent = initialize_agent()
            st.success("✓ Agent initialized successfully!")
        except Exception as e:
            st.error(f"Error initializing agent: {str(e)}")
            st.stop()

    # Sidebar with information
    with st.sidebar:
        st.header("About")
        st.info("""
        This is an AI-powered mental wellness assistant that uses:
        - **LangGraph** for workflow orchestration
        - **RAG** for retrieving relevant context
        - **ChromaDB** for vector storage
        - **OpenAI** for embeddings and generation
        """)

        st.header("How it works")
        st.write("""
        1. **Plan**: Analyzes your question
        2. **Retrieve**: Finds relevant information
        3. **Answer**: Generates a response
        4. **Reflect**: Validates the answer
        """)

        st.header("Sample Questions")
        sample_questions = [
            "How is your day, tell me all about it",
            "I'm feeling stressed today",
            "What are healthy ways to process my emotions?",
            "How can I reflect on my daily experiences?",
            "I had a challenging day at work"
        ]

        for q in sample_questions:
            if st.button(q, key=f"sample_{q}"):
                st.session_state.selected_question = q

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("Ask a Question")

        # Check if a sample question was selected
        default_question = st.session_state.get("selected_question", "")

        question = st.text_area(
            "Your question:",
            value=default_question,
            height=100,
            placeholder="How is your day? Tell me all about it..."
        )

        # Clear the selected question after using it
        if default_question:
            st.session_state.selected_question = ""

        col_button1, col_button2 = st.columns([1, 1])
        with col_button1:
            submit_button = st.button("🚀 Ask Question", type="primary")
        with col_button2:
            show_details = st.checkbox("Show workflow details", value=False)

    with col2:
        st.header("Quick Stats")
        if 'history' not in st.session_state:
            st.session_state.history = []

        st.metric("Questions Asked", len(st.session_state.history))

    # Process question
    if submit_button and question:
        with st.spinner("🤔 Processing your question..."):
            try:
                # Create a container for the workflow
                workflow_container = st.container()

                with workflow_container:
                    if show_details:
                        st.subheader("Workflow Progress")

                        # Create placeholders for each step
                        plan_placeholder = st.empty()
                        retrieve_placeholder = st.empty()
                        answer_placeholder = st.empty()
                        reflect_placeholder = st.empty()

                    # Run the agent
                    result = agent.run(question)

                    # Display workflow steps if requested
                    if show_details:
                        with plan_placeholder:
                            display_workflow_step(
                                "Step 1: Plan",
                                f"**Needs Retrieval:** {'Yes' if result['needs_retrieval'] else 'No'}\n\n"
                                f"The agent analyzed your question to determine if it needs to search the knowledge base.",
                                "🎯"
                            )

                        with retrieve_placeholder:
                            if result['needs_retrieval']:
                                docs_info = f"Retrieved {len(result['retrieved_docs'])} relevant documents from the knowledge base."
                            else:
                                docs_info = "No retrieval needed for this question."
                            display_workflow_step(
                                "Step 2: Retrieve",
                                docs_info,
                                "📚"
                            )

                        with answer_placeholder:
                            display_workflow_step(
                                "Step 3: Answer",
                                "Generated response using retrieved context and LLM.",
                                "💬"
                            )

                        with reflect_placeholder:
                            relevance_icon = "✅" if result['is_relevant'] else "⚠️"
                            display_workflow_step(
                                "Step 4: Reflect",
                                f"**Relevance:** {relevance_icon}\n\n{result['reflection']}",
                                "🔍"
                            )

                # Display the final answer
                st.markdown("---")
                st.subheader("💡 Answer")
                st.markdown(f"<div style='background-color: #e8f4f8; padding: 1.5rem; border-radius: 0.5rem; border-left: 4px solid #4A90E2;'>{result['answer']}</div>", unsafe_allow_html=True)

                # Add to history
                st.session_state.history.append({
                    "question": question,
                    "answer": result["answer"],
                    "is_relevant": result["is_relevant"]
                })

                # Show retrieved documents if available
                if show_details and result.get('retrieved_docs'):
                    with st.expander("📄 Retrieved Documents", expanded=False):
                        for i, doc in enumerate(result['retrieved_docs'], 1):
                            st.markdown(f"**Document {i}**")
                            st.text(f"Source: {doc['metadata'].get('source', 'Unknown')}")
                            st.text(f"Similarity: {doc['similarity_score']:.4f}")
                            st.text_area(f"Content {i}", doc['content'], height=150, key=f"doc_{i}")
                            st.markdown("---")

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.exception(e)

    # Conversation history
    if st.session_state.history:
        st.markdown("---")
        st.header("📜 Conversation History")

        for i, item in enumerate(reversed(st.session_state.history[-5:]), 1):
            relevance_icon = "✅" if item["is_relevant"] else "⚠️"
            with st.expander(f"{relevance_icon} Q{len(st.session_state.history) - i + 1}: {item['question'][:60]}...", expanded=False):
                st.markdown(f"**Question:** {item['question']}")
                st.markdown(f"**Answer:** {item['answer']}")


if __name__ == "__main__":
    main()
