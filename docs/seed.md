# Seed inicial para testes

Este seed cria uma estrutura inicial segura para testar o acesso e a aprovação de membros.

## O que é criado

- Igreja-mãe: Igreja Central
- Filial Norte
- Filial Sul
- Papéis: Administrador Global e Membro
- Permissões administrativas e operacionais
- Um administrador aprovado
- Dois membros pendentes, um em cada filial

## Como executar

```bash
cd ~/Projetos/ecclesia-next
git pull origin main

sudo docker compose down
sudo docker compose up -d --build

sudo docker compose exec api python -m app.seed
```

## Credenciais de teste

### Administrador

```text
Email: admin@teste.com
Senha: Teste@1234
Status: aprovado
Filial: Igreja Central
```

### Membro da Filial Norte

```text
Email: membro.norte@teste.com
Senha: Membro@1234
Status: pendente
Filial: Filial Norte
```

### Membro da Filial Sul

```text
Email: membro.sul@teste.com
Senha: Membro@1234
Status: pendente
Filial: Filial Sul
```

## O que testar

1. Entre como administrador.
2. Acesse Membros.
3. Aprove ou rejeite os dois membros pendentes.
4. Entre como um dos membros para confirmar o acesso básico.
5. Acesse Finanças, Donativos, Modelo 25, Mídia, Devocionais, Estudos e Área Kids.

## Segurança

Estas credenciais são apenas para desenvolvimento local. Antes de colocar em produção, altere as senhas e remova os utilizadores de teste.
