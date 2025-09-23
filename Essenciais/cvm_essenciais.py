
import sys, os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
	sys.path.insert(0, project_root)
from utils.cvm_utils import baixar_arquivo, gerar_lista_ano_mes

# ================================
# Função para baixar e salvar arquivos essenciais (LAMINA)
# ================================
def baixar_lamina(ano_mes):
    url = f"https://dados.cvm.gov.br/dados/FI/DOC/LAMINA/DADOS/lamina_fi_{ano_mes}.zip"
    nome_arquivo = f"lamina_fi_{ano_mes}.zip"
    return baixar_arquivo(url, nome_arquivo)

# ================================

# ================================
# Escolha dos anos e meses (edite conforme necessário)
# ================================
anos = [2024, 2025]
meses = [1, 2, 3, 4, 5]
ano_mes_list = gerar_lista_ano_mes(anos, meses)

for ano_mes in ano_mes_list:
	try:
		zip_path = baixar_lamina(ano_mes)
	except Exception as e:
		print(f"Erro ao baixar arquivo para {ano_mes}: {e}")