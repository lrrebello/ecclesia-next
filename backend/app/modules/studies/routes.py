from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.models import AuditLog, Ministry, User
from app.db.base import get_db
from app.modules.studies.ai_service import (
    build_image_prompt,
    build_kids_activity_prompt,
    build_quiz_prompt,
    build_summary_prompt,
    generate_structured_content,
)
from app.modules.studies.models import (
    KidsContent,
    Lesson,
    LessonProgress,
    Quiz,
    QuizAttempt,
    QuizQuestion,
    Study,
    StudyModule,
)

router = APIRouter(prefix="/studies", tags=["Estudos, Quizzes e Kids"])


class StudyInput(BaseModel):
    title: str
    description: str | None = None
    ministry_id: str | None = None
    target_audience: str = "adults"
    difficulty: str = "beginner"
    is_kids_content: bool = False
    age_range: str | None = None
    is_published: bool = False


class ModuleInput(BaseModel):
    study_id: str
    title: str
    description: str | None = None
    order: int = 1


class LessonInput(BaseModel):
    study_module_id: str
    title: str
    content: str
    scripture_reference: str | None = None
    video_url: str | None = None
    audio_url: str | None = None
    order: int = 1
    is_published: bool = False


class QuizInput(BaseModel):
    lesson_id: str
    title: str
    description: str | None = None
    question_count: int = 5
    difficulty: str = "beginner"


class QuizAnswerInput(BaseModel):
    answers: dict[str, int]


class KidsContentInput(BaseModel):
    title: str
    topic: str
    age_range: str
    content_type: str = "activity"


def serialize_study(study: Study) -> dict:
    return {
        "id": study.id,
        "title": study.title,
        "description": study.description,
        "target_audience": study.target_audience,
        "difficulty": study.difficulty,
        "is_kids_content": study.is_kids_content,
        "age_range": study.age_range,
        "is_published": study.is_published,
        "modules": [
            {
                "id": module.id,
                "title": module.title,
                "order": module.order,
                "lessons": [
                    {
                        "id": lesson.id,
                        "title": lesson.title,
                        "order": lesson.order,
                    }
                    for lesson in module.lessons
                    if lesson.is_active and lesson.is_published
                ],
            }
            for module in study.modules
            if module.is_active
        ],
    }


def serialize_quiz(quiz: Quiz) -> dict:
    return {
        "id": quiz.id,
        "title": quiz.title,
        "description": quiz.description,
        "lesson_id": quiz.lesson_id,
        "questions": [
            {
                "id": question.id,
                "question": question.question,
                "options": question.options,
            }
            for question in quiz.questions
        ],
    }


@router.get("")
def list_studies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    studies = db.query(Study).filter_by(
        church_id=current_user.church_id,
        is_active=True,
        is_published=True,
    ).order_by(Study.created_at.desc()).all()

    return {"studies": [serialize_study(study) for study in studies]}


@router.post("")
def create_study(
    payload: StudyInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ministry = None

    if payload.ministry_id:
        ministry = db.query(Ministry).filter_by(
            id=payload.ministry_id,
            church_id=current_user.church_id,
        ).first()

        if not ministry:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Ministério não encontrado")

    study = Study(
        church_id=current_user.church_id,
        ministry_id=ministry.id if ministry else None,
        title=payload.title.strip(),
        description=payload.description,
        target_audience=payload.target_audience,
        difficulty=payload.difficulty,
        is_kids_content=payload.is_kids_content,
        age_range=payload.age_range,
        is_published=payload.is_published,
        created_by=current_user.id,
    )

    db.add(study)
    db.commit()
    db.refresh(study)

    return serialize_study(study)


@router.post("/modules")
def create_module(
    payload: ModuleInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    study = db.query(Study).filter_by(
        id=payload.study_id,
        church_id=current_user.church_id,
    ).first()

    if not study:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Estudo não encontrado")

    module = StudyModule(
        study_id=study.id,
        title=payload.title.strip(),
        description=payload.description,
        order=payload.order,
    )

    db.add(module)
    db.commit()
    db.refresh(module)

    return {"id": module.id, "title": module.title}


@router.post("/lessons")
def create_lesson(
    payload: LessonInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    module = db.query(StudyModule).join(Study).filter(
        StudyModule.id == payload.study_module_id,
        Study.church_id == current_user.church_id,
    ).first()

    if not module:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Módulo não encontrado")

    lesson = Lesson(
        church_id=current_user.church_id,
        study_module_id=module.id,
        title=payload.title.strip(),
        content=payload.content,
        scripture_reference=payload.scripture_reference,
        video_url=payload.video_url,
        audio_url=payload.audio_url,
        order=payload.order,
        is_published=payload.is_published,
    )

    db.add(lesson)
    db.commit()
    db.refresh(lesson)

    return {"id": lesson.id, "title": lesson.title}


@router.post("/lessons/{lesson_id}/complete")
def complete_lesson(
    lesson_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lesson = db.query(Lesson).filter_by(
        id=lesson_id,
        church_id=current_user.church_id,
    ).first()

    if not lesson:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Lição não encontrada")

    existing = db.query(LessonProgress).filter_by(
        lesson_id=lesson.id,
        user_id=current_user.id,
    ).first()

    if existing:
        return {"id": existing.id, "already_completed": True}

    progress = LessonProgress(
        lesson_id=lesson.id,
        user_id=current_user.id,
    )

    db.add(progress)
    db.commit()

    return {"id": progress.id, "already_completed": False}


@router.post("/lessons/{lesson_id}/generate-quiz")
async def generate_quiz(
    lesson_id: str,
    payload: QuizInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lesson = db.query(Lesson).filter_by(
        id=lesson_id,
        church_id=current_user.church_id,
    ).first()

    if not lesson:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Lição não encontrada")

    study = lesson.study_module.study

    prompt = build_quiz_prompt(
        content=lesson.content,
        question_count=payload.question_count,
        difficulty=payload.difficulty,
        target_audience=study.target_audience,
    )

    try:
        generated = await generate_structured_content(prompt)
    except Exception as error:
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY,
            f"Não foi possível gerar o quiz: {error}",
        )

    quiz = Quiz(
        church_id=current_user.church_id,
        lesson_id=lesson.id,
        title=payload.title.strip(),
        description=payload.description,
        created_by=current_user.id,
    )

    db.add(quiz)
    db.flush()

    for index, item in enumerate(generated.get("questions", []), start=1):
        db.add(
            QuizQuestion(
                quiz_id=quiz.id,
                question=item["question"],
                options=item["options"],
                correct_option=item["correct_option"],
                explanation=item.get("explanation"),
                order=index,
            )
        )

    db.commit()
    db.refresh(quiz)

    db.add(
        AuditLog(
            user_id=current_user.id,
            church_id=current_user.church_id,
            action="AI_GENERATE",
            module="QUIZ",
            description=f"Quiz gerado por IA para a lição {lesson.title}",
            new_values={"quiz_id": quiz.id},
        )
    )
    db.commit()

    return serialize_quiz(quiz)


@router.get("/quizzes/{quiz_id}")
def get_quiz(
    quiz_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    quiz = db.query(Quiz).filter_by(
        id=quiz_id,
        church_id=current_user.church_id,
        is_active=True,
        is_published=True,
    ).first()

    if not quiz:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Quiz não encontrado")

    return serialize_quiz(quiz)


@router.post("/quizzes/{quiz_id}/attempt")
def submit_quiz_attempt(
    quiz_id: str,
    payload: QuizAnswerInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    quiz = db.query(Quiz).filter_by(
        id=quiz_id,
        church_id=current_user.church_id,
        is_active=True,
        is_published=True,
    ).first()

    if not quiz:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Quiz não encontrado")

    score = 0

    for question in quiz.questions:
        answer = payload.answers.get(question.id)

        if answer == question.correct_option:
            score += 1

    attempt = QuizAttempt(
        quiz_id=quiz.id,
        user_id=current_user.id,
        answers=payload.answers,
        score=score,
        total_questions=len(quiz.questions),
    )

    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return {
        "id": attempt.id,
        "score": attempt.score,
        "total_questions": attempt.total_questions,
    }


@router.post("/kids/generate-activity")
async def generate_kids_activity(
    payload: KidsContentInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    prompt = build_kids_activity_prompt(
        topic=payload.topic,
        age_range=payload.age_range,
    )

    try:
        generated = await generate_structured_content(prompt)
    except Exception as error:
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY,
            f"Não foi possível gerar a atividade: {error}",
        )

    content = KidsContent(
        church_id=current_user.church_id,
        title=payload.title.strip(),
        topic=payload.topic.strip(),
        age_range=payload.age_range,
        content_type=payload.content_type,
        content=generated,
        image_prompt=build_image_prompt(payload.topic),
        created_by=current_user.id,
    )

    db.add(content)
    db.commit()
    db.refresh(content)

    db.add(
        AuditLog(
            user_id=current_user.id,
            church_id=current_user.church_id,
            action="AI_GENERATE",
            module="KIDS",
            description=f"Atividade infantil gerada por IA: {content.title}",
            new_values={"id": content.id},
        )
    )
    db.commit()

    return {
        "id": content.id,
        "title": content.title,
        "topic": content.topic,
        "age_range": content.age_range,
        "content": content.content,
        "image_prompt": content.image_prompt,
    }


@router.get("/kids")
def list_kids_content(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    contents = db.query(KidsContent).filter_by(
        church_id=current_user.church_id,
        is_active=True,
        is_published=True,
    ).order_by(KidsContent.created_at.desc()).all()

    return {
        "contents": [
            {
                "id": content.id,
                "title": content.title,
                "topic": content.topic,
                "age_range": content.age_range,
                "content_type": content.content_type,
                "content": content.content,
                "image_path": content.image_path,
            }
            for content in contents
        ]
    }
