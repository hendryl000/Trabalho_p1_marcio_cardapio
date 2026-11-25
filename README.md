# À Mesa — Cardápio e comandas

Sistema Django para gerenciar restaurantes, pratos, combos, mesas e comandas, com cardápio público para clientes, API REST e dashboard de vendas. Cada usuário possui um Perfil vinculado a uma organização (restaurante); as telas internas mostram os dados dessa organização.

## Guia de instalação e uso

- [Dependências](#dependências)
- [Instalação no Windows](#instalação-no-windows-powershell)
- [Primeiro acesso](#primeiro-acesso-usuário-organização-e-perfil)
- [Dados de exemplo](#dados-de-exemplo)
- [Como iniciar novamente](#como-iniciar-novamente)
- [Caminhos das telas](#caminhos-das-telas)
- [Fluxo de atendimento](#fluxo-de-atendimento)
- [Configuração do banco](#configuração-do-banco)
- [Problemas comuns](#problemas-comuns)
- [API de pratos](#api-de-pratos)
- [Validação e testes](#validar)

## Dependências

Instale **Python** e **Git** no computador. O ambiente local foi executado com Python **3.14.6**. No instalador do Python para Windows, habilite a opção de adicionar Python ao PATH.

As bibliotecas abaixo estão fixadas em `requirements.txt`; o comando de instalação instala todas de uma vez.

| Dependência | Versão no projeto | Uso |
| --- | --- | --- |
| Django | 5.2.17 | Aplicação web, autenticação, banco e painel administrativo |
| Django REST Framework | 3.18.3 | API REST e interface navegável da API |
| python-dotenv | 1.2.3 | Leitura da configuração do arquivo `.env` |
| psycopg / psycopg-binary | 3.3.6 | Conexão com PostgreSQL, quando escolhido |
| asgiref | 3.13.0 | Dependência de execução do Django |
| sqlparse | 0.6.1 | Utilitários de SQL usados pelo Django |
| tzdata | 2026.6 | Dados de fuso horário, inclusive no Windows |

**SQLite já acompanha o Python**: não é necessário instalar um servidor de banco para rodar localmente. **Node.js e npm não são necessários**: HTML, CSS, JavaScript, ilustrações e Chart.js 4.5.1 já estão no repositório. A instalação inicial das bibliotecas exige internet.

## Instalação no Windows (PowerShell)

### 1. Clonar o projeto

Abra o PowerShell na pasta em que deseja guardar o projeto e execute:

```powershell
git clone https://github.com/hendryl000/Trabalho_p1_marcio_cardapio.git
cd Trabalho_p1_marcio_cardapio
```

Todos os comandos seguintes devem ser executados nessa pasta, onde está o arquivo `manage.py`.

### 2. Criar o ambiente e instalar as bibliotecas

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Se o Windows reconhecer apenas `py`, use `py -m venv .venv` para criar o ambiente. Os comandos restantes usam diretamente o Python da `.venv`, portanto **não é necessário ativar o ambiente nem alterar a política de execução do PowerShell**.

### 3. Preparar a configuração local

Em uma instalação nova:

```powershell
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
notepad .env
```

Copie a chave gerada para `SECRET_KEY`, mantendo-a entre aspas simples no `.env`. Mantenha `DEBUG=True` e `DB_ENGINE=sqlite` para desenvolvimento local. Se já tiver um `.env`, edite o existente em vez de sobrescrevê-lo.

### 4. Criar as tabelas, o administrador e iniciar

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py runserver
```

O comando `createsuperuser` solicita nome de usuário, e-mail e senha. A senha não aparece enquanto é digitada no terminal. Escolha suas próprias credenciais: **o clone não inclui usuários, senhas ou o banco de demonstração deste PC**.

Deixe o terminal aberto enquanto usa o sistema. Acesse [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) e faça a configuração abaixo antes de abrir as telas internas.

## Primeiro acesso: usuário, organização e perfil

1. Entre no **Django Admin** (`/admin/`) com o superusuário criado.
2. Em **Organizações**, crie o restaurante ou use uma organização existente. As migrações podem criar a “Organização padrão”.
3. Em **Perfis**, adicione um Perfil: escolha seu usuário, o restaurante e o papel **Administrador**. Se já existir um Perfil para esse usuário, edite-o; cada usuário tem apenas um.
4. Abra [o sistema](http://127.0.0.1:8000/). Se necessário, entre em [Login](http://127.0.0.1:8000/entrar/) com as mesmas credenciais.
5. Para criar contas da equipe, cadastre usuários no Admin e crie um Perfil para cada um, escolhendo a organização e o papel adequado.

**Criar o superusuário não cria automaticamente seu Perfil.** Sem esse vínculo, as telas internas e a API retornam 403. O superusuário ainda consegue acessar o Admin para configurar o vínculo.

O papel **Administrador** do Perfil permite gráfico mensal e exportação CSV; **Operador** visualiza os quatro indicadores, ranking e distribuição. A restrição por papel está implementada no dashboard/relatórios; os demais cadastros exigem autenticação e organização, sem uma matriz completa de permissões por papel. O Django Admin é a administração global, reservada ao superusuário, e é diferente do papel Administrador do restaurante.

No cabeçalho, **Minha conta** abre os dados do usuário/restaurante e o botão **Sair da conta**. A tela de login não exibe o menu interno.

## Dados de exemplo

Os comandos abaixo são opcionais. Execute em um segundo terminal aberto na pasta do projeto ou pare o servidor com `Ctrl + C` e inicie-o novamente depois.

### Pratos, combos e mesas

Descubra o ID do restaurante no Admin: ao abrir sua edição, o endereço termina em `/core/organizacao/ID/change/`. Também pode listar os IDs pelo terminal:

```powershell
.\.venv\Scripts\python.exe manage.py shell -c "from core.models import Organizacao; print(list(Organizacao.objects.values_list('id', 'nome')))"
```

Se o ID escolhido for **1**, execute:

```powershell
.\.venv\Scripts\python.exe manage.py popular_demo --organizacao 1
```

Substitua `1` pelo ID real. O comando prepara seis pratos de exemplo, dois combos e seis mesas, reaproveitando registros existentes sem apagar os dados. Ele **não cria usuário, Perfil ou vendas fechadas**.

### Vendas para demonstrar o dashboard

```powershell
.\.venv\Scripts\python.exe manage.py popular_dashboard_demo
```

Esse comando cria uma organização separada chamada **Restaurante demonstração · Dashboard**, com vendas fictícias no mês atual e nos dois anteriores; não cria vendas futuras no mês atual. O terminal informa o ID. Se essa organização já tiver comandas, uma nova execução não altera os registros.

Para visualizar esses dados, crie um usuário pelo Admin e um Perfil **Administrador** associado à organização de demonstração. Entre com esse usuário em `/entrar/` e abra `/dashboard/`. O comando não cria uma conta ou senha automaticamente. Uma conta vinculada a outro restaurante não verá essas vendas.

## Como iniciar novamente

Depois da primeira instalação, não precisa recriar o ambiente ou o administrador. Abra o terminal na pasta do projeto e execute:

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

Neste PC, o projeto está em:

```text
C:\Users\hendr\Documents\Codex\2026-11-17\2304\outputs\Trabalho_p1_marcio_cardapio
```

Para entrar nessa pasta pelo PowerShell:

```powershell
cd "C:\Users\hendr\Documents\Codex\2026-11-17\2304\outputs\Trabalho_p1_marcio_cardapio"
.\.venv\Scripts\python.exe manage.py runserver
```

Em outro computador, use a pasta em que você clonou. Para parar o servidor, pressione `Ctrl + C` no terminal. Após receber atualizações do projeto, instale novamente `requirements.txt` e execute `migrate` antes de iniciar.

## Caminhos das telas

Base local: **http://127.0.0.1:8000**. Acrescente o caminho abaixo a essa base. IDs são números reais dos registros; não digite os sinais `<` e `>`.

| Tela | Caminho | Para que serve / acesso |
| --- | --- | --- |
| Login | `/entrar/` | Entrar com usuário e senha |
| Mesas / salão | `/` | Mesas livres e ocupadas; abrir e acompanhar comandas; exige Perfil |
| Cardápio interno | `/cardapio/` | Consultar pratos e combos do restaurante; exige Perfil |
| Cardápio do cliente | `/menu/<organizacao_id>/` | Catálogo público, sem login; exemplo: `/menu/1/` se a organização 1 existir |
| Dashboard | `/dashboard/` | Indicadores, ranking, distribuição e gráfico conforme o papel |
| CSV | `/dashboard/exportar.csv` | Baixar relatório de comandas fechadas; Administrador do Perfil |
| Histórico | `/historico/` | Consultar comandas fechadas do restaurante |
| Cadastro de pratos | `/cadastros/pratos/` | Criar e listar pratos, bebidas, sobremesas etc. |
| Cadastro de combos | `/cadastros/combos/` | Criar e listar combinações de pratos |
| Cadastro de mesas | `/cadastros/mesas/` | Criar e listar mesas e capacidades |
| Editar cadastro | `/cadastros/<tipo>/<id>/` | `tipo`: `pratos`, `combos` ou `mesas` |
| Excluir cadastro | `/cadastros/<tipo>/<id>/excluir/` | Tela de confirmação; exclusão ocorre ao enviar o formulário |
| Comanda | `/comandas/<id>/` | Ver itens e total; adicionar itens enquanto estiver aberta |
| Fechar comanda | `/comandas/<id>/fechar/` | Conferir e confirmar o fechamento pelo formulário |
| Administração global | `/admin/` | Gerenciar usuários, organizações e perfis com superusuário |
| API de pratos | `/api/pratos/` | Lista e criação de pratos; login e Perfil obrigatórios |
| Detalhe de prato na API | `/api/pratos/<id>/` | Consultar, alterar ou excluir prato da própria organização |
| API do dashboard | `/api/dashboard/` | Indicadores em JSON, respeitando organização e papel |
| Login da API | `/api-auth/login/?next=/api/pratos/` | Autenticar pela interface navegável do DRF |

As ações `/mesas/<id>/abrir/`, `/comandas/<id>/itens/<item_id>/remover/` e `/sair/` são **POST**: use os botões da interface, pois abrir esses endereços diretamente na barra do navegador não executa a ação.

**Cardápio interno e público são diferentes:** `/cardapio/` é usado pela equipe; `/menu/<organizacao_id>/` é a experiência do cliente. O link **Cardápio do cliente ↗** do menu interno já abre a organização correta. No público, **Minha escolha** guarda uma seleção no navegador para mostrar ao atendente; não envia pedidos nem cria comandas.

### Filtros nos endereços

- Cardápio: `/cardapio/?q=frango&categoria=principal`.
- Público: `/menu/1/?q=suco&categoria=bebida` (troque o ID conforme o restaurante).
- Dashboard: `/dashboard/?inicio=2026-11-01&fim=2026-11-30`.
- CSV: `/dashboard/exportar.csv?inicio=2026-11-01&fim=2026-11-30`.
- API: `/api/dashboard/?inicio=2026-11-01&fim=2026-11-30`.

As datas na URL usam `AAAA-MM-DD`; escolha um período com vendas. Sem datas, o dashboard considera todo o histórico de comandas fechadas. Um período invertido ou inválido retorna erro 400. O botão de CSV mantém o período aplicado na tela.

## Fluxo de atendimento

1. Cadastre **pratos**, depois **combos** e **mesas**, ou use os exemplos.
2. No salão (`/`), abra uma comanda pelo botão da mesa desejada.
3. Na comanda, selecione **um prato ou um combo**, informe a quantidade e adicione. Repita para os demais itens.
4. Confira o total e, ao finalizar o atendimento, confirme **Fechar comanda**. A mesa fica disponível novamente.
5. Consulte o atendimento no **Histórico** e os resultados no **Dashboard**. Comandas abertas não entram nas métricas de vendas.
6. Como Administrador do Perfil, aplique o período e exporte o **CSV**.

Pratos/combos com histórico podem ter exclusão bloqueada para preservar as vendas; marque-os como indisponíveis quando necessário.

## Configuração do banco

O arquivo `.env` fica ao lado de `manage.py`. As opções lidas pelo projeto são:

| Variável | Uso |
| --- | --- |
| `SECRET_KEY` | Chave da aplicação |
| `DEBUG` | `True` no desenvolvimento local |
| `DB_ENGINE` | `sqlite` (padrão) ou `postgresql` |
| `DB_NAME` | Nome do banco PostgreSQL |
| `DB_USER` / `DB_PASSWORD` | Credenciais do PostgreSQL |
| `DB_HOST` / `DB_PORT` | Endereço e porta do PostgreSQL |
| `LOG_SQL` | `True` registra consultas no terminal quando `DEBUG=True` |

Com SQLite, os dados ficam em `db.sqlite3`, na pasta do projeto; as variáveis `DB_NAME`, `DB_USER` etc. não são usadas. `.env`, `.venv`, banco SQLite e senhas locais não são enviados ao GitHub.

Para PostgreSQL, instale e inicie o servidor de banco, crie um banco e usuário com acesso e ajuste o `.env`, por exemplo:

```dotenv
DB_ENGINE=postgresql
DB_NAME=cardapio_db
DB_USER=postgres
DB_PASSWORD=sua_senha_local
DB_HOST=localhost
DB_PORT=5432
```

Em seguida execute `migrate` e prepare usuário/Perfil nesse banco. Alterar o banco não transfere automaticamente os dados do SQLite. A validação registrada neste projeto foi feita com SQLite; PostgreSQL não foi validado nesta entrega.

`runserver` e `127.0.0.1` são usados para desenvolvimento no próprio computador. Para compartilhar o cardápio fora dele, é necessário configurar uma implantação e um domínio; este guia não publica o sistema na internet.

## Problemas comuns

| Problema | Como resolver |
| --- | --- |
| `python` não reconhecido | Confira a instalação/PATH ou use `py` para criar a `.venv` |
| `No module named django` | Instale `requirements.txt` e execute com `.\.venv\Scripts\python.exe` |
| `no such table` / tabela inexistente | Execute `manage.py migrate` com o Python da `.venv` |
| 403: credenciais não fornecidas na API | Entre em `/api-auth/login/?next=/api/pratos/` no mesmo navegador |
| Login funciona, mas telas retornam 403 | Crie/confira o Perfil e a organização do usuário no Admin |
| CSV retorna 403 ou gráfico mensal não aparece | Confira se o Perfil tem papel Administrador |
| Dashboard zerado | Confira organização e período; feche uma comanda ou use a demonstração e seu Perfil correspondente |
| Cardápio público vazio | Confira o ID do restaurante e se há pratos/combos disponíveis nessa organização |
| Registro retorna 404 | Confira ID e organização; usuários não acessam registros de outro restaurante |
| Porta 8000 em uso | Use `manage.py runserver 8001` e abra `http://127.0.0.1:8001/` |
| Esqueci a senha | Execute `.\.venv\Scripts\python.exe manage.py changepassword NOME_DO_USUARIO` |
| Estilo antigo no navegador | Atualize com `Ctrl + F5`; reinicie o servidor se ele estiver sem recarga automática |

## Estrutura do projeto

```text
config/                  Configurações e URLs principais
core/                    Organização, Perfil e isolamento por restaurante
cardapio/                Models, formulários, views, API e testes
cardapio/templates/      Telas HTML
cardapio/static/          CSS, JavaScript, ilustrações e Chart.js
cardapio/management/      Comandos de demonstração e auditoria SQL
manage.py                Entrada dos comandos Django
requirements.txt         Dependências Python com versões fixadas
.env.example             Modelo de configuração local
MELHORIAS_P1.md           Revisão da P1
BACKLOG_P2.md             Planejamento da P2
```

As seções abaixo detalham a API, as entregas das aulas e as verificações executadas.

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

A Aula 14 implementa organizações e login nas telas HTML. A Aula 17 adiciona dashboard e papéis administrador/operador para os relatórios, descritos ao final deste documento. O Django Admin é reservado ao superusuário do sistema e não equivale ao papel administrador de uma organização.

Referências técnicas: [generics do DRF](https://www.django-rest-framework.org/api-guide/generic-views/) e [permissões do DRF](https://www.django-rest-framework.org/api-guide/permissions/).


## Aula 14 — estrutura e migração

- `core.Organizacao`: nome e data de criação; `core.Perfil`: usuário único e organização.
- Base abstrata `DaOrganizacao`, herdada por **Prato, Combo, Mesa, Comanda e Item**. Todos têm FK obrigatória com `PROTECT`; Organizacao e User são raízes e não herdam a base.
- Migrações em três etapas: `0004` adiciona FKs nulas, `0005` preenche a organização padrão e os perfis dos usuários existentes, `0006` torna as FKs obrigatórias. Não existe default fixo de organização nos modelos.
- Usuários criados depois das migrações recebem seu Perfil pelo Admin. Sem perfil: 403 nas telas e API, inclusive para superusuário. Visitantes são enviados ao login nas telas HTML.
- `org_atual(request)` centraliza o vínculo. Criações usam a organização da sessão; formulários omitem esse campo e filtram FK/M2M. Models validam vínculos FK e o sinal M2M impede pratos de outra organização em combos.
- A mesa é única por `(organizacao, numero)`; duplicatas na mesma organização geram erro amigável no formulário.
- O Admin global é reservado ao dono do sistema (superusuário), com colunas/filtros de organização. A organização de um cadastro existente não é alterável pelo Admin. Para criar um combo no Admin, salve a organização e depois escolha seus pratos.
- No HTML, o botão Minha conta abre usuário e organização e permite sair por POST com CSRF; o menu interno não aparece no login.

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
