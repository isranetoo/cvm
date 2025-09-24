#!/usr/bin/env python3
"""
Pipeline CVM Download: Sistema para baixar dados de fundos da CVM.

Este pipeline automatiza o processo de download de dados dos fundos
de investimento disponibilizados pela CVM, incluindo:
- Balancetes
- Informações diárias
- Composição de carteiras (CDA)
- Lâminas dos fundos

Autor: Pipeline CVM
Data: 2024
"""

import subprocess
import sys
import argparse
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

class CVMPipeline:
    """Classe principal do pipeline CVM para downloads."""
    
    def __init__(self):
        self.root = Path(__file__).parent
        self.scripts_download = {
            'essenciais': self.root / 'Essenciais' / 'cvm_essenciais.py',
            'diario': self.root / 'Diario' / 'cvm_diario.py', 
            'composicao': self.root / 'Composição' / 'cvm_composicao.py',
            'balancete': self.root / 'Balancete' / 'cvm_balancete.py',
        }
        
    def log(self, message: str, level: str = "INFO"):
        """Log com timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def validate_inputs(self, anos: List[int], meses: List[int]) -> bool:
        """Valida os anos e meses fornecidos."""
        current_year = datetime.now().year
        
        for ano in anos:
            if ano < 2010 or ano > current_year + 1:
                self.log(f"Ano {ano} fora do intervalo válido (2010-{current_year + 1})", "ERROR")
                return False
                
        for mes in meses:
            if mes < 1 or mes > 12:
                self.log(f"Mês {mes} inválido (deve estar entre 1 e 12)", "ERROR")
                return False
                
        return True
        
    def update_script_parameters(self, script_path: Path, anos: List[int], meses: List[int]):
        """Atualiza os parâmetros de anos e meses nos scripts."""
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            new_lines = []
            for line in lines:
                if line.strip().startswith('anos ='):
                    new_lines.append(f'anos = {anos}\n')
                elif line.strip().startswith('meses ='):
                    new_lines.append(f'meses = {meses}\n')
                else:
                    new_lines.append(line)
                    
            with open(script_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
                
            self.log(f"Parâmetros atualizados em {script_path.name}")
            
        except Exception as e:
            self.log(f"Erro ao atualizar {script_path.name}: {e}", "ERROR")
            raise
            
    def run_script(self, script_path: Path, description: str = None) -> bool:
        """Executa um script Python e retorna sucesso/falha."""
        script_name = script_path.name
        desc = description or f"script {script_name}"
        
        self.log(f"Executando {desc}...")
        
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)], 
                capture_output=True, 
                text=True,
                timeout=300  # 5 minutos de timeout
            )
            
            if result.stdout.strip():
                print(result.stdout)
                
            if result.returncode == 0:
                self.log(f"✓ {desc} executado com sucesso")
                return True
            else:
                self.log(f"✗ Erro ao executar {desc}", "ERROR")
                if result.stderr:
                    print("STDERR:", result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            self.log(f"✗ Timeout ao executar {desc}", "ERROR")
            return False
        except Exception as e:
            self.log(f"✗ Erro inesperado ao executar {desc}: {e}", "ERROR")
            return False
            
    def get_user_inputs(self) -> tuple[List[int], List[int]]:
        """Coleta anos e meses do usuário interativamente."""
        while True:
            try:
                entrada_anos = input('Digite o(s) ano(s) (ex: 2024 ou 2024,2025): ')
                anos = [int(a) for a in entrada_anos.replace(',', ' ').split() if a.strip()]
                break
            except ValueError:
                print("Por favor, digite anos válidos (números inteiros).")
                
        while True:
            try:
                entrada_meses = input('Digite o(s) mês(es) (ex: 1 ou 1,2,3): ')
                meses = [int(m) for m in entrada_meses.replace(',', ' ').split() if m.strip()]
                break
            except ValueError:
                print("Por favor, digite meses válidos (números de 1 a 12).")
                
        return anos, meses
        
    def show_summary(self, anos: List[int], meses: List[int]):
        """Mostra resumo dos parâmetros antes da execução."""
        print("\n" + "="*60)
        print("RESUMO DA EXECUÇÃO")
        print("="*60)
        print("Anos selecionados: {', '.join(map(str, anos))}")
        print(f"Meses selecionados: {', '.join(map(str, meses))}")
        print(f"Total de períodos: {len(anos) * len(meses)}")
        print("\nTipos de dados que serão baixados:")
        for nome, script in self.scripts_download.items():
            print(f"  • {nome.capitalize()}: {script.name}")
        print("="*60)
        
        resposta = input("\nDeseja continuar com o download? (s/N): ").lower()
        if resposta not in ['s', 'sim', 'y', 'yes']:
            print("Download cancelado pelo usuário.")
            sys.exit(0)
            
    def run_pipeline(self, anos: List[int], meses: List[int], skip_download: bool = False):
        """Executa apenas os downloads dos dados."""
        start_time = datetime.now()
        self.log("Iniciando pipeline de download CVM")
        
        # Validação
        if not self.validate_inputs(anos, meses):
            return False
            
        # Resumo
        self.show_summary(anos, meses)
        
        success_count = 0
        total_steps = len(self.scripts_download)
        
        if not skip_download:
            # Fase única: Atualizar parâmetros e executar downloads
            self.log("=== EXECUTANDO DOWNLOADS DOS DADOS ===")
            
            for nome, script_path in self.scripts_download.items():
                if not script_path.exists():
                    self.log(f"Script não encontrado: {script_path}", "WARNING")
                    continue
                    
                self.update_script_parameters(script_path, anos, meses)
                
                if self.run_script(script_path, f"download de dados {nome}"):
                    success_count += 1
                else:
                    self.log(f"Falha no download de {nome}", "WARNING")
        else:
            self.log("=== DOWNLOAD PULADO (--skip-download) ===")
            success_count = len(self.scripts_download)
            
        # Relatório final
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n" + "="*60)
        print("RELATÓRIO FINAL - DOWNLOADS")
        print("="*60)
        print(f"Downloads executados com sucesso: {success_count}/{total_steps}")
        print(f"Tempo total de execução: {duration}")
        
        # Verificar arquivos baixados na pasta temp
        temp_path = self.root / "utils" / "temp"
        if temp_path.exists():
            temp_files = list(temp_path.glob("*.zip"))
            print(f"✓ Arquivos ZIP na pasta temp: {len(temp_files)}")
            
        data_path = self.root / "utils" / "data"  
        if data_path.exists():
            csv_files = list(data_path.glob("*.csv"))
            print(f"✓ Arquivos CSV na pasta data: {len(csv_files)}")
        
        print("="*60)
        
        if success_count == total_steps:
            self.log("✓ Downloads executados com sucesso!")
            return True
        else:
            self.log(f"✗ Downloads finalizados com {total_steps - success_count} falhas", "WARNING")
            return False

def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Pipeline CVM Download: Baixa dados de fundos da CVM.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python pipeline_cvm.py --ano 2024 --mes 1 2 3
  python pipeline_cvm.py --ano 2023 2024 --mes 12 1
  python pipeline_cvm.py --skip-download (pula downloads)
  python pipeline_cvm.py  (modo interativo)
        """
    )
    
    parser.add_argument('--ano', type=int, nargs='+', 
                       help='Ano(s) desejado(s), ex: --ano 2024 2025')
    parser.add_argument('--mes', type=int, nargs='+', 
                       help='Mês(es) desejado(s), ex: --mes 1 3 4')
    parser.add_argument('--skip-download', action='store_true',
                       help='Pula a fase de download (retorna sucesso sem fazer nada)')
    
    args = parser.parse_args()
    
    pipeline = CVMPipeline()
    
    # Determinar anos e meses
    if args.ano:
        anos = args.ano
    else:
        anos, _ = pipeline.get_user_inputs()[:1], None
        anos = anos[0] if anos else []
        
    if args.mes:
        meses = args.mes
    else:
        if not args.ano:  # Se não passou ano por argumento, já pegou interativamente
            _, meses = pipeline.get_user_inputs()
        else:  # Passou ano mas não mês
            _, meses = pipeline.get_user_inputs()
    
    # Executar pipeline
    success = pipeline.run_pipeline(anos, meses, args.skip_download)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
