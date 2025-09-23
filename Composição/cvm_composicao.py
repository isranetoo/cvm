
import sys, os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
	sys.path.insert(0, project_root)
from utils.cvm_utils import baixar_arquivo, gerar_lista_ano_mes

# ================================
# Função para baixar e carregar dados de composição CDA de um período
# ================================
def carregar_dados_composicao(ano_mes):
    url = f'https://dados.cvm.gov.br/dados/FI/DOC/CDA/DADOS/cda_fi_{ano_mes}.zip'
    nome_arquivo = f"cda_fi_{ano_mes}.zip"
    return baixar_arquivo(url, nome_arquivo)

# ================================
# 2. Definir anos e meses desejados (edite conforme necessário)
# ================================
anos = [2024, 2025]
meses = [1, 2, 3, 4, 5]
ano_mes_list = gerar_lista_ano_mes(anos, meses)

for ano_mes in ano_mes_list:
	try:
		zip_path = carregar_dados_composicao(ano_mes)
	except Exception as e:
		print(f"Erro ao baixar arquivo para {ano_mes}: {e}")