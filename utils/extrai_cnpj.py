import os
import pandas as pd
import json
import zipfile
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# Descompacta arquivos ZIP da pasta temp
temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
data_dir = os.path.join(os.path.dirname(__file__), 'data')

# Cria a pasta data se não existir
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Descompacta todos os arquivos ZIP da pasta temp para a pasta data
if os.path.exists(temp_dir):
    for arquivo in os.listdir(temp_dir):
        if arquivo.endswith('.zip'):
            caminho_zip = os.path.join(temp_dir, arquivo)
            print(f'Descompactando {arquivo}...')
            try:
                with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
                    zip_ref.extractall(data_dir)
                print(f'{arquivo} descompactado com sucesso!')
            except Exception as e:
                print(f'Erro ao descompactar {arquivo}: {e}')


# Novo: Organiza todos os CNPJs encontrados nos arquivos CSV

# Salva incrementalmente cada CNPJ encontrado
resultados = {}
json_path = 'informacoes_cnpj.json'
if os.path.exists(json_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            resultados = json.load(f)
    except Exception:
        resultados = {}


csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]

def process_csv(nome_arquivo):
    caminho_arquivo = os.path.join(data_dir, nome_arquivo)
    df = None
    for encoding in ['utf-8', 'latin1']:
        for sep in [None, ';', ',']:
            try:
                df = pd.read_csv(caminho_arquivo, dtype=str, sep=sep, engine='python', encoding=encoding)
                break
            except Exception:
                df = None
        if df is not None:
            break
    if df is None:
        return nome_arquivo, None
    # Busca por colunas de CNPJ de forma mais flexível
    possiveis_colunas_cnpj = ['CNPJ_FUNDO_CLASSE', 'CNPJ_FUNDO', 'CNPJ', 'Cnpj_Fundo']
    col_cnpj = None
    for col in possiveis_colunas_cnpj:
        if col in df.columns:
            col_cnpj = col
            break
    
    # Se não encontrou, procura por qualquer coluna que contenha 'cnpj'
    if col_cnpj is None:
        for col in df.columns:
            if 'cnpj' in col.lower():
                col_cnpj = col
                break
    
    tqdm.write(f'Arquivo {nome_arquivo}: Coluna CNPJ encontrada = {col_cnpj}')
    cnpj_dict = {}
    if col_cnpj:
        df = df.fillna('NaN')
        grupos = df.groupby(col_cnpj)
        for cnpj, grupo in grupos:
            cnpj_dict[cnpj] = grupo.to_dict(orient='records')
        return nome_arquivo, cnpj_dict
    return nome_arquivo, None

num_workers = min(32, os.cpu_count() or 4)  # Usa até 32 threads
with ThreadPoolExecutor(max_workers=num_workers) as executor:
    futures = {executor.submit(process_csv, nome_arquivo): nome_arquivo for nome_arquivo in csv_files}
    for future in tqdm(as_completed(futures), total=len(futures), desc=f'Processando arquivos CSV ({num_workers} threads)'):
        nome_arquivo = futures[future]
        try:
            nome_arquivo, cnpj_dict = future.result()
            if cnpj_dict:
                for cnpj, registros in cnpj_dict.items():
                    if cnpj not in resultados:
                        resultados[cnpj] = {}
                    resultados[cnpj][nome_arquivo] = registros
                tqdm.write(f'{len(cnpj_dict)} CNPJs do arquivo {nome_arquivo} processados')
            else:
                tqdm.write(f'Não foi possível ler o arquivo {nome_arquivo}')
        except Exception as e:
            tqdm.write(f'Erro ao processar {nome_arquivo}: {e}')


# Salva o JSON apenas uma vez ao final
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2)

print(f'Arquivo informacoes_cnpj.json criado com dados de {len(resultados)} CNPJs.')
print(f'Total de arquivos CSV processados: {len(csv_files)}')
print(f'CNPJs encontrados: {list(resultados.keys())}')
