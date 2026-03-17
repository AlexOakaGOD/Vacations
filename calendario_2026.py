import streamlit as st
from datetime import date, timedelta
import json
import urllib.parse

st.set_page_config(page_title="Calendário de Férias 2026", layout="wide")

# --- 1. CAPTURA DOS DADOS ---
if 'ferias' not in st.session_state:
    st.session_state.ferias = []

# Captura os dados que vêm do "Link de Salto"
if "dados" in st.query_params:
    try:
        dados_brutos = st.query_params["dados"]
        st.session_state.ferias = json.loads(urllib.parse.unquote(dados_brutos))
        st.query_params.clear()
        st.rerun()
    except:
        pass

# --- 2. LÓGICA DE PERÍODOS (Lado Esquerdo) ---
def calcular_periodos(lista):
    if not lista: return []
    datas = sorted([date.fromisoformat(d) for d in lista])
    res = []
    if not datas: return []
    ini = datas[0]
    fim = ini
    for i in range(1, len(datas)):
        if datas[i] == fim + timedelta(days=1):
            fim = datas[i]
        else:
            res.append((ini, fim))
            ini = datas[i]
            fim = ini
    res.append((ini, fim))
    return res

# --- 3. BARRA LATERAL ---
with st.sidebar:
    st.title("📊 Gestão")
    saldo = st.number_input("Dias de Direito:", value=22)
    marcados = len(st.session_state.ferias)
    st.metric("Selecionados", marcados, delta=f"{saldo-marcados} restantes")
    
    st.write("---")
    st.subheader("📅 Períodos:")
    for i_ini, i_fim in calcular_periodos(st.session_state.ferias):
        texto = f"{i_ini.day}/{i_ini.month} a {i_fim.day}/{i_fim.month}"
        c1, c2 = st.columns([4, 1])
        c1.write(f"✅ {texto}")
        if c2.button("❌", key=f"del_{i_ini}"):
            st.session_state.ferias = [d for d in st.session_state.ferias if not (i_ini <= date.fromisoformat(d) <= i_fim)]
            st.rerun()

# --- 4. O CALENDÁRIO VISUAL (CORES FIXAS) ---
FERIADOS = ["2026-01-01", "2026-04-03", "2026-04-05", "2026-04-25", "2026-05-01", "2026-06-04", "2026-06-10", "2026-08-15", "2026-10-05", "2026-11-01", "2026-12-01", "2026-12-08", "2026-12-25"]

html_design = f"""
<div style="background: #0e1117; padding: 15px; border-radius: 10px; font-family: sans-serif;">
    <style>
        .tabela {{ border-collapse: collapse; width: 100%; color: white; table-layout: fixed; }}
        .tabela th, .tabela td {{ border: 1px solid #333; height: 35px; text-align: center; font-size: 13px; }}
        .mes-nome {{ background: #1e1e1e; text-align: left !important; padding-left: 10px; font-weight: bold; color: #00d4ff; width: 100px; }}
        .dia-comum {{ cursor: pointer; background: #161b22; color: #ffffff !important; }}
        .fds {{ background: #2d2417; color: #ffab40 !important; font-weight: bold; }}
        .feriado {{ background: #3d1b1b; color: #ff6b6b !important; font-weight: bold; }}
        .selecionado {{ background: #1f6feb !important; color: white !important; box-shadow: inset 0 0 5px white; }}
        
        #botao-link {{
            display: inline-block; margin-top: 20px; padding: 12px 25px;
            background: #238636; color: white; text-decoration: none;
            border-radius: 6px; font-weight: bold; cursor: pointer;
        }}
    </style>

    <table class="tabela" id="calendario"></table>
    <a id="botao-link">💾 Gravar Seleção e Ver Períodos</a>
</div>

<script>
    const marcados = new Set({json.dumps(st.session_state.ferias)});
    const feriados = new Set({json.dumps(FERIADOS)});
    const meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"];
    const semanas = ["S","D","T","Q","Q","S","S","S","D","T","Q","Q","S","S","S","D","T","Q","Q","S","S","S","D","T","Q","Q","S","S","S","D","T","Q","Q","S","S","S","D"];

    const table = document.getElementById('calendario');
    let header = "<tr><th>2026</th>" + semanas.slice(0,37).map(s => `<th>${{s}}</th>`).join('') + "</tr>";
    table.innerHTML = header;

    meses.forEach((nome, mIdx) => {{
        let row = table.insertRow();
        row.insertCell().className = 'mes-nome';
        row.cells[0].innerText = nome;
        
        let d = new Date(2026, mIdx, 1);
        let offset = (d.getDay() === 0) ? 6 : d.getDay() - 1;
        for(let i=0; i<offset; i++) row.insertCell();

        while(d.getMonth() === mIdx) {{
            let cell = row.insertCell();
            let dStr = d.toISOString().split('T')[0];
            let isFds = d.getDay() === 0 || d.getDay() === 6;
            let isFer = feriados.has(dStr);
            
            cell.innerText = isFer ? "F" : d.getDate();
            if(isFer) cell.className = 'feriado';
            else if(isFds) cell.className = 'fds';
            else {{
                cell.className = 'dia-comum' + (marcados.has(dStr) ? ' selecionado' : '');
                cell.onclick = () => {{
                    if(marcados.has(dStr)) {{ marcados.delete(dStr); cell.classList.remove('selecionado'); }}
                    else {{ marcados.add(dStr); cell.classList.add('selecionado'); }}
                    atualizarLink();
                }};
            }}
            d.setDate(d.getDate() + 1);
        }}
        while(row.cells.length < 38) row.insertCell();
    }});

    function atualizarLink() {{
        const lista = Array.from(marcados);
        const link = document.getElementById('botao-link');
        // Criamos o link que aponta para a página principal com os dados
        const base = window.parent.location.origin + window.parent.location.pathname;
        link.href = base + "?dados=" + encodeURIComponent(JSON.stringify(lista));
        link.target = "_top"; // Garante que abre na janela principal
    }}
    atualizarLink(); // Inicia o link vazio
</script>
"""

import streamlit.components.v1 as components
components.html(html_design, height=600)
