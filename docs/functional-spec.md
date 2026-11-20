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
- Membros, famílias, ministérios, eventos, finanças, donativos, mídia e devocionais pertencem à filial.

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
- Contas a pagar com valor, vencimento, fornecedor e status
- Dashboard com receita, despesa, saldo, contas pendentes e vencidas

### Donativos e Modelo 25

- Cadastro de doadores por filial
- Registo de donativos com valor, data, recibo e observações
- Identificação de donativos elegíveis para o Modelo 25
- Criação de declaração anual por ano fiscal
- Inclusão e remoção de donativos na declaração
- Impedimento de duplicação de donativos entre declarações
- Exportação de ficheiro CSV para conferência e envio ao Portal das Finanças
- Marcação da declaração como enviada
- Auditoria de donativos e envio da declaração

### Mídia

- Álbuns de mídia por filial
- Vínculo opcional a ministérios
- Itens de imagem, vídeo, áudio e documento
- Suporte a arquivo local e URL externa
- Miniaturas, tamanho e duração
- Controle de publicação e desativação

### Devocionais

- Criação de devocionais por filial
- Título, referência bíblica, texto bíblico, conteúdo e oração
- Vínculo opcional a ministérios
- Data de publicação
- Publicação e despublicação
- Marcação de leitura pelo membro
- Prevenção de leituras duplicadas

## Regras do Modelo 25

- Nem toda receita é donativo.
- Nem todo donativo é automaticamente elegível para o Modelo 25.
- Donativos elegíveis exigem doador, NIF, valor, data e recibo.
- Um donativo só pode pertencer a uma declaração.
- A declaração deve ser criada por ano fiscal.
- A declaração só pode ser marcada como enviada se possuir donativos.
- Após o envio, a declaração não pode ser alterada.
- O envio ao Portal das Finanças deve ocorrer até ao fim de fevereiro do ano seguinte.

## Próximos módulos

- Estudos e quizzes
- Área infantil
- Administração e dashboards
