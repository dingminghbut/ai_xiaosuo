"""Chapter generator - generates chapters using AI."""

import re
from typing import Optional, Generator
from dataclasses import dataclass
from sqlalchemy.orm import Session

from ai_xiaosuo.api.minimax_client import MiniMaxClient
from ai_xiaosuo.api.prompts import (
    SYSTEM_PROMPT,
    CHAPTER_GENERATION_PROMPT,
)
from ai_xiaosuo.core.context_assembler import ContextAssembler
from ai_xiaosuo.config import TARGET_CHAPTER_LENGTH, MIN_CHAPTER_LENGTH


@dataclass
class GenerationParams:
    """Parameters for chapter generation."""
    chapter_goal: str = ""  # User's goal for this chapter
    emotional_tone: str = "neutral"  # emotional tone
    ending_hook: str = ""  # Ending hook
    special_events: str = ""  # Special events to trigger
    target_words: int = TARGET_CHAPTER_LENGTH
    dialogue_ratio: int = 30  # 30% dialogue
    pace: str = "normal"  # fast/normal/slow
    temperature: float = 0.8


@dataclass
class GenerationResult:
    """Result of chapter generation."""
    content: str
    word_count: int
    input_tokens: int
    output_tokens: int
    cost: float
    titles: list[str]
    quality_score: float


class ChapterGenerator:
    """Generates novel chapters using AI."""
    
    def __init__(self, session: Session, api_client: Optional[MiniMaxClient] = None):
        """Initialize chapter generator.
        
        Args:
            session: Database session
            api_client: MiniMax API client (creates new if not provided)
        """
        self.session = session
        self.api_client = api_client or MiniMaxClient()
        self.context_assembler = ContextAssembler(session)
    
    def _count_words(self, text: str) -> int:
        """Count Chinese characters + English words in text."""
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        english_words = len(re.findall(r'[a-zA-Z]+', text))
        return chinese_chars + english_words
    
    def _generate_titles(self, content: str) -> list[str]:
        """Generate candidate titles for the chapter.
        
        Args:
            content: Chapter content
            
        Returns:
            List of candidate titles
        """
        # Use simple keyword extraction for now
        # In production, this would call the AI
        titles = []
        
        # Extract key phrases (simplified)
        lines = content.split('\n')
        if len(lines) > 5:
            # Extract first meaningful paragraph
            for line in lines[3:8]:
                if len(line) > 10 and len(line) < 50:
                    titles.append(line.strip())
                    if len(titles) >= 3:
                        break
        
        # Add numbered titles
        titles.extend([
            f"第X章 新的挑战",
            f"命运转折",
            f"逆袭时刻",
        ])
        
        return titles[:8]
    
    def _generate(
        self,
        context: str,
        params: GenerationParams,
    ) -> GenerationResult:
        """Generate chapter content.
        
        Args:
            context: Assembled context
            params: Generation parameters
            
        Returns:
            GenerationResult
        """
        # Build generation prompt
        prompt = CHAPTER_GENERATION_PROMPT.format(
            chapter_goal=params.chapter_goal or "继续故事发展",
            emotional_tone=params.emotional_tone or "中性",
            ending_hook=params.ending_hook or "设置悬念结尾",
            special_events=params.special_events or "无",
            target_words=params.target_words,
            dialogue_ratio=params.dialogue_ratio,
            pace=params.pace,
        )
        
        # Build full messages
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": context},
            {"role": "user", "content": prompt},
        ]
        
        # Call API
        content, input_tokens, output_tokens, cost = self.api_client.chat(
            messages=messages,
            temperature=params.temperature,
            max_tokens=params.target_words * 2,  # Allow extra for output
        )
        
        # Clean content
        content = content.strip()
        
        # Count words
        word_count = self._count_words(content)
        
        # Generate titles
        titles = self._generate_titles(content)
        
        # Calculate quality score (simplified)
        quality_score = 0.7  # Default score
        
        return GenerationResult(
            content=content,
            word_count=word_count,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            titles=titles,
            quality_score=quality_score,
        )
    
    def generate(
        self,
        project_id: int,
        current_chapter: int,
        params: Optional[GenerationParams] = None,
    ) -> GenerationResult:
        """Generate a chapter.
        
        Args:
            project_id: Project ID
            current_chapter: Chapter number to generate
            params: Generation parameters (optional)
            
        Returns:
            GenerationResult
        """
        params = params or GenerationParams()
        
        # Get context
        context, layer_info = self.context_assembler.get_context_for_generation(
            project_id, current_chapter
        )
        
        # Generate chapter
        result = self._generate(context, params)
        
        # Check if chapter is too short
        if result.word_count < MIN_CHAPTER_LENGTH:
            # TODO: Implement expansion logic
            pass
        
        return result
    
    def generate_stream(
        self,
        project_id: int,
        current_chapter: int,
        params: Optional[GenerationParams] = None,
    ) -> Generator[tuple[str, int, float], None, None]:
        """Generate a chapter with streaming output.
        
        Args:
            project_id: Project ID
            current_chapter: Chapter number to generate
            params: Generation parameters (optional)
            
        Yields:
            Tuple of (chunk_text, cumulative_word_count, cumulative_cost)
        """
        params = params or GenerationParams()
        
        # Get context
        context, layer_info = self.context_assembler.get_context_for_generation(
            project_id, current_chapter
        )
        
        # Build generation prompt
        prompt = CHAPTER_GENERATION_PROMPT.format(
            chapter_goal=params.chapter_goal or "继续故事发展",
            emotional_tone=params.emotional_tone or "中性",
            ending_hook=params.ending_hook or "设置悬念结尾",
            special_events=params.special_events or "无",
            target_words=params.target_words,
            dialogue_ratio=params.dialogue_ratio,
            pace=params.pace,
        )
        
        # Build full messages
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": context},
            {"role": "user", "content": prompt},
        ]
        
        # Stream from API
        accumulated_text = ""
        total_cost = 0.0
        
        for chunk_text, input_tokens, output_tokens, cost in self.api_client.chat_stream(
            messages=messages,
            temperature=params.temperature,
            max_tokens=params.target_words * 2,
        ):
            if chunk_text:  # Skip empty final chunk
                accumulated_text += chunk_text
                word_count = self._count_words(accumulated_text)
                total_cost = cost
                yield chunk_text, word_count, total_cost
