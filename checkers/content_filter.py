"""Content filter - detects prohibited content and words."""

import re
from typing import Optional, NamedTuple
from dataclasses import dataclass
from pathlib import Path

from ai_xiaosuo.config import PROHIBITED_CATEGORIES


class ProhibitedWord(NamedTuple):
    """Represents a prohibited word."""
    word: str
    category: str  # politics, porn, violence, illegal
    severity: str  # high, medium, low


@dataclass
class ContentFilterResult:
    """Result of content filtering."""
    is_clean: bool
    prohibited_words: list[ProhibitedWord]
    total_count: int
    categories_found: list[str]


class ContentFilter:
    """Filters prohibited content from text."""
    
    # Default prohibited word lists
    DEFAULT_FORBIDDEN_WORDS = {
        "politics": [
            "台独", "港独", "藏独", "疆独", "民主运动", "维权人士",
            "法轮功", "全能神", "呼喊派", "门徒会", "统一教",
        ],
        "porn": [
            "黄色", "色情", "淫秽", "淫荡", "性交", "做爱",
            "高潮", "裸体", "裸露", "脱衣", "成人网站",
        ],
        "violence": [
            "屠杀", "杀戮", "血腥", "暴砍", "分尸", "凶杀",
            "恐怖分子", "爆炸装置", "枪支", "弹药", "武器",
        ],
        "illegal": [
            "赌博", "吸毒", "贩毒", "走私", "诈骗", "黑客",
        ],
    }
    
    def __init__(self, custom_words_path: Optional[Path] = None):
        """Initialize content filter.
        
        Args:
            custom_words_path: Path to custom prohibited words file
        """
        self.forbidden_words = dict(self.DEFAULT_FORBIDDEN_WORDS)
        
        # Load custom words if provided
        if custom_words_path and custom_words_path.exists():
            self._load_custom_words(custom_words_path)
    
    def _load_custom_words(self, path: Path):
        """Load custom prohibited words from file.
        
        Expected format (category: words):
        politics: word1, word2
        porn: word3, word4
        """
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or ":" not in line:
                    continue
                
                category, words = line.split(":", 1)
                category = category.strip().lower()
                word_list = [w.strip() for w in words.split(",") if w.strip()]
                
                if category in self.forbidden_words:
                    self.forbidden_words[category].extend(word_list)
                else:
                    self.forbidden_words[category] = word_list
    
    def _create_patterns(self, words: list[str]) -> re.Pattern:
        """Create regex pattern from word list.
        
        Args:
            words: List of words
            
        Returns:
            Compiled regex pattern
        """
        # Escape special regex characters and join with |
        escaped = [re.escape(w) for w in words]
        pattern = "|".join(escaped)
        return re.compile(pattern, re.IGNORECASE)
    
    def check(self, text: str) -> ContentFilterResult:
        """Check text for prohibited content.
        
        Args:
            text: Text to check
            
        Returns:
            ContentFilterResult
        """
        prohibited_words = []
        categories_found = set()
        
        for category, words in self.forbidden_words.items():
            if not words:
                continue
            
            pattern = self._create_patterns(words)
            matches = pattern.findall(text)
            
            for match in matches:
                # Determine severity based on category
                severity = "high" if category in ["politics", "illegal"] else "medium"
                
                prohibited_words.append(ProhibitedWord(
                    word=match,
                    category=category,
                    severity=severity
                ))
                categories_found.add(category)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_words = []
        for pw in prohibited_words:
            if pw.word.lower() not in seen:
                seen.add(pw.word.lower())
                unique_words.append(pw)
        
        return ContentFilterResult(
            is_clean=len(unique_words) == 0,
            prohibited_words=unique_words,
            total_count=len(unique_words),
            categories_found=list(categories_found),
        )
    
    def check_with_positions(self, text: str) -> list[dict]:
        """Check text and return positions of prohibited words.
        
        Args:
            text: Text to check
            
        Returns:
            List of dicts with word, category, position info
        """
        results = []
        
        for category, words in self.forbidden_words.items():
            if not words:
                continue
            
            pattern = self._create_patterns(words)
            
            for match in pattern.finditer(text):
                # Determine severity
                severity = "high" if category in ["politics", "illegal"] else "medium"
                
                results.append({
                    "word": match.group(),
                    "category": category,
                    "severity": severity,
                    "start": match.start(),
                    "end": match.end(),
                    "context": text[max(0, match.start()-20):min(len(text), match.end()+20)]
                })
        
        # Sort by position
        results.sort(key=lambda x: x["start"])
        
        return results
    
    def highlight_prohibited(self, text: str) -> tuple[str, list[dict]]:
        """Highlight prohibited words in text.
        
        Args:
            text: Text to check
            
        Returns:
            Tuple of (highlighted_text, list of findings)
        """
        findings = self.check_with_positions(text)
        
        if not findings:
            return text, []
        
        # Create highlighted version
        highlighted = text
        offset = 0
        
        for finding in findings:
            start = finding["start"] + offset
            end = finding["end"] + offset
            
            # Insert markers (use different markers to avoid counting them)
            before = highlighted[:start]
            word = highlighted[start:end]
            after = highlighted[end:]
            
            # Highlight with markers
            highlighted = f"{before}[[{word}]]{after}"
            offset += 4  # Length of [[ ]] markers
        
        return highlighted, findings
    
    def add_custom_word(self, word: str, category: str, severity: str = "medium"):
        """Add a custom prohibited word.
        
        Args:
            word: Word to add
            category: Category (politics, porn, violence, illegal)
            severity: Severity level (high, medium, low)
        """
        if category not in self.forbidden_words:
            self.forbidden_words[category] = []
        
        if word not in self.forbidden_words[category]:
            self.forbidden_words[category].append(word)
    
    def remove_word(self, word: str):
        """Remove a word from all categories.
        
        Args:
            word: Word to remove
        """
        for category in self.forbidden_words:
            if word in self.forbidden_words[category]:
                self.forbidden_words[category].remove(word)
    
    def get_categories(self) -> list[str]:
        """Get list of available categories.
        
        Returns:
            List of category names
        """
        return list(self.forbidden_words.keys())
