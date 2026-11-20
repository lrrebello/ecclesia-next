import uuid
from datetime import datetime, date
from sqlalchemy import String, Boolean, DateTime, Date, ForeignKey, Text, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


def uuid_default():
    return str(uuid.uuid4())


class Study(Base):
    __tablename__ = "studies"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_default)
    church_id: Mapped[str] = mapped_column(ForeignKey("churches.id"), nullable=False)
    ministry_id: Mapped[str | None] = mapped_column(ForeignKey("ministries.id"))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    cover_image: Mapped[str | None] = mapped_column(String(255))
    target_audience: Mapped[str] = mapped_column(String(50), default="adults")
    difficulty: Mapped[str] = mapped_column(String(30), default="beginner")
    is_kids_content: Mapped[bool] = mapped_column(Boolean, default=False)
    age_range: Mapped[str | None] = mapped_column(String(30))
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, onupdate=datetime.utcnow)

    modules = relationship("StudyModule", back_populates="study")


class StudyModule(Base):
    __tablename__ = "study_modules"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_default)
    study_id: Mapped[str] = mapped_column(ForeignKey("studies.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    order: Mapped[int] = mapped_column(Integer, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    study = relationship("Study", back_populates="modules")
    lessons = relationship("Lesson", back_populates="study_module")


class Lesson(Base):
    __tablename__ = "lessons"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_default)
    church_id: Mapped[str] = mapped_column(ForeignKey("churches.id"), nullable=False)
    study_module_id: Mapped[str] = mapped_column(ForeignKey("study_modules.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    scripture_reference: Mapped[str | None] = mapped_column(String(200))
    video_url: Mapped[str | None] = mapped_column(String(500))
    audio_url: Mapped[str | None] = mapped_column(String(500))
    image_path: Mapped[str | None] = mapped_column(String(255))
    order: Mapped[int] = mapped_column(Integer, default=1)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    study_module = relationship("StudyModule", back_populates="lessons")
    progress = relationship("LessonProgress", back_populates="lesson")
    highlights = relationship("Highlight", back_populates="lesson")
    notes = relationship("StudyNote", back_populates="lesson")
    quizzes = relationship("Quiz", back_populates="lesson")


class LessonProgress(Base):
    __tablename__ = "lesson_progress"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_default)
    lesson_id: Mapped[str] = mapped_column(ForeignKey("lessons.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    lesson = relationship("Lesson", back_populates="progress")
    user = relationship("User", foreign_keys=[user_id])


class Highlight(Base):
    __tablename__ = "highlights"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_default)
    lesson_id: Mapped[str] = mapped_column(ForeignKey("lessons.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    lesson = relationship("Lesson", back_populates="highlights")
    user = relationship("User", foreign_keys=[user_id])


class StudyNote(Base):
    __tablename__ = "study_notes"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_default)
    lesson_id: Mapped[str] = mapped_column(ForeignKey("lessons.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, onupdate=datetime.utcnow)

    lesson = relationship("Lesson", back_populates="notes")
    user = relationship("User", foreign_keys=[user_id])


class Quiz(Base):
    __tablename__ = "quizzes"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_default)
    church_id: Mapped[str] = mapped_column(ForeignKey("churches.id"), nullable=False)
    lesson_id: Mapped[str | None] = mapped_column(ForeignKey("lessons.id"))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    lesson = relationship("Lesson", back_populates="quizzes")
    questions = relationship("QuizQuestion", back_populates="quiz")
    attempts = relationship("QuizAttempt", back_populates="quiz")


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_default)
    quiz_id: Mapped[str] = mapped_column(ForeignKey("quizzes.id"), nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[list] = mapped_column(JSON, nullable=False)
    correct_option: Mapped[int] = mapped_column(Integer, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text)
    order: Mapped[int] = mapped_column(Integer, default=1)

    quiz = relationship("Quiz", back_populates="questions")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_default)
    quiz_id: Mapped[str] = mapped_column(ForeignKey("quizzes.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    answers: Mapped[dict] = mapped_column(JSON, nullable=False)
    score: Mapped[int] = mapped_column(Integer, default=0)
    total_questions: Mapped[int] = mapped_column(Integer, default=0)
    completed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    quiz = relationship("Quiz", back_populates="attempts")
    user = relationship("User", foreign_keys=[user_id])


class KidsContent(Base):
    __tablename__ = "kids_contents"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_default)
    church_id: Mapped[str] = mapped_column(ForeignKey("churches.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    topic: Mapped[str] = mapped_column(String(200), nullable=False)
    age_range: Mapped[str] = mapped_column(String(30), nullable=False)
    content_type: Mapped[str] = mapped_column(String(30), default="activity")
    content: Mapped[dict | None] = mapped_column(JSON)
    image_prompt: Mapped[str | None] = mapped_column(Text)
    image_path: Mapped[str | None] = mapped_column(String(255))
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
