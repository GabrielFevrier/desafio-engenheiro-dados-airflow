from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Adiciona o diretório /opt/airflow ao path para o Python encontrar seu script
sys.path.append('/opt/airflow/dags')
from processar_dados import formatar_csv, enviar_para_solr

# Configurações padrão da DAG
default_args = {
    'owner': 'gabriel',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def pipeline_completo():
    caminho_csv = '/opt/airflow/dags/data/aluno.csv'
    dados = formatar_csv(caminho_csv)
    if dados is not None:
        enviar_para_solr(dados)
    else:
        raise Exception(f"Falha no processamento: Arquivo não encontrado em {caminho_csv}")

# Definição da DAG
with DAG(
    'dag_importacao_solr',
    default_args=default_args,
    description='Pipeline que formata CSV e envia para o Solr',
    schedule_interval=None, # Execução manual por enquanto
    catchup=False
) as dag:

    tarefa_importacao = PythonOperator(
        task_id='processar_e_enviar_dados',
        python_callable=pipeline_completo
    )
     