"""Consistency checker - checks content consistency with settings."""

import json
import re
from typing import Optional
from dataclasses import dataclass
from sqlalchemy.orm import Session

from ai_xiaosuo.api.minimax_client import MiniMaxClient
from ai_xiaosuo.api.prompts import CONSISTENCY_CHECK_PROMPT
from ai_xiaosuo.models import Project, Character, Event


@dataclass
class ConsistencyIssue:
    """Represents a consistency issue."""
    issue_type: str
    description: str
    severity: str  # high, medium, low
    location: Optional[str] = None


@dataclass
class ConsistencyCheckResult:
    """Result of consistency check."""
    is_passed: bool
    issues: list[ConsistencyIssue]
    score: float  # 0.0 to 1.0


class ConsistencyChecker:
    """Checks chapter content consistency with project settings."""
    
    def __init__(self, session: Session, api_client: Optional[MiniMaxClient] = None):
        """Initialize consistency checker.
        
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
    
    def _quick_check_dead_characters(
        self,
        chapter_content: str,
        characters: list[Character],
    ) -> list[ConsistencyIssue]:
        """Quick check: detect if dead characters appear alive in content."""
        issues = []
        
        for char in characters:
            if not char.is_alive:
                # Check if character appears in content
                if char.name in chapter_content:
                    # More detailed check needed
                    issues.append(ConsistencyIssue(
                        issue_type="dead_character_appearance",
                        description=f"已死亡角色 '{char.name}' 出现在本章内容中",
                        severity="high",
                        location=f"角色: {char.name}"
                    ))
        
        return issues
    
    def _quick_check_character_realms(
        self,
        chapter_content: str,
        characters: list[Character],
    ) -> list[ConsistencyIssue]:
        """Quick check: detect realm/level contradictions."""
        issues = []
        
        # Simple keyword matching for cultivation realms
        realm_keywords = {
            "qi": ["练气", "聚气"],
            "foundation": ["筑基"],
            "core": ["金丹", "结丹"],
            "nascent": ["元婴", "化神"],
            "immortal": ["飞升", "仙人"],
        }
        
        for char in characters:
            if char.cultivation_realm:
                # Check if content mentions a higher/lower realm
                current_realm = char.cultivation_realm.lower()
                
                for realm_name, keywords in realm_keywords.items():
                    if realm_name in current_realm:
                        # Check if content mentions contradictory realms
                        for kw in keywords:
                            if kw in chapter_content and kw not in current_realm:
                                issues.append(ConsistencyIssue(
                                    issue_type="realm_contradiction",
                                    description=f"角色 '{char.name}' 当前境界为 {char.cultivation_realm}，但本章提到 {kw}",
                                    severity="medium",
                                    location=f"角色: {char.name}"
                                ))
        
        return issues
    
    def check(
        self,
        project_id: int,
        chapter_content: str,
        use_ai: bool = True,
    ) -> ConsistencyCheckResult:
        """Check consistency of chapter content.
        
        Args:
            project_id: Project ID
            chapter_content: Chapter content to check
            use_ai: Whether to use AI for deep checking
            
        Returns:
            ConsistencyCheckResult
        """
        # Get project and characters
        project = self.session.query(Project).filter(Project.id == project_id).first()
        if not project:
            return ConsistencyCheckResult(
                is_passed=False,
                issues=[ConsistencyIssue("project_not_found", "项目不存在", "high")],
                score=0.0
            )
        
        # Get living characters
        characters = self.session.query(Character).filter(
            Character.project_id == project_id
        ).all()
        
        # Quick checks first
        all_issues = []
        all_issues.extend(self._quick_check_dead_characters(chapter_content, characters))
        all_issues.extend(self._quick_check_character_realms(chapter_content, characters))
        
        # AI deep check if enabled
        if use_ai and len(chapter_content) > 500:
            try:
                ai_issues = self._ai_check(project, characters, chapter_content)
                all_issues.extend(ai_issues)
            except Exception:
                pass  # Silently fail AI check if it errors
        
        # Calculate score
        if not all_issues:
            score = 1.0
            is_passed = True
        else:
            high_count = sum(1 for i in all_issues if i.severity == "high")
            medium_count = sum(1 for i in all_issues if i.severity == "medium")
            
            if high_count > 0:
                score = 0.3
                is_passed = False
            elif medium_count > 0:
                score = 0.6
                is_passed = False
            else:
                score = 0.8
                is_passed = True
        
        return ConsistencyCheckResult(
            is_passed=is_passed,
            issues=all_issues,
            score=score,
        )
    
    def _ai_check(
        self,
        project: Project,
        characters: list[Character],
        chapter_content: str,
    ) -> list[ConsistencyIssue]:
        """Use AI to check consistency deeply.
        
        Args:
            project: Project instance
            characters: List of characters
            chapter_content: Chapter content
            
        Returns:
            List of ConsistencyIssue
        """
        # Build character status string
        char_status = "\n".join([
            f"- {c.name}: 境界={c.cultivation_realm or '未设定'}, "
            f"位置={c.current_location or '未设定'}, "
            f"存活={'是' if c.is_alive else '否'}"
            for c in characters[:10]  # Limit to first 10
        ])
        
        prompt = CONSISTENCY_CHECK_PROMPT.format(
            world_setting=project.world_setting or "（无）",
            character_status=char_status,
            chapter_content=chapter_content[:3000],  # Truncate if needed
        )
        
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        result, _, _, _ = self.api_client.chat(messages, temperature=0.3, max_tokens=1500)
        
        # Parse JSON
        data = self._extract_json_from_response(result)
        
        if not data:
            return []
        
        # Convert to ConsistencyIssue objects
        issues = []
        for item in data.get("issues", []):
            issues.append(ConsistencyIssue(
                issue_type=item.get("type", "unknown"),
                description=item.get("description", ""),
                severity=item.get("severity", "low"),
            ))
        
        return issues
