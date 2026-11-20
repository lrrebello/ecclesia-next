# Arquitetura

## Princípios

- Multi-tenant por igreja, com isolamento obrigatório no serviço e no banco.
- Autorização centralizada: usuário -> papel -> permissão -> escopo.
- Domínio separado da camada HTTP.
- Valores monetários em decimais.
- Auditoria para operações sensíveis.
- Configuração por ambiente, sem segredos no código.
- Testes obrigatórios para autenticação, permissões e isolamento entre igrejas.

## Módulos

- auth: identidade, sessões, MFA e recuperação de acesso
- churches: igrejas, filiais, configurações e temas
- members: pessoas, famílias, perfis e consentimentos
- ministries: ministérios, lideranças e vínculos
- events: agenda, recorrência e inscrições
- finance: transações, contas, categorias, recibos e dívidas
- media: álbuns, arquivos e publicações
- studies: estudos, progresso, destaques e notas
- kids: atividades, histórias, quizzes e jogos
- admin: dashboards, configurações e auditoria

## Serviço de IA

O serviço de IA é centralizado em `backend/app/services/ai_service.py`.

Casos de uso previstos:

- Geração de questões para estudos bíblicos
- Geração de quizzes
- Geração de jogos de emojis e palavras
- Resumo e sugestão de conteúdo devocional
- Apoio à criação de atividades infantis

O provedor pode ser OpenAI ou Google Gemini, configurado por variáveis de ambiente.
