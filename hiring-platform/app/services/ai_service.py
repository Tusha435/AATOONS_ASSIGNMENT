"""
AI Code Analysis Service

Uses GPT-4 and other AI models to:
- Evaluate code quality and architecture
- Detect AI-generated vs human-written code
- Provide detailed technical reviews
- Compare HR evaluations against AI assessments
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from openai import OpenAI
from sqlalchemy.orm import Session

from app.models import (
    ProjectSubmission, AIAnalysis, Evaluation,
    CodeQualityMetric, HRvsAIComparison
)
from app.core.database import get_db_context


class AICodeAnalysisService:
    """
    AI-powered code analysis service.

    This is the "objective referee" that evaluates both:
    1. Candidate code quality
    2. HR evaluation quality (by comparing HR assessment to AI assessment)
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI analysis service.

        Args:
            api_key: OpenAI API key
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4-turbo-preview"  # or "gpt-4o" for latest

    def analyze_code_architecture(
        self,
        code_files: Dict[str, str],
        architecture_doc: str,
        project_description: str
    ) -> Dict:
        """
        Analyze code architecture and design decisions.

        Args:
            code_files: Dictionary of {filename: code_content}
            architecture_doc: Candidate's architecture explanation
            project_description: What the project is supposed to do

        Returns:
            Architecture analysis with scores and insights
        """
        # Prepare code context (limit to key files to avoid token limits)
        code_context = "\n\n".join([
            f"### {filename}\n```\n{content[:2000]}\n```"  # Truncate long files
            for filename, content in list(code_files.items())[:10]  # Max 10 files
        ])

        prompt = f"""
You are an expert software architect evaluating a candidate's project submission.

**Project Description:**
{project_description}

**Candidate's Architecture Explanation:**
{architecture_doc}

**Code Sample:**
{code_context}

Please provide a comprehensive technical review covering:

1. **Architecture Quality (0-100)**: Rate the overall system design
   - Are design patterns used appropriately?
   - Is the code well-structured and maintainable?
   - Are concerns properly separated?

2. **Production Readiness (0-100)**: How deployment-ready is this code?
   - Error handling
   - Input validation
   - Security considerations
   - Scalability

3. **Creativity Score (0-100)**: Did they show original thinking?
   - Novel approaches
   - Going beyond basic requirements
   - Thoughtful trade-offs

4. **AI-Generated Probability (0-100)**: Likelihood this was AI-generated
   - Code patterns typical of AI (overly generic, perfect but soulless)
   - Lack of personal style or quirks
   - Too perfect documentation
   - Missing the "human touch" (TODOs, comments, refactoring traces)

5. **Key Strengths**: List 3-5 specific strong points

6. **Key Weaknesses**: List 3-5 areas for improvement

7. **Overall Assessment**: 2-3 sentence summary

Respond in JSON format:
{{
    "architecture_score": 85,
    "production_readiness": 70,
    "creativity_score": 65,
    "ai_generated_probability": 30,
    "key_strengths": ["...", "..."],
    "key_weaknesses": ["...", "..."],
    "architecture_review": "...",
    "code_review": "...",
    "overall_assessment": "..."
}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert software architect and code reviewer."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3  # Lower temperature for more consistent analysis
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            print(f"❌ AI analysis failed: {str(e)}")
            return {
                "architecture_score": 0,
                "production_readiness": 0,
                "creativity_score": 0,
                "ai_generated_probability": 0,
                "key_strengths": [],
                "key_weaknesses": [],
                "architecture_review": f"Analysis failed: {str(e)}",
                "code_review": "",
                "overall_assessment": ""
            }

    def evaluate_documentation(self, documentation: str, code_complexity: float) -> Dict:
        """
        Evaluate quality of documentation relative to code complexity.

        Args:
            documentation: Architecture/trade-offs documentation
            code_complexity: Code complexity metric

        Returns:
            Documentation quality score and insights
        """
        prompt = f"""
Evaluate this technical documentation for a code project with complexity score {code_complexity:.1f}.

**Documentation:**
{documentation}

Rate the documentation quality (0-100) based on:
- Clarity and organization
- Depth of technical explanation
- Discussion of trade-offs
- Acknowledgment of limitations
- Future improvement ideas

Respond in JSON:
{{
    "documentation_score": 85,
    "insights": ["...", "..."],
    "missing_elements": ["..."]
}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.3
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            return {
                "documentation_score": 50.0,
                "insights": [],
                "missing_elements": [f"Analysis failed: {str(e)}"]
            }

    def compare_hr_to_ai_evaluation(
        self,
        hr_evaluation: Evaluation,
        ai_analysis: AIAnalysis
    ) -> Dict:
        """
        Compare HR's evaluation to AI's assessment.

        This is the breakthrough feature: scoring HR based on whether they
        understood the code as well as AI did.

        Args:
            hr_evaluation: HR's evaluation
            ai_analysis: AI's analysis

        Returns:
            Comparison scores and insights
        """
        prompt = f"""
You are evaluating how well an HR manager assessed a candidate's code project.

**AI's Assessment:**
- Architecture Score: {ai_analysis.architecture_score if hasattr(ai_analysis, 'architecture_score') else 'N/A'}
- Production Readiness: {ai_analysis.production_readiness}
- AI Generated Probability: {ai_analysis.ai_generated_probability}%
- Key Strengths: {json.dumps(ai_analysis.key_strengths)}
- Key Weaknesses: {json.dumps(ai_analysis.key_weaknesses)}

**HR Manager's Assessment:**
- Recommendation: {hr_evaluation.hire_recommendation.value}
- Predicted Success: {hr_evaluation.predicted_success_likelihood}%
- Strengths Identified: {json.dumps(hr_evaluation.strengths_identified)}
- Weaknesses Identified: {json.dumps(hr_evaluation.weaknesses_identified)}
- Technical Assessment: {hr_evaluation.technical_assessment}

Compare these evaluations and score the HR manager's assessment (0-100) on:
1. Did they catch the key strengths AI found?
2. Did they identify the same weaknesses?
3. Did they miss critical red flags?
4. Was their technical depth adequate?

Respond in JSON:
{{
    "hr_quality_score": 75,
    "delta_from_ai": 15,
    "hr_caught_that_ai_missed": ["..."],
    "ai_caught_that_hr_missed": ["..."],
    "evaluation_depth_score": 80,
    "insights": ["HR showed good understanding of...", "HR missed..."]
}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.3
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            return {
                "hr_quality_score": 50.0,
                "delta_from_ai": 0.0,
                "hr_caught_that_ai_missed": [],
                "ai_caught_that_hr_missed": [],
                "evaluation_depth_score": 50.0,
                "insights": [f"Comparison failed: {str(e)}"]
            }

    def analyze_submission_full(
        self,
        submission_id: str,
        code_files: Dict[str, str],
        project_description: str = "General software project"
    ) -> Dict:
        """
        Full AI analysis pipeline for a submission.

        Args:
            submission_id: Project submission ID
            code_files: Dictionary of code files
            project_description: What the project should do

        Returns:
            Complete analysis results
        """
        with get_db_context() as db:
            submission = db.query(ProjectSubmission).filter(
                ProjectSubmission.id == submission_id
            ).first()

            if not submission:
                raise ValueError(f"Submission {submission_id} not found")

            print(f"\n🤖 Running AI analysis on submission: {submission_id}")

            # 1. Analyze architecture and code
            print("📐 Analyzing architecture...")
            arch_analysis = self.analyze_code_architecture(
                code_files=code_files,
                architecture_doc=submission.architecture_doc,
                project_description=project_description
            )

            # 2. Evaluate documentation
            print("📝 Evaluating documentation...")
            doc_analysis = self.evaluate_documentation(
                documentation=submission.architecture_doc + "\n\n" + submission.trade_offs_doc,
                code_complexity=70.0  # Would come from static analysis
            )

            # 3. Save AI analysis to database
            ai_analysis = AIAnalysis(
                submission_id=submission_id,
                model_used=self.model,
                architecture_review=arch_analysis.get('architecture_review', ''),
                code_review=arch_analysis.get('code_review', ''),
                documentation_review=json.dumps(doc_analysis),
                creativity_score=arch_analysis.get('creativity_score', 0),
                production_readiness=arch_analysis.get('production_readiness', 0),
                ai_generated_probability=arch_analysis.get('ai_generated_probability', 0),
                key_strengths=arch_analysis.get('key_strengths', []),
                key_weaknesses=arch_analysis.get('key_weaknesses', [])
            )

            db.add(ai_analysis)
            db.commit()
            db.refresh(ai_analysis)

            print(f"✅ AI analysis complete!")
            print(f"   Architecture: {arch_analysis.get('architecture_score', 0)}/100")
            print(f"   Production Ready: {arch_analysis.get('production_readiness', 0)}/100")
            print(f"   AI Generated Probability: {arch_analysis.get('ai_generated_probability', 0)}%")

            return {
                'submission_id': submission_id,
                'ai_analysis_id': str(ai_analysis.id),
                'architecture_analysis': arch_analysis,
                'documentation_analysis': doc_analysis
            }

    def score_hr_evaluation(self, evaluation_id: str) -> Dict:
        """
        Score an HR evaluation by comparing it to AI analysis.

        This is the accountability mechanism: HR can't fake understanding.

        Args:
            evaluation_id: HR evaluation ID

        Returns:
            HR quality scores and comparison results
        """
        with get_db_context() as db:
            evaluation = db.query(Evaluation).filter(
                Evaluation.id == evaluation_id
            ).first()

            if not evaluation:
                raise ValueError(f"Evaluation {evaluation_id} not found")

            # Get AI analysis for the same submission
            ai_analysis = db.query(AIAnalysis).filter(
                AIAnalysis.submission_id == evaluation.submission_id
            ).first()

            if not ai_analysis:
                print("⚠️ No AI analysis found for this submission")
                return {'error': 'AI analysis not available'}

            print(f"\n⚖️  Comparing HR evaluation to AI analysis...")

            # Compare HR to AI
            comparison = self.compare_hr_to_ai_evaluation(evaluation, ai_analysis)

            # Update evaluation with quality scores
            evaluation.hr_quality_score = comparison['hr_quality_score']
            evaluation.delta_from_ai = comparison['delta_from_ai']
            evaluation.evaluation_depth_score = comparison['evaluation_depth_score']

            db.commit()

            print(f"✅ HR Quality Score: {comparison['hr_quality_score']}/100")
            print(f"   Evaluation Depth: {comparison['evaluation_depth_score']}/100")

            return comparison


class AIInterviewBot:
    """
    AI bot that interviews candidates about their code.

    This bot competes with HR to see who can better assess the candidate.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4-turbo-preview"

    def conduct_interview(
        self,
        submission_id: str,
        candidate_responses: List[Dict[str, str]],
        max_questions: int = 10
    ) -> Dict:
        """
        Conduct an AI interview with the candidate.

        Args:
            submission_id: Project submission ID
            candidate_responses: List of {question: str, answer: str}
            max_questions: Maximum questions to ask

        Returns:
            Interview assessment
        """
        with get_db_context() as db:
            submission = db.query(ProjectSubmission).filter(
                ProjectSubmission.id == submission_id
            ).first()

            if not submission:
                raise ValueError(f"Submission {submission_id} not found")

            # Build interview context
            context = f"""
You are interviewing a candidate about their project:

**Repository:** {submission.github_repo_url}
**Architecture Doc:** {submission.architecture_doc[:500]}...
**Trade-offs:** {submission.trade_offs_doc[:500]}...

Based on their responses, evaluate:
1. Technical Depth (0-100): How well do they understand their own code?
2. Communication (0-100): Can they explain technical concepts clearly?
3. Reasoning (0-100): Do they make sound technical decisions?
4. Adaptability (0-100): How do they handle unknowns?

**Interview Transcript:**
"""

            for qa in candidate_responses:
                context += f"\nQ: {qa['question']}\nA: {qa['answer']}\n"

            context += """

Provide your assessment in JSON:
{{
    "technical_depth_score": 85,
    "communication_score": 90,
    "reasoning_score": 80,
    "adaptability_score": 75,
    "overall_recommendation": "hire",
    "confidence_level": 85,
    "insights": ["Strong understanding of...", "Could improve on..."]
}}
"""

            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": context}],
                    response_format={"type": "json_object"},
                    temperature=0.3
                )

                return json.loads(response.choices[0].message.content)

            except Exception as e:
                return {
                    "technical_depth_score": 0,
                    "communication_score": 0,
                    "reasoning_score": 0,
                    "adaptability_score": 0,
                    "overall_recommendation": "unknown",
                    "confidence_level": 0,
                    "insights": [f"Interview analysis failed: {str(e)}"]
                }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("AI Code Analysis Service")
    print("=" * 60)

    # Example: Analyze a simple code snippet
    service = AICodeAnalysisService()

    sample_code = {
        "main.py": """
def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

# This is inefficient but simple
print(calculate_fibonacci(10))
""",
        "utils.py": """
def validate_input(value):
    # TODO: Add better validation
    return isinstance(value, int) and value >= 0
"""
    }

    sample_doc = """
I implemented a simple Fibonacci calculator using recursion.

**Architecture:**
- Simple recursive approach for clarity
- Separate validation utility for reusability

**Trade-offs:**
- Chose simplicity over performance
- Recursive approach is O(2^n) - would use memoization in production
- Left TODO for better input validation as future improvement
"""

    result = service.analyze_code_architecture(
        code_files=sample_code,
        architecture_doc=sample_doc,
        project_description="Calculate Fibonacci numbers"
    )

    print("\n🤖 AI Analysis Results:")
    print(f"Architecture Score: {result.get('architecture_score', 'N/A')}/100")
    print(f"Production Readiness: {result.get('production_readiness', 'N/A')}/100")
    print(f"AI Generated Probability: {result.get('ai_generated_probability', 'N/A')}%")
    print(f"\nKey Strengths: {result.get('key_strengths', [])}")
    print(f"Key Weaknesses: {result.get('key_weaknesses', [])}")
