"""SQLAlchemy ORM tables for persistence layer."""

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class RunTable(Base):
    """Database table storing content generation pipeline runs."""

    __tablename__ = "runs"

    id = Column(String(64), primary_key=True)
    topic = Column(String(512), nullable=False)
    content_type = Column(String(64), nullable=False)
    target_audience = Column(String(512), nullable=True)
    target_word_count = Column(Integer, default=500)
    actual_word_count = Column(Integer, default=0)
    title = Column(String(512), nullable=True)
    markdown_content = Column(Text, nullable=True)
    workflow_status = Column(String(64), default="in_progress")
    export_ready = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
