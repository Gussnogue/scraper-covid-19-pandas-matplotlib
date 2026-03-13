import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import os
import re

# 1. Baixar os dados
url = "https://www.worldometers.info/coronavirus"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
response = requests.get(url, headers=headers)
html_content = response.text

# 2. Parsear HTML
soup = BeautifulSoup(html_content, 'html.parser')
table = soup.find('table', attrs={'id': 'main_table_countries_today'})

# 3. Extrair linhas
rows = table.find_all("tr")

# 4. Processar dados
data = []
for row in rows:
    # Extrai todas as células da linha (th e td)
    cells = row.find_all(['th', 'td'])
    # Pega o texto de cada célula, limpa espaços e quebras
    row_data = [cell.get_text(strip=True) for cell in cells]
    data.append(row_data)

# 5. Identificar cabeçalho (primeira linha)
header = data[0]
# Dados a partir da segunda linha
dados = data[1:]

# Criar DataFrame
df = pd.DataFrame(dados, columns=header)

# 6. Limpeza: remover vírgulas e converter colunas numéricas
# Lista de colunas que devem ser numéricas (baseado na estrutura esperada)
colunas_numericas = ['TotalCases', 'NewCases', 'TotalDeaths', 'NewDeaths', 
                     'TotalRecovered', 'NewRecovered', 'ActiveCases', 'Serious,Critical']

for col in colunas_numericas:
    if col in df.columns:
        # Substituir valores vazios por '0' e remover vírgulas
        df[col] = df[col].replace('', '0').str.replace(',', '', regex=False)
        # Converter para float (ou int)
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

# 7. Salvar CSV
os.makedirs('data', exist_ok=True)
df.to_csv('data/covid19.csv', index=False)
print("✅ Dados salvos em data/covid19.csv")
print("Primeiras linhas:")
print(df.head())

# 8. Visualizar (top 10 países por TotalCases)
df_plot = df[['Country,Other', 'TotalCases']].head(10)
df_plot = df_plot.sort_values('TotalCases', ascending=True)  # para gráfico horizontal melhor

plt.figure(figsize=(10, 6))
plt.barh(df_plot['Country,Other'], df_plot['TotalCases'], color='skyblue')
plt.xlabel('Total de Casos')
plt.title('Top 10 países com mais casos de COVID-19')
plt.tight_layout()
plt.show()

