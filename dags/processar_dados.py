import subprocess
import sys
import os

# CONFIGURAÇÕES PARA AMBIENTE DOCKER
# 1. No Docker, usamos o nome do serviço 'solr_instance' em vez de 'localhost'
SOLR_URL = 'http://solr_instance:8983/solr/desafio_core'

# 2. O caminho deve ser o caminho INTERNO do container (onde montamos o volume)
CAMINHO_CSV = '/opt/airflow/dags/data/aluno.csv'

def instalar_dependencias():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pysolr", "pandas"])

def formatar_csv(path, separador=',', encoding='utf-8'):
    import pandas as pd
    try:
        # Verifica se o arquivo existe para dar um erro mais claro no log do Airflow
        if not os.path.exists(path):
            print(f"❌ Arquivo não encontrado no caminho interno: {path}")
            return None

        df = pd.read_csv(path, sep=separador, encoding=encoding)
        df.columns = df.columns.str.strip()
        print(f"✅ Arquivo '{path}' importado com sucesso!")
        
        try:
            # Conversão numérica (usando nomes exatos do seu CSV)
            df['Idade'] = pd.to_numeric(df['Idade'], errors='coerce').fillna(0).astype(int)
            df['Série'] = pd.to_numeric(df['Série'], errors='coerce').fillna(0).astype(int)
            df['Nota Média'] = pd.to_numeric(df['Nota Média'], errors='coerce').fillna(0.0).astype(float)
            
            # Limpeza de strings
            colunas_texto = ['Nome', 'Endereço', 'Nome do Pai', 'Nome da Mãe'] 
            for col in colunas_texto:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.strip()
                
            # Tratamento de Data (corrigido para evitar erro de atribuição em série)
            df['Data de Nascimento'] = pd.to_datetime(df['Data de Nascimento'], errors='coerce')
            df['Data de Nascimento'] = df['Data de Nascimento'].dt.strftime('%Y-%m-%dT%H:%M:%SZ').fillna('1900-01-01T00:00:00Z')

        except Exception as e:
            print(f"⚠️ Alerta na conversão de tipos: {e}")

        return df

    except UnicodeDecodeError:
        # Tenta latin1 se o utf-8 falhar (comum em arquivos gerados no Excel/Windows)
        return formatar_csv(path, separador=separador, encoding='latin1')
    except Exception as e:
        print(f"❌ Erro inesperado ao formatar CSV: {e}")
        return None

def enviar_para_solr(df):
    instalar_dependencias()
    import pysolr
    if df is None:
        print("⚠️ Operação cancelada: O DataFrame está vazio ou deu erro na leitura.")
        return

    try:
        # Timeout aumentado para evitar quebras em conexões lentas no Docker
        solr = pysolr.Solr(SOLR_URL, always_commit=True, timeout=20)
        
        documentos = df.to_dict(orient='records')
        
        print(f"📤 Enviando {len(documentos)} registros para o Solr...")
        solr.add(documentos)
        print("🚀 Sucesso! Dados inseridos no Solr.")

    except Exception as e:
        print(f"❌ Erro ao enviar para o Solr: {e}")
        # Levantamos o erro para a DAG do Airflow marcar a tarefa como "Failed"
        raise 

if __name__ == "__main__":
    # Teste local (se você rodar o script manualmente)
    dados = formatar_csv(CAMINHO_CSV)
    if dados is not None:
        enviar_para_solr(dados)