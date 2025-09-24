import json
from datetime import datetime
from pathlib import Path
import re

# Função para converter valores numéricos
def to_float(value):
    try:
        if value in ("NaN", None, "", "nan"):
            return None
        return float(value)
    except Exception:
        return None

# Função para converter datas
def to_date(value):
    try:
        if value in ("NaN", None, "", "nan"):
            return None
        return datetime.strptime(value, "%Y-%m-%d").date().isoformat()
    except Exception:
        return None

# Função para detectar períodos disponíveis nos dados
def get_available_periods(data_dict):
    periods = set()
    # Busca por padrões de período nos nomes dos arquivos (ex: 202401, 202402, etc)
    for filename in data_dict.keys():
        match = re.search(r'(\d{6})', filename)
        if match:
            periods.add(match.group(1))
    return sorted(list(periods))

def normalize_json(original_json):
    # Processa todos os fundos no JSON
    if not original_json:
        print('Nenhum dado de CNPJ encontrado no JSON. Verifique os arquivos de entrada.')
        return []
    
    funds_dict = {}
    # Itera sobre todos os CNPJs no JSON
    for cnpj, data_dict in original_json.items():
        available_periods = get_available_periods(data_dict)
        if not available_periods:
            print(f'Nenhum período encontrado para CNPJ {cnpj}')
            continue
        print(f'Processando CNPJ {cnpj} - Períodos disponíveis: {available_periods}')
        fund = {"cnpj": cnpj, "name": None, "tipo": None}
        for period in available_periods:
            first_app_key = f"cda_fi_BLC_1_{period}.csv"
            if first_app_key in data_dict and data_dict[first_app_key]:
                first_app = data_dict[first_app_key][0]
                fund["name"] = first_app.get("DENOM_SOCIAL")
                fund["tipo"] = first_app.get("TP_FUNDO_CLASSE")
                break
        balances = []
        for period in available_periods:
            balance_key = f"balancete_fi_{period}.csv"
            if balance_key in data_dict:
                for row in data_dict[balance_key]:
                    balances.append({
                        "data": to_date(row.get("DT_COMPTC")),
                        "plano_conta": row.get("PLANO_CONTA_BALCTE"),
                        "codigo_conta": row.get("CD_CONTA_BALCTE"),
                        "saldo": to_float(row.get("VL_SALDO_BALCTE"))
                    })
        applications = []
        for period in available_periods:
            app_key = f"cda_fi_BLC_1_{period}.csv"
            if app_key in data_dict:
                for row in data_dict[app_key]:
                    if fund["name"] is None:
                        fund["name"] = row.get("DENOM_SOCIAL")
                    if fund["tipo"] is None:
                        fund["tipo"] = row.get("TP_FUNDO_CLASSE")
                    applications.append({
                        "data": to_date(row.get("DT_COMPTC")),
                        "tipo_aplic": row.get("TP_APLIC"),
                        "tipo_ativo": row.get("TP_ATIVO"),
                        "emissor_ligado": None if row.get("EMISSOR_LIGADO") in ("NaN", None) else row.get("EMISSOR_LIGADO") == "S",
                        "tipo_negoc": row.get("TP_NEGOC"),
                        "quantidade": to_float(row.get("QT_POS_FINAL")),
                        "valor_mercado": to_float(row.get("VL_MERC_POS_FINAL")),
                        "custo": to_float(row.get("VL_CUSTO_POS_FINAL")),
                        "isin": row.get("CD_ISIN"),
                        "selic": row.get("CD_SELIC"),
                        "emissao": to_date(row.get("DT_EMISSAO")),
                        "vencimento": to_date(row.get("DT_VENC"))
                    })
        patrimonio = []
        for period in available_periods:
            patrimonio_key = f"cda_fi_PL_{period}.csv"
            if patrimonio_key in data_dict:
                for row in data_dict[patrimonio_key]:
                    patrimonio.append({
                        "data": to_date(row.get("DT_COMPTC")),
                        "vl_patrim_liq": to_float(row.get("VL_PATRIM_LIQ"))
                    })
        daily_info = []
        for period in available_periods:
            daily_key = f"inf_diario_fi_{period}.csv"
            if daily_key in data_dict:
                for row in data_dict[daily_key]:
                    daily_info.append({
                        "data": to_date(row.get("DT_COMPTC")),
                        "vl_total": to_float(row.get("VL_TOTAL")),
                        "vl_quota": to_float(row.get("VL_QUOTA")),
                        "vl_patrim_liq": to_float(row.get("VL_PATRIM_LIQ")),
                        "captc_dia": to_float(row.get("CAPTC_DIA")),
                        "resg_dia": to_float(row.get("RESG_DIA")),
                        "nr_cotst": to_float(row.get("NR_COTST")),
                    })
        if fund["name"] is not None and fund["tipo"] is not None:
            funds_dict[cnpj] = {
                "fund": fund,
                "balances": balances,
                "applications": applications,
                "patrimonio": patrimonio,
                "daily_info": daily_info
            }
    return funds_dict

# ---------------- MAIN ----------------
if __name__ == "__main__":
    # Caminho do JSON original
    input_file = Path("informacoes_cnpj.json")
    output_file = Path("normalized.json")

    print(f"Lendo dados de {input_file}...")
    # Lê o JSON original
    with open(input_file, "r", encoding="utf-8") as f:
        original_data = json.load(f)

    print(f"Encontrados {len(original_data)} CNPJs para processar...")
    
    # Normaliza todos os CNPJs
    normalized_dict = normalize_json(original_data)

    print(f"Processados {len(normalized_dict)} fundos com sucesso (fundos com name e tipo válidos).")
    print(f"Filtrados: {len(original_data) - len(normalized_dict)} fundos com dados incompletos.")
    # Salva o novo JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(normalized_dict, f, indent=2, ensure_ascii=False)
    print(f"Nova lista de fundos salva em {output_file}")
    print(f"Total de fundos válidos processados: {len(normalized_dict)}")
