"""Event model - manages key events in the novel."""

from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ai_xiaosuo.models import Base


class Event(Base):
    """Event model for tracking key story events."""
    
    __tablename__ = "events"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    
    # Event info
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=True)  # battle, discovery, plot, etc.
    chapter_id: Mapped[int] = mapped_column(Integer, nullable=True)  # First appearance
    
    # Event details
    description: Mapped[str] = mapped_column(Text, nullable=True)
    significance: Mapped[str] = mapped_column(String(50), nullable=True)  # major, minor, turning_point
    
    # Participants
    participants: Mapped[str] = mapped_column(Text, nullable=True)  # JSON array of character names
    
    # Impact
    impact: Mapped[str] = mapped_column(Text, nullable=True)  # How it affects the story
    
    # Status
    is_resolved: Mapped[bool] = mapped_column(default=False)
    resolved_chapter_id: Mapped[int] = mapped_column(Integer, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="events")
    
    def __repr__(self):
        return f"<Event(id={self.id}, name='{self.name}', type='{self.event_type}')>"
