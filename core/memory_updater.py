"""Memory updater - updates story memory after chapter confirmation."""

import json
import re
from typing import Optional
from sqlalchemy.orm import Session

from ai_xiaosuo.models import Project, Chapter, Character, Event, Foreshadowing
from ai_xiaosuo.api.minimax_client import MiniMaxClient
from ai_xiaosuo.api.prompts import (
    MEMORY_UPDATE_PROMPT,
    CHAPTER_SUMMARY_PROMPT,
    CHARACTER_EXTRACTION_PROMPT,
)


class MemoryUpdater:
    """Updates story memory after chapter is confirmed by user."""
    
    def __init__(self, session: Session, api_client: Optional[MiniMaxClient] = None):
        """Initialize memory updater.
        
        Args:
            session: Database session
            api_client: MiniMax API client
        """
        self.session = session
        self.api_client = api_client or MiniMaxClient()
    
    def _extract_json_from_response(self, text: str) -> Optional[dict]:
        """Extract JSON from AI response that might contain extra text.
        
        Args:
            text: AI response text
            
        Returns:
            Parsed JSON dict or None
        """
        # Try to find JSON in the response
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Try parsing the whole response
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None
    
    def _count_words(self, text: str) -> int:
        """Count Chinese characters + English words in text."""
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        english_words = len(re.findall(r'[a-zA-Z]+', text))
        return chinese_chars + english_words
    
    def generate_summary(self, chapter_content: str) -> str:
        """Generate chapter summary.
        
        Args:
            chapter_content: Chapter content
            
        Returns:
            Summary string (~100 words)
        """
        # Truncate if too long
        content = chapter_content[:3000]
        
        prompt = CHAPTER_SUMMARY_PROMPT.format(chapter_content=content)
        
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        result, _, _, _ = self.api_client.chat(messages, temperature=0.5, max_tokens=300)
        
        # Clean result
        summary = result.strip()
        
        # Ensure it's not too long
        words = self._count_words(summary)
        if words > 150:
            # Truncate to ~100 words
            summary = summary[:200] + "..."
        
        return summary
    
    def extract_character_updates(self, chapter_content: str) -> list[dict]:
        """Extract character status changes from chapter.
        
        Args:
            chapter_content: Chapter content
            
        Returns:
            List of character update dicts
        """
        # Truncate if too long
        content = chapter_content[:3000]
        
        prompt = CHARACTER_EXTRACTION_PROMPT.format(chapter_content=content)
        
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        result, _, _, _ = self.api_client.chat(messages, temperature=0.3, max_tokens=1000)
        
        # Parse JSON
        data = self._extract_json_from_response(result)
        
        if not data:
            return []
        
        # Convert to list format
        updates = []
        for name, changes in data.get("character_name", {}).items():
            updates.append({
                "name": name,
                "status_changed": changes.get("status_changed", False),
                "location_change": changes.get("location_change"),
                "realm_change": changes.get("realm_change"),
                "equipment_changes": changes.get("equipment_changes", []),
                "relationship_changes": changes.get("relationship_changes", []),
            })
        
        return updates
    
    def analyze_chapter_for_memory(
        self,
        chapter_content: str,
        chapter_number: int,
    ) -> dict:
        """Analyze chapter to extract memory information.
        
        Args:
            chapter_content: Chapter content
            chapter_number: Chapter number
            
        Returns:
            Dict with summary, character_updates, new_events, foreshadowings
        """
        # Truncate if too long
        content = chapter_content[:4000]
        
        prompt = MEMORY_UPDATE_PROMPT.format(
            chapter_content=content,
            chapter_number=chapter_number,
        )
        
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        result, _, _, _ = self.api_client.chat(messages, temperature=0.3, max_tokens=2000)
        
        # Parse JSON
        data = self._extract_json_from_response(result)
        
        if not data:
            return {
                "summary": "",
                "character_updates": [],
                "new_events": [],
                "foreshadowings": [],
            }
        
        return {
            "summary": data.get("summary", ""),
            "character_updates": data.get("character_updates", []),
            "new_events": data.get("new_events", []),
            "foreshadowings": data.get("foreshadowings", []),
        }
    
    def update_memory(
        self,
        project_id: int,
        chapter_id: int,
        user_confirmed: bool = True,
    ) -> dict:
        """Update story memory after user confirms chapter.
        
        This is the main entry point - user must confirm before memory updates.
        
        Args:
            project_id: Project ID
            chapter_id: Chapter ID to update memory from
            user_confirmed: Whether user confirmed this chapter
            
        Returns:
            Dict with update results
        """
        if not user_confirmed:
            return {"status": "pending_confirmation", "message": "等待用户确认"}
        
        # Get chapter
        chapter = self.session.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not chapter:
            raise ValueError(f"Chapter {chapter_id} not found")
        
        if chapter.is_memory_updated:
            return {"status": "already_updated", "message": "记忆已更新"}
        
        # Generate summary
        summary = self.generate_summary(chapter.content)
        chapter.summary = summary
        
        # Analyze for memory
        memory_data = self.analyze_chapter_for_memory(
            chapter.content, chapter.number
        )
        
        # Update chapter summary in DB
        chapter.summary = memory_data.get("summary", summary)
        
        # Update character statuses
        for char_update in memory_data.get("character_updates", []):
            character = self.session.query(Character).filter(
                Character.project_id == project_id,
                Character.name == char_update["name"]
            ).first()
            
            if character:
                if char_update.get("location_change"):
                    character.current_location = char_update["location_change"]
                if char_update.get("realm_change"):
                    character.cultivation_realm = char_update["realm_change"]
                character.last_chapter_id = chapter_id
        
        # Add new events
        for event_data in memory_data.get("new_events", []):
            event = Event(
                project_id=project_id,
                name=event_data.get("name", "未命名事件"),
                description=event_data.get("description"),
                chapter_id=chapter_id,
                event_type="plot",
                significance="minor",
            )
            self.session.add(event)
        
        # Add foreshadowings
        for foreshadow_data in memory_data.get("foreshadowings", []):
            foreshadow = Foreshadowing(
                project_id=project_id,
                content=foreshadow_data.get("content", ""),
                hint_type=foreshadow_data.get("type", "description"),
                chapter_id=chapter_id,
                importance="medium",
            )
            self.session.add(foreshadow)
        
        # Mark chapter as memory updated
        chapter.is_memory_updated = True
        
        # Commit changes
        self.session.commit()
        
        return {
            "status": "success",
            "summary": chapter.summary,
            "character_updates_count": len(memory_data.get("character_updates", [])),
            "events_count": len(memory_data.get("new_events", [])),
            "foreshadowings_count": len(memory_data.get("foreshadowings", [])),
        }
