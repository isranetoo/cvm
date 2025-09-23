import os
import zipfile
import pandas as pd
import json

# Caminho da pasta de arquivos baixados
temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp')

# Lista todos os arquivos .zip na pasta temp
zip_files = [f for f in os.listdir(temp_dir) if f.endswith('.zip')]

all_data = []
for zip_file in zip_files:
    zip_path = os.path.join(temp_dir, zip_file)
    with zipfile.ZipFile(zip_path, 'r') as z:
        # Assume que há apenas um arquivo CSV por zip
        csv_name = [name for name in z.namelist() if name.endswith('.csv')][0]
        with z.open(csv_name) as csvfile:
            df = pd.read_csv(csvfile, sep=';', encoding='latin1')
            # Converte cada linha do DataFrame em dict e adiciona à lista
            all_data.extend(df.to_dict(orient='records'))

# Salva todos os dados em um arquivo JSON
json_path = os.path.join(temp_dir, 'dados_diarios.json')
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print(f'Dados salvos em: {json_path}')
