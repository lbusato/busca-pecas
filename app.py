
import streamlit as st
import pandas as pd
import re

def extrair_intervalo(serie_periodos):
    anos = []
    for per in serie_periodos:
        m = re.match(r"(\d{4})/(\d{4})", str(per))
        if m:
            anos.append((int(m.group(1)), int(m.group(2))))
    if not anos:
        return ""
    menor_inicio = min(i for i, f in anos)
    maior_fim = max(f for i, f in anos)
    return f"{menor_inicio}/{maior_fim}"

def busca_pecas(consulta, df):
    termos = consulta.lower().split()
    ano = next((int(t) for t in termos if t.isdigit() and len(t) == 4), None)

    filtro_produto = df[
        df['Linha de produto'].str.lower().str.contains("terminal", na=False) &
        df['Linha de produto'].str.lower().str.contains("direção", na=False)
    ]
    if "pivô" in consulta or "pivo" in consulta:
        filtro_produto = df[df['Linha de produto'].str.lower().str.contains("pivô|pivo", na=False)]
    if "axial" in consulta:
        filtro_produto = df[df['Linha de produto'].str.lower().str.contains("axial", na=False)]

    modelos = [m for m in df['Modelo'].dropna().unique() if any(m.lower() in consulta for termo in termos)]
    if not modelos:
        modelos = [m for m in df['Modelo'].dropna().unique() if any(termo in m.lower() for termo in termos)]
    if modelos:
        filtro_produto = filtro_produto[filtro_produto['Modelo'].isin(modelos)]
    else:
        pass

    if ano:
        def ano_no_intervalo(periodo):
            m = re.match(r"(\d{4})/(\d{4})", str(periodo))
            return m and int(m.group(1)) <= ano <= int(m.group(2))
        filtro_produto = filtro_produto[filtro_produto['periodoFabricacao'].apply(ano_no_intervalo)]

    if filtro_produto.empty:
        return None

    agrupado = filtro_produto.groupby([
        'Produto', 'Linha de produto', 'Montadora', 'Modelo', 'periodoFabricacao'
    ])['posicao'].apply(lambda x: ', '.join(sorted(x.dropna().unique()))).reset_index()

    return agrupado

st.set_page_config(page_title="Catálogo de Peças Inteligente", page_icon="🛠️")
st.title("🔎 Catálogo de Peças Viemar – Busca Inteligente")

st.markdown("""
Digite abaixo o nome da peça, modelo, ano, etc.  
*Exemplo:*  
- `terminal do palio 2015`
- `pivô hilux 2014`
- `axial etios`
""")

df = pd.read_csv("base_teste_a.csv", sep=";", engine="python")

consulta = st.text_input("🔍 O que você procura?", "")

if consulta:
    resultados = busca_pecas(consulta, df)
    if resultados is None or resultados.empty:
        st.warning("❌ Nenhuma peça encontrada para sua busca. Tente outro termo ou revise a digitação.")
    else:
        for _, row in resultados.iterrows():
            st.markdown(
                f"""
🟩 **Produto:** `{row['Produto']}`  
• {row['Linha de produto']}  
• Aplicação: {row['Montadora']} {row['Modelo']} ({row['periodoFabricacao']})  
• Posição: {row['posicao']}
---
"""
            )
