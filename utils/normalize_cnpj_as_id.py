import json
from pathlib import Path

input_file = Path("normalized.json")
output_file = Path("normalized_by_cnpj.json")

def main():
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Se já está no formato dict, não faz nada
    if isinstance(data, dict):
        print("O arquivo já está no formato desejado.")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return

    # Converte lista para dict usando o CNPJ como chave
    result = {}
    for item in data:
        cnpj = item.get("fund", {}).get("cnpj")
        if cnpj:
            result[cnpj] = item

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Arquivo salvo em {output_file} com CNPJ como chave principal.")

if __name__ == "__main__":
    main()
