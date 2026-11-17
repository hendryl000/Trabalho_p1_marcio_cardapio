# Melhorias identificadas na P1

Revisão do código para a Aula 13 (17/11/2026). Não foram fornecidos comentários da correção do professor; os itens abaixo vêm da inspeção do projeto.

- [ ] **Centralizar as regras dos pedidos.** A seleção de prato ou combo fica em `ItemForm.clean`, enquanto cópia de preço e bloqueio de comanda fechada ficam nas views. Extrair uma operação de domínio reutilizável antes de expor itens e comandas na API. Aceite: HTML e API recusam as mesmas operações inválidas.
- [ ] **Eliminar duplicação da validação de preço.** `PratoForm.clean_preco` e o `MinValueValidator` do model repetem a regra. Preservar a mensagem amigável no formulário e usar uma definição central. Aceite: zero e negativos são recusados por formulário, model e serializer, com testes.
- [ ] **Proteger as telas de operação.** As views de cadastro, abertura e fechamento de comandas não exigem login. Adicionar autenticação e os papéis da P2. Aceite: visitantes não alteram dados e operadores não acessam funções administrativas. A nova API já exige sessão autenticada.
- [ ] **Limitar consultas do histórico e início.** `inicio` carrega todas as comandas e seus itens por mesa; `historico` não tem paginação nem período. Consultar somente comandas abertas no início e paginar/filtrar histórico. Aceite: dados antigos não aumentam indefinidamente o volume carregado por página.
- [ ] **Simplificar configuração de ambiente.** `settings.py` redefine segredo, debug, hosts, idioma e fuso ao final. Consolidar definições e documentar `.env.example` sem segredos. Aceite: SQLite local e PostgreSQL configurável funcionam sem credenciais no Git.
