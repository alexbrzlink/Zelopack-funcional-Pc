import pandas as pd
import json
import datetime
from pathlib import Path

# Classe customizada para serialização JSON de objetos especiais
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        # Tratar objetos do tipo datetime
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        # Tratar objetos do tipo time
        elif isinstance(obj, datetime.time):
            return obj.isoformat()
        # Outros tipos especiais que podem aparecer em DataFrames
        elif hasattr(obj, 'item'):  # Para tipos numpy como np.int64
            return obj.item()
        else:
            # Para todos os outros tipos, converter para string
            try:
                return str(obj)
            except:
                return "Não serializável"

def extract_excel_data(excel_path):
    """
    Extrair dados de um arquivo Excel e retornar um dicionário com informações
    sobre todas as planilhas e seus conteúdos.
    """
    print(f"Tentando abrir o arquivo: {excel_path}")
    
    # Verificar se o arquivo existe
    if not Path(excel_path).exists():
        print(f"Erro: O arquivo {excel_path} não existe.")
        return None
    
    try:
        # Ler o arquivo Excel sem carregar o conteúdo ainda
        xl = pd.ExcelFile(excel_path)
        sheet_names = xl.sheet_names
        
        print(f"Planilhas encontradas: {sheet_names}")
        
        result = {
            "arquivo": excel_path,
            "planilhas": {}
        }
        
        # Processar cada planilha
        for sheet_name in sheet_names:
            print(f"\nProcessando planilha: {sheet_name}")
            
            # Ler a planilha
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            
            # Informações sobre a planilha
            num_rows, num_cols = df.shape
            
            # Extrair cabeçalhos ou primeiras linhas
            headers = df.columns.tolist() if not df.empty else []
            
            # Verificar se há fórmulas (isso é mais complexo, estamos simplificando)
            has_formulas = "Não verificado"
            
            # Identificar possíveis cálculos na planilha
            # Procurar por títulos ou cabeçalhos com palavras-chave relacionadas a cálculos
            potential_calculations = []
            
            calculation_keywords = [
                "calcul", "fórmula", "ratio", "brix", "acidez", "pH", 
                "peso", "volume", "rendimento", "concentração", "diluição",
                "temperatura", "correção", "densidade", "média", "desvio",
                "total", "soma", "multiplicação", "divisão", "peróxido"
            ]
            
            # Verificar nas colunas
            for header in headers:
                header_str = str(header).lower()
                for keyword in calculation_keywords:
                    if keyword.lower() in header_str:
                        potential_calculations.append(f"Possível cálculo (coluna): {header}")
                        break
            
            # Verificar nas primeiras linhas para identificar títulos
            if not df.empty:
                for i in range(min(5, num_rows)):
                    row_values = df.iloc[i].astype(str).tolist()
                    for cell in row_values:
                        cell_str = str(cell).lower()
                        for keyword in calculation_keywords:
                            if keyword.lower() in cell_str:
                                potential_calculations.append(f"Possível cálculo (linha {i+1}): {cell}")
                                break
            
            # Converter DataFrame para dict, tratando dados que não são facilmente serializáveis
            sample_data = []
            if not df.empty:
                try:
                    # Converter cada linha para um dict, lidando com tipos especiais
                    for i in range(min(10, len(df))):
                        row_dict = {}
                        for col in df.columns:
                            value = df.iloc[i][col]
                            # Converter tipos especiais para string
                            if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
                                row_dict[str(col)] = value.isoformat()
                            elif pd.isna(value):  # Tratar NaN/None
                                row_dict[str(col)] = None
                            else:
                                row_dict[str(col)] = value
                        sample_data.append(row_dict)
                except Exception as e:
                    print(f"Erro ao converter dados para JSON: {str(e)}")
                    sample_data = [{"erro": "Não foi possível converter os dados para JSON"}]
            
            # Dados da planilha
            sheet_data = {
                "nome": sheet_name,
                "linhas": num_rows,
                "colunas": num_cols,
                "cabeçalhos": [str(h) for h in headers],  # Converter cabeçalhos para string
                "tem_formulas": has_formulas,
                "possiveis_calculos": potential_calculations,
                "amostra_dados": sample_data
            }
            
            # Adicionar ao resultado
            result["planilhas"][sheet_name] = sheet_data
        
        return result
    
    except Exception as e:
        print(f"Erro ao processar o arquivo Excel: {str(e)}")
        return None

def save_to_json(data, output_path):
    """Salvar os dados extraídos em um arquivo JSON."""
    try:
        with open(output_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, cls=CustomJSONEncoder, ensure_ascii=False, indent=2)
        print(f"Dados salvos em {output_path}")
        return True
    except Exception as e:
        print(f"Erro ao salvar JSON: {str(e)}")
        return False

if __name__ == "__main__":
    excel_path = "./attached_assets/CALCULOS_LAB_RAFA.xlsx"
    output_path = "./extracted_excel_data.json"
    
    print("Iniciando extração de dados do Excel...")
    excel_data = extract_excel_data(excel_path)
    
    if excel_data:
        print("\nSalvando os dados extraídos em JSON...")
        save_to_json(excel_data, output_path)
        print("\nProcesso concluído.")
    else:
        print("\nFalha na extração de dados.")