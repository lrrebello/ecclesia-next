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
- Membros, famílias, ministérios, eventos, finanças e permissões pertencem à filial.
- A igreja-mãe pode ter visão consolidada das filiais.

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
- Recorrência diária, semanal e mensal
- Ocorrências calculadas dinamicamente
- Agenda filtrada pelos ministérios do usuário

### Finanças

- Categorias de receita e despesa por filial
- Métodos de pagamento por filial
- Contas bancárias da filial ou ministério
- Lançamentos de receita e despesa
- Valores monetários em precisão decimal
- Vínculo opcional do lançamento a membro, ministério, conta e conta a pagar
- Categorias podem exigir identificação do membro
- Contas a pagar com valor, vencimento, fornecedor e status
- Dashboard com receita, despesa, saldo, contas pendentes e vencidas
- Auditoria de criação de lançamentos

## Regras de negócio

- Um usuário pertence a uma filial.
- Uma família pertence a uma filial.
- Um ministério pertence a uma filial.
- Um evento pertence a uma filial e pode pertencer a um ministério.
- Um lançamento financeiro pertence a uma filial e pode estar vinculado a ministério, membro, conta ou conta a pagar.
- Valores financeiros usam precisão decimal.
- A permissão `finance.manage` é necessária para configurar e lançar finanças.
- A aprovação de membros exige a permissão `member.approve`.

## Próximos módulos

- Mídia e devocionais
- Estudos e quizzes
- Área infantil
- Administração e dashboards
