# Cardápio e comandas — P1 / P2

Projeto Django da P1, evoluído com API REST (Aula 13) e isolamento por organização (Aula 14).

## Executar no Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver
```

O clone preparado já possui `.venv` e as migrações locais aplicadas. Em uma instalação nova, crie seu usuário com `createsuperuser`, entre em `/admin/` e cadastre uma organização e um Perfil vinculando seu usuário a ela. O superusuário sem Perfil acessa o Admin, mas recebe 403 nas telas de negócio e na API.

- Aplicação (exige login): http://127.0.0.1:8000/
- Login do sistema: http://127.0.0.1:8000/entrar/
- Login da API: http://127.0.0.1:8000/api-auth/login/?next=/api/pratos/
- API navegável: http://127.0.0.1:8000/api/pratos/
- Dados de demonstração opcionais: `python manage.py popular_demo --organizacao ID` (com o ambiente ativo; use o ID exibido no Admin). O comando não apaga registros e deve receber explicitamente a organização.

SQLite é o padrão. PostgreSQL pode ser configurado via `.env` com `DB_ENGINE=postgresql`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` e `DB_PORT`. `.env`, `.venv` e o banco local ficam fora do Git.

## API de pratos

Todas as operações exigem login por sessão Django e um Perfil com organização. Sem login a resposta é 403. Escritas com sessão exigem token CSRF; a interface navegável cuida disso após o login.

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

O campo `id` é somente leitura. A organização é determinada pelo perfil, não é exposta como campo editável e qualquer valor `organizacao` enviado pelo cliente é ignorado. Listagem, detalhe, alteração e exclusão são limitados à organização do usuário; IDs de outra organização retornam 404. Categorias: `entrada`, `principal`, `acompanhamento`, `sobremesa`, `bebida`, `outros`. O preço deve ser no mínimo 0,01, com até duas casas decimais; o serializer reaproveita o validador do model. Dados inválidos retornam 400 e IDs inexistentes retornam 404. A exclusão retorna 400 quando o prato participa de um combo ou possui histórico de pedidos; nesse caso, use PATCH com `{"disponivel": false}`.

## Validar

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
```

A suíte cobre regressões da P1 e CRUD, validação, autenticação por sessão, CSRF e exclusões protegidas da API. A Aula 14 adiciona migrações de esquema e de dados, com teste de preservação do legado.

## Escopo da Aula 13

- Revisão com cinco itens em [MELHORIAS_P1.md](MELHORIAS_P1.md).
- DRF instalado, habilitado e fixado em `requirements.txt`.
- Serializer com campos explícitos, generics e URLs separadas de pratos.
- Planejamento da P2 em [BACKLOG_P2.md](BACKLOG_P2.md).

A Aula 14 implementa organizações e login nas telas HTML. Papéis administrador/operador e dashboard continuam no backlog das próximas aulas. O Django Admin é reservado ao superusuário do sistema; não equivale ao futuro papel administrador de uma organização.

Referências técnicas: [generics do DRF](https://www.django-rest-framework.org/api-guide/generic-views/) e [permissões do DRF](https://www.django-rest-framework.org/api-guide/permissions/).


## Aula 14 — estrutura e migração

- `core.Organizacao`: nome e data de criação; `core.Perfil`: usuário único e organização.
- Base abstrata `DaOrganizacao`, herdada por **Prato, Combo, Mesa, Comanda e Item**. Todos têm FK obrigatória com `PROTECT`; Organizacao e User são raízes e não herdam a base.
- Migrações em três etapas: `0004` adiciona FKs nulas, `0005` preenche a organização padrão e os perfis dos usuários existentes, `0006` torna as FKs obrigatórias. Não existe default fixo de organização nos modelos.
- Usuários criados depois das migrações recebem seu Perfil pelo Admin. Sem perfil: 403 nas telas e API, inclusive para superusuário. Visitantes são enviados ao login nas telas HTML.
- `org_atual(request)` centraliza o vínculo. Criações usam a organização da sessão; formulários omitem esse campo e filtram FK/M2M. Models validam vínculos FK e o sinal M2M impede pratos de outra organização em combos.
- A mesa é única por `(organizacao, numero)`; duplicatas na mesma organização geram erro amigável no formulário.
- O Admin global é reservado ao dono do sistema (superusuário), com colunas/filtros de organização. A organização de um cadastro existente não é alterável pelo Admin. Para criar um combo no Admin, salve a organização e depois escolha seus pratos.
- No HTML, o cabeçalho mostra usuário e organização e permite sair por POST com CSRF.

Antes de migrar o banco local, foi criado um backup SQLite fora do Git (`work/antes-aula14.sqlite3` no diretório da atividade). A comparação de todas as colunas antigas confirmou preservação integral: 7 pratos, 2 combos, 6 mesas, 5 vínculos combo/prato e 1 usuário. O banco local ainda não tinha comandas nem itens; o teste de migração cobre esses registros também.

## Roteiro de isolamento — executado em 17/11/2026

Cenário automatizado: Restaurante A e Restaurante B, um usuário com Perfil por organização, pratos/combos próprios e mesa número 1 em ambos. O roteiro foi executado com o cliente de testes Django/DRF, passando pelas URLs, formulários, sessões e banco de teste, sem depender de inspeção visual.

| Verificação do slide (adaptada ao cardápio) | Resultado observado |
| --- | --- |
| A lista pratos e mesas; repetir como B | Somente os registros da própria organização, em HTML e API |
| A abre URL de edição de B | 404; também verificado para exclusão, comanda, fechamento e API GET/PUT/PATCH/DELETE |
| A cria prato enviando organização B | Registro salvo na organização A; PATCH também não transfere organização |
| A abre formulário de combo/pedido | Selects contêm apenas pratos e combos de A; POST forjado com IDs de B é recusado |
| A cadastra número de mesa usado por B | Permitido entre organizações; duplicata dentro de A exibe erro no formulário |
| Histórico e operação de comandas | Histórico isolado; itens e novas comandas recebem organização A |
| Usuário sem Perfil | 403 controlado; sem erro 500 ou exposição de dados |
| Migração com dados legados | Pratos, combos, mesas, comandas, itens, M2M e usuário preservados/vinculados |

Resultado: **30 testes passaram** (`python manage.py test`), incluindo as regressões da P1 e da Aula 13. `check` sem problemas e `makemigrations --check --dry-run` sem alterações pendentes. Testes executados com SQLite; PostgreSQL não foi validado nesta etapa.

Para repetir: `python manage.py test cardapio.test_isolamento cardapio.test_migracao`.

### Conferência manual com duas sessões

1. No Admin, crie duas organizações, dois usuários comuns e um Perfil para cada usuário. Não dê acesso staff/superusuário às contas dos restaurantes.
2. Crie exemplos com `python manage.py popular_demo --organizacao ID` para cada organização.
3. Entre com A e B em navegadores ou sessões privadas separadas em `/entrar/`.
4. Repita as cinco primeiras linhas da tabela, usando o ID de um prato de B ao tentar abrir sua edição como A.
5. Registre o resultado novamente ao adicionar novas telas. Os testes automatizados já executam esse roteiro a cada suíte.

No PC desta atividade, as contas locais `teste_a` e `teste_b` já têm perfis em organizações distintas e dados de demonstração. Suas senhas ficam no arquivo local `ACESSOS_TESTE_LOCAL.txt`, fora do repositório. `admin_local` preservou a senha e foi vinculado à organização padrão.

Verificação adicional no servidor local: login HTTP com `teste_a` e `teste_b`, listagem JSON com 7 pratos de cada organização (IDs disjuntos) e tentativa de acessar prato B como A retornando HTTP 404.


## Cardápio público para os clientes

O endereço `/menu/<id-da-organizacao>/` abre o catálogo do restaurante **sem login**. No ambiente local, acesse http://127.0.0.1:8000/menu/1/ para a organização padrão. O link **Cardápio do cliente ↗** no cabeçalho interno leva ao catálogo da organização do usuário.

- Layout próprio, responsivo, com ilustrações SVG locais e identificação do restaurante. As ilustrações representam categorias; não são fotografias dos produtos.
- Busca instantânea por nome/descrição/componentes, categorias e estado vazio. Os filtros também funcionam por GET sem JavaScript.
- Somente pratos disponíveis e combos disponíveis com componentes disponíveis da mesma organização são exibidos. Combos vazios ou com vínculos inconsistentes não aparecem.
- **Minha escolha** permite selecionar itens, ajustar quantidades e conferir o total. A lista fica no navegador, separada por organização, e remove referências a produtos que deixaram de estar no catálogo ao recarregar a página.
- A lista é uma ajuda para conversar com o atendente: **não envia pedido, não reserva produto e não cria comanda**. Preços são calculados em centavos; taxas adicionais não são incluídas.
- Essa rota pública aceita apenas GET/HEAD. API, cadastros, mesas e comandas continuam exigindo autenticação e isolamento por perfil. Apenas o catálogo foi tornado público.
- Não há dependências externas de fontes/imagens nem nova migração de banco.

Para compartilhar com clientes fora deste PC, é necessário hospedar o Django e usar o domínio da implantação. O endereço `127.0.0.1` é apenas local; o projeto não foi publicado na internet.

### Validação do cardápio público

**34 testes passaram**, incluindo acesso anônimo, isolamento, indisponibilidade, rejeição de escrita, combinações inconsistentes, escape de conteúdo e filtros sem JavaScript. Mantidas todas as regressões das aulas anteriores.

No navegador: conferidos visual padrão e largura de 390 px, busca, categorias, mensagem sem resultados, adição, aumento/redução de quantidade, exclusão da seleção e total (2 pudins de R$ 12,00 = R$ 24,00). Não houve transbordamento horizontal da página no celular.


## Aula 17 — Dashboard e relatórios (23/11/2026)

Acesso: `/dashboard/`, pelo link **Dashboard** no menu interno. Exportação: `/dashboard/exportar.csv`. API: `/api/dashboard/`. Os três usam o mesmo filtro validado e a mesma base por organização, centralizada em `cardapio/dashboard.py`.

### Quatro perguntas e quatro tipos de análise

| Pergunta semanal | Tipo | Implementação |
| --- | --- | --- |
| Quanto o restaurante vendeu? | KPI | Faturamento com Sum; também cartões de comandas, ticket médio (Avg) e unidades vendidas |
| Quais produtos mais saíram? | Ranking | Top 5 por quantidade vendida com values, annotate, Sum e order_by |
| Como as vendas evoluíram ao longo dos meses? | Série temporal | TruncMonth, soma dos valores fechados e gráfico de linha Chart.js |
| Qual a participação de pratos e combos nas vendas? | Distribuição | Soma condicional de unidades por tipo; barras e valores legíveis |

Todas as análises consideram somente **comandas fechadas**. O filtro usa `fechada_em`, em America/Sao_Paulo. As datas inicial e final são inclusivas; internamente o fim usa limite exclusivo no início do dia seguinte, preservando horas e microssegundos. Campos em branco não limitam esse lado do período; sem datas, considera todo o histórico. Datas inválidas, invertidas ou fora do intervalo 1900–9998 retornam 400, com mensagem no HTML e erros estruturados na API. Nunca há fallback silencioso para dados sem filtro.

Faturamento e ticket usam `total_fechado`, sem recalcular com preços atuais. Ranking e distribuição usam os itens e preços copiados no pedido. Combo conta como uma unidade, não novamente cada componente; neste domínio o model Prato inclui bebidas, sobremesas e acompanhamentos. O ranking agrupa por ID do prato/combo e pelo nome preservado; nomes diferentes ao longo do histórico aparecem em linhas distintas. A série mostra meses com vendas e informa isso na tela; a tabela do gráfico oferece os mesmos números sem depender do canvas. Não há cache compartilhado entre organizações; respostas levam `no-store`.

### Papéis e acesso

O pré-requisito de papéis necessário para esta aula foi adicionado a Perfil: `admin` ou `operador`. Novos perfis são operadores por padrão. A migração promove apenas os perfis dos superusuários já existentes; por isso `admin_local` continua adequado para a demonstração completa. Configure outros papéis pelo Django Admin. Superusuário sem Perfil continua bloqueado nas telas de negócio.

| Recurso | Administrador | Operador |
| --- | --- | --- |
| KPIs, ranking e distribuição da própria organização | Sim | Sim |
| Série mensal no HTML e na API | Sim | Não |
| CSV, inclusive por URL direta | Sim | Não (403) |

Essa matriz é aplicada ao dashboard/relatórios. A implementação completa de permissões por papel nos demais CRUDs e a API dos demais recursos continuam sendo assuntos das aulas 15/16; esta entrega não os declara concluídos.

### Gráfico e exportação

Chart.js **4.5.1** está versionado em `cardapio/static/cardapio/vendor/`, com licença MIT. O pacote veio do registro npm e teve a integridade SHA-512 conferida. Nenhum CDN é necessário para visualizar o gráfico. Os dados são enviados por `json_script` e lidos por `dashboard.js`. Referências: [integração oficial do Chart.js](https://www.chartjs.org/docs/latest/getting-started/integration.html) e [agregações do Django](https://docs.djangoproject.com/en/5.2/topics/db/aggregation/).

O CSV exporta todas as comandas fechadas da organização no período (a tela lista apenas as últimas 20). Usa `select_related('mesa')`, streaming com iterator, UTF-8 com BOM, separador ponto e vírgula e valores decimais com vírgula. Inclui organização, ID da comanda, mesa, abertura, fechamento e total. Textos iniciados por caracteres de fórmula são neutralizados para planilhas. A URL do botão mantém exatamente as datas aplicadas.

### Consultas sem N+1 — evidências

Foi corrigido o N+1 do salão: cada comanda aberta antes consultava seus itens separadamente. Agora há prefetch de comandas e itens por organização com `to_attr`; a propriedade `total` reutiliza essa lista. A tela da comanda usa o mesmo carregamento e traz a mesa com `select_related`. Perfil e organização são carregados juntos e reutilizados durante a requisição.

Medição com `CaptureQueriesContext`, incluindo autenticação e renderização, na organização de demonstração (12 comandas fechadas):

| Rota | Consultas |
| --- | ---: |
| Salão sem comandas abertas | 5 |
| Cardápio interno | 6 |
| Histórico | 4 |
| Dashboard completo | 8 |
| API do dashboard completo | 7 |
| Cardápio público | 4 |
| Detalhe da comanda | 7 |
| CSV completo, consumindo o streaming | 4 |

Teste de crescimento: salão com 1 e 11 comandas abertas manteve **6 → 6** consultas; dashboard manteve **8 → 8**. Métricas + relatório completo permaneceram em **5 consultas** ao passar de 3 para 53 comandas fechadas. O relatório com acesso à mesa usa **1 consulta**. Esses limites são protegidos por testes. O índice composto `(organizacao, fechada_em)` acompanha os filtros mais frequentes.

Para reproduzir a auditoria:

```powershell
.\.venv\Scripts\python.exe manage.py auditar_consultas --usuario dashboard_demo
```

Também é possível definir `LOG_SQL=True` no `.env` local para registrar SQL no terminal; só funciona com DEBUG=True e não é ativado em produção. Não foi necessário instalar Debug Toolbar, pois a aula permite log SQL como alternativa.

### Roteiro executado

- Dados conhecidos: organização A com contas de R$ 20, R$ 30 e R$ 40; organização B com R$ 9.000; comanda aberta excluída.
- Resultado A: faturamento R$ 90, 3 contas, ticket R$ 30, 7 unidades; distribuição 6 pratos / 1 combo. Série: outubro R$ 20, novembro R$ 70.
- Filtro de 01/11 a 23/11: R$ 70, 2 contas, ticket R$ 35, 5 unidades; limites de meia-noite e microssegundos verificados.
- Conferidos: base vazia, preços históricos, IDs/organização enviados na URL, proteção de CSV, ausência de série para operador, autenticação e perfil ausente.
- **46 testes passaram**, incluindo 12 testes do dashboard e as regressões anteriores. Banco de testes: SQLite; PostgreSQL não foi executado nesta etapa.
- No navegador: gráfico renderizado, filtro aplicado e CSV baixado. A demonstração filtrada de novembro exibiu R$ 652,60 em 4 contas; o arquivo baixado somou os mesmos R$ 652,60.

```powershell
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
```

### Dados para apresentar

`python manage.py popular_dashboard_demo` prepara uma organização exclusiva, **Restaurante demonstração · Dashboard**, com vendas fictícias em três meses. Executá-lo novamente não duplica vendas existentes. Os dados dos outros restaurantes são preservados. No PC desta atividade, `dashboard_demo` tem papel administrador nessa organização; suas credenciais estão em `ACESSO_DASHBOARD_DEMO.txt`, fora do Git. Em outra instalação, crie um usuário e seu Perfil pelo Admin para acessar essa organização.

Backup local anterior à migração: `work/antes-aula17.sqlite3`, fora do repositório. Senhas, sessões, banco e backup não são versionados.
