import sys, os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
	sys.path.insert(0, project_root)
from utils.cvm_utils import baixar_arquivo
import pandas as pd

# Configuração de exibição
pd.options.display.float_format = '{:.4f}'.format

# ================================
# 1. Função para baixar e carregar dados diários de um mês/ano
# ================================
def carregar_dados_diarios(ano, mes):
    mes = str(mes).zfill(2)
    url = f'https://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS/inf_diario_fi_{ano}{mes}.zip'
    nome_arquivo = f"inf_diario_fi_{ano}{mes}.zip"
    return baixar_arquivo(url, nome_arquivo)


# ================================
# 2. Definir anos e meses desejados (edite conforme necessário)
# ================================
anos = [2024]  # Exemplo: pode adicionar/remover anos
meses = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]       # Exemplo: pode adicionar/remover meses

for ano in anos:
	for mes in meses:
		try:
			zip_path = carregar_dados_diarios(str(ano), mes)
		except Exception as e:
			print(f"Erro ao baixar arquivo para {ano}-{mes:02d}: {e}")

