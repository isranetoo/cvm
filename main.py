
import os
import pandas as pd
import requests
import zipfile

# Configuração de exibição
pd.options.display.float_format = '{:.4f}'.format

# ================================
# 1. Função para baixar e carregar dados mensais
# ================================
def carregar_dados_mensais(ano, mes):
    mes = str(mes).zfill(2)  # garante 2 dígitos
    url = f'https://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS/inf_diario_fi_{ano}{mes}.zip'

    # Pasta temp para arquivos baixados
    os.makedirs("temp", exist_ok=True)
    zip_path = os.path.join("temp", f"inf_diario_fi_{ano}{mes}.zip")

    # Download do arquivo ZIP
    download = requests.get(url, timeout=60)
    if download.status_code != 200:
        raise Exception(f"Arquivo não encontrado para {ano}-{mes}")

    with open(zip_path, "wb") as arquivo_cvm:
        arquivo_cvm.write(download.content)

    # Ler arquivo CSV dentro do ZIP
    arquivo_zip = zipfile.ZipFile(zip_path)
    try:
        dados = pd.read_csv(
            arquivo_zip.open(arquivo_zip.namelist()[0]),
            sep=";",
            encoding="ISO-8859-1",
            low_memory=False,
            dtype={"CNPJ_FUNDO": str, "CNPJ_FUNDO_CLASSE": str}
        )

        # Verificar se alguma das colunas CNPJ existe e padronizar
        if 'CNPJ_FUNDO' in dados.columns:
            # Já está no formato esperado
            pass
        elif 'CNPJ_FUNDO_CLASSE' in dados.columns:
            # Renomear para o formato padrão
            dados = dados.rename(columns={'CNPJ_FUNDO_CLASSE': 'CNPJ_FUNDO'})
        else:
            print(f"⚠️ Arquivo {ano}-{mes} sem coluna 'CNPJ_FUNDO' ou 'CNPJ_FUNDO_CLASSE'. Pulando...")
            return pd.DataFrame()

        return dados
    except Exception as e:
        print(f"⚠️ Erro ao ler CSV {ano}-{mes}: {e}")
        return pd.DataFrame()

# ================================
# 2. Cadastro dos fundos (carrega 1 vez só)
# ================================
dados_cadastro = pd.read_csv(
    'https://dados.cvm.gov.br/dados/FI/CAD/DADOS/cad_fi.csv',
    sep=";",
    encoding="ISO-8859-1"
)
dados_cadastro = dados_cadastro[['CNPJ_FUNDO', 'DENOM_SOCIAL']].drop_duplicates()

# ================================
# 3. Loop sobre anos e meses (2020–2025)
# ================================
anos = range(2021, 2026)  # de 2020 até 2025
resultados = []

for ano in anos:
    for mes in range(1, 13):  # janeiro a dezembro
        try:
            dados_fundos = carregar_dados_mensais(str(ano), mes)

            # Verificar se dados foram carregados com sucesso
            if dados_fundos.empty:
                continue

            # Ordenar datas disponíveis
            datas = sorted(dados_fundos['DT_COMPTC'].unique())
            if len(datas) < 2:
                continue
            data_inicio_mes, data_fim_mes = datas[0], datas[-1]

            # Filtrar apenas início e fim do mês
            dados_filtrados = dados_fundos[
                dados_fundos['DT_COMPTC'].isin([data_inicio_mes, data_fim_mes])
            ]

            # Juntar com cadastro
            base = pd.merge(
                dados_filtrados,
                dados_cadastro,
                how="left",
                on="CNPJ_FUNDO"
            )
            # Patrimônio no fim do mês
            patrimonio = (
                base[base['DT_COMPTC'] == data_fim_mes]
                [['CNPJ_FUNDO', 'VL_PATRIM_LIQ']]
                .rename(columns={'VL_PATRIM_LIQ': 'Patrimonio_MM'})
            )
            patrimonio['Patrimonio_MM'] = (patrimonio['Patrimonio_MM'] / 1_000_000).round(2)

            # Retorno mensal (%)
            inicio = base[base['DT_COMPTC'] == data_inicio_mes][['CNPJ_FUNDO', 'VL_QUOTA']]
            fim = base[base['DT_COMPTC'] == data_fim_mes][['CNPJ_FUNDO', 'VL_QUOTA']]
            retorno = pd.merge(inicio, fim, on='CNPJ_FUNDO', suffixes=('_ini', '_fim'))
            retorno['Retorno_%'] = ((retorno['VL_QUOTA_fim'] / retorno['VL_QUOTA_ini'] - 1) * 100).round(2)

            # Consolidar
            resumo = pd.merge(patrimonio, retorno[['CNPJ_FUNDO', 'Retorno_%']], on='CNPJ_FUNDO', how='left')
            resumo['Ano'] = ano
            resumo['Mes'] = mes
            resumo = pd.merge(resumo, dados_cadastro, on='CNPJ_FUNDO', how='left')

            resultados.append(resumo)

            print(f"✅ {ano}-{mes:02d} processado")
        except Exception as e:
            print(f"❌ Erro em {ano}-{mes:02d}: {e}")

# ================================
# 4. Consolidar resultados mensais
# ================================
df_mensal = pd.concat(resultados, ignore_index=True)
df_mensal = df_mensal[['Ano', 'Mes', 'CNPJ_FUNDO', 'DENOM_SOCIAL', 'Patrimonio_MM', 'Retorno_%']]

# Filtrar fundos sem denominação social
total_antes = len(df_mensal)
df_mensal = df_mensal.dropna(subset=['DENOM_SOCIAL'])
df_mensal = df_mensal[df_mensal['DENOM_SOCIAL'].str.strip() != '']
total_depois = len(df_mensal)
print(f"🔍 Filtro DENOM_SOCIAL: {total_antes:,} → {total_depois:,} registros ({total_antes - total_depois:,} removidos)")

# ================================
# 5. Resumo anual
# ================================
# Patrimônio: último mês do ano
patrimonio_anual = (
    df_mensal.sort_values(['Ano', 'Mes'])
    .groupby(['Ano', 'CNPJ_FUNDO'])
    .last()[['Patrimonio_MM']]
    .reset_index()
)

# Retorno acumulado: multiplicar rentabilidades mensais
df_mensal['Fator'] = 1 + (df_mensal['Retorno_%'].fillna(0) / 100)
retorno_anual = (
    df_mensal.groupby(['Ano', 'CNPJ_FUNDO'])['Fator']
    .prod()
    .reset_index()
)
retorno_anual['Retorno_Acumulado_%'] = ((retorno_anual['Fator'] - 1) * 100).round(2)
retorno_anual = retorno_anual.drop(columns=['Fator'])

# Juntar patrimônio + retorno
df_anual = pd.merge(patrimonio_anual, retorno_anual, on=['Ano', 'CNPJ_FUNDO'], how='left')
df_anual = pd.merge(df_anual, dados_cadastro, on='CNPJ_FUNDO', how='left')
df_anual = df_anual[['Ano', 'CNPJ_FUNDO', 'DENOM_SOCIAL', 'Patrimonio_MM', 'Retorno_Acumulado_%']]

# Filtrar fundos sem denominação social no resumo anual
total_anual_antes = len(df_anual)
df_anual = df_anual.dropna(subset=['DENOM_SOCIAL'])
df_anual = df_anual[df_anual['DENOM_SOCIAL'].str.strip() != '']
total_anual_depois = len(df_anual)
print(f"🔍 Filtro DENOM_SOCIAL anual: {total_anual_antes:,} → {total_anual_depois:,} registros ({total_anual_antes - total_anual_depois:,} removidos)")


# ================================
# 6. Filtrar dados para Excel e salvar arquivos
# ================================
os.makedirs("temp", exist_ok=True)

# Aplicar filtros para reduzir tamanho dos dados para Excel
# Filtro 1: Fundos com patrimônio mínimo de 10 milhões
df_mensal_filtrado = df_mensal[df_mensal['Patrimonio_MM'] >= 10].copy()
df_anual_filtrado = df_anual[df_anual['Patrimonio_MM'] >= 10].copy()

# Filtro 2: Se ainda muito grande, manter apenas top fundos por patrimônio
MAX_EXCEL_ROWS = 1000000  # Margem de segurança abaixo do limite do Excel

if len(df_mensal_filtrado) > MAX_EXCEL_ROWS:
    # Ordenar por patrimônio e manter os maiores
    df_mensal_filtrado = (df_mensal_filtrado
                         .sort_values('Patrimonio_MM', ascending=False)
                         .head(MAX_EXCEL_ROWS))
    print(f"⚠️ Dados mensais limitados aos {MAX_EXCEL_ROWS} maiores fundos por patrimônio")

if len(df_anual_filtrado) > MAX_EXCEL_ROWS:
    df_anual_filtrado = (df_anual_filtrado
                        .sort_values('Patrimonio_MM', ascending=False)
                        .head(MAX_EXCEL_ROWS))
    print(f"⚠️ Dados anuais limitados aos {MAX_EXCEL_ROWS} maiores fundos por patrimônio")

# Nomes dos arquivos
mensal_csv = os.path.join("temp", "fundos_mensal_2020_2025.csv")
anual_csv = os.path.join("temp", "fundos_anual_2020_2025.csv")
mensal_xlsx = os.path.join("temp", "fundos_mensal_2020_2025.xlsx")
anual_xlsx = os.path.join("temp", "fundos_anual_2020_2025.xlsx")

# Salvar CSVs completos (sem limite de linhas)
df_mensal.to_csv(mensal_csv, index=False, encoding="utf-8-sig")
df_anual.to_csv(anual_csv, index=False, encoding="utf-8-sig")

# Salvar Excel com dados filtrados
print(f"📊 Salvando Excel mensal com {len(df_mensal_filtrado):,} linhas...")
df_mensal_filtrado.to_excel(mensal_xlsx, index=False)

print(f"📊 Salvando Excel anual com {len(df_anual_filtrado):,} linhas...")
df_anual_filtrado.to_excel(anual_xlsx, index=False)

print("\n📂 Arquivos gerados:")
print(f"- CSV completo: {mensal_csv} ({len(df_mensal):,} linhas)")
print(f"- CSV completo: {anual_csv} ({len(df_anual):,} linhas)")
print(f"- Excel filtrado: {mensal_xlsx} ({len(df_mensal_filtrado):,} linhas)")
print(f"- Excel filtrado: {anual_xlsx} ({len(df_anual_filtrado):,} linhas)")

print("\n📊 Prévia dos dados mensais:")
print(df_mensal.head(10))

print("\n📊 Prévia dos dados anuais:")
print(df_anual.head(10))

print("\n💡 Filtros aplicados no Excel:")
print("- Patrimônio mínimo: 10 milhões")
print("- Fundos sem denominação social removidos")
print("- Dados completos salvos em CSV (sem limitação de linhas)")
print("- Dados filtrados salvos em Excel (compatível com limites do Excel)")
