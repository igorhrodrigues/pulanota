import streamlit as st
import pandas as pd
import re
import io

# Configuração da página
st.set_page_config(page_title="Análise de Notas Fiscais Faltantes", layout="wide")

# 🌈 CSS customizado para design bonito
st.markdown("""
    <style>
        .big-title {
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 0px;
        }
        .sub-title {
            font-size: 18px;
            color: #6c757d;
        }
        .card {
            background-color: #fff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }
        .faltantes {
            color: red;
            font-weight: bold;
        }
        .copy-box {
            font-family: monospace;
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            overflow-x: auto;
        }
    </style>
""", unsafe_allow_html=True)

# Título principal
st.markdown("<div class='big-title'>📄 Analisador de Documentos Fiscais Faltantes</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Faça upload de um arquivo .txt para identificar notas fiscais ausentes.</div><br>", unsafe_allow_html=True)

# Upload do arquivo
uploaded_file = st.file_uploader("📂 Upload do arquivo TXT", type=["txt"])

# Função para calcular os números faltantes
def calcular_faltantes(start, end):
    return [n for n in range(start + 1, end)]

# Processamento do arquivo
if uploaded_file:
    content = uploaded_file.read().decode("utf-8")

    # Expressão regular
    pattern = re.compile(
        r"Do documento fiscal\s+\.*:\s+(\d+)\s+"
        r"Até o documento fiscal\s+\.*:\s+(\d+)\s+"
        r"Número de documentos faltantes na contagem\s+\.*:\s+(\d+)"
    )

    matches = pattern.findall(content)

    if not matches:
        st.error("❌ Nenhum dado encontrado no formato esperado.")
    else:
        # Criação do dataframe
        df = pd.DataFrame(matches, columns=["Inicio", "Fim", "Qtd_Faltantes"])
        df["Inicio"] = df["Inicio"].astype(int)
        df["Fim"] = df["Fim"].astype(int)
        df["Qtd_Faltantes"] = df["Qtd_Faltantes"].astype(int)

        # Geração das listas de faltantes
        df["Numeros_Faltantes"] = df.apply(lambda row: calcular_faltantes(row["Inicio"], row["Fim"]), axis=1)

        # Todos os números faltantes
        all_missing = sum(df["Numeros_Faltantes"].tolist(), [])
        total_missing = len(all_missing)

        # Bloco principal do resultado
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown(f"<h4>🔢 Total de notas faltantes: <span class='faltantes'>{total_missing}</span></h4>", unsafe_allow_html=True)
        st.markdown(f"<div class='copy-box'>{'   '.join([str(n) for n in all_missing])}</div>", unsafe_allow_html=True)

        # ⬅️ Botões alinhados à esquerda
        st.markdown("<div style='text-align: left;'>", unsafe_allow_html=True)

        st.download_button(
            "📋 Copiar Números",
            data="\n".join([str(n) for n in all_missing]),
            file_name="numeros_faltantes.txt",
            mime="text/plain",
            use_container_width=False
        )

        # Explode para Excel
        export_df = df.copy()
        export_df["Numeros_Faltantes"] = export_df["Numeros_Faltantes"].apply(lambda x: list(map(int, x)))
        export_df = export_df.explode("Numeros_Faltantes").reset_index(drop=True)
        export_df["Numeros_Faltantes"] = export_df["Numeros_Faltantes"].astype(int)

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            export_df.to_excel(writer, index=False, sheet_name="Relatorio")
        buffer.seek(0)

        st.download_button(
            "📥 Exportar Excel",
            data=buffer,
            file_name="relatorio_faltantes.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=False
        )

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Detalhes por faixa
        st.markdown("<h4 style='margin-top:40px;'>🧩 Detalhes da Análise</h4>", unsafe_allow_html=True)

        for _, row in df.iterrows():
            st.markdown(f"""
                <div class='card'>
                    <b>Modelo:</b> 55 &nbsp;&nbsp; <b>Série:</b> 001 &nbsp;&nbsp;
                    <b>Situação:</b> <span style='color:green'>Análise de Intervalo</span><br><br>
                    <b>Início:</b> <span>{row["Inicio"]}</span> &nbsp;&nbsp;
                    <b>Fim:</b> <span>{row["Fim"]}</span> &nbsp;&nbsp;
                    <b>Notas Faltantes:</b> <span class='faltantes'>{row["Qtd_Faltantes"]}</span><br><br>
                    <b>Números:</b><br>
                    <span class='faltantes'>{", ".join([str(n) for n in row["Numeros_Faltantes"]])}</span>
                </div>
            """, unsafe_allow_html=True)
