"""
Evaluation Script for Mental Wellness Q&A Agent
Uses RAGAs framework for comprehensive evaluation of RAG system
"""

import os
from typing import List, Dict
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
    answer_similarity,
    answer_correctness
)
from agent import MentalWellnessAgent
import pandas as pd
from datetime import datetime


class AgentEvaluator:
    """Evaluates the Mental Wellness Agent using RAGAs metrics."""

    def __init__(self):
        """Initialize the evaluator."""
        self.agent = None
        self.test_data = []
        self.results = None

    def initialize_agent(self):
        """Initialize the agent for evaluation."""
        print("Initializing agent for evaluation...")
        self.agent = MentalWellnessAgent()
        self.agent.initialize_rag(force_reload=False)
        self.agent.build_graph()
        print("Agent initialized successfully\n")

    def create_test_dataset(self) -> List[Dict]:
        """
        Create test dataset with questions, ground truth answers, and contexts.

        Returns:
            List of test cases
        """
        test_cases = [
            {
                "question": "How is your day, tell me all about it?",
                "ground_truth": "It's important to reflect on your day by considering your emotions, energy levels, accomplishments, challenges, and interactions with others. Sharing about your day can be therapeutic and helps process emotions."
            },
            {
                "question": "What are healthy ways to process my emotions?",
                "ground_truth": "Healthy ways to process emotions include journaling, talking to someone trusted, mindful meditation, physical activity, and creative expression. These methods help you acknowledge and work through your feelings in a constructive manner."
            },
            {
                "question": "I'm having a stressful day at work, what should I do?",
                "ground_truth": "When having a stressful day, you can use coping techniques like deep breathing exercises, breaking tasks into smaller steps, taking short breaks, practicing mindfulness, and reaching out for support if needed. Be gentle with yourself and adjust expectations."
            },
            {
                "question": "How can I reflect on my daily experiences?",
                "ground_truth": "Daily reflection can be done through journaling, meditation, talking with others, or simply taking quiet time to think about your experiences. Focus on what made you happy, challenges you faced, accomplishments, and how you felt throughout the day."
            },
            {
                "question": "What should I do on days when I feel neither good nor bad?",
                "ground_truth": "Neutral or 'meh' days are completely normal. On these days, recognize that emotional variety is part of being human, maintain your routine and self-care practices, find small moments of joy or peace, and don't pressure yourself to feel a certain way."
            },
            {
                "question": "Why is it important to talk about how my day went?",
                "ground_truth": "Talking about your day is therapeutic because it helps you process emotions, identify patterns in mood and behavior, celebrate positive moments, work through difficulties, and develop greater self-awareness. Expressing feelings is a healthy part of mental wellness."
            }
        ]

        return test_cases

    def run_agent_on_testset(self, test_cases: List[Dict]) -> List[Dict]:
        """
        Run the agent on test cases and collect results.

        Args:
            test_cases: List of test questions and ground truths

        Returns:
            List of results with questions, answers, contexts, and ground truths
        """
        print("Running agent on test dataset...")
        print("="*70)

        results = []

        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest Case {i}/{len(test_cases)}")
            print(f"Question: {test_case['question']}")

            # Run agent
            result = self.agent.run(test_case['question'])

            # Extract contexts from retrieved documents
            contexts = [doc['content'] for doc in result['retrieved_docs']] if result['retrieved_docs'] else []

            # Compile result
            eval_result = {
                "question": test_case['question'],
                "answer": result['answer'],
                "contexts": contexts,
                "ground_truth": test_case['ground_truth']
            }

            results.append(eval_result)

            print(f"Answer length: {len(result['answer'])} chars")
            print(f"Contexts retrieved: {len(contexts)}")
            print(f"Relevant: {'Yes' if result['is_relevant'] else 'No'}")

        print("\n" + "="*70)
        print(f"Completed {len(results)} test cases\n")

        return results

    def evaluate_with_ragas(self, results: List[Dict]) -> Dict:
        """
        Evaluate results using RAGAs metrics.

        Args:
            results: List of results from agent runs

        Returns:
            Dictionary containing evaluation scores
        """
        print("Evaluating with RAGAs metrics...")
        print("="*70)

        # Convert to dataset format for RAGAs
        dataset_dict = {
            "question": [r["question"] for r in results],
            "answer": [r["answer"] for r in results],
            "contexts": [r["contexts"] for r in results],
            "ground_truth": [r["ground_truth"] for r in results]
        }

        dataset = Dataset.from_dict(dataset_dict)

        # Define metrics to evaluate
        metrics = [
            faithfulness,           # Measures factual consistency with retrieved context
            answer_relevancy,       # Measures how relevant the answer is to the question
            context_precision,      # Measures precision of retrieved context
            context_recall,         # Measures recall of retrieved context
            answer_similarity,      # Semantic similarity between answer and ground truth
            answer_correctness      # Overall correctness combining similarity and faithfulness
        ]

        print("\nEvaluating the following metrics:")
        for metric in metrics:
            print(f"  - {metric.name}")

        # Run evaluation
        print("\nRunning evaluation (this may take a few minutes)...")
        evaluation_result = evaluate(
            dataset,
            metrics=metrics,
        )

        print("\n" + "="*70)
        print("EVALUATION RESULTS")
        print("="*70)

        # Print scores
        for metric_name, score in evaluation_result.items():
            print(f"{metric_name:.<30} {score:.4f}")

        return evaluation_result

    def save_results(self, results: List[Dict], evaluation_scores: Dict):
        """
        Save evaluation results to files.

        Args:
            results: Agent results
            evaluation_scores: RAGAs evaluation scores
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save detailed results as CSV
        df = pd.DataFrame(results)
        csv_filename = f"evaluation_results_{timestamp}.csv"
        df.to_csv(csv_filename, index=False)
        print(f"\n✓ Detailed results saved to: {csv_filename}")

        # Save evaluation scores
        scores_df = pd.DataFrame([evaluation_scores])
        scores_filename = f"evaluation_scores_{timestamp}.csv"
        scores_df.to_csv(scores_filename, index=False)
        print(f"✓ Evaluation scores saved to: {scores_filename}")

        # Save summary report
        report_filename = f"evaluation_report_{timestamp}.txt"
        with open(report_filename, 'w') as f:
            f.write("MENTAL WELLNESS Q&A AGENT - EVALUATION REPORT\n")
            f.write("="*70 + "\n\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Number of test cases: {len(results)}\n\n")

            f.write("RAGAS METRICS SCORES:\n")
            f.write("-"*70 + "\n")
            for metric_name, score in evaluation_scores.items():
                f.write(f"{metric_name:.<40} {score:.4f}\n")

            f.write("\n\nMETRIC DESCRIPTIONS:\n")
            f.write("-"*70 + "\n")
            f.write("faithfulness: Factual consistency with retrieved context (0-1)\n")
            f.write("answer_relevancy: How relevant the answer is to question (0-1)\n")
            f.write("context_precision: Precision of retrieved context (0-1)\n")
            f.write("context_recall: Recall of retrieved context (0-1)\n")
            f.write("answer_similarity: Semantic similarity to ground truth (0-1)\n")
            f.write("answer_correctness: Overall correctness score (0-1)\n")

            f.write("\n\nINTERPRETATION:\n")
            f.write("-"*70 + "\n")

            avg_score = sum(evaluation_scores.values()) / len(evaluation_scores)
            if avg_score >= 0.8:
                f.write("EXCELLENT: The agent is performing very well across all metrics.\n")
            elif avg_score >= 0.6:
                f.write("GOOD: The agent is performing well with room for improvement.\n")
            elif avg_score >= 0.4:
                f.write("FAIR: The agent needs improvement in several areas.\n")
            else:
                f.write("NEEDS IMPROVEMENT: The agent requires significant optimization.\n")

        print(f"✓ Evaluation report saved to: {report_filename}")

    def run_full_evaluation(self):
        """Run complete evaluation pipeline."""
        print("\n" + "🔬 "*35)
        print("MENTAL WELLNESS Q&A AGENT - COMPREHENSIVE EVALUATION")
        print("🔬 "*35 + "\n")

        # Initialize agent
        self.initialize_agent()

        # Create test dataset
        print("Creating test dataset...")
        test_cases = self.create_test_dataset()
        print(f"Created {len(test_cases)} test cases\n")

        # Run agent on test cases
        results = self.run_agent_on_testset(test_cases)

        # Evaluate with RAGAs
        evaluation_scores = self.evaluate_with_ragas(results)

        # Save results
        self.save_results(results, evaluation_scores)

        print("\n" + "="*70)
        print("✓ EVALUATION COMPLETE")
        print("="*70)

        return evaluation_scores


def main():
    """Main function to run evaluation."""
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set it using: export OPENAI_API_KEY='your-key-here'")
        return

    # Create evaluator and run evaluation
    evaluator = AgentEvaluator()
    scores = evaluator.run_full_evaluation()

    # Print summary
    print("\n" + "📊 SUMMARY")
    print("="*70)
    avg_score = sum(scores.values()) / len(scores)
    print(f"Average Score: {avg_score:.4f}")

    if avg_score >= 0.8:
        print("Rating: ⭐⭐⭐⭐⭐ EXCELLENT")
    elif avg_score >= 0.6:
        print("Rating: ⭐⭐⭐⭐ GOOD")
    elif avg_score >= 0.4:
        print("Rating: ⭐⭐⭐ FAIR")
    else:
        print("Rating: ⭐⭐ NEEDS IMPROVEMENT")


if __name__ == "__main__":
    main()
