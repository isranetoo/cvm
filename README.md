# CVM Data Downloader

Este projeto é uma coleção de scripts Python para automatizar o download de dados da Comissão de Valores Mobiliários (CVM) do Brasil. O sistema está organizado em módulos especializados para diferentes tipos de dados de fundos de investimento.

## 📋 Visão Geral

O projeto permite o download automatizado dos seguintes tipos de dados da CVM:

- **Balancetes**: Dados mensais de balancetes de fundos de investimento
- **Composição**: Dados de Composição Detalhada de Ativos (CDA) dos fundos
- **Informações Diárias**: Dados diários de cotas e patrimônio dos fundos
- **Lâminas Essenciais**: Documentos essenciais dos fundos (lâminas)

## 🏗️ Estrutura do Projeto

```
cvm/
├── Balancete/
│   ├── cvm_balancete.py     # Download de balancetes mensais
│   └── funcs/               # Funções auxiliares (futuro)
├── Composição/
│   ├── cvm_composicao.py    # Download de dados CDA
│   └── funcs/               # Funções auxiliares (futuro)
├── Diario/
│   ├── cvm_diario.py        # Download de informações diárias
│   └── funcs/               # Funções auxiliares (futuro)
├── Essenciais/
│   ├── cvm_essenciais.py    # Download de lâminas essenciais
│   └── funcs/               # Funções auxiliares (futuro)
├── utils/
│   ├── __init__.py
│   └── cvm_utils.py         # Funções utilitárias compartilhadas
├── LICENSE                  # Licença MIT
└── README.md               # Este arquivo
```

## 📦 Dependências

- **requests**: Para realizar downloads HTTP
- **pandas**: Para manipulação de dados (usado no módulo diário)
- **typing**: Para type hints (Python 3.5+)

Instale as dependências com:
```bash
pip install requests pandas
```

## 🚀 Como Usar

### 1. Balancetes (cvm_balancete.py)

Baixa dados mensais de balancetes de fundos de investimento.

```python
# Configurar anos e meses desejados
anos = [2025]
meses = [6, 7, 8]

# O script baixará automaticamente os arquivos:
# balancete_fi_202506.zip
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