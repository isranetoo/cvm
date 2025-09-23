import os
import json
from collections import defaultdict

# Caminho do arquivo JSON salvo
json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp', 'dados_diarios.json')

# Carrega os dados do JSON
with open(json_path, 'r', encoding='utf-8') as f:
    all_data = json.load(f)

# Organiza os dados por CNPJ_FUNDO_CLASSE
grouped = defaultdict(list)
for item in all_data:
    cnpj = item.get('CNPJ_FUNDO_CLASSE')
    # Remove o campo CNPJ_FUNDO_CLASSE dos dados individuais
    dados_item = {k: v for k, v in item.items() if k != 'CNPJ_FUNDO_CLASSE'}
    grouped[cnpj].append(dados_item)

# Cria a estrutura final
final_data = []
for cnpj, dados in grouped.items():
    final_data.append({
        'CNPJ_FUNDO_CLASSE': cnpj,
        'dados': dados
    })

# Salva o resultado em um novo JSON
json_out_path = os.path.join(os.path.dirname(json_path), 'dados_diarios_organizado.json')
with open(json_out_path, 'w', encoding='utf-8') as f:
    json.dump(final_data, f, ensure_ascii=False, indent=2)

print(f'Dados organizados salvos em: {json_out_path}')
