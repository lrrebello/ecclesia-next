-- Cria a primeira igreja para testes locais.
-- Execute dentro do banco ecclesia.

INSERT INTO churches (id, name, slug, country, currency_code, is_active, created_at)
VALUES (
  gen_random_uuid()::text,
  'Igreja de Teste',
  'igreja-teste',
  'Portugal',
  'EUR',
  true,
  now()
)
ON CONFLICT (slug) DO NOTHING;
