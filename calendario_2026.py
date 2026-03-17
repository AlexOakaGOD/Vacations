import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import json

st.set_page_config(page_title="Calendário Partilhado 2026", layout="wide")

# --- LIGAÇÃO À BASE DE DADOS (Google Sheets) ---
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_ferias():
    try:
        df = conn.read(ttl=0) # ttl=0 garante que lê sempre a versão mais recente
        return df['data'].tolist()
    except:
        return []

# Inicializar o estado com os dados da nuvem
if 'ferias' not in st.session_state:
    st.session_state.ferias = carregar_ferias()

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("📊 Painel Online")
    saldo = st.number_input("Saldo:", value=22)
    st.metric("Dias Gastos", len(st.session_state.ferias))
    
    if st.button("🔄 Atualizar Dados"):
        st.session_state.ferias = carregar_ferias()
        st.rerun()

# --- O CALENDÁRIO (CÓDIGO VISUAL) ---
# [Aqui mantém-se o código HTML/JS que já tinhamos, mas com uma pequena alteração no envio]
# Vou focar na parte que recebe o valor do JS para gravar:

FERIADOS = ["2026-01-01", "2026-04-25", "2026-05-01"] # Adiciona os restantes

html_input = f"""
<script>
    // ... lógica do calendário ...
    document.getElementById('btn-confirmar').onclick = () => {{
        const lista = Array.from(selecionados);
        window.parent.postMessage({{
            type: 'streamlit:setComponentValue',
            value: lista
        }}, '*');
    }};
</script>
"""

import streamlit.components.v1 as components
valor_do_calendario = components.html(html_input, height=600)

# --- GRAVAÇÃO REAL ---
if valor_do_calendario is not None:
    st.session_state.ferias = valor_do_calendario

st.write("---")
if st.button("💾 GRAVAR ALTERAÇÕES PARA TODOS"):
    # Criar um DataFrame com as novas datas
    novo_df = pd.DataFrame({"data": st.session_state.ferias})
    # Escrever no Google Sheets
    conn.update(data=novo_df)
    st.success("Gravado no Google Sheets! Agora todos podem ver.")
