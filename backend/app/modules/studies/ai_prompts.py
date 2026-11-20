QUIZ_GENERATION_PROMPT = """
Você é um especialista em educação cristã e criação de conteúdos didáticos para igrejas.

Crie perguntas de múltipla escolha a partir do conteúdo abaixo.

Regras:
- Use linguagem clara, acessível e fiel ao conteúdo.
- Não invente doutrinas, versículos ou informações que não estejam no material.
- Crie {question_count} perguntas.
- Cada pergunta deve ter 4 alternativas.
- Apenas uma alternativa deve estar correta.
- Explique brevemente por que a resposta correta está correta.
- Adapte o nível de dificuldade para: {difficulty}.
- Público-alvo: {target_audience}.
- Se o conteúdo for infantil, use linguagem simples, positiva e adequada à idade.

Conteúdo base:
{content}

Responda apenas com JSON válido no formato:
{
  "questions": [
    {
      "question": "",
      "options": ["", "", "", ""],
      "correct_option": 0,
      "explanation": ""
    }
  ]
}
"""


LESSON_SUMMARY_PROMPT = """
Você é um assistente de ensino cristão.

Crie um resumo didático, fiel e claro do conteúdo abaixo.

Regras:
- Não invente informações bíblicas ou doutrinárias.
- Destaque as ideias principais.
- Use no máximo {max_words} palavras.
- Adapte a linguagem para: {target_audience}.

Conteúdo:
{content}

Responda apenas com JSON válido:
{
  "summary": ""
}
"""


KIDS_ACTIVITY_PROMPT = """
Você é um especialista em educação cristã infantil.

Crie uma atividade segura, criativa e adequada para crianças de {age_range} anos.

Tema:
{topic}

Regras:
- Use linguagem simples, alegre e respeitosa.
- Não inclua conteúdo assustador, violento ou inadequado.
- Baseie-se apenas no tema e nas referências bíblicas fornecidas.
- Inclua objetivo, materiais, instruções e uma breve aplicação espiritual.

Responda apenas com JSON válido:
{
  "title": "",
  "objective": "",
  "materials": [""],
  "instructions": [""],
  "spiritual_application": ""
}
"""


IMAGE_GENERATION_PROMPT = """
Crie uma ilustração cristã infantil, acolhedora e educativa sobre: {topic}.

Regras visuais:
- Estilo: ilustração digital infantil, cores suaves, luz acolhedora, composição simples e clara.
- Personagens: crianças diversas, expressões alegres e seguras.
- Ambiente: {environment}.
- Não inclua texto, marcas, logotipos, símbolos religiosos complexos ou elementos assustadores.
- A imagem deve transmitir esperança, cuidado, fé e aprendizagem.
- Formato horizontal, adequado para apresentação em tela.
"""
