# Especificação funcional inicial

## Módulos implementados

### Autenticação

- Cadastro de usuário vinculado a uma igreja
- Login com JWT
- Endpoint de perfil autenticado
- Endpoint de permissões efetivas
- Sessão no frontend
- Dashboard protegido

### Membros

- Cadastro completo de membro
- Dados pessoais, contato, endereço, batismo e conversão
- Consentimento LGPD/GDPR
- Perfil autenticado
- Edição do próprio perfil
- Listagem de membros da igreja
- Aprovação e rejeição de cadastros pendentes
- Auditoria de cadastro, atualização de perfil e aprovação

### Famílias

- Criação de famílias
- Listagem de famílias da igreja
- Detalhe de família
- Atualização de família
- Exclusão de família
- Vínculo e desvinculação de membros
- Definição de responsável familiar
- Dados de contato e endereço da família
- Auditoria das operações sensíveis

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
- Um usuário pode pertencer a uma família.
- Uma família pertence a uma igreja.
- Uma família pode ter um responsável.
- Ao excluir uma família, seus membros são desvinculados.
- Um usuário pode participar de vários ministérios.
- Cadastros iniciam como pendentes.
- A aprovação exige a permissão `member.approve`.
- Apenas membros ativos da mesma igreja podem ser vinculados a ministérios.
- Líder, vice-líder e líderes extras podem gerenciar o ministério.

## Próximos módulos

- Eventos e recorrência
- Finanças
- Mídia e devocionais
- Estudos e quizzes
- Área infantil
- Administração e dashboards
