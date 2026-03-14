"""Outline model - manages novel outlines."""

from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ai_xiaosuo.models import Base


class Outline(Base):
    """Outline model for managing volume/chapter outlines."""
    
    __tablename__ = "outlines"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    
    # Outline structure
    outline_type: Mapped[str] = mapped_column(String(20), nullable=False)  # volume, arc, chapter
    parent_id: Mapped[int] = mapped_column(Integer, nullable=True)  # Parent outline ID
    
    # Content
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    goals: Mapped[str] = mapped_column(Text, nullable=True)  # What should be achieved
    
    # Timeline
    target_chapter_start: Mapped[int] = mapped_column(Integer, nullable=True)
    target_chapter_end: Mapped[int] = mapped_column(Integer, nullable=True)
    
    # Status
    is_completed: Mapped[bool] = mapped_column(default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="outlines")
    
    def __repr__(self):
        return f"<Outline(id={self.id}, title='{self.title}', type='{self.outline_type}')>"
