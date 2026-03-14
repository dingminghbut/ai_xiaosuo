"""Project model - manages novel projects."""

from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ai_xiaosuo.models import Base


class Project(Base):
    """Novel project model."""
    
    __tablename__ = "projects"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    genre: Mapped[str] = mapped_column(String(50), nullable=True)  # fantasy, urban, etc.
    target_platform: Mapped[str] = mapped_column(String(50), nullable=True)  # tomato, etc.
    
    # Settings
    world_setting: Mapped[str] = mapped_column(Text, nullable=True)  # World background
    protagonist_setting: Mapped[str] = mapped_column(Text, nullable=True)  # Protagonist details
    style_requirement: Mapped[str] = mapped_column(Text, nullable=True)  # Writing style
    
    # Stats
    total_words: Mapped[int] = mapped_column(Integer, default=0)
    total_chapters: Mapped[int] = mapped_column(Integer, default=0)
    
    # Cost tracking
    total_cost: Mapped[float] = mapped_column(Float, default=0.0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    api_call_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    chapters: Mapped[list["Chapter"]] = relationship(
        "Chapter", back_populates="project", cascade="all, delete-orphan"
    )
    characters: Mapped[list["Character"]] = relationship(
        "Character", back_populates="project", cascade="all, delete-orphan"
    )
    outlines: Mapped[list["Outline"]] = relationship(
        "Outline", back_populates="project", cascade="all, delete-orphan"
    )
    events: Mapped[list["Event"]] = relationship(
        "Event", back_populates="project", cascade="all, delete-orphan"
    )
    foreshadowings: Mapped[list["Foreshadowing"]] = relationship(
        "Foreshadowing", back_populates="project", cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}')>"
