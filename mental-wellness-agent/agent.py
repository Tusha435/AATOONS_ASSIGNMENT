"""
Mental Wellness Q&A Agent using LangGraph
Implements a 4-node workflow: plan -> retrieve -> answer -> reflect
"""

import os
from typing import TypedDict, Annotated, List, Dict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from rag_system import RAGSystem, initialize_rag_system


# Define the state structure for the agent
class AgentState(TypedDict):
    """State object that passes through all nodes in the graph."""
    question: str
    needs_retrieval: bool
    retrieved_docs: List[Dict]
    context: str
    answer: str
    reflection: str
    is_relevant: bool


class MentalWellnessAgent:
    """LangGraph-based agent for mental wellness Q&A with RAG."""

    def __init__(self, model_name: str = "gpt-4o-mini"):
        """
        Initialize the agent with LLM and RAG system.

        Args:
            model_name: OpenAI model to use
        """
        self.llm = ChatOpenAI(model=model_name, temperature=0.7)
        self.rag_system: RAGSystem = None
        self.graph = None

    def initialize_rag(self, force_reload: bool = False):
        """Initialize the RAG system."""
        print("Initializing RAG system...")
        self.rag_system = initialize_rag_system(force_reload=force_reload)
        print("RAG system initialized\n")

    def plan_node(self, state: AgentState) -> AgentState:
        """
        Node 1: Plan - Analyze the question and decide if retrieval is needed.
        """
        print("\n" + "="*70)
        print("NODE 1: PLAN")
        print("="*70)

        question = state["question"]
        print(f"Question: {question}")

        # Create prompt to analyze if retrieval is needed
        plan_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a planning agent for a mental wellness Q&A system.
Your job is to analyze the user's question and decide if we need to retrieve information from the knowledge base.

Respond with ONLY 'YES' or 'NO' followed by a brief reason.

Examples:
- "How is your day?" -> YES - This is about daily wellness and emotional check-ins
- "What is the capital of France?" -> NO - This is not related to mental wellness
- "I'm feeling stressed" -> YES - This relates to mental wellness and coping
"""),
            ("user", "Question: {question}\n\nDoes this question need retrieval from our mental wellness knowledge base?")
        ])

        response = self.llm.invoke(plan_prompt.format_messages(question=question))
        response_text = response.content.strip()

        # Parse response
        needs_retrieval = response_text.upper().startswith("YES")

        print(f"Planning decision: {'NEEDS RETRIEVAL' if needs_retrieval else 'NO RETRIEVAL NEEDED'}")
        print(f"Reasoning: {response_text}")

        state["needs_retrieval"] = needs_retrieval
        return state

    def retrieve_node(self, state: AgentState) -> AgentState:
        """
        Node 2: Retrieve - Perform RAG to get relevant context.
        """
        print("\n" + "="*70)
        print("NODE 2: RETRIEVE")
        print("="*70)

        if not state["needs_retrieval"]:
            print("Skipping retrieval (not needed based on plan)")
            state["retrieved_docs"] = []
            state["context"] = ""
            return state

        question = state["question"]

        # Retrieve relevant documents
        retrieved_docs = self.rag_system.retrieve_documents(question, k=3)
        context = self.rag_system.format_context(retrieved_docs)

        state["retrieved_docs"] = retrieved_docs
        state["context"] = context

        print(f"\nRetrieved {len(retrieved_docs)} documents")
        return state

    def answer_node(self, state: AgentState) -> AgentState:
        """
        Node 3: Answer - Generate response using LLM and retrieved context.
        """
        print("\n" + "="*70)
        print("NODE 3: ANSWER")
        print("="*70)

        question = state["question"]
        context = state.get("context", "")

        # Create answer prompt
        if state["needs_retrieval"] and context:
            answer_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a compassionate mental wellness assistant.
Use the provided context from the knowledge base to answer the user's question.
Be empathetic, supportive, and encouraging. If the user is sharing about their day,
respond in a warm and understanding manner.

Context from knowledge base:
{context}
"""),
                ("user", "{question}")
            ])
            messages = answer_prompt.format_messages(context=context, question=question)
        else:
            # No context needed or available
            answer_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a compassionate mental wellness assistant.
Answer the user's question with empathy and support."""),
                ("user", "{question}")
            ])
            messages = answer_prompt.format_messages(question=question)

        print("Generating answer with LLM...")
        response = self.llm.invoke(messages)
        answer = response.content.strip()

        state["answer"] = answer
        print(f"\nAnswer generated ({len(answer)} characters)")
        return state

    def reflect_node(self, state: AgentState) -> AgentState:
        """
        Node 4: Reflect - Evaluate if the answer is relevant and complete.
        """
        print("\n" + "="*70)
        print("NODE 4: REFLECT")
        print("="*70)

        question = state["question"]
        answer = state["answer"]

        # Create reflection prompt
        reflect_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a quality control agent. Evaluate if the answer is:
1. Relevant to the question
2. Appropriate for mental wellness context
3. Helpful and supportive
4. Complete and coherent

Provide your evaluation as:
- RELEVANT or NOT_RELEVANT
- Brief explanation of your assessment
- Any suggestions for improvement (if applicable)
"""),
            ("user", """Question: {question}

Answer: {answer}

Evaluate this answer:""")
        ])

        response = self.llm.invoke(reflect_prompt.format_messages(
            question=question,
            answer=answer
        ))
        reflection = response.content.strip()

        is_relevant = "RELEVANT" in reflection.split('\n')[0].upper() and "NOT_RELEVANT" not in reflection.split('\n')[0].upper()

        state["reflection"] = reflection
        state["is_relevant"] = is_relevant

        print(f"Relevance: {'✓ RELEVANT' if is_relevant else '✗ NOT RELEVANT'}")
        print(f"Reflection:\n{reflection}")

        return state

    def build_graph(self):
        """Build the LangGraph workflow."""
        print("Building LangGraph workflow...")

        # Create the graph
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("plan", self.plan_node)
        workflow.add_node("retrieve", self.retrieve_node)
        workflow.add_node("answer", self.answer_node)
        workflow.add_node("reflect", self.reflect_node)

        # Define edges (workflow)
        workflow.set_entry_point("plan")
        workflow.add_edge("plan", "retrieve")
        workflow.add_edge("retrieve", "answer")
        workflow.add_edge("answer", "reflect")
        workflow.add_edge("reflect", END)

        # Compile the graph
        self.graph = workflow.compile()
        print("Graph built successfully\n")

    def run(self, question: str) -> Dict:
        """
        Run the agent on a question.

        Args:
            question: User's question

        Returns:
            Final state with answer and reflection
        """
        if self.graph is None:
            raise ValueError("Graph not built. Call build_graph() first.")

        print("\n" + "🤖 " + "="*68)
        print("MENTAL WELLNESS Q&A AGENT - Starting Workflow")
        print("="*70)

        # Initialize state
        initial_state = {
            "question": question,
            "needs_retrieval": False,
            "retrieved_docs": [],
            "context": "",
            "answer": "",
            "reflection": "",
            "is_relevant": False
        }

        # Run the graph
        final_state = self.graph.invoke(initial_state)

        print("\n" + "="*70)
        print("✓ WORKFLOW COMPLETE")
        print("="*70)

        return final_state


def main():
    """Main function to demonstrate the agent."""
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set it using: export OPENAI_API_KEY='your-key-here'")
        return

    # Initialize agent
    print("Initializing Mental Wellness Q&A Agent...")
    agent = MentalWellnessAgent()

    # Initialize RAG system
    agent.initialize_rag(force_reload=False)

    # Build the graph
    agent.build_graph()

    # Test questions
    test_questions = [
        "How is your day, tell me all about it",
        "I'm having a stressful day at work, what should I do?",
        "What are some good ways to reflect on my daily experiences?"
    ]

    for i, question in enumerate(test_questions, 1):
        print(f"\n\n{'#'*70}")
        print(f"# EXAMPLE {i}")
        print(f"{'#'*70}")

        result = agent.run(question)

        # Print final answer
        print("\n" + "📝 FINAL ANSWER:")
        print("-"*70)
        print(result["answer"])
        print("-"*70)

        if i < len(test_questions):
            input("\nPress Enter to continue to next example...")


if __name__ == "__main__":
    main()
