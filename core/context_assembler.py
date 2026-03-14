"""Context assembler - assembles 5-layer context for chapter generation."""

from typing import Optional
from sqlalchemy.orm import Session

from ai_xiaosuo.models import Project, Chapter, Character, Event, Outline
from ai_xiaosuo.api.prompts import CONTEXT_ASSEMBLY_PROMPT
from ai_xiaosuo.config import (
    CONTEXT_LAYER_1_PERMANENT,
    CONTEXT_LAYER_2_OUTLINE,
    CONTEXT_LAYER_3_CHARACTERS,
    CONTEXT_LAYER_4_EVENTS,
    CONTEXT_LAYER_5_RECENT,
)


class ContextAssembler:
    """Assembles 5-layer context for chapter generation."""
    
    def __init__(self, session: Session):
        """Initialize context assembler.
        
        Args:
            session: Database session
        """
        self.session = session
    
    def _get_permanent_setting(self, project: Project) -> str:
        """Get layer 1: permanent settings (world, protagonist, style).
        
        Args:
            project: Project instance
            
        Returns:
            Formatted permanent settings string
        """
        parts = []
        
        if project.world_setting:
            parts.append(f"世界观设定：\n{project.world_setting[:CONTEXT_LAYER_1_PERMANENT]}")
        
        if project.protagonist_setting:
            parts.append(f"主角设定：\n{project.protagonist_setting[:500]}")
        
        if project.style_requirement:
            parts.append(f"文风要求：\n{project.style_requirement[:500]}")
        
        return "\n\n".join(parts) if parts else "（暂无设定）"
    
    def _get_outline_context(self, project: Project, current_chapter: int) -> str:
        """Get layer 2: outline context (volume goals + nearby chapter summaries).
        
        Args:
            project: Project instance
            current_chapter: Current chapter number
            
        Returns:
            Formatted outline context
        """
        # Get current volume/arc
        outlines = self.session.query(Outline).filter(
            Outline.project_id == project.id,
            Outline.outline_type == "volume"
        ).order_by(Outline.target_chapter_start).all()
        
        current_volume = None
        for outline in outlines:
            if (outline.target_chapter_start and 
                outline.target_chapter_start <= current_chapter <= (outline.target_chapter_end or 9999)):
                current_volume = outline
                break
        
        volume_context = ""
        if current_volume:
            volume_context = f"当前卷目标：{current_volume.title}\n"
            if current_volume.description:
                volume_context += f"卷描述：{current_volume.description[:300]}\n"
            if current_volume.goals:
                volume_context += f"卷目标：{current_volume.goals[:200]}"
        
        # Get nearby chapter summaries (±3 chapters)
        nearby_summaries = []
        for ch_num in range(max(1, current_chapter - 3), current_chapter + 4):
            if ch_num == current_chapter:
                continue
            chapter = self.session.query(Chapter).filter(
                Chapter.project_id == project.id,
                Chapter.number == ch_num,
                Chapter.is_verified == True
            ).first()
            
            if chapter:
                summary = chapter.summary or f"第{ch_num}章"
                nearby_summaries.append(f"第{ch_num}章：{summary[:100]}")
        
        nearby_text = "\n".join(nearby_summaries) if nearby_summaries else "（暂无前后章节）"
        
        return f"{volume_context}\n\n前后章节摘要：\n{nearby_text}"[:CONTEXT_LAYER_2_OUTLINE]
    
    def _get_character_context(self, project: Project) -> str:
        """Get layer 3: character status snapshot.
        
        Args:
            project: Project instance
            
        Returns:
            Formatted character context
        """
        characters = self.session.query(Character).filter(
            Character.project_id == project.id,
            Character.is_alive == True
        ).all()
        
        if not characters:
            return "（暂无人物信息）"
        
        char_parts = []
        for char in characters:
            parts = [f"【{char.name}】"]
            if char.role:
                parts.append(f"角色：{char.role}")
            if char.cultivation_realm:
                parts.append(f"境界：{char.cultivation_realm}")
            if char.level:
                parts.append(f"等级：{char.level}")
            if char.current_location:
                parts.append(f"位置：{char.current_location}")
            if char.equipment:
                parts.append(f"装备：{char.equipment[:100]}")
            if char.relationships:
                parts.append(f"关系：{char.relationships[:100]}")
            
            char_parts.append(" | ".join(parts))
        
        return "\n\n".join(char_parts)[:CONTEXT_LAYER_3_CHARACTERS]
    
    def _get_event_context(self, project: Project, current_chapter: int) -> str:
        """Get layer 4: key events related to current chapter.
        
        Args:
            project: Project instance
            current_chapter: Current chapter number
            
        Returns:
            Formatted event context
        """
        # Get events that happened in the last 10 chapters or unresolved
        events = self.session.query(Event).filter(
            Event.project_id == project.id,
            Event.is_resolved == False
        ).order_by(Event.chapter_id.desc()).limit(10).all()
        
        # Also get events that happened in nearby chapters
        recent_events = self.session.query(Event).filter(
            Event.project_id == project.id,
            Event.chapter_id >= current_chapter - 10,
            Event.chapter_id <= current_chapter
        ).all()
        
        # Combine and deduplicate
        event_dict = {e.id: e for e in events + recent_events}
        
        if not event_dict:
            return "（暂无关键事件）"
        
        event_parts = []
        for event in list(event_dict.values())[:5]:
            parts = [f"【{event.name}】({event.event_type})"]
            if event.description:
                parts.append(f"描述：{event.description[:150]}")
            if event.participants:
                parts.append(f"参与者：{event.participants[:100]}")
            if event.impact:
                parts.append(f"影响：{event.impact[:100]}")
            event_parts.append(" | ".join(parts))
        
        return "\n\n".join(event_parts)[:CONTEXT_LAYER_4_EVENTS]
    
    def _get_recent_content(self, project: Project, current_chapter: int) -> str:
        """Get layer 5: recent 3 chapters full text.
        
        Args:
            project: Project instance
            current_chapter: Current chapter number
            
        Returns:
            Formatted recent content
        """
        # Get last 3 verified chapters
        chapters = self.session.query(Chapter).filter(
            Chapter.project_id == project.id,
            Chapter.number < current_chapter,
            Chapter.is_verified == True
        ).order_by(Chapter.number.desc()).limit(3).all()
        
        if not chapters:
            return "（暂无前文）"
        
        # Reverse to get them in chronological order
        chapters = list(reversed(chapters))
        
        content_parts = []
        for chapter in chapters:
            header = f"=== 第{chapter.number}章 {chapter.title or ''} ===\n"
            content_parts.append(header + chapter.content[:1500])
        
        result = "\n\n".join(content_parts)
        
        # If still too long, truncate
        if len(result) > CONTEXT_LAYER_5_RECENT * 2:  # Approximate
            result = result[:CONTEXT_LAYER_5_RECENT * 2]
        
        return result
    
    def assemble_context(
        self,
        project: Project,
        current_chapter: int,
    ) -> tuple[str, dict]:
        """Assemble full context for chapter generation.
        
        Args:
            project: Project instance
            current_chapter: Current chapter number to generate
            
        Returns:
            Tuple of (assembled_context, layer_info_dict)
        """
        # Build each layer
        layer1 = self._get_permanent_setting(project)
        layer2 = self._get_outline_context(project, current_chapter)
        layer3 = self._get_character_context(project)
        layer4 = self._get_event_context(project, current_chapter)
        layer5 = self._get_recent_content(project, current_chapter)
        
        # Assemble full context
        full_context = CONTEXT_ASSEMBLY_PROMPT.format(
            world_setting=layer1,
            outline_context=layer2,
            character_context=layer3,
            event_context=layer4,
            recent_content=layer5,
        )
        
        layer_info = {
            "layer1_permanent": layer1,
            "layer2_outline": layer2,
            "layer3_characters": layer3,
            "layer4_events": layer4,
            "layer5_recent": layer5,
            "total_estimated_chars": len(layer1 + layer2 + layer3 + layer4 + layer5),
        }
        
        return full_context, layer_info
    
    def get_context_for_generation(
        self,
        project_id: int,
        current_chapter: int,
    ) -> tuple[str, dict]:
        """Get context for chapter generation by project ID.
        
        Args:
            project_id: Project ID
            current_chapter: Current chapter number
            
        Returns:
            Tuple of (assembled_context, layer_info_dict)
        """
        project = self.session.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        return self.assemble_context(project, current_chapter)
