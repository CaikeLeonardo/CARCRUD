# CARCRUD API

API feita com **FastAPI** para gerenciar a frota de um vendedor de carros: cadastro de veículos, controle de despesas por veículo, registro de vendas e um resumo financeiro de cada carro.

> Projeto desenvolvido durante um curso de Python. Depois do curso, revisei o código sozinho para corrigir falhas de segurança e bugs, como forma de praticar boas práticas de backend.

## O que foi corrigido em relação à versão original

| Problema | Correção |
|---|---|
| Queries montadas com f-string, vulneráveis a SQL injection | Todas as queries agora usam parâmetros (`?`) |
| Senha do usuário salva em texto puro | Senha salva com hash (PBKDF2 + salt) |
| Login comparava a senha com a palavra literal `"senha"` | Corrigido para comparar com o hash da senha do banco |
| `vender_carro` usava `VALUE` em vez de `VALUES` e coluna errada | Corrigido, e endpoint `/vender_veiculo` criado |
| `JOIN` sem `ON` e `SUM` sem `GROUP BY` no resumo do veículo | Reescrito com `LEFT JOIN ... ON` e `GROUP BY` |
| Chave do JWT fixa (`"secret"`) no código | Chave lida de variável de ambiente `SECRET_KEY` |
| Token sem data de expiração | Token expira em 60 minutos |
| Caminho do banco fixo no computador do autor original | Caminho relativo ao projeto (configurável por `DATABASE_PATH`) |
| Autenticação aplicada só em parte dos endpoints | Endpoints de escrita (cadastrar veículo, despesa, venda) exigem token |

## Tecnologias

- Python 3.11
- FastAPI
- SQLite
- PyJWT
- Pydantic

## Como rodar

1. Clone o repositório:
   ```bash
   git clone https://github.com/CaikeLeonardo/CARCRUD_API.git
   cd CARCRUD_API
   ```
2. Crie um ambiente virtual e instale as dependências:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. (Opcional) Defina uma chave secreta para o JWT. Sem isso, uma chave temporária é gerada a cada execução:
   ```bash
   export SECRET_KEY="troque-por-uma-chave-aleatoria"   # Windows: set SECRET_KEY=...
   ```
4. Rode a API:
   ```bash
   python main.py
   ```
5. Acesse a documentação interativa em `http://localhost:8000/docs`.

## Endpoints

### Autenticação
| Método | Rota | Descrição |
|---|---|---|
| POST | `/cadastrar_usuario` | Cria um usuário e devolve o token |
| POST | `/login` | Autentica um usuário existente e devolve o token |

### Veículos (rotas de escrita exigem o header `token`)
| Método | Rota | Descrição |
|---|---|---|
| POST | `/cadastrar_veiculo` | Cadastra um novo veículo |
| GET | `/visualizar_veiculos` | Lista todos os veículos, ou busca por `placa` |
| GET | `/resumo_veiculo` | Dados do veículo, valor de compra e total gasto |

### Despesas
| Método | Rota | Descrição |
|---|---|---|
| POST | `/cadastrar_despesa` | Cadastra uma despesa de um veículo |
| GET | `/consultar_despesas_veiculo` | Lista despesas de um veículo |

### Vendas
| Método | Rota | Descrição |
|---|---|---|
| POST | `/vender_veiculo` | Registra a venda de um veículo e atualiza seu status |

## Testando pelo `/docs`

1. Chame `/cadastrar_usuario` com um usuário e senha. A resposta traz o `token`.
2. Clique em **Authorize** (cadeado no topo da página) e cole o token.
3. Use os demais endpoints normalmente.

## Estrutura

```
CARCRUD_API/
├── main.py              # rotas da API
├── models.py             # modelos Pydantic (validação dos dados)
├── conecta_banco.py       # conexão e todas as operações no banco SQLite
├── gerador_token.py       # geração e verificação do JWT
├── requirements.txt
└── .gitignore
```

## Próximos passos

- Migrar de SQLite para PostgreSQL
- Escrever testes automatizados com `pytest`
- Adicionar paginação em `/visualizar_veiculos`

## Autor

**Caike Leonardo**
[LinkedIn](https://www.linkedin.com/in/caikeleonardo) · [GitHub](https://github.com/CaikeLeonardo)
