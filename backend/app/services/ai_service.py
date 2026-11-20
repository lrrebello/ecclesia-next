from app.core.config import get_settings

class AIService:
    def __init__(self):
        self.settings = get_settings()

    def generate_quiz(self, topic: str, quantity: int = 5, difficulty: str = "medium") -> dict:
        prompt = f"""
Crie {quantity} questões de múltipla escolha sobre: {topic}.
Dificuldade: {difficulty}.
Responda apenas em JSON válido com esta estrutura:
{{"questions":[{{"question":"","options":["","","",""],"correct_index":0,"explanation":""}}]}}
"""
        if self.settings.ai_provider == "openai":
            return self._openai(prompt)
        if self.settings.ai_provider == "gemini":
            return self._gemini(prompt)
        raise ValueError("Provedor de IA não configurado")

    def _openai(self, prompt: str) -> dict:
        from openai import OpenAI
        client = OpenAI(api_key=self.settings.openai_api_key)
        response = client.chat.completions.create(
            model=self.settings.openai_model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        import json
        return json.loads(response.choices[0].message.content)

    def _gemini(self, prompt: str) -> dict:
        from google import genai
        client = genai.Client(api_key=self.settings.google_ai_api_key)
        response = client.models.generate_content(
            model=self.settings.gemini_model,
            contents=prompt,
        )
        import json, re
        text = response.text.strip().removeprefix("```json").removesuffix("```").strip()
        return json.loads(text)
