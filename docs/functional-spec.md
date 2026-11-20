# Especificação funcional inicial

## Módulos implementados

### Autenticação

- Cadastro de usuário vinculado a uma igreja
- Login com JWT
- Endpoint de perfil autenticado
- Endpoint de permissões efetivas
- Sessão no frontend
- Dashboard protegido

### Ministérios

- Criação de ministérios
- Listagem de ministérios da igreja do usuário
- Detalhe de ministério
- Atualização de ministério
- Desativação de ministério
- Vínculo de membros ativos
- Remoção de membros
- Líder, vice-líder e líderes extras
- Identificação de ministério infantil
- Registro de auditoria nas operações sensíveis

## Regras de negócio

- Um usuário pertence a uma igreja.
- Um ministério pertence a uma igreja.
- Um usuário pode participar de vários ministérios.
- Um ministério pode ter líder, vice-líder e líderes extras.
- Líder, vice-líder e líderes extras podem gerenciar o ministério.
- Apenas membros ativos da mesma igreja podem ser vinculados.
- A exclusão de ministério é lógica, preservando histórico e auditoria.

## Próximos módulos

- Membros e famílias
- Aprovação de cadastros
- Eventos e recorrência
- Finanças
- Mídia e devocionais
- Estudos e quizzes
- Área infantil
- Administração e dashboards
