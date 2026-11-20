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
- Membros, famílias, ministérios e permissões pertencem à filial.
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
- Auditoria de cadastro, atualização de perfil e aprovação

### Famílias

- Criação de famílias
- Listagem de famílias da filial
- Detalhe de família
- Atualização de família
- Exclusão de família
- Vínculo e desvinculação de membros
- Definição de responsável familiar

### Ministérios

- Criação de ministérios
- Listagem de ministérios da filial
- Detalhe de ministério
- Atualização de ministério
- Desativação de ministério
- Vínculo de membros ativos
- Remoção de membros
- Líder, vice-líder e líderes extras
- Identificação de ministério infantil

## Próximos módulos

- Eventos e recorrência
- Finanças
- Mídia e devocionais
- Estudos e quizzes
- Área infantil
- Administração e dashboards
