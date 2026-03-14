"""Style checker - checks writing style and quality."""

import json
import re
from typing import Optional
from dataclasses import dataclass
from sqlalchemy.orm import Session

from ai_xiaosuo.api.minimax_client import MiniMaxClient
from ai_xiaosuo.api.prompts import STYLE_CHECK_PROMPT
from ai_xiaosuo.models import Project


@dataclass
class StyleIssue:
    """Represents a style issue."""
    issue_type: str
    description: str
    severity: str  # high, medium, low


@dataclass
class StyleCheckResult:
    """Result of style check."""
    is_passed: bool
    issues: list[StyleIssue]
    repetition_ratio: float
    style_match_score: float
    overall_score: float


class StyleChecker:
    """Checks writing style consistency and quality."""
    
    def __init__(self, session: Session, api_client: Optional[MiniMaxClient] = None):
        """Initialize style checker.
        
        Args:
            session: Database session
            api_client: MiniMax API client
        """
        self.session = session
        self.api_client = api_client or MiniMaxClient()
    
    def _extract_json_from_response(self, text: str) -> Optional[dict]:
        """Extract JSON from AI response."""
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None
    
    def _calculate_repetition_ratio(self, text: str) -> float:
        """Calculate sentence repetition ratio.
        
        Args:
            text: Text to analyze
            
        Returns:
            Repetition ratio (0.0 to 1.0)
        """
        # Split into sentences
        sentences = re.split(r'[。！？\n]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 0.0
        
        # Count unique sentences
        unique_sentences = set(sentences)
        
        # Calculate ratio
        return 1 - (len(unique_sentences) / len(sentences))
    
    def _calculate_word_repetition(self, text: str) -> float:
        """Calculate word/phrase repetition.
        
        Args:
            text: Text to analyze
            
        Returns:
            Repetition ratio
        """
        # Extract 2-gram and 3-gram phrases
        chinese_chars = [c for c in text if '\u4e00' <= c <= '\u9fff']
        
        if len(chinese_chars) < 3:
            return 0.0
        
        # Build n-grams
        bigrams = [''.join(chinese_chars[i:i+2]) for i in range(len(chinese_chars)-1)]
        trigrams = [''.join(chinese_chars[i:i+3]) for i in range(len(chinese_chars)-2)]
        
        # Count frequencies
        bigram_freq = {}
        for bg in bigrams:
            bigram_freq[bg] = bigram_freq.get(bg, 0) + 1
        
        trigram_freq = {}
        for tg in trigrams:
            trigram_freq[tg] = trigram_freq.get(tg, 0) + 1
        
        # Calculate repetition score
        total_bigrams = len(bigrams)
        repeated_bigrams = sum(1 for c in bigram_freq.values() if c > 1)
        
        if total_bigrams == 0:
            return 0.0
        
        return repeated_bigrams / total_bigrams
    
    def _detect_ai_patterns(self, text: str) -> list[StyleIssue]:
        """Detect AI-generated patterns (mechanical feel).
        
        Args:
            text: Text to analyze
            
        Returns:
            List of StyleIssue
        """
        issues = []
        
        # Check for common AI patterns
        patterns = [
            (r'首先，其次，最后', '过度使用首先/其次/最后结构'),
            (r'总的来说', '过度使用"总的来说"'),
            (r'可以看出', '过度使用"可以看出"'),
            (r'值得注意的是', '过度使用"值得注意的是"'),
            (r'一般来说', '过度使用"一般来说"'),
        ]
        
        for pattern, description in patterns:
            matches = re.findall(pattern, text)
            if len(matches) > 3:
                issues.append(StyleIssue(
                    issue_type="ai_pattern",
                    description=f"{description} ({len(matches)}次)",
                    severity="medium"
                ))
        
        return issues
    
    def check(
        self,
        project_id: int,
        chapter_content: str,
        use_ai: bool = True,
    ) -> StyleCheckResult:
        """Check style of chapter content.
        
        Args:
            project_id: Project ID
            chapter_content: Content to check
            use_ai: Whether to use AI for deep checking
            
        Returns:
            StyleCheckResult
        """
        # Get project for style requirements
        project = self.session.query(Project).filter(Project.id == project_id).first()
        
        all_issues = []
        
        # Calculate repetition ratio
        repetition_ratio = self._calculate_repetition_ratio(chapter_content)
        if repetition_ratio > 0.15:
            all_issues.append(StyleIssue(
                issue_type="repetition",
                description=f"句式重复度过高: {repetition_ratio:.1%}",
                severity="high" if repetition_ratio > 0.3 else "medium"
            ))
        
        # Calculate word repetition
        word_repetition = self._calculate_word_repetition(chapter_content)
        if word_repetition > 0.2:
            all_issues.append(StyleIssue(
                issue_type="word_repetition",
                description=f"词汇重复度过高: {word_repetition:.1%}",
                severity="medium"
            ))
        
        # Detect AI patterns
        all_issues.extend(self._detect_ai_patterns(chapter_content))
        
        # AI style check if enabled
        style_match_score = 0.8  # Default
        if use_ai and len(chapter_content) > 500:
            try:
                ai_result = self._ai_check(project, chapter_content)
                all_issues.extend(ai_result.get("issues", []))
                style_match_score = ai_result.get("style_match_score", 0.8)
            except Exception:
                pass
        
        # Calculate overall score
        if not all_issues:
            overall_score = 1.0
            is_passed = True
        else:
            high_count = sum(1 for i in all_issues if i.severity == "high")
            medium_count = sum(1 for i in all_issues if i.severity == "medium")
            
            if high_count > 0:
                overall_score = 0.4
                is_passed = False
            elif medium_count > 1:
                overall_score = 0.6
                is_passed = False
            elif medium_count == 1:
                overall_score = 0.75
                is_passed = True
            else:
                overall_score = 0.85
                is_passed = True
        
        return StyleCheckResult(
            is_passed=is_passed,
            issues=all_issues,
            repetition_ratio=repetition_ratio,
            style_match_score=style_match_score,
            overall_score=overall_score,
        )
    
    def _ai_check(
        self,
        project: Optional[Project],
        chapter_content: str,
    ) -> dict:
        """Use AI to check style deeply.
        
        Args:
            project: Project instance
            chapter_content: Content to check
            
        Returns:
            Dict with issues and style_match_score
        """
        style_requirement = project.style_requirement if project else ""
        
        prompt = STYLE_CHECK_PROMPT.format(
            style_requirement=style_requirement or "（无特定要求）",
            chapter_content=chapter_content[:3000],
        )
        
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        result, _, _, _ = self.api_client.chat(messages, temperature=0.3, max_tokens=1500)
        
        # Parse JSON
        data = self._extract_json_from_response(result)
        
        if not data:
            return {"issues": [], "style_match_score": 0.8}
        
        # Convert to StyleIssue objects
        issues = []
        for item in data.get("issues", []):
            issues.append(StyleIssue(
                issue_type=item.get("type", "unknown"),
                description=item.get("description", ""),
                severity=item.get("severity", "low"),
            ))
        
        # Get style match score
        style_match = data.get("style_match_score", 0.8)
        
        return {
            "issues": issues,
            "style_match_score": style_match,
        }
