"""Quality checker - checks chapter quality for publishing."""

import json
import re
from typing import Optional, NamedTuple
from dataclasses import dataclass
from sqlalchemy.orm import Session

from ai_xiaosuo.api.minimax_client import MiniMaxClient
from ai_xiaosuo.api.prompts import QUALITY_CHECK_PROMPT
from ai_xiaosuo.config import MIN_CHAPTER_LENGTH


class TitleCandidate(NamedTuple):
    """Represents a candidate title."""
    title: str
    title_type: str  # suspense,爽点,数字


@dataclass
class QualityCheckResult:
    """Result of quality check."""
    word_count: int
    is_qualified: bool  # Above minimum word count
    titles: list[TitleCandidate]
    has_ending_hook: bool
    is_good_start: bool
    quality_score: float
    suggestions: list[str]


class QualityChecker:
    """Checks chapter quality for publishing requirements."""
    
    def __init__(self, session: Session, api_client: Optional[MiniMaxClient] = None):
        """Initialize quality checker.
        
        Args:
            session: Database session
            api_client: MiniMax API client
        """
        self.session = session
        self.api_client = api_client or MiniMaxClient()
        self.min_word_count = MIN_CHAPTER_LENGTH
    
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
    
    def _count_words(self, text: str) -> int:
        """Count Chinese characters + English words."""
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        english_words = len(re.findall(r'[a-zA-Z]+', text))
        return chinese_chars + english_words
    
    def _check_word_count(self, text: str) -> tuple[int, bool]:
        """Check word count.
        
        Args:
            text: Text to check
            
        Returns:
            Tuple of (word_count, is_qualified)
        """
        word_count = self._count_words(text)
        is_qualified = word_count >= self.min_word_count
        return word_count, is_qualified
    
    def _check_ending_hook(self, text: str) -> bool:
        """Check if chapter has an ending hook.
        
        Args:
            text: Chapter content
            
        Returns:
            True if hook detected
        """
        # Common hook patterns
        hook_patterns = [
            r'就在此时',
            r'突然',
            r'没想到',
            r'就在这时',
            r'悬念',
            r'预知后事如何',
            r'且听下回分解',
            r'未完待续',
            r'（未完）',
            r'============',
            r'---',
        ]
        
        # Get last 500 characters
        last_part = text[-500:] if len(text) > 500 else text
        
        for pattern in hook_patterns:
            if re.search(pattern, last_part):
                return True
        
        return False
    
    def _check_good_start(self, text: str) -> bool:
        """Check if chapter has a good opening.
        
        Args:
            text: Chapter content
            
        Returns:
            True if good start detected
        """
        # Get first 300 characters
        first_part = text[:300] if len(text) > 300 else text
        
        # Good start indicators
        good_patterns = [
            r'清晨',
            r'黎明',
            r'夜幕',
            r'阳光',
            r'突然',
            r'就在',
            r'今天',
            r'这一日',
            r'这一',
            r'某一',
            r'"',  # Dialogue start
            '「',  # Chinese quote
            '『',
        ]
        
        for pattern in good_patterns:
            if re.search(pattern, first_part):
                return True
        
        return False
    
    def _generate_local_titles(self, text: str) -> list[TitleCandidate]:
        """Generate title candidates locally.
        
        Args:
            text: Chapter content
            
        Returns:
            List of TitleCandidate
        """
        titles = []
        
        # Extract potential keywords from content
        lines = text.split('\n')
        meaningful_lines = [l.strip() for l in lines if len(l.strip()) > 5][:20]
        
        # Generate suspense titles
        titles.extend([
            TitleCandidate("命运转折", "suspense"),
            TitleCandidate("危机降临", "suspense"),
            TitleCandidate("真相大白", "suspense"),
        ])
        
        # Generate 爽点 titles
        titles.extend([
            TitleCandidate("逆袭成功", "爽点"),
            TitleCandidate("实力突破", "爽点"),
            TitleCandidate("大获全胜", "爽点"),
        ])
        
        # Generate numbered titles
        titles.extend([
            TitleCandidate("第X章 新的开始", "数字"),
            TitleCandidate("第X话 命运之战", "数字"),
            TitleCandidate("第X节 终极对决", "数字"),
        ])
        
        return titles[:8]
    
    def check(
        self,
        chapter_content: str,
        use_ai: bool = True,
    ) -> QualityCheckResult:
        """Check quality of chapter content.
        
        Args:
            chapter_content: Content to check
            use_ai: Whether to use AI for title generation
            
        Returns:
            QualityCheckResult
        """
        # Basic checks
        word_count, is_qualified = self._check_word_count(chapter_content)
        has_ending_hook = self._check_ending_hook(chapter_content)
        is_good_start = self._check_good_start(chapter_content)
        
        # Generate titles
        titles = self._generate_local_titles(chapter_content)
        
        # AI enhancement if enabled
        if use_ai and len(chapter_content) > 500:
            try:
                ai_titles = self._ai_generate_titles(chapter_content)
                if ai_titles:
                    titles = ai_titles
            except Exception:
                pass
        
        # Generate suggestions
        suggestions = []
        
        if not is_qualified:
            suggestions.append(f"字数不足：当前{word_count}字，建议扩展至{self.min_word_count}字以上")
        
        if not has_ending_hook:
            suggestions.append("建议添加结尾钩子以吸引读者继续阅读")
        
        if not is_good_start:
            suggestions.append("开头建议更加吸引人")
        
        # Calculate quality score
        quality_score = 0.5
        
        if is_qualified:
            quality_score += 0.2
        
        if has_ending_hook:
            quality_score += 0.1
        
        if is_good_start:
            quality_score += 0.1
        
        # Bonus for good titles
        if len(titles) >= 5:
            quality_score += 0.1
        
        quality_score = min(1.0, quality_score)
        
        return QualityCheckResult(
            word_count=word_count,
            is_qualified=is_qualified,
            titles=titles,
            has_ending_hook=has_ending_hook,
            is_good_start=is_good_start,
            quality_score=quality_score,
            suggestions=suggestions,
        )
    
    def _ai_generate_titles(
        self,
        chapter_content: str,
    ) -> Optional[list[TitleCandidate]]:
        """Use AI to generate title candidates.
        
        Args:
            chapter_content: Chapter content
            
        Returns:
            List of TitleCandidate or None
        """
        prompt = QUALITY_CHECK_PROMPT.format(
            chapter_content=chapter_content[:2000],
        )
        
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        result, _, _, _ = self.api_client.chat(messages, temperature=0.7, max_tokens=1000)
        
        # Parse JSON
        data = self._extract_json_from_response(result)
        
        if not data:
            return None
        
        # Extract titles
        titles_dict = data.get("titles", {})
        
        titles = []
        
        for title_type, title_list in titles_dict.items():
            for title in title_list:
                titles.append(TitleCandidate(title, title_type))
        
        return titles if titles else None
