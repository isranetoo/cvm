
from utils.cvm_utils import baixar_arquivo

# ================================
# Função para baixar e carregar dados de balancete de um mês/ano
# ================================
def carregar_dados_balancete(ano, mes):
    mes = str(mes).zfill(2)
    url = f'https://dados.cvm.gov.br/dados/FI/DOC/BALANCETE/DADOS/balancete_fi_{ano}{mes}.zip'
    nome_arquivo = f"balancete_fi_{ano}{mes}.zip"
    return baixar_arquivo(url, nome_arquivo)

# ================================
# 2. Definir anos e meses desejados (edite conforme necessário)
# ================================
anos = [2025]
meses = [6, 7, 8]

for ano in anos:
	for mes in meses:
		try:
			zip_path = carregar_dados_balancete(str(ano), mes)
		except Exception as e:
			print(f"Erro ao baixar arquivo para {ano}-{str(mes).zfill(2)}: {e}")