import os
import pandas as pd
import requests
import zipfile

# Configuração de exibição
pd.options.display.float_format = '{:.4f}'.format

# ================================
# 1. Função para baixar e carregar dados diários de um mês/ano
# ================================
def carregar_dados_diarios(ano, mes):
	mes = str(mes).zfill(2)
	url = f'https://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS/inf_diario_fi_{ano}{mes}.zip'

	pasta_temp = os.path.join(os.path.dirname(__file__), "temp")
	os.makedirs(pasta_temp, exist_ok=True)
	zip_path = os.path.join(pasta_temp, f"inf_diario_fi_{ano}{mes}.zip")

	download = requests.get(url, timeout=60)
	if download.status_code != 200:
		raise Exception(f"Arquivo não encontrado para {ano}-{mes}")

	with open(zip_path, "wb") as arquivo_cvm:
		arquivo_cvm.write(download.content)

	print(f"Arquivo baixado: {zip_path}")
	return zip_path


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

