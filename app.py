import streamlit as st
import pandas as pd

# Cargar archivo Excel
archivo_excel = "Ventas.xlsm"
df = pd.read_excel(archivo_excel, sheet_name=0, engine="openpyxl")

# Mostrar preview
st.title("📊 Dashboard de Ventas")
st.dataframe(df)
