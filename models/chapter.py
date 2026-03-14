"""Chapter model - manages novel chapters."""

from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ai_xiaosuo.models import Base


class Chapter(Base):
    """Chapter model for storing generated chapters."""
    
    __tablename__ = "chapters"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    
    # Chapter info
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=True)
    volume: Mapped[str] = mapped_column(String(100), nullable=True)  # Volume name
    
    # Content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # AI generation metadata
    chapter_goal: Mapped[str] = mapped_column(Text, nullable=True)  # User's goal for this chapter
    emotional_tone: Mapped[str] = mapped_column(String(50), nullable=True)  # emotional tone
    ending_hook: Mapped[str] = mapped_column(Text, nullable=True)  # Ending hook
    
    # Summary (for context assembly)
    summary: Mapped[str] = mapped_column(Text, nullable=True)  # ~100 words summary
    
    # Quality metrics
    quality_score: Mapped[float] = mapped_column(Float, nullable=True)
    
    # Cost tracking
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    cost: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Status
    is_verified: Mapped[bool] = mapped_column(default=False)  # User verified
    is_memory_updated: Mapped[bool] = mapped_column(default=False)  # Memory updated
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="chapters")
    
    def __repr__(self):
        return f"<Chapter(id={self.id}, number={self.number}, title='{self.title}')>"
