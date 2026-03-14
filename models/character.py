"""Character model - manages novel characters."""

from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ai_xiaosuo.models import Base


class Character(Base):
    """Character model for tracking character status."""
    
    __tablename__ = "characters"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    
    # Basic info
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=True)  # protagonist, antagonist, supporting
    alias: Mapped[str] = mapped_column(String(100), nullable=True)  # Nicknames
    
    # Appearance
    appearance: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Personality
    personality: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Background
    background: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Current status (dynamic - updated by memory updater)
    current_location: Mapped[str] = mapped_column(String(200), nullable=True)
    cultivation_realm: Mapped[str] = mapped_column(String(100), nullable=True)  # For xianxia
    level: Mapped[int] = mapped_column(Integer, nullable=True)  # Level/grade
    
    # Equipment/items
    equipment: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string of items
    
    # Relationships
    relationships: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string
    
    # Status tracking
    is_alive: Mapped[bool] = mapped_column(default=True)
    last_chapter_id: Mapped[int] = mapped_column(Integer, nullable=True)  # Last appearance
    
    # Notes
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="characters")
    
    def __repr__(self):
        return f"<Character(id={self.id}, name='{self.name}', role='{self.role}')>"
