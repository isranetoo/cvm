from pydantic import BaseModel
from typing import List, Optional

class FundInfo(BaseModel):
    cnpj: str
    name: str
    tipo: str

class Balance(BaseModel):
    data: str
    plano_conta: str
    codigo_conta: str
    saldo: float

class Application(BaseModel):
    data: str
    tipo_aplic: Optional[str] = None
    tipo_ativo: Optional[str] = None
    emissor_ligado: Optional[bool] = None
    tipo_negoc: Optional[str] = None
    quantidade: Optional[float] = None
    valor_mercado: Optional[float] = None
    custo: Optional[float] = None
    isin: Optional[str] = None
    selic: Optional[str] = None
    emissao: Optional[str] = None
    vencimento: Optional[str] = None

class Patrimonio(BaseModel):
    data: str
    vl_patrim_liq: Optional[float] = None

class DailyInfo(BaseModel):
    data: str
    vl_total: Optional[float] = None
    vl_quota: Optional[float] = None
    vl_patrim_liq: Optional[float] = None
    captc_dia: Optional[float] = None
    resg_dia: Optional[float] = None
    nr_cotst: Optional[float] = None

class Fundo(BaseModel):
    fund: FundInfo
    balances: List[Balance] = []
    applications: List[Application] = []
    patrimonio: List[Patrimonio] = []
    daily_info: List[DailyInfo] = []
