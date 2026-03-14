"""Cost tracker - tracks API usage and costs."""

from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass
from sqlalchemy.orm import Session

from ai_xiaosuo.models import Project
from ai_xiaosuo.config import DAILY_TOKEN_LIMIT


@dataclass
class CostStats:
    """Cost statistics."""
    total_cost: float
    total_tokens: int
    api_call_count: int
    daily_cost: float
    daily_tokens: int
    daily_calls: int


class CostTracker:
    """Tracks API usage and costs."""
    
    def __init__(self, session: Session):
        """Initialize cost tracker.
        
        Args:
            session: Database session
        """
        self.session = session
    
    def record_usage(
        self,
        project_id: int,
        input_tokens: int,
        output_tokens: int,
        cost: float,
    ):
        """Record API usage for a project.
        
        Args:
            project_id: Project ID
            input_tokens: Input tokens used
            output_tokens: Output tokens used
            cost: Cost in USD
        """
        project = self.session.query(Project).filter(Project.id == project_id).first()
        
        if project:
            project.total_tokens += input_tokens + output_tokens
            project.total_cost += cost
            project.api_call_count += 1
            project.updated_at = datetime.now()
            
            self.session.commit()
    
    def get_project_stats(self, project_id: int) -> CostStats:
        """Get cost stats for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            CostStats object
        """
        project = self.session.query(Project).filter(Project.id == project_id).first()
        
        if not project:
            return CostStats(0, 0, 0, 0, 0, 0)
        
        return CostStats(
            total_cost=project.total_cost,
            total_tokens=project.total_tokens,
            api_call_count=project.api_call_count,
            daily_cost=0,  # Would need date tracking
            daily_tokens=0,
            daily_calls=0,
        )
    
    def check_daily_limit(self, project_id: int) -> tuple[bool, int]:
        """Check if daily token limit would be exceeded.
        
        Args:
            project_id: Project ID
            
        Returns:
            Tuple of (is_within_limit, remaining_tokens)
        """
        # This would need date tracking in the database
        # For now, just check against total
        project = self.session.query(Project).filter(Project.id == project_id).first()
        
        if not project:
            return True, DAILY_TOKEN_LIMIT
        
        # Estimate daily usage (simplified - assumes all usage is today)
        remaining = DAILY_TOKEN_LIMIT - project.total_tokens
        
        return remaining > 0, max(0, remaining)
    
    def get_cost_summary(self, project_id: int) -> dict:
        """Get cost summary for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Dict with cost summary
        """
        project = self.session.query(Project).filter(Project.id == project_id).first()
        
        if not project:
            return {
                "total_cost": 0,
                "total_tokens": 0,
                "api_calls": 0,
                "avg_cost_per_1k_tokens": 0,
                "estimated_chapters": 0,
            }
        
        avg_cost = 0
        if project.total_tokens > 0:
            avg_cost = (project.total_cost / project.total_tokens) * 1000
        
        # Estimate chapters based on avg 3000 tokens per chapter
        estimated_chapters = project.total_tokens // 3000
        
        return {
            "total_cost": round(project.total_cost, 4),
            "total_tokens": project.total_tokens,
            "api_calls": project.api_call_count,
            "avg_cost_per_1k_tokens": round(avg_cost, 4),
            "estimated_chapters": estimated_chapters,
        }
    
    def format_cost_report(self, project_id: int) -> str:
        """Format a cost report string.
        
        Args:
            project_id: Project ID
            
        Returns:
            Formatted report string
        """
        summary = self.get_cost_summary(project_id)
        
        report = f"""=== 成本报告 ===
总消耗: ${summary['total_cost']:.4f}
Token使用: {summary['total_tokens']:,}
API调用次数: {summary['api_calls']}
平均每千Token: ${summary['avg_cost_per_1k_tokens']:.4f}
预计产出章节: {summary['estimated_chapters']}
"""
        
        return report


class DailyBudget:
    """Manages daily budget for API calls."""
    
    def __init__(self, daily_limit: int = DAILY_TOKEN_LIMIT, warning_threshold: float = 0.8):
        """Initialize daily budget.
        
        Args:
            daily_limit: Daily token limit
            warning_threshold: Warning threshold (0.0 to 1.0)
        """
        self.daily_limit = daily_limit
        self.warning_threshold = warning_threshold
        self._today_usage = 0
    
    def add_usage(self, tokens: int):
        """Add token usage for today.
        
        Args:
            tokens: Tokens to add
        """
        self._today_usage += tokens
    
    def get_remaining(self) -> int:
        """Get remaining tokens for today.
        
        Returns:
            Remaining tokens
        """
        return max(0, self.daily_limit - self._today_usage)
    
    def get_usage_ratio(self) -> float:
        """Get usage ratio for today.
        
        Returns:
            Usage ratio (0.0 to 1.0)
        """
        return self._today_usage / self.daily_limit
    
    def is_over_limit(self) -> bool:
        """Check if over daily limit.
        
        Returns:
            True if over limit
        """
        return self._today_usage >= self.daily_limit
    
    def should_warn(self) -> bool:
        """Check if should warn about usage.
        
        Returns:
            True if should warn
        """
        return self.get_usage_ratio() >= self.warning_threshold
    
    def reset(self):
        """Reset daily usage."""
        self._today_usage = 0
