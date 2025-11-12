"""
Git Integration Service

Analyzes GitHub repositories to detect:
- Commit patterns (bulk vs iterative development)
- Code authorship authenticity
- Development timeline consistency
- AI-generated vs human-crafted work patterns
"""

import os
import tempfile
import shutil
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from git import Repo, GitCommandError
from github import Github, GithubException
from sqlalchemy.orm import Session

from models import ProjectSubmission, CommitAnalysis
from database import get_db_context


class GitAnalysisService:
    """
    Service for analyzing Git repositories to detect work authenticity.

    Real developers show:
    - Iterative commits over time
    - Meaningful commit messages
    - Refactoring and refinement
    - Varied commit sizes

    AI-generated code shows:
    - Bulk commits (large changes at once)
    - Generic commit messages
    - Lack of iterative refinement
    - Sudden appearance of complete features
    """

    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize Git analysis service.

        Args:
            github_token: GitHub personal access token for API access
        """
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.github_client = Github(self.github_token) if self.github_token else None

    def clone_repository(self, repo_url: str) -> str:
        """
        Clone a GitHub repository to a temporary directory.

        Args:
            repo_url: GitHub repository URL

        Returns:
            Path to cloned repository

        Raises:
            GitCommandError: If cloning fails
        """
        temp_dir = tempfile.mkdtemp(prefix="git_analysis_")

        try:
            print(f"📥 Cloning repository: {repo_url}")
            Repo.clone_from(repo_url, temp_dir)
            print(f"✅ Cloned to: {temp_dir}")
            return temp_dir
        except GitCommandError as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise Exception(f"Failed to clone repository: {str(e)}")

    def analyze_commits(self, repo_path: str) -> List[Dict]:
        """
        Analyze all commits in a repository.

        Args:
            repo_path: Path to local git repository

        Returns:
            List of commit analysis dictionaries
        """
        repo = Repo(repo_path)
        commits = list(repo.iter_commits('--all'))

        commit_data = []
        previous_commit_time = None

        for commit in reversed(commits):  # Oldest to newest
            # Calculate time gap from previous commit
            commit_time = datetime.fromtimestamp(commit.committed_date)
            time_gap_hours = None
            if previous_commit_time:
                time_gap_hours = (commit_time - previous_commit_time).total_seconds() / 3600

            # Get file statistics
            stats = commit.stats.total
            files_changed = len(commit.stats.files)
            lines_added = stats['insertions']
            lines_deleted = stats['deletions']

            # Detect bulk commit (suspicious pattern)
            is_bulk_commit = self._is_bulk_commit(
                files_changed=files_changed,
                lines_added=lines_added,
                time_gap_hours=time_gap_hours
            )

            # Score commit message quality
            message_quality = self._score_commit_message(commit.message)

            commit_data.append({
                'hash': commit.hexsha,
                'message': commit.message,
                'timestamp': commit_time,
                'author': str(commit.author),
                'files_changed': files_changed,
                'lines_added': lines_added,
                'lines_deleted': lines_deleted,
                'is_bulk_commit': is_bulk_commit,
                'time_gap_hours': time_gap_hours,
                'message_quality_score': message_quality
            })

            previous_commit_time = commit_time

        return commit_data

    def _is_bulk_commit(
        self,
        files_changed: int,
        lines_added: int,
        time_gap_hours: Optional[float]
    ) -> bool:
        """
        Detect if a commit appears to be a "bulk commit" (suspicious pattern).

        AI-generated code often appears as large, sudden commits.
        Real developers make smaller, iterative changes.

        Args:
            files_changed: Number of files modified
            lines_added: Lines of code added
            time_gap_hours: Hours since previous commit

        Returns:
            True if commit appears suspicious
        """
        # Thresholds for suspicious commits
        BULK_FILES_THRESHOLD = 15
        BULK_LINES_THRESHOLD = 500

        # Large commit with many files
        if files_changed >= BULK_FILES_THRESHOLD and lines_added >= BULK_LINES_THRESHOLD:
            return True

        # First commit after long gap with huge changes
        if time_gap_hours and time_gap_hours > 48 and lines_added > 1000:
            return True

        return False

    def _score_commit_message(self, message: str) -> float:
        """
        Score the quality of a commit message (0-10).

        Good commit messages:
        - Are descriptive
        - Explain the "why"
        - Follow conventions
        - Are specific

        Bad commit messages:
        - "Update"
        - "Fix"
        - "Changes"
        - "Initial commit" (for non-initial commits)

        Args:
            message: Commit message text

        Returns:
            Quality score from 0-10
        """
        message_lower = message.lower().strip()
        score = 5.0  # Start at neutral

        # Deduct points for generic messages
        generic_messages = ['update', 'fix', 'changes', 'wip', 'stuff', 'misc']
        if message_lower in generic_messages:
            score -= 3.0

        # Deduct for very short messages
        if len(message) < 10:
            score -= 2.0

        # Add points for detailed messages
        if len(message) > 50:
            score += 2.0

        # Add points for conventional commit format
        conventional_prefixes = ['feat:', 'fix:', 'docs:', 'refactor:', 'test:', 'chore:']
        if any(message_lower.startswith(prefix) for prefix in conventional_prefixes):
            score += 2.0

        # Add points for explaining "why"
        explanation_words = ['because', 'to enable', 'improves', 'resolves', 'addresses']
        if any(word in message_lower for word in explanation_words):
            score += 1.5

        return max(0.0, min(10.0, score))  # Clamp to 0-10

    def calculate_commit_pattern_score(self, commits: List[Dict]) -> Dict:
        """
        Calculate overall commit pattern score and insights.

        Returns a comprehensive analysis of whether the work appears authentic.

        Args:
            commits: List of commit dictionaries from analyze_commits()

        Returns:
            Dictionary with scores and insights
        """
        if not commits:
            return {
                'overall_score': 0.0,
                'authenticity_score': 0.0,
                'insights': ['No commits found']
            }

        total_commits = len(commits)
        bulk_commits = sum(1 for c in commits if c['is_bulk_commit'])
        avg_message_quality = sum(c['message_quality_score'] for c in commits) / total_commits

        # Calculate time distribution (iterative vs bulk)
        time_gaps = [c['time_gap_hours'] for c in commits if c['time_gap_hours']]
        avg_time_gap = sum(time_gaps) / len(time_gaps) if time_gaps else 0

        # Authenticity indicators
        insights = []

        # Check 1: Bulk commit ratio
        bulk_ratio = bulk_commits / total_commits
        if bulk_ratio > 0.5:
            insights.append(f"⚠️ {bulk_ratio*100:.0f}% of commits are bulk commits (suspicious)")
        elif bulk_ratio < 0.2:
            insights.append(f"✓ Only {bulk_ratio*100:.0f}% bulk commits (good iterative pattern)")

        # Check 2: Commit message quality
        if avg_message_quality < 4.0:
            insights.append(f"⚠️ Low commit message quality (avg: {avg_message_quality:.1f}/10)")
        elif avg_message_quality > 6.5:
            insights.append(f"✓ Good commit messages (avg: {avg_message_quality:.1f}/10)")

        # Check 3: Development timeline
        if avg_time_gap < 2.0 and total_commits > 10:
            insights.append("✓ Consistent development pattern (commits spread over time)")
        elif avg_time_gap > 24.0:
            insights.append(f"⚠️ Large gaps between commits (avg: {avg_time_gap:.1f} hours)")

        # Check 4: Commit count
        if total_commits < 5:
            insights.append("⚠️ Very few commits (possible bulk copy-paste)")
        elif total_commits > 20:
            insights.append("✓ Many commits (shows iterative development)")

        # Calculate overall authenticity score (0-100)
        authenticity_score = 100.0

        # Penalties
        authenticity_score -= (bulk_ratio * 30)  # -30 points for 100% bulk commits
        authenticity_score -= max(0, (5.0 - avg_message_quality) * 5)  # Poor messages
        if total_commits < 5:
            authenticity_score -= 20  # Very few commits

        # Bonuses
        if total_commits > 15:
            authenticity_score += 10
        if avg_message_quality > 7.0:
            authenticity_score += 10

        authenticity_score = max(0.0, min(100.0, authenticity_score))

        return {
            'total_commits': total_commits,
            'bulk_commits': bulk_commits,
            'bulk_commit_ratio': round(bulk_ratio, 2),
            'avg_message_quality': round(avg_message_quality, 2),
            'avg_time_gap_hours': round(avg_time_gap, 2),
            'authenticity_score': round(authenticity_score, 2),
            'insights': insights
        }

    def save_commit_analysis(self, submission_id: str, commits: List[Dict], db: Session):
        """
        Save commit analysis to database.

        Args:
            submission_id: Project submission ID
            commits: List of commit analysis dictionaries
            db: Database session
        """
        for commit in commits:
            commit_record = CommitAnalysis(
                submission_id=submission_id,
                commit_hash=commit['hash'],
                commit_message=commit['message'],
                commit_timestamp=commit['timestamp'],
                files_changed=commit['files_changed'],
                lines_added=commit['lines_added'],
                lines_deleted=commit['lines_deleted'],
                is_bulk_commit=commit['is_bulk_commit'],
                time_gap_hours=commit['time_gap_hours'],
                message_quality_score=commit['message_quality_score']
            )
            db.add(commit_record)

        db.commit()
        print(f"✅ Saved {len(commits)} commit analyses to database")

    def analyze_submission(self, submission_id: str) -> Dict:
        """
        Full analysis pipeline for a project submission.

        Args:
            submission_id: Project submission ID

        Returns:
            Complete analysis results
        """
        with get_db_context() as db:
            # Get submission
            submission = db.query(ProjectSubmission).filter(
                ProjectSubmission.id == submission_id
            ).first()

            if not submission:
                raise ValueError(f"Submission {submission_id} not found")

            print(f"\n🔍 Analyzing submission: {submission_id}")
            print(f"📦 Repository: {submission.github_repo_url}")

            # Clone repository
            repo_path = self.clone_repository(submission.github_repo_url)

            try:
                # Analyze commits
                commits = self.analyze_commits(repo_path)
                print(f"📊 Analyzed {len(commits)} commits")

                # Calculate pattern score
                pattern_analysis = self.calculate_commit_pattern_score(commits)
                print(f"\n🎯 Authenticity Score: {pattern_analysis['authenticity_score']}/100")

                for insight in pattern_analysis['insights']:
                    print(f"   {insight}")

                # Save to database
                self.save_commit_analysis(submission_id, commits, db)

                # Update submission metrics
                submission.commit_count = len(commits)
                db.commit()

                return {
                    'submission_id': submission_id,
                    'commits_analyzed': len(commits),
                    'pattern_analysis': pattern_analysis,
                    'commit_details': commits
                }

            finally:
                # Clean up temporary directory
                shutil.rmtree(repo_path, ignore_errors=True)
                print(f"🧹 Cleaned up temporary files")


# ============================================================================
# GITHUB API INTEGRATION
# ============================================================================

class GitHubAPIService:
    """
    Service for interacting with GitHub API to gather additional insights.
    """

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.client = Github(self.token) if self.token else None

    def get_repository_stats(self, repo_url: str) -> Dict:
        """
        Get repository statistics from GitHub API.

        Args:
            repo_url: GitHub repository URL

        Returns:
            Repository statistics dictionary
        """
        if not self.client:
            raise ValueError("GitHub token required for API access")

        # Extract owner/repo from URL
        # Example: https://github.com/owner/repo -> owner/repo
        parts = repo_url.rstrip('/').split('/')
        owner, repo_name = parts[-2], parts[-1]

        try:
            repo = self.client.get_repo(f"{owner}/{repo_name}")

            return {
                'stars': repo.stargazers_count,
                'forks': repo.forks_count,
                'open_issues': repo.open_issues_count,
                'created_at': repo.created_at,
                'updated_at': repo.updated_at,
                'language': repo.language,
                'size_kb': repo.size,
                'has_wiki': repo.has_wiki,
                'has_issues': repo.has_issues,
            }

        except GithubException as e:
            raise Exception(f"Failed to fetch GitHub stats: {str(e)}")


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python git_service.py <github_repo_url>")
        sys.exit(1)

    repo_url = sys.argv[1]

    service = GitAnalysisService()
    temp_repo = service.clone_repository(repo_url)

    try:
        commits = service.analyze_commits(temp_repo)
        print(f"\n📊 Analyzed {len(commits)} commits\n")

        for commit in commits[:5]:  # Show first 5
            print(f"Commit: {commit['hash'][:7]}")
            print(f"  Message: {commit['message'][:60]}")
            print(f"  Quality: {commit['message_quality_score']:.1f}/10")
            print(f"  Changes: +{commit['lines_added']} -{commit['lines_deleted']} ({commit['files_changed']} files)")
            print(f"  Bulk: {commit['is_bulk_commit']}")
            print()

        analysis = service.calculate_commit_pattern_score(commits)
        print("\n" + "="*60)
        print(f"🎯 AUTHENTICITY SCORE: {analysis['authenticity_score']}/100")
        print("="*60)

        for insight in analysis['insights']:
            print(f"  {insight}")

    finally:
        shutil.rmtree(temp_repo, ignore_errors=True)
