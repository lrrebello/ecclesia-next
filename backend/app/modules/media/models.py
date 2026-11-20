import uuid
from datetime import datetime, date
from sqlalchemy import String, Boolean, DateTime, Date, ForeignKey, Text, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


def uuid_default():
    return str(uuid.uuid4())


class MediaAlbum(Base):
    __tablename__ = "media_albums"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_default)
    church_id: Mapped[str] = mapped_column(ForeignKey("churches.id"), nullable=False)
    ministry_id: Mapped[str | None] = mapped_column(ForeignKey("ministries.id"))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    cover_image: Mapped[str | None] = mapped_column(String(255))
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, onupdate=datetime.utcnow)

    items = relationship("MediaItem", back_populates="album")


class MediaItem(Base):
    __tablename__ = "media_items"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_default)
    church_id: Mapped[str] = mapped_column(ForeignKey("churches.id"), nullable=False)
    album_id: Mapped[str] = mapped_column(ForeignKey("media_albums.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    media_type: Mapped[str] = mapped_column(String(30), nullable=False)
    file_path: Mapped[str | None] = mapped_column(String(255))
    external_url: Mapped[str | None] = mapped_column(String(500))
    thumbnail_path: Mapped[str | None] = mapped_column(String(255))
    file_size: Mapped[int | None] = mapped_column(Integer)
    duration_seconds: Mapped[int | None] = mapped_column(Integer)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    album = relationship("MediaAlbum", back_populates="items")


class Devotional(Base):
    __tablename__ = "devotionals"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_default)
    church_id: Mapped[str] = mapped_column(ForeignKey("churches.id"), nullable=False)
    ministry_id: Mapped[str | None] = mapped_column(ForeignKey("ministries.id"))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    scripture_reference: Mapped[str | None] = mapped_column(String(200))
    scripture_text: Mapped[str | None] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    prayer: Mapped[str | None] = mapped_column(Text)
    author_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    publish_date: Mapped[date | None] = mapped_column(Date)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, onupdate=datetime.utcnow)

    author = relationship("User", foreign_keys=[author_id])
    readings = relationship("DevotionalReading", back_populates="devotional")


class DevotionalReading(Base):
    __tablename__ = "devotional_readings"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_default)
    devotional_id: Mapped[str] = mapped_column(ForeignKey("devotionals.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    read_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    devotional = relationship("Devotional", back_populates="readings")
    user = relationship("User", foreign_keys=[user_id])
