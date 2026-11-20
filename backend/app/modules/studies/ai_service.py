import json
import os
import httpx
from app.modules.studies.ai_prompts import (
    IMAGE_GENERATION_PROMPT,
    KIDS_ACTIVITY_PROMPT,
    LESSON_SUMMARY_PROMPT,
    QUIZ_GENERATION_PROMPT,
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
OPENAI_IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")


def build_quiz_prompt(content: str, question_count: int, difficulty: str, target_audience: str) -> str:
    return QUIZ_GENERATION_PROMPT.format(
        question_count=question_count,
        difficulty=difficulty,
        target_audience=target_audience,
        content=content,
    )


def build_summary_prompt(content: str, max_words: int, target_audience: str) -> str:
    return LESSON_SUMMARY_PROMPT.format(
        max_words=max_words,
        target_audience=target_audience,
        content=content,
    )


def build_kids_activity_prompt(topic: str, age_range: str) -> str:
    return KIDS_ACTIVITY_PROMPT.format(
        age_range=age_range,
        topic=topic,
    )


def build_image_prompt(topic: str, environment: str = "ambiente acolhedor e seguro") -> str:
    return IMAGE_GENERATION_PROMPT.format(
        topic=topic,
        environment=environment,
    )


async def generate_structured_content(prompt: str) -> dict:
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY não configurada")

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{OPENAI_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": OPENAI_CHAT_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "Responda apenas com JSON válido, sem texto adicional.",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                "temperature": 0.4,
            },
        )

    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    return json.loads(content)
