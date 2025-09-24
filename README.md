# CVM Data Downloader

Este projeto é uma coleção de scripts Python para automatizar o download e consulta de dados da Comissão de Valores Mobiliários (CVM) do Brasil, especialmente sobre fundos de investimento. O sistema está organizado em módulos especializados para diferentes tipos de dados e inclui uma API para consulta estruturada.

## 📋 Visão Geral

O projeto permite:
- Download automatizado dos principais conjuntos de dados da CVM (balancetes, composição de ativos, informações diárias, lâminas essenciais)
- Consulta estruturada via API local aos dados dos fundos
- Facilidade de personalização e integração

## 🏗️ Estrutura do Projeto

```
cvm/
├── Balancete/
│   ├── cvm_balancete.py     # Download de balancetes mensais
│   └── funcs/
├── Composição/
│   ├── cvm_composicao.py    # Download de dados CDA
│   └── funcs/
├── Diario/
│   ├── cvm_diario.py        # Download de informações diárias
│   └── funcs/
├── Essenciais/
│   ├── cvm_essenciais.py    # Download de lâminas essenciais
│   └── funcs/
├── utils/
│   ├── cvm_utils.py         # Funções utilitárias compartilhadas
│   └── ...
├── api/
│   ├── main.py              # API FastAPI para consulta aos dados
│   ├── models.py            # Modelos de dados (Pydantic)
│   └── database.json        # Banco de dados local dos fundos
├── LICENSE
└── README.md
```

## 📦 Dependências

- **requests**: Para downloads HTTP
- **pandas**: Manipulação de dados (usado no módulo diário)
- **fastapi**: API web
- **uvicorn**: Servidor ASGI para FastAPI
- **pydantic**: Modelos de dados

Instale as dependências com:
```bash
pip install requests pandas fastapi uvicorn pydantic
```

## 🚀 Como Usar os Scripts de Download

### 1. Balancetes (`Balancete/cvm_balancete.py`)
Baixa dados mensais de balancetes de fundos de investimento.

**Exemplo de uso:**
```python
anos = [2025]
meses = [6, 7, 8]
for ano in anos:
  for mes in meses:
    carregar_dados_balancete(ano, mes)
```
O script baixa arquivos como `balancete_fi_202506.zip`.

**Função principal:**
```python
def carregar_dados_balancete(ano, mes):
  url = f'https://dados.cvm.gov.br/dados/FI/DOC/BALANCETE/DADOS/balancete_fi_{ano}{str(mes).zfill(2)}.zip'
  ...
```

### 2. Composição de Ativos (`Composição/cvm_composicao.py`)
Baixa dados de Composição Detalhada de Ativos (CDA) dos fundos.

**Exemplo de uso:**
```python
anos = [2024, 2025]
meses = [1, 2, 3]
ano_mes_list = gerar_lista_ano_mes(anos, meses)
for ano_mes in ano_mes_list:
  carregar_dados_composicao(ano_mes)
```
O script baixa arquivos como `cda_fi_202401.zip`.

### 3. Informações Diárias (`Diario/cvm_diario.py`)
Baixa dados diários de cotas e patrimônio dos fundos.

**Exemplo de uso:**
```python
anos = [2024]
meses = [1, 2, 3]
for ano in anos:
  for mes in meses:
    carregar_dados_diarios(ano, mes)
```
O script baixa arquivos como `inf_diario_fi_202401.zip`.

### 4. Lâminas Essenciais (`Essenciais/cvm_essenciais.py`)
Baixa documentos essenciais dos fundos.

**Exemplo de uso:**
```python
anos = [2024]
meses = [1, 2, 3]
ano_mes_list = gerar_lista_ano_mes(anos, meses)
for ano_mes in ano_mes_list:
  baixar_lamina(ano_mes)
```
O script baixa arquivos como `lamina_fi_202401.zip`.

## 🛠️ Funções Utilitárias (`utils/cvm_utils.py`)

### baixar_arquivo()
```python
def baixar_arquivo(url: str, nome_arquivo: str, pasta_temp: Optional[str] = None, timeout: int = 60) -> str
```
- Baixa um arquivo de uma URL e salva localmente na pasta `temp/`.

### gerar_lista_ano_mes()
```python
def gerar_lista_ano_mes(anos, meses) -> list
```
- Gera lista de strings no formato AAAAMM para facilitar downloads em lote.

## 🌐 API de Consulta aos Dados (`api/main.py`)

O projeto inclui uma API REST desenvolvida com FastAPI para consulta aos dados dos fundos de investimento.

### Como executar a API
```bash
uvicorn api.main:app --reload
```
Acesse em: http://localhost:8000

### Endpoints principais

- `GET /` — Mensagem de boas-vindas
- `GET /fundos` — Lista todos os fundos cadastrados
- `GET /fundos/{cnpj}` — Detalhes completos de um fundo pelo CNPJ
- `GET /fundos/{cnpj}/balances` — Lista de saldos (balancetes) do fundo

**Exemplo de resposta de `/fundos/{cnpj}`:**
```json
{
  "fund": {
  "cnpj": "12345678000195",
  "name": "Fundo Exemplo",
  "tipo": "FII"
  },
  "balances": [...],
  "applications": [...],
  "patrimonio": [...],
  "daily_info": [...]
}
```

## 🗂️ Modelos de Dados (`api/models.py`)

Os dados dos fundos são estruturados em modelos Pydantic, incluindo:
- `FundInfo`: Informações básicas do fundo
- `Balance`: Saldos de balancetes
- `Application`: Composição de ativos
- `Patrimonio`: Patrimônio líquido
- `DailyInfo`: Informações diárias
- `Fundo`: Modelo principal agregando todos os dados

## 📁 Arquivos Baixados

Todos os arquivos são salvos na pasta `temp/` criada automaticamente ao lado de cada script. Os arquivos seguem o padrão de nomenclatura da CVM:

- **Balancetes**: `balancete_fi_AAAAMM.zip`
- **CDA**: `cda_fi_AAAAMM.zip`
- **Diário**: `inf_diario_fi_AAAAMM.zip`
- **Lâminas**: `lamina_fi_AAAAMM.zip`

## 🔧 Personalização

Para personalizar os downloads, edite as variáveis `anos` e `meses` em cada script:
```python
# Exemplo: baixar dados de 2023 e 2024, apenas primeiro trimestre
anos = [2023, 2024]
meses = [1, 2, 3]
```

## ⚠️ Tratamento de Erros

Todos os scripts incluem tratamento de erros que:
- Captura falhas de download
- Exibe mensagens informativas sobre o erro
- Continua o processamento dos demais arquivos

## 🔗 Fonte dos Dados

Todos os dados são obtidos do portal oficial da CVM:
- **Site**: https://dados.cvm.gov.br/
- **Seção**: Fundos de Investimento
- **Formato**: Arquivos ZIP contendo dados em CSV

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🤝 Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir melhorias
- Adicionar novos tipos de dados da CVM
- Melhorar a documentação

## 📞 Contato

**Autor**: Israel Antunes Neto  
**Licença**: MIT  
**Ano**: 2025
# balancete_fi_202507.zip  
# balancete_fi_202508.zip
```

**URL padrão**: `https://dados.cvm.gov.br/dados/FI/DOC/BALANCETE/DADOS/balancete_fi_{ANO}{MES}.zip`

### 2. Composição de Ativos (cvm_composicao.py)

Baixa dados de Composição Detalhada de Ativos (CDA) dos fundos.

```python
# Configurar anos e meses desejados
anos = [2024, 2025]
meses = [1, 2, 3, 4, 5]

# O script gerará automaticamente as combinações ano-mês
# e baixará os arquivos correspondentes
```

**URL padrão**: `https://dados.cvm.gov.br/dados/FI/DOC/CDA/DADOS/cda_fi_{ANOMÊS}.zip`

### 3. Informações Diárias (cvm_diario.py)

Baixa dados diários de cotas e patrimônio dos fundos de investimento.

```python
# Configurar anos e meses desejados
anos = [2024]
meses = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

# O script inclui configuração de formato de exibição para pandas
# e baixa os arquivos mensais de dados diários
```

**URL padrão**: `https://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS/inf_diario_fi_{ANO}{MES}.zip`

### 4. Lâminas Essenciais (cvm_essenciais.py)

Baixa documentos essenciais (lâminas) dos fundos de investimento.

```python
# Configurar anos e meses desejados
anos = [2024, 2025]
meses = [1, 2, 3, 4, 5]

# O script baixa as lâminas essenciais dos fundos
```

**URL padrão**: `https://dados.cvm.gov.br/dados/FI/DOC/LAMINA/DADOS/lamina_fi_{ANOMÊS}.zip`

## 🛠️ Funções Utilitárias (utils/cvm_utils.py)

### baixar_arquivo()
```python
def baixar_arquivo(url: str, nome_arquivo: str, pasta_temp: Optional[str] = None, timeout: int = 60) -> str
```
- **Propósito**: Baixa um arquivo de uma URL e salva localmente
- **Parâmetros**:
  - `url`: URL do arquivo para download
  - `nome_arquivo`: Nome do arquivo para salvar
  - `pasta_temp`: Pasta de destino (padrão: `temp/` ao lado do script)
  - `timeout`: Tempo limite em segundos (padrão: 60s)
- **Retorna**: Caminho completo do arquivo baixado

### gerar_lista_ano_mes()
```python
def gerar_lista_ano_mes(anos, meses) -> list
```
- **Propósito**: Gera lista de strings no formato AAAAMM
- **Parâmetros**:
  - `anos`: Lista de anos
  - `meses`: Lista de meses
- **Retorna**: Lista de strings no formato "AAAAMM"

## 📁 Arquivos Baixados

Todos os arquivos são salvos na pasta `temp/` criada automaticamente ao lado de cada script. Os arquivos seguem o padrão de nomenclatura da CVM:

- **Balancetes**: `balancete_fi_AAAAMM.zip`
- **CDA**: `cda_fi_AAAAMM.zip`
- **Diário**: `inf_diario_fi_AAAAMM.zip`
- **Lâminas**: `lamina_fi_AAAAMM.zip`

## 🔧 Personalização

Para personalizar os downloads, edite as variáveis `anos` e `meses` em cada script:

```python
# Exemplo: baixar dados de 2023 e 2024, apenas primeiro trimestre
anos = [2023, 2024]
meses = [1, 2, 3]
```

## ⚠️ Tratamento de Erros

Todos os scripts incluem tratamento de erros que:
- Captura falhas de download
- Exibe mensagens informativas sobre o erro
- Continua o processamento dos demais arquivos

## 🔗 Fonte dos Dados

Todos os dados são obtidos do portal oficial da CVM:
- **Site**: https://dados.cvm.gov.br/
- **Seção**: Fundos de Investimento
- **Formato**: Arquivos ZIP contendo dados em CSV

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🤝 Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir melhorias
- Adicionar novos tipos de dados da CVM
- Melhorar a documentação

## 📞 Contato

**Autor**: Israel Antunes Neto  
**Licença**: MIT  
**Ano**: 2025