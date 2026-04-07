Markdown
# 🚀 Pipeline de Dados: Airflow + Apache Solr

![Airflow](https://img.shields.io/badge/Airflow-017CEE?style=for-the-badge&logo=Apache%20Airflow&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Solr](https://img.shields.io/badge/Solr-D9411E?style=for-the-badge&logo=Apache%20Solr&logoColor=white)

## 📑 Sumário  
1. [Sobre o Projeto](#-sobre-o-projeto)  
2. [Tecnologias Utilizadas](#-tecnologias-utilizadas)  
3. [Estrutura do Projeto](#-estrutura-do-projeto)  
4. [Lógica do Fluxo de Dados](#-lógica-do-fluxo-de-dados)  
5. [Passo-a-passo de Execução](#-passo-a-passo-de-execução)  

---

# 📊 Sobre o Projeto

Este projeto demonstra a criação de um pipeline de dados automatizado para o processamento e indexação de informações acadêmicas.

🎯 **Objetivo:** Extrair dados de um arquivo CSV bruto (`aluno.csv`), realizar o tratamento e limpeza dos dados via Python e carregar as informações no motor de busca **Apache Solr**, utilizando o **Apache Airflow** como orquestrador.

---

# 🛠 Tecnologias Utilizadas

- **Orquestração:** Apache Airflow 2.7.1
- **Linguagem:** Python 3.8+ (Pandas, PySolr)
- **Infraestrutura:** Docker & Docker Compose
- **Destino:** Apache Solr 8.11

---

# 🗂 Estrutura do Projeto

```text
airflow/
│
├── dags/
│   ├── dag_desafio.py          # Definição da DAG e orquestração
│   ├── processar_dados.py      # Lógica de ETL e conexão com Solr
│   └── data/
│       └── aluno.csv           # Arquivo bruto de origem
│
├── logs/
│   └── .gitkeep                # Estrutura para logs de execução
├── plugins/
│   └── .gitkeep                # Estrutura para plugins customizados
│
├── docker-compose.yaml         # Configuração do ambiente (Airflow + Solr + DB)
├── .gitignore                  # Filtro de arquivos para o repositório
└── README.md                   # Documentação do projeto
🔄 Lógica do Fluxo de Dados
O pipeline é executado de forma manual ou agendada através da DAG dag_importacao_solr.

Leitura: O arquivo aluno.csv é lido do diretório de dados local.

Transformação: O Python (Pandas) realiza a limpeza, tipagem de campos (como datas e notas) e gera IDs únicos para cada documento.

Carga: Utilizando a biblioteca pysolr, os dados são enviados para o core do Apache Solr para indexação imediata.

▶ Passo-a-passo de Execução
1. Preparação
Certifique-se de ter o Docker e o Git instalados. Clone o repositório:

Bash
git clone [https://github.com/GabrielFevrier/desafio-engenheiro-dados-airflow.git](https://github.com/GabrielFevrier/desafio-engenheiro-dados-airflow.git)
2. Inicialização do Ambiente
Dentro da pasta do projeto, suba os containers:

Bash
docker-compose up -d
3. Instalação de Dependências
Como o Airflow roda em containers isolados, instale as bibliotecas necessárias no Scheduler:

Bash
docker exec -u 0 -it airflow-scheduler-1 pip install pysolr pandas
4. Execução da DAG
Acesse o Airflow em http://localhost:8080 (Login/Senha: airflow).

Ative a DAG dag_importacao_solr.

Clique no botão Trigger para iniciar o processamento.

5. Verificação dos Resultados
Acesse o painel do Solr em http://localhost:8983 para consultar os 156 documentos indexados.

✨ Projeto desenvolvido por Gabriel Fevrier