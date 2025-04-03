import streamlit as st
import pandas as pd
import re
import io

st.set_page_config(page_title="Análise de Notas Fiscais Faltantes", layout="wide")

st.title("📄 Analisador de Documentos Fiscais Faltantes")

uploaded_file = st.file_uploader("📂 Faça upload do arquivo TXT", type=["txt"])

def calcular_faltantes(start, end):
    return [str(n) for n in range(start + 1, end)]

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
        df["Numeros_Faltantes"] = df.apply(lambda row: calcular_faltantes(row["Inicio"], row["Fim"]), axis=1)

        # 📌 Lista total de notas faltantes
        all_missing = sum(df["Numeros_Faltantes"].tolist(), [])
        total_missing = len(all_missing)

        st.markdown("### 🧾 Números Faltantes")
        st.markdown(f"<b>Total de notas faltantes:</b> <span style='color:red;font-size:18px'>{total_missing}</span>", unsafe_allow_html=True)

        # 💡 Mostrar todos os números em linha
        st.code("   ".join(all_missing), language='txt')

        # Botão copiar
        st.download_button(
            label="📋 Copiar Números",
            data="\n".join(all_missing),
            file_name="numeros_faltantes.txt",
            mime="text/plain"
        )

        # Botão Excel
        export_df = df.explode("Numeros_Faltantes").reset_index(drop=True)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            export_df.to_excel(writer, index=False, sheet_name="Relatorio")
        buffer.seek(0)
        st.download_button(
            label="📥 Exportar Excel",
            data=buffer,
            file_name="relatorio_faltantes.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.markdown("---")
        st.markdown("### 🧩 Detalhes da Análise")

        # 🎨 Layout por faixa
        for i, row in df.iterrows():
            st.markdown(f"""
                <div style='border:1px solid #ccc; padding: 15px; border-radius: 10px; margin-bottom:10px'>
                    <b>Modelo:</b> 55 &nbsp;&nbsp; <b>Série:</b> 001 &nbsp;&nbsp;
                    <b>Situação:</b> <span style='color:green'>Análise de Intervalo</span><br><br>
                    <b>Início:</b> <span style='color:#444'>{row["Inicio"]}</span> &nbsp;&nbsp;
                    <b>Fim:</b> <span style='color:#444'>{row["Fim"]}</span> &nbsp;&nbsp;
                    <b>Números Faltantes:</b> <span style='color:red'>{row["Qtd_Faltantes"]}</span><br><br>
                    <b>Números:</b><br>
                    <span style='color:red'>{", ".join(row["Numeros_Faltantes"])}</span>
                </div>
            """, unsafe_allow_html=True)
