# app.py
import streamlit as st
import pandas as pd
from PIL import Image
from pathlib import Path
import base64
from io import BytesIO
import os

# ---------- CONFIGURAÇÃO ----------
st.set_page_config(page_title="Catálogo - Pronta Entrega", layout="wide")

# ---------- BASE DIR ----------
BASE_DIR = Path(__file__).parent  # caminho relativo, funciona local e no Render

# ---------- LOGO ----------
logo_path = BASE_DIR / "logo.png"
if logo_path.exists():
    logo = Image.open(logo_path)
    buffered_logo = BytesIO()
    logo.save(buffered_logo, format="PNG")
    logo_base64 = base64.b64encode(buffered_logo.getvalue()).decode()
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; justify-content:flex-start; margin-bottom:10px;">
            <img src="data:image/png;base64,{logo_base64}" style="width:90px; height:auto; object-fit:contain;">
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.warning("⚠️ Logo não encontrada no diretório do projeto.")

# ---------- TÍTULO CENTRALIZADO ----------
st.markdown('<h1 style="text-align: center;">CATÁLOGO - PRONTA ENTREGA</h1>', unsafe_allow_html=True)

# ---------- CARREGAR PLANILHA ----------
excel_path = BASE_DIR / "ESTOQUE PRONTA ENTREGA CLAMI.xlsx"
if not excel_path.exists():
    st.error("❌ Arquivo de catálogo não encontrado. Verifique se 'ESTOQUE PRONTA ENTREGA CLAMI.xlsx' está no repositório.")
    st.stop()

df = pd.read_excel(excel_path, header=1)
df.columns = df.columns.str.strip()
df = df.drop_duplicates(subset="CODIGO DO PRODUTO", keep="first")

# ---------- FILTROS ----------
col1, col2 = st.columns([2, 3])

with col1:
    st.markdown("""
        <style>
        div.stMultiSelect > div:first-child {
            background-color: #ffffff !important;
            border: 1.5px solid #4B7BEC !important;
            border-radius: 10px !important;
            padding: 5px 8px !important;
        }
        div.stMultiSelect [data-baseweb="tag"] {
            background-color: #e0e0e0 !important;
            color: #333 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    marca_filter = st.multiselect("Marca", options=df["MARCA"].unique())

with col2:
    st.markdown("""
        <style>
        div.stTextInput > div > input { font-size: 16px; height: 35px; }
        div.stTextInput > label { font-size: 18px; }
        </style>
    """, unsafe_allow_html=True)
    search_term = st.text_input("Pesquisar Produto")

# ---------- FILTRAR DADOS ----------
df_filtered = df.copy()
if marca_filter:
    df_filtered = df_filtered[df_filtered["MARCA"].isin(marca_filter)]
if search_term:
    df_filtered = df_filtered[df_filtered["DESCRIÇÃO DO PRODUTO"].str.contains(search_term, case=False, na=False)]

st.write(f"Total de produtos exibidos: {len(df_filtered)}")

# ---------- IMAGENS ----------
IMAGES_DIR = BASE_DIR / "IMAGENS"
if not IMAGES_DIR.exists():
    st.warning("⚠️ Pasta 'IMAGENS' não encontrada no repositório. Verifique se foi enviada ao GitHub.")

# ---------- EXIBIÇÃO DOS PRODUTOS ----------
num_cols = 5
for i in range(0, len(df_filtered), num_cols):
    cols = st.columns(num_cols)
    for j, idx in enumerate(range(i, min(i + num_cols, len(df_filtered)))):
        row = df_filtered.iloc[idx]
        with cols[j]:
            # Imagem do produto
            img_name = row.get("LINK_IMAGEM", None)
            img_path = IMAGES_DIR / (img_name if img_name else "SEM IMAGEM.jpg")
            if not img_path.exists():
                img_path = IMAGES_DIR / "SEM IMAGEM.jpg"

            try:
                image = Image.open(img_path)
                buffered = BytesIO()
                image.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
            except Exception:
                img_str = ""

            # Preços formatados
            def format_valor(valor):
                try:
                    num = float(str(valor).replace(',', '.'))
                    return f"R$ {num:,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.')
                except:
                    return "R$ 0,00"

            de_valor = format_valor(row.get('DE', 0))
            por_valor = format_valor(row.get('POR', 0))

            # Dimensões
            dimensoes = []
            if row.get('COMPRIMENTO'): dimensoes.append(f"Comp.: {row.get('COMPRIMENTO')}")
            if row.get('ALTURA'): dimensoes.append(f"Alt.: {row.get('ALTURA')}")
            if row.get('LARGURA'): dimensoes.append(f"Larg.: {row.get('LARGURA')}")
            if row.get('DIAMETRO'): dimensoes.append(f"Ø Diam: {row.get('DIAMETRO')}")
            dimensoes_str = ', '.join(dimensoes)

            # Card
            st.markdown(
                f"""
                <div style="border:1px solid #e0e0e0; border-radius:15px; margin:5px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15); background-color:#ffffff;
                    display:flex; flex-direction:column; height:800px; overflow:hidden;">
                    <div style="text-align:center;">
                        <img src="data:image/png;base64,{img_str}" style="width:100%; height:auto; object-fit:cover; border-radius:15px 15px 0 0;">
                    </div>
                    <div style="padding:10px; text-align:left;">
                        <h4 style="margin-bottom:5px; font-size:18px;">{row['DESCRIÇÃO DO PRODUTO']}</h4>
                        <p style="margin:0;"><b>Código:</b> {row['CODIGO DO PRODUTO']}</p>
                        <p style="margin:0;"><b>Marca:</b> {row['MARCA']}</p>
                        <p style="margin:0;">{dimensoes_str}</p>
                        <p style="margin:0;"><b>De:</b> <span style="text-decoration: line-through; color:#999;">{de_valor}</span></p>
                        <p style="margin:0;"><b>Por:</b> <span style="color:#d32f2f; font-size:20px; font-weight:bold;">{por_valor}</span></p>
                        <p style="margin:0;"><b>Estoque:</b> {row.get('ESTOQUE DISPONIVEL', '')}</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
