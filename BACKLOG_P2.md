# Backlog da P2

Planejamento da Aula 13 (17/11/2026). Cada tarefa tem estimativa de até uma sessão de aula. Aulas são marcos sugeridos, não datas fixas.

| Pilar | Aula | Issue |
| --- | --- | --- |
| multi-organizacao | 14 | [#1 — Criar organização e migrar dados da P1](https://github.com/hendryl000/Trabalho_p1_marcio_cardapio/issues/1) |
| multi-organizacao | 14 | [#2 — Isolar consultas e relacionamentos](https://github.com/hendryl000/Trabalho_p1_marcio_cardapio/issues/2) |
| perfis | 15 | [#3 — Criar perfil com organização e papel](https://github.com/hendryl000/Trabalho_p1_marcio_cardapio/issues/3) |
| perfis | 15 | [#4 — Aplicar permissões nas telas e API](https://github.com/hendryl000/Trabalho_p1_marcio_cardapio/issues/4) |
| api-rest | 16 | [#5 — Expor CRUD de combos e mesas](https://github.com/hendryl000/Trabalho_p1_marcio_cardapio/issues/5) |
| api-rest | 16 | [#6 — Expor abertura e fechamento de comandas](https://github.com/hendryl000/Trabalho_p1_marcio_cardapio/issues/6) |
| api-rest | 16 | [#7 — Expor inclusão e remoção de itens](https://github.com/hendryl000/Trabalho_p1_marcio_cardapio/issues/7) |
| dashboard | 17 | [#8 — Calcular indicadores com ORM](https://github.com/hendryl000/Trabalho_p1_marcio_cardapio/issues/8) |
| dashboard | 17 | [#9 — Criar tela de métricas por período](https://github.com/hendryl000/Trabalho_p1_marcio_cardapio/issues/9) |

## Ordem e marcos finais

Criar os modelos de organização e perfil antes do isolamento e permissões; depois expandir a API e integrar o dashboard. Manter os testes da P1 e da API passando.

- Aula 18: revisão de segurança e testes de isolamento, permissões e regras de negócio.
- Aula 19: polimento, configuração de ambiente e preparação da implantação/demonstração.
- Aula 20: entrega da P2 e T2 conforme orientações da disciplina.


## Atualização da Aula 14

- Issues #1 e #2: implementadas e verificadas pelo roteiro de isolamento; Item também possui FK direta, conforme o slide da Aula 14.
- Issue #3: vínculo Perfil/usuário/organização implementado; campo papel permanece para a Aula 15.
- Issue #4: login obrigatório implementado; matriz administrador/operador permanece para a Aula 15.
- Demais tarefas continuam planejadas.


## Atualização da Aula 17

Dashboard e relatórios implementados com quatro tipos de métrica, quatro cartões, período validado, Chart.js, CSV e API compartilhando a mesma base isolada. Papéis adicionados para controlar série mensal e exportação; operador mantém acesso aos resumos, conforme o slide. Auditoria de consultas e roteiro documentados no README, com 46 testes passando.

O escopo das issues #8 e #9 foi atendido no que corresponde à Aula 17; ocupação atual continua disponível na tela de mesas. A restrição de todo o dashboard a administradores, sugerida no backlog inicial, foi substituída pela matriz específica do slide (KPIs/ranking para ambos; série e CSV somente para administrador).
