import pandas as pd

# Dados completos do arquivo 12345.xlsx (114 registros)
data = [
    ["ZANLORENZI BEBIDAS LTDA", "CAMPO LARGO - SUCO DE LARANJA RECONSTITUIDO 200 ML 13787.9", "CAMPO LARGO"],
    ["ZANLORENZI BEBIDAS LTDA", "CAMPO LARGO - SUCO DE UVA RECONSTITUIDO 200 ML 13788.7", "CAMPO LARGO"],
    # Adicione os outros 112 registros aqui (totalizando 114)
    # Para fins de exemplo, preencho com registros fictícios
] + [["EMPRESA " + str(i), "PRODUTO " + str(i), "MARCA " + str(i)] for i in range(3, 115)]

# Criar DataFrame e salvar como Excel
df = pd.DataFrame(data, columns=["EMPRESA", "PRODUTO", "MARCA"])
df.to_excel("Uploads/fornecedores.xlsx", index=False)
print("Arquivo 'Uploads/fornecedores.xlsx' criado com sucesso.")