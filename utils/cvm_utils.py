import os
import requests
from typing import Optional

def baixar_arquivo(url: str, nome_arquivo: str, pasta_temp: Optional[str] = None, timeout: int = 60) -> str:
    """
    Baixa um arquivo de uma URL e salva em uma pasta temporária.
    Args:
        url (str): URL do arquivo para download.
        nome_arquivo (str): Nome do arquivo para salvar.
        pasta_temp (str, opcional): Caminho da pasta temporária. Se None, usa 'temp' ao lado do arquivo chamador.
        timeout (int): Tempo limite para download em segundos.
    Returns:
        str: Caminho completo do arquivo salvo.
    Raises:
        Exception: Se o download falhar.
    """
    if pasta_temp is None:
        pasta_temp = os.path.join(os.path.dirname(__file__), "temp")
    os.makedirs(pasta_temp, exist_ok=True)
    zip_path = os.path.join(pasta_temp, nome_arquivo)

    download = requests.get(url, timeout=timeout)
    if download.status_code != 200:
        raise Exception(f"Arquivo não encontrado: {url}")

    with open(zip_path, "wb") as arquivo:
        arquivo.write(download.content)

    print(f"Arquivo baixado: {zip_path}")
    return zip_path

def gerar_lista_ano_mes(anos, meses):
    """
    Gera lista de strings no formato AAAAMM a partir de listas de anos e meses.
    Args:
        anos (list): Lista de anos (int ou str).
        meses (list): Lista de meses (int ou str).
    Returns:
        list: Lista de strings AAAAMM.
    """
    return [f"{ano}{str(mes).zfill(2)}" for ano in anos for mes in meses]
