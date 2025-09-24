from fastapi import FastAPI, HTTPException
import json
import os
from typing import Dict
from models import Fundo
import re

app = FastAPI(title="API de Fundos de Investimentos", version="1.0")

# ------------------------------
# FUNÇÃO PARA CARREGAR O "BANCO"
# ------------------------------
def load_data() -> Dict[str, Fundo]:
    db_path = os.path.join(os.path.dirname(__file__), "database.json")
    with open(db_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    fundos = {}
    for cnpj, data in raw_data.items():
        try:
            fundos[normalize_cnpj(cnpj)] = Fundo(**data)
        except Exception as e:
            print(f"Erro ao carregar fundo {cnpj}: {e}")
    return fundos

# ------------------------------
# FUNÇÃO PARA NORMALIZAR CNPJs
# ------------------------------
def normalize_cnpj(cnpj: str) -> str:
    """Remove pontos, barras e hífens do CNPJ"""
    return re.sub(r"\D", "", cnpj)

# ------------------------------
# ENDPOINTS
# ------------------------------
@app.get("/")
def root():
    return {"message": "Bem-vindo à API de Fundos de Investimentos"}

@app.get("/fundos")
def listar_fundos():
    """Lista todos os fundos (dados básicos)"""
    data = load_data()
    return [f.fund.dict() for f in data.values()]

@app.get("/fundos/{cnpj:path}")
def detalhes_fundo(cnpj: str):
    """Detalhes completos de um fundo pelo CNPJ (qualquer formato)"""
    data = load_data()
    fundo = data.get(normalize_cnpj(cnpj))
    if not fundo:
        raise HTTPException(status_code=404, detail="Fundo não encontrado")
    return fundo

@app.get("/fundos/{cnpj:path}/balances")
def get_balances(cnpj: str):
    """Lista de saldos (balances)"""
    data = load_data()
    fundo = data.get(normalize_cnpj(cnpj))
    if not fundo:
        raise HTTPException(status_code=404, detail="Fundo não encontrado")
    return fundo.balances

@app.get("/fundos/{cnpj:path}/applications")
def get_applications(cnpj: str):
    """Lista de aplicações"""
    data = load_data()
    fundo = data.get(normalize_cnpj(cnpj))
    if not fundo:
        raise HTTPException(status_code=404, detail="Fundo não encontrado")
    return fundo.applications

@app.get("/fundos/{cnpj:path}/patrimonio")
def get_patrimonio(cnpj: str):
    """Histórico de patrimônio líquido"""
    data = load_data()
    fundo = data.get(normalize_cnpj(cnpj))
    if not fundo:
        raise HTTPException(status_code=404, detail="Fundo não encontrado")
    return fundo.patrimonio

@app.get("/fundos/{cnpj:path}/daily-info")
def get_daily_info(cnpj: str):
    """Informações diárias do fundo"""
    data = load_data()
    fundo = data.get(normalize_cnpj(cnpj))
    if not fundo:
        raise HTTPException(status_code=404, detail="Fundo não encontrado")
    return fundo.daily_info
