# Calcula os números faltantes (como inteiros)
def calcular_faltantes(start, end):
    return [n for n in range(start + 1, end)]

# Aplica no DataFrame
df["Numeros_Faltantes"] = df.apply(lambda row: calcular_faltantes(row["Inicio"], row["Fim"]), axis=1)

# TOTAL faltantes real (todos os números explodidos)
all_missing = sum(df["Numeros_Faltantes"].tolist(), [])
total_missing = len(all_missing)

# EXPORTAÇÃO CERTA
export_df = df.copy()

# Explode corretamente os números faltantes mantendo contexto de intervalo
export_df = export_df.explode("Numeros_Faltantes").reset_index(drop=True)
export_df["Numeros_Faltantes"] = export_df["Numeros_Faltantes"].astype(int)

# Cria o Excel com todas as linhas esperadas
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
    export_df.to_excel(writer, index=False, sheet_name="Relatorio")
buffer.seek(0)

# Botão para baixar o arquivo Excel
st.download_button(
    label="📥 Exportar Excel",
    data=buffer,
    file_name="relatorio_faltantes.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
