import streamlit as st
import pandas as pd
import re
import io

st.set_page_config(page_title="Relatório de Documentos Fiscais Faltantes", layout="wide")

st.title("📄 Analisador de Documentos Fiscais Faltantes")
st.write("Faça upload de um arquivo `.txt` no formato do relatório de CAJAMAR para analisar os documentos faltantes.")

uploaded_file = st.file_uploader("📂 Upload do arquivo TXT", type=["txt"])

if uploaded_file:
    content = uploaded_file.read().decode("utf-8")

    pattern = re.compile(
        r"Do documento fiscal\s+\.*:\s+(\d+)\s+"
        r"Até o documento fiscal\s+\.*:\s+(\d+)\s+"
        r"Número de documentos faltantes na contagem\s+\.*:\s+(\d+)"
    )

    matches = pattern.findall(content)

    if not matches:
        st.error("❌ Nenhum dado encontrado no formato esperado.")
    else:
        df = pd.DataFrame(matches, columns=["Inicio", "Fim", "Qtd_Faltantes"])
        df["Inicio"] = df["Inicio"].astype(int)
        df["Fim"] = df["Fim"].astype(int)
        df["Qtd_Faltantes"] = df["Qtd_Faltantes"].astype(int)

        def calcular_faltantes(start, end):
            return [n for n in range(start + 1, end)]

        df["Numeros_Faltantes"] = df.apply(lambda row: calcular_faltantes(row["Inicio"], row["Fim"]), axis=1)

        total_faltantes = df["Qtd_Faltantes"].sum()
        st.success(f"✅ Total de documentos fiscais faltantes: {total_faltantes}")

        st.subheader("📋 Relatório de Faixas com Faltas")
        st.dataframe(df, use_container_width=True)

        export = df.explode("Numeros_Faltantes").reset_index(drop=True)

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            export.to_excel(writer, index=False, sheet_name="Relatorio")
        buffer.seek(0)

        st.download_button(
            label="📥 Baixar relatório em Excel",
            data=buffer,
            file_name="relatorio_faltantes.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
