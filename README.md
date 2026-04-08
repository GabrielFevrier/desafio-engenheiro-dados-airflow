# Pipeline de Dados: Airflow + Apache Solr

![Airflow](https://img.shields.io/badge/Apache%20Airflow-2.7.1-017CEE?style=flat-square&logo=Apache%20Airflow&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![Solr](https://img.shields.io/badge/Apache%20Solr-latest-D9411E?style=flat-square&logo=Apache%20Solr&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-3.x-150458?style=flat-square&logo=pandas&logoColor=white)

Pipeline de dados orquestrado pelo **Apache Airflow** que realiza a leitura, limpeza e indexação de registros acadêmicos no motor de busca **Apache Solr**, com toda a infraestrutura containerizada via **Docker Compose**.

---

## Sumário

- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Tecnologias](#tecnologias)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Fluxo de Dados](#fluxo-de-dados)
- [Como Executar](#como-executar)
- [Verificação dos Resultados](#verificação-dos-resultados)

---

## Visão Geral

Este projeto foi desenvolvido como solução para um desafio técnico de engenharia de dados. O objetivo é construir um pipeline ETL completo que:

1. **Extrai** dados brutos de um arquivo CSV (`aluno.csv`) com informações de alunos do ensino básico
2. **Transforma** os dados aplicando limpeza, tipagem e padronização com Python e Pandas
3. **Carrega** os documentos formatados no Apache Solr para indexação e busca

---

## Arquitetura

```
┌─────────────┐     ┌───────────────────────────────────────────┐     ┌────────────────────┐
│             │     │              Apache Airflow                │     │                    │
│  aluno.csv  │────▶│  DAG: dag_importacao_solr                  │────▶│    Apache Solr     │
│             │     │  Task: processar_e_enviar_dados            │     │  core: desafio_core│
└─────────────┘     │   ├─ formatar_csv()   (pandas)            │     │                    │
                    │   └─ enviar_para_solr() (pysolr)          │     └────────────────────┘
                    └───────────────────────────────────────────┘
                                        
                            
                            
```

Todos os serviços são definidos e inicializados via `docker-compose.yml`.

---

## Tecnologias

| Camada | Tecnologia | Versão |
|---|---|---|
| Orquestração | Apache Airflow | 2.7.1 |
| Processamento | Python + Pandas | 3.8+ / 3.x |
| Integração Solr | PySolr | 3.11.0 |
| Indexação | Apache Solr | latest |
| Metadados do Airflow | PostgreSQL | 13 |
| Infraestrutura | Docker + Docker Compose | — |

---

## Estrutura do Projeto

```
airflow/
│
├── dags/
│   ├── dag_desafio.py          # Definição da DAG e orquestração da task
│   ├── processar_dados.py      # Lógica de ETL e integração com o Solr
│   └── data/
│       └── aluno.csv           # Arquivo de origem com dados brutos
│
├── logs/                       # Logs gerados pelo Airflow em execução
│   └── .gitkeep
├── plugins/
│   └── .gitkeep
│
├── docker-compose.yml          # Definição dos serviços (Airflow + Solr + PostgreSQL)
├── requirements.txt            # Dependências Python do projeto
├── .gitignore
└── README.md
```

---

## Fluxo de Dados

A DAG `dag_importacao_solr` contém uma única task (`processar_e_enviar_dados`) que executa o pipeline completo em sequência, chamando duas funções do módulo `processar_dados.py`:

### `formatar_csv()`

Responsável pela etapa de transformação dos dados brutos:

- Leitura do `aluno.csv` com fallback automático de encoding (UTF-8 → latin-1)
- Remoção de espaços em branco nos cabeçalhos das colunas
- Conversão de tipos: `Idade` e `Série` → inteiro, `Nota Média` → float
- Limpeza de strings nas colunas de texto (`Nome`, `Endereço`, `Nome do Pai`, `Nome da Mãe`)
- Padronização de `Data de Nascimento` para o formato ISO 8601 (`yyyy-MM-ddTHH:mm:ssZ`)
- Tratamento de valores nulos com preenchimento de defaults seguros

### `enviar_para_solr()`

Responsável pela etapa de carga no core `desafio_core` do Solr:

- Instalação de dependências em runtime via `pip` (compatível com a imagem base do Airflow)
- Conexão ao Solr pelo nome de serviço interno do Docker (`solr_instance:8983`)
- Conversão do DataFrame para lista de documentos e envio via `pysolr`
- Commit automático ao final da inserção (`always_commit=True`)
- Tratamento de exceções com re-raise para que o Airflow registre a task como `Failed`

---

## Como Executar

### Pré-requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e em execução
- [Git](https://git-scm.com/) instalado (Opcional)

### 1. Clone o repositório

```bash
git clone https://github.com/GabrielFevrier/desafio-engenheiro-dados-airflow.git
cd desafio-engenheiro-dados-airflow
```

### 2. Inicialize o banco de metadados do Airflow

Este passo é necessário apenas na primeira execução:

```bash
docker compose run --rm scheduler airflow db init
```

### 3. Suba os containers

```bash
docker compose up -d
```

> O primeiro start pode levar 1–2 minutos enquanto as imagens são baixadas e os serviços inicializam.

### 4. Instale as dependências Python no Scheduler e no Webserver

Como a imagem base do Airflow não inclui as bibliotecas do projeto, instale-as nos containers em execução:

```bash
docker compose exec scheduler pip install pysolr pandas
docker compose exec webserver pip install pysolr pandas
```

### 5. Acesse o Airflow

Abra [http://localhost:8080](http://localhost:8080) no navegador.

| Campo | Valor |
|---|---|
| Usuário | `airflow` |
| Senha | `airflow` |

### 6. Execute o pipeline

1. Localize a DAG `dag_importacao_solr` na listagem
2. Ative a DAG pelo toggle lateral (caso esteja pausada)
3. Clique em **Trigger DAG** para iniciar a execução manualmente
4. Acompanhe o progresso em **Graph View** ou nos **Logs** da task `processar_e_enviar_dados`

---

## Verificação dos Resultados

Após a DAG concluir com sucesso, acesse o painel administrativo do Solr:

```
http://localhost:8983/solr
```

O core `desafio_core` deve conter **80 documentos** indexados ao final da execução.

---

## Encerrando o Ambiente

Para parar os containers sem remover os dados:

```bash
docker compose down
```

Para remover containers e volumes (reinício limpo):

```bash
docker compose down -v
```

---

Desenvolvido por [Gabriel Fevrier](https://github.com/GabrielFevrier)
