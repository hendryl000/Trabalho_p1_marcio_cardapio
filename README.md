# Cardápio e comandas — P1 / início da P2

Projeto Django da P1, evoluído na Aula 13 com Django REST Framework.

## Executar no Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver
```

O clone preparado já possui `.venv` e as migrações locais aplicadas. Crie seu usuário com `createsuperuser` e escolha a senha no terminal.

- Aplicação: http://127.0.0.1:8000/
- Login da API: http://127.0.0.1:8000/api-auth/login/?next=/api/pratos/
- API navegável: http://127.0.0.1:8000/api/pratos/
- Dados de demonstração opcionais: `python manage.py popular_demo` (com o ambiente ativo).

SQLite é o padrão. PostgreSQL pode ser configurado via `.env` com `DB_ENGINE=postgresql`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` e `DB_PORT`. `.env`, `.venv` e o banco local ficam fora do Git.

## API de pratos

Todas as operações exigem login por sessão Django. Sem login a resposta é 403. Escritas com sessão exigem token CSRF; a interface navegável cuida disso após o login.

| Método | URL | Resultado |
| --- | --- | --- |
| GET | `/api/pratos/` | Lista, 200 |
| POST | `/api/pratos/` | Criação, 201 |
| GET | `/api/pratos/<id>/` | Detalhe, 200 |
| PUT / PATCH | `/api/pratos/<id>/` | Atualização completa/parcial, 200 |
| DELETE | `/api/pratos/<id>/` | Exclusão, 204 |

Exemplo de JSON para POST na interface navegável:

```json
{
  "nome": "Arroz da casa",
  "descricao": "Porção individual",
  "categoria": "acompanhamento",
  "preco": "12.50",
  "disponivel": true
}
```

O campo `id` é somente leitura. Categorias: `entrada`, `principal`, `acompanhamento`, `sobremesa`, `bebida`, `outros`. O preço deve ser no mínimo 0,01, com até duas casas decimais; o serializer reaproveita o validador do model. Dados inválidos retornam 400 e IDs inexistentes retornam 404. A exclusão retorna 400 quando o prato participa de um combo ou possui histórico de pedidos; nesse caso, use PATCH com `{"disponivel": false}`.

## Validar

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
```

A suíte cobre regressões da P1 e CRUD, validação, autenticação por sessão, CSRF e exclusões protegidas da API. Não há alteração de modelos nesta etapa.

## Escopo da Aula 13

- Revisão com cinco itens em [MELHORIAS_P1.md](MELHORIAS_P1.md).
- DRF instalado, habilitado e fixado em `requirements.txt`.
- Serializer com campos explícitos, generics e URLs separadas de pratos.
- Planejamento da P2 em [BACKLOG_P2.md](BACKLOG_P2.md).

Organizações, papéis e dashboard são próximos passos. Atualmente usuários autenticados acessam todos os pratos; o isolamento será implementado na Aula 14. As telas HTML da P1 ainda precisam das restrições listadas nas melhorias.

Referências técnicas: [generics do DRF](https://www.django-rest-framework.org/api-guide/generic-views/) e [permissões do DRF](https://www.django-rest-framework.org/api-guide/permissions/).
