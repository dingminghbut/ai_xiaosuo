"""Foreshadowing model - manages story foreshadowing."""

from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ai_xiaosuo.models import Base


class Foreshadowing(Base):
    """Foreshadowing model for tracking hints and setups."""
    
    __tablename__ = "foreshadowings"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    
    # Foreshadowing info
    content: Mapped[str] = mapped_column(Text, nullable=False)  # The hint/setup
    hint_type: Mapped[str] = mapped_column(String(50), nullable=True)  # dialogue, action, description
    
    # Origin
    chapter_id: Mapped[int] = mapped_column(Integer, nullable=False)  # Where it's introduced
    
    # Resolution
    resolution: Mapped[str] = mapped_column(Text, nullable=True)  # How it's resolved
    resolved_chapter_id: Mapped[int] = mapped_column(Integer, nullable=True)
    
    # Status
    is_resolved: Mapped[bool] = mapped_column(default=False)
    
    # Importance
    importance: Mapped[str] = mapped_column(String(20), nullable=True)  # high, medium, low
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="foreshadowings")
    
    def __repr__(self):
        return f"<Foreshadowing(id={self.id}, chapter_id={self.chapter_id})>"
