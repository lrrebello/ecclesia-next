# Especificação funcional inicial

## Estrutura organizacional

A aplicação suporta uma hierarquia de igrejas e filiais:

```text
Igreja-mãe
├── Filial A
├── Filial B
└── Filial C
```

- Cada filial é um tenant operacional.
- Membros, famílias, ministérios, eventos e permissões pertencem à filial.
- A igreja-mãe pode ter visão consolidada das filiais.
- O cadastro público exige a escolha da igreja-mãe e da filial.

## Módulos implementados

### Igrejas e filiais

- Hierarquia de igreja-mãe e filiais
- Tipos: sede e filial
- Listagem pública de igrejas e filiais
- Criação de igrejas e filiais autenticada
- Vínculo do membro à filial escolhida

### Autenticação

- Cadastro de usuário vinculado a uma filial
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
- Listagem de membros da filial
- Aprovação e rejeição de cadastros pendentes

### Famílias

- Criação, listagem, edição e exclusão de famílias
- Vínculo e desvinculação de membros
- Responsável familiar

### Ministérios

- Criação, listagem, edição e desativação de ministérios
- Vínculo de membros
- Líder, vice-líder e líderes extras
- Ministérios infantis

### Eventos

- Criação de eventos gerais ou vinculados a ministérios
- Título, descrição, local, início e fim
- Eventos públicos e internos
- Recorrência diária, semanal e mensal
- Ocorrências calculadas dinamicamente, sem duplicar registros
- Agenda filtrada pelos ministérios do usuário
- Permissão de líderes para eventos do ministério
- Auditoria de criação, atualização e desativação

## Regras de negócio

- Um usuário pertence a uma filial.
- Uma família pertence a uma filial.
- Um ministério pertence a uma filial.
- Um evento pertence a uma filial e pode pertencer a um ministério.
- Eventos recorrentes são armazenados como uma única série.
- Líder, vice-líder e líderes extras podem gerenciar eventos do ministério.
- A exclusão de eventos é lógica, preservando histórico e auditoria.

## Próximos módulos

- Finanças
- Mídia e devocionais
- Estudos e quizzes
- Área infantil
- Administração e dashboards
