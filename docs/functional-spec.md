# Especificação funcional inicial

## MVP

1. Cadastro e aprovação de membros
2. Autenticação e recuperação de senha
3. Multi-tenant por igreja
4. Papéis e permissões
5. Perfil do membro
6. Ministérios e lideranças
7. Eventos e agenda
8. Finanças básicas
9. Mídia e devocionais
10. Estudos e quizzes
11. Área infantil
12. Auditoria

## Regras preservadas

- Novo cadastro inicia como pendente.
- E-mail deve ser verificado antes do login.
- Liderança aprova ou rejeita o cadastro.
- Membros podem pertencer a vários ministérios.
- Ministérios têm líder, vice-líder e líderes extras.
- Eventos podem ser gerais ou vinculados a ministérios.
- Eventos recorrentes devem ser representados por série, não duplicados fisicamente.
- Categorias financeiras podem exigir vínculo com membro.
- Transações financeiras devem usar precisão monetária adequada.
- Ações sensíveis devem ser auditadas.

## Permissões

| Permissão | Escopo |
|---|---|
| member.approve | Igreja |
| member.update | Próprio usuário ou igreja |
| ministry.create | Igreja |
| ministry.update | Igreja ou ministério |
| ministry.member.manage | Ministério |
| event.create | Igreja ou ministério |
| finance.transaction.create | Igreja ou ministério |
| finance.report.view | Igreja ou ministério |
| media.upload | Igreja ou ministério |
| study.publish | Igreja |
| kids.content.manage | Igreja ou ministério infantil |
| admin.settings.manage | Igreja |
