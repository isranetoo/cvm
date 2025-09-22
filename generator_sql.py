
import os
import pandas as pd
import requests
import zipfile
import re

pd.options.display.float_format = '{:.4f}'.format

# Criar diretório temp
os.makedirs("temp", exist_ok=True)

# Função para gerar slug
def gerar_slug(nome):
    slug = nome.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    return slug.strip('-')

# Função para baixar dados mensais
def carregar_dados_mensais(ano, mes):
    mes = str(mes).zfill(2)
    url = f'https://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS/inf_diario_fi_{ano}{mes}.zip'
    download = requests.get(url, timeout=60)
    if download.status_code != 200:
        raise Exception(f"Arquivo não encontrado para {ano}-{mes}")
    zip_path = os.path.join("temp", f"inf_diario_fi_{ano}{mes}.zip")
    with open(zip_path, "wb") as f:
        f.write(download.content)
    zip_file = zipfile.ZipFile(zip_path)
    df = pd.read_csv(zip_file.open(zip_file.namelist()[0]), sep=";", encoding="ISO-8859-1")

    # Verificar qual coluna CNPJ está disponível e padronizar para CNPJ_FUNDO
    if "CNPJ_FUNDO_CLASSE" in df.columns and "CNPJ_FUNDO" not in df.columns:
        df = df.rename(columns={"CNPJ_FUNDO_CLASSE": "CNPJ_FUNDO"})
    elif "CNPJ_FUNDO" not in df.columns and "CNPJ_FUNDO_CLASSE" not in df.columns:
        raise Exception(f"Nenhuma coluna CNPJ encontrada no arquivo {ano}-{mes}")

    return df

# Cadastro de fundos
cadastro_raw = pd.read_csv(
    "https://dados.cvm.gov.br/dados/FI/CAD/DADOS/cad_fi.csv",
    sep=";", encoding="ISO-8859-1"
)

# Padronizar coluna CNPJ no cadastro também
if "CNPJ_FUNDO_CLASSE" in cadastro_raw.columns and "CNPJ_FUNDO" not in cadastro_raw.columns:
    cadastro_raw = cadastro_raw.rename(columns={"CNPJ_FUNDO_CLASSE": "CNPJ_FUNDO"})

cadastro = cadastro_raw[["CNPJ_FUNDO", "DENOM_SOCIAL"]].drop_duplicates()

anos = range(2021, 2025)
dados = []

for ano in anos:
    for mes in range(1, 13):
        try:
            df = carregar_dados_mensais(ano, mes)
            df = pd.merge(df, cadastro, on="CNPJ_FUNDO", how="left")
            df["Ano"] = ano
            df["Mes"] = mes
            # Filtrar fundos sem DENOM_SOCIAL
            df_filtrado = df[df["DENOM_SOCIAL"].notna()]
            dados.append(df_filtrado[["CNPJ_FUNDO", "DENOM_SOCIAL", "DT_COMPTC", "VL_QUOTA", "VL_PATRIM_LIQ"]])
            print(f"✅ {ano}-{mes:02d} processado")
        except Exception as e:
            print(f"❌ Erro {ano}-{mes:02d}: {e}")

# Consolidar
df_final = pd.concat(dados, ignore_index=True)

# ============================
# Gerar SQL
# ============================

sql_path = os.path.join("temp", "insert_funds_and_prices.sql")
with open(sql_path, "w", encoding="utf-8") as f:

    fundos_unicos = df_final[["CNPJ_FUNDO", "DENOM_SOCIAL"]].drop_duplicates()

    f.write("-- Inserção de fundos\n")
    for _, row in fundos_unicos.iterrows():
        nome = row["DENOM_SOCIAL"].replace("'", "''")
        cnpj = row["CNPJ_FUNDO"]
        slug = gerar_slug(nome)
        f.write(f"""
INSERT INTO funds (name, slug, cnpj, is_active)
VALUES ('{nome}', '{slug}', '{cnpj}', true)
ON CONFLICT (cnpj) DO NOTHING;
""")

    f.write("\n-- Inserção de preços históricos\n")
    for _, row in df_final.iterrows():
        nome = row["DENOM_SOCIAL"].replace("'", "''")
        cnpj = row["CNPJ_FUNDO"]
        data = row["DT_COMPTC"]
        quota = row["VL_QUOTA"]
        pl = row["VL_PATRIM_LIQ"]

        f.write(f"""
INSERT INTO fund_prices (fund_id, price_date, quota_value, net_worth)
SELECT id, '{data}', {quota:.6f}, {pl:.2f}
FROM funds WHERE cnpj = '{cnpj}'
ON CONFLICT (fund_id, price_date) DO NOTHING;
""")

print(f"📂 Arquivo '{sql_path}' gerado com sucesso!")
