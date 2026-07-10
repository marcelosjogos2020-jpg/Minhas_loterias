import streamlit as st
import pandas as pd
import requests
import itertools
import math
import streamlit.components.v1 as components
from collections import Counter
from datetime import datetime

# ============================================================
# CONFIGURAÇÃO DA PÁGINA E ESTADO
# ============================================================

st.set_page_config(
    page_title="Lotofácil | Análises e Desdobramentos",
    page_icon="🍀",
    layout="wide"
)

if "jogos_gerados" not in st.session_state:
    st.session_state["jogos_gerados"] = []

# Variável de controle para ocultar/mostrar gabaritos
if "esconder_gabarito" not in st.session_state:
    st.session_state["esconder_gabarito"] = False

# ============================================================
# CSS CUSTOMIZADO
# ============================================================

st.markdown(
    """
<style>
    html, body, [class*="css"] {
        background-color: #0b111a;
        color: #ffffff;
    }
    .main {
        background-color: #0b111a;
    }
    h1, h2, h3 {
        color: #ffffff;
        font-weight: 900;
    }
    .subtitulo {
        font-size: 22px;
        color: #ffffff;
        font-weight: 800;
        margin-bottom: 24px;
    }
    .ultimo-sorteio {
        border: 2px solid #1e88ff;
        border-radius: 12px;
        padding: 20px;
        margin: 12px 0 26px 0;
        background: linear-gradient(90deg, #111827, #162033);
        box-shadow: 0 0 14px rgba(30,136,255,0.28);
    }
    .ultimo-label {
        font-size: 14px;
        color: #93c5fd;
        font-weight: 800;
        margin-bottom: 12px;
    }
    .ultimo-concurso {
        font-size: 22px;
        color: #ffffff;
        font-weight: 900;
        margin-bottom: 16px;
    }
    .ultimo-local {
        color: #ffffff;
        font-size: 14px;
        margin-bottom: 20px;
    }
    .dezenas-resultado-container {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        align-items: center;
        margin-top: 8px;
    }
    .dezena-resultado {
        display: inline-flex;
        justify-content: center;
        align-items: center;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, #5cff75, #16a34a 65%, #0f7a35);
        color: #ffffff;
        font-weight: 900;
        font-size: 13px;
        border: 2px solid rgba(255,255,255,0.18);
        box-shadow: 0 0 10px rgba(34,197,94,0.45);
    }
    .info-box {
        background: #1c2d45;
        border-left: 4px solid #1e88ff;
        color: #ffffff;
        padding: 16px 18px;
        border-radius: 8px;
        margin: 20px 0 14px 0;
        font-size: 14px;
        font-weight: 700;
    }
    .metric-card {
        background: #111821;
        border: 1px solid #2d3b4f;
        border-radius: 10px;
        padding: 22px 16px;
        text-align: center;
        min-height: 95px;
    }
    .metric-label {
        font-size: 13px;
        color: #9bd1ff;
        margin-bottom: 12px;
    }
    .metric-value {
        color: #2f83ff;
        font-size: 24px;
        font-weight: 900;
    }
    .section-divider {
        border-top: 1px solid #2d3b4f;
        margin: 30px 0;
    }
    .dezena-base {
        display: inline-flex;
        justify-content: center;
        align-items: center;
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background: #1e88ff;
        color: white;
        font-weight: 900;
        margin: 4px;
        box-shadow: 0 0 8px rgba(30,136,255,0.45);
    }
    .dezena-fixa-painel {
        display: inline-flex;
        justify-content: center;
        align-items: center;
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background: linear-gradient(135deg, #6366f1, #4f46e5);
        color: white;
        font-weight: 900;
        margin: 4px;
        border: 2px solid #818cf8;
        box-shadow: 0 0 12px rgba(99, 102, 241, 0.7);
    }
    .dezena-fria {
        display: inline-flex;
        justify-content: center;
        align-items: center;
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background: #ef4444;
        color: white;
        font-weight: 900;
        margin: 4px;
        box-shadow: 0 0 8px rgba(239,68,68,0.45);
    }
    .jogo-box {
        background: #111821;
        border: 1px solid #2d3b4f;
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 10px;
    }
    .jogo-titulo {
        color: #93c5fd;
        font-weight: 800;
        margin-bottom: 8px;
    }
    .dezena-jogo {
        display: inline-flex;
        justify-content: center;
        align-items: center;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: #16a34a;
        color: white;
        font-weight: 800;
        margin: 3px;
        font-size: 12px;
    }
    .dezena-acerto {
        display: inline-flex;
        justify-content: center;
        align-items: center;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, #facc15, #ca8a04 65%, #854d0e);
        color: white;
        font-weight: 800;
        margin: 3px;
        font-size: 12px;
        box-shadow: 0 0 8px rgba(234, 179, 8, 0.6);
    }
    .premio-card {
        background: #16222f;
        border: 1px solid #ca8a04;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
    }
    .premio-titulo {
        font-size: 12px;
        color: #fef08a;
    }
    .premio-valor {
        font-size: 20px;
        font-weight: 900;
        color: #facc15;
    }
    .stDownloadButton button, .stButton button {
        border-radius: 8px;
        font-weight: 800;
    }

    /* ============================================================
       REGRAS EXCLUSIVAS DE IMPRESSÃO (VOLANTES A4 OCULTOS NA TELA)
       ============================================================ */
    
    /* Na tela, esconde o bloco de impressão */
    .printable-print-area { display: none; }

    @media print {
        /* Esconde tudo na impressão, exceto a área de impressão */
        body * { visibility: hidden; }
        
        .printable-print-area, .printable-print-area * {
            visibility: visible;
        }

        .printable-print-area {
            position: absolute;
            left: 0;
            top: 0;
            width: 210mm;
            padding: 20mm;
        }

        .volante-wrapper-print {
            display: inline-block;
            border: 0.5px dashed #777777;
            width: 84mm;
            height: 143mm;
            margin: 10mm;
            padding: 5mm;
            page-break-inside: avoid;
        }

        .volante-grid-print {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 4mm;
            justify-items: center;
        }

        .dezena-volante-print {
            width: 10mm;
            height: 8mm;
            color: transparent;
            border: none;
        }

        .dezena-volante-print.marcada {
            background-color: #000000;
            border-radius: 1px;
        }
    }
</style>
""",
    unsafe_allow_html=True
)

# ============================================================
# FUNÇÕES DE BUSCA NA CAIXA E ANÁLISE
# ============================================================
BASE_URL = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil"

@st.cache_data(ttl=600)
def buscar_concurso(numero=None):
    headers = {"User-Agent": "Mozilla/5.0"}
    url = BASE_URL if numero is None else f"{BASE_URL}/{numero}"
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()
    dados = response.json()
    dezenas = [str(d).zfill(2) for d in dados.get("listaDezenas", [])]
    return {
        "numero": dados.get("numero"),
        "data": dados.get("dataApuracao"),
        "dezenas": dezenas,
        "municipio": dados.get("nomeMunicipioUFSorteio") or dados.get("nomeMunicipioSorteio"),
        "local": dados.get("localSorteio"),
        "raw": dados
    }

@st.cache_data(ttl=600)
def carregar_concursos(qtd):
    ultimo = buscar_concurso()
    numero_ultimo = int(ultimo["numero"])
    concursos = []
    for numero in range(numero_ultimo, numero_ultimo - qtd, -1):
        try:
            concurso = buscar_concurso(numero)
            if concurso["dezenas"]: concursos.append(concurso)
        except: continue
    return concursos

def analisar_concursos(concursos):
    todas_dezenas = []
    for c in concursos: todas_dezenas.extend(c["dezenas"])
    frequencia = Counter(todas_dezenas)
    universo = [str(i).zfill(2) for i in range(1, 26)]
    df_freq = pd.DataFrame({"dezena": universo, "frequencia": [frequencia.get(d, 0) for d in universo]})
    return df_freq.sort_values(by=["frequencia", "dezena"], ascending=[False, True]).reset_index(drop=True)

def calcular_atrasos(concursos):
    universo = [str(i).zfill(2) for i in range(1, 26)]
    atrasos = {}
    for dezena in universo:
        atraso = 0
        for c in concursos:
            if dezena in c["dezenas"]: break
            atraso += 1
        atrasos[dezena] = atraso
    df_atrasos = pd.DataFrame({"dezena": list(atrasos.keys()), "atraso": list(atrasos.values())})
    return df_atrasos.sort_values(by=["atraso", "dezena"], ascending=[False, True]).reset_index(drop=True)

def estatisticas_jogo(jogo, ultimo_resultado):
    numeros = [int(x) for x in jogo]
    pares = sum(1 for n in numeros if n % 2 == 0)
    return {"pares": pares, "impares": 15 - pares, "soma": sum(numeros), "repetidas_ultimo": len(set(jogo).intersection(set(ultimo_resultado)))}

def pontuar_jogo(jogo, mapa_freq, mapa_atraso):
    return sum(mapa_freq.get(d, 0) for d in jogo) + sum(mapa_atraso.get(d, 0) for d in jogo) * 0.25

def gerar_desdobramento_com_fixos(base_variavel, fixos, qtd_jogos, ultimo_resultado, mapa_freq, mapa_atraso, p_min, p_max, s_min, s_max, r_min, r_max, sob_max):
    vagas = 15 - len(fixos)
    combinacoes = list(itertools.combinations(base_variavel, vagas))
    jogos_validos = []

    for combo in combinacoes:
        jogo = sorted(list(fixos) + list(combo), key=lambda x: int(x))
        stats = estatisticas_jogo(jogo, ultimo_resultado)
        if not (p_min <= stats["pares"] <= p_max): continue
        if not (s_min <= stats["soma"] <= s_max): continue
        if not (r_min <= stats["repetidas_ultimo"] <= r_max): continue
        
        pontos = pontuar_jogo(jogo, mapa_freq, mapa_atraso)
        jogos_validos.append({"jogo": jogo, "score": pontos, **stats})

    jogos_validos.sort(key=lambda x: x["score"], reverse=True)
    selecionados = []
    for item in jogos_validos:
        if not selecionados:
            selecionados.append(item)
        else:
            if all(len(set(item["jogo"]).intersection(set(s["jogo"]))) <= sob_max for s in selecionados):
                selecionados.append(item)
        if len(selecionados) >= qtd_jogos: break

    if len(selecionados) < qtd_jogos:
        for item in jogos_validos:
            if item not in selecionados: selecionados.append(item)
            if len(selecionados) >= qtd_jogos: break

    return selecionados[:qtd_jogos]

def jogos_para_csv(jogos):
    linhas = []
    for idx, item in enumerate(jogos, start=1):
        linha = {"Jogo": idx, "Dezenas": " ".join(item["jogo"]), "Pares": item["pares"], "Ímpares": item["impares"], "Soma": item["soma"], "Repetidas": item["repetidas_ultimo"], "Score": round(item["score"], 2)}
        for p, d in enumerate(item["jogo"], start=1): linha[f"D{p:02d}"] = d
        linhas.append(linha)
    return pd.DataFrame(linhas).to_csv(index=False, sep=";", encoding="utf-8-sig")

# ============================================================
# CÓDIGO DA TELA
# ============================================================
st.markdown("# 🍀 Lotofácil | Análises e Desdobramentos")

try:
    ultimo_concurso = buscar_concurso()
except:
    st.error("Erro na Caixa.")
    st.stop()

dezenas_ultimo = ultimo_concurso["dezenas"]

st.sidebar.header("⚙️ Configurações")
qtd_concursos = st.sidebar.number_input("Concursos analisados", 5, 100, 11)
tamanho_base = st.sidebar.number_input("Tamanho da base (Total números jogados)", 15, 25, 20)
qtd_jogos = st.sidebar.number_input("Qtd de jogos gerados", 1, 100, 12)

st.sidebar.divider()
dezenas_fixas = st.sidebar.multiselect("Dezenas FIXAS (Máx 5)", [str(i).zfill(2) for i in range(1, 26)], max_selections=5)
dezenas_para_descartar = st.sidebar.multiselect("Dezenas descartadas", [str(i).zfill(2) for i in range(1, 26) if str(i).zfill(2) not in dezenas_fixas])

st.sidebar.divider()
pares_min, pares_max = st.sidebar.slider("Pares", 0, 15, (6, 9))
soma_min = st.sidebar.number_input("Soma mínima", 120, 300, 170)
soma_max = st.sidebar.number_input("Soma máxima", 120, 300, 220)
repetidas_min, repetidas_max = st.sidebar.slider("Repetidas", 0, 15, (8, 11))
sobreposicao_max = st.sidebar.slider("Sobreposição máxima", 8, 15, 13)

with st.spinner("Analisando..."):
    concursos = carregar_concursos(qtd_concursos)
df_freq = analisar_concursos(concursos)
df_atrasos = calcular_atrasos(concursos)
mapa_freq = dict(zip(df_freq["dezena"], df_freq["frequencia"]))
mapa_atraso = dict(zip(df_atrasos["dezena"], df_atrasos["atraso"]))

opcoes_concurso = {f"Concurso {c['numero']} ({c['data']})": c['dezenas'] for c in concursos}
opcoes_concurso["Inserir Dezenas Manualmente"] = []

st.markdown("## 📊 Visão Geral")
c1, c2 = st.columns(2)
with c1:
    st.markdown("### 🔥 Fortes")
    st.markdown("".join([f'<span class="dezena-base">{r["dezena"]}</span>' for _, r in df_freq.head(10).iterrows()]), unsafe_allow_html=True)
with c2:
    st.markdown("### 🧊 Atrasadas")
    st.markdown("".join([f'<span class="dezena-fria">{r["dezena"]}</span>' for _, r in df_atrasos.head(10).iterrows()]), unsafe_allow_html=True)

st.markdown("## 🎯 Base Sugerida")
df_base = df_freq[~df_freq["dezena"].isin(dezenas_para_descartar + dezenas_fixas)]
base_variavel = df_base.head(tamanho_base - len(dezenas_fixas))["dezena"].tolist()
base_sugerida = sorted(list(set(base_variavel + dezenas_fixas)), key=lambda x: int(x))
st.markdown("".join([f'<span class="{"dezena-fixa-painel" if d in dezenas_fixas else "dezena-base"}">{d}</span>' for d in base_sugerida]), unsafe_allow_html=True)

st.markdown("## 🧩 Desdobramento")
if st.button("🎲 Gerar Novo Desdobramento", type="primary", use_container_width=True):
    st.session_state["jogos_gerados"] = gerar_desdobramento_com_fixos(
        base_variavel, dezenas_fixas, qtd_jogos, dezenas_ultimo, mapa_freq, mapa_atraso,
        pares_min, pares_max, soma_min, soma_max, repetidas_min, repetidas_max, sobreposicao_max
    )
    st.success("Jogos gerados!")

if st.session_state["jogos_gerados"]:
    jogos = st.session_state["jogos_gerados"]

    st.markdown("## 🎟️ Conferência")
    st.checkbox("Ocultar resultados visuais da conferência (apenas jogos limpos)", key="esconder_gabarito")

    col_s, col_b = st.columns([3, 1])
    sel_conc = col_s.selectbox("Selecione para conferir:", list(opcoes_concurso.keys()), label_visibility="collapsed")
    dezenas_alvo = []
    if sel_conc == "Inserir Dezenas Manualmente":
        d_man = st.text_input("Dezenas separadas por espaço:")
        if d_man: dezenas_alvo = [d.zfill(2) for d in d_man.strip().split()][:15]
    else: dezenas_alvo = opcoes_concurso[sel_conc]

    rodar_conf = col_b.button("🔍 Rodar Conferência", use_container_width=True)

    if not st.session_state["esconder_gabarito"] and dezenas_alvo and rodar_conf:
        contadores = {11: 0, 12: 0, 13: 0, 14: 0, 15: 0}
        for item in jogos:
            acertos = len(set(item["jogo"]).intersection(set(dezenas_alvo)))
            if acertos in contadores: contadores[acertos] += 1
        st.markdown("### 🏆 Premiações")
        cp = st.columns(5)
        for i, pt in enumerate([11, 12, 13, 14, 15]):
            cp[i].markdown(f'<div class="premio-card"><div class="premio-titulo">{pt} Acertos</div><div class="premio-valor">{contadores[pt]} jg</div></div>', unsafe_allow_html=True)

    st.markdown("### 📋 Seus Jogos (Visualização Original)")
    
    # Adicionando botão que dispara a janela de impressão
    if st.button("🖨️ Imprimir Cartões A4 (Apenas Marcações)", use_container_width=True):
        components.html("<script>window.print();</script>", height=0, width=0)

    # Renderiza o visual de blocos antigos
    for idx, item in enumerate(jogos):
        html_jogo = ""
        acertos_set = set(item["jogo"]).intersection(set(dezenas_alvo)) if (dezenas_alvo and rodar_conf and not st.session_state["esconder_gabarito"]) else set()
        
        for dezena in item["jogo"]:
            if dezena in acertos_set:
                html_jogo += f'<span class="dezena-acerto">{dezena}</span>'
            else:
                html_jogo += f'<span class="dezena-jogo">{dezena}</span>'

        texto_acertos = f' | Acertos: <strong style="color:#facc15;">{len(acertos_set)}</strong>' if acertos_set else ""
        
        st.markdown(f"""
        <div class="jogo-box">
            <div class="jogo-titulo">Jogo {idx + 1}</div>
            <div>{html_jogo}</div>
            <div style="margin-top:10px;color:#cbd5e1;font-size:13px;">
                Pares: <strong>{item['pares']}</strong> | Ímpares: <strong>{item['impares']}</strong> | Soma: <strong>{item['soma']}</strong> | Repetidas: <strong>{item['repetidas_ultimo']}</strong> {texto_acertos}
            </div>
        </div>""", unsafe_allow_html=True)

    # Estrutura HTML Oculta gerada APENAS para a impressão (Formato Volante)
    ORDEM_VOLANTE = ["21", "16", "11", "06", "01", "22", "17", "12", "07", "02", "23", "18", "13", "08", "03", "24", "19", "14", "09", "04", "25", "20", "15", "10", "05"]
    
    html_print = '<div class="printable-print-area">'
    for item in jogos:
        jogo_set = set(item["jogo"])
        html_print += '<div class="volante-wrapper-print"><div class="volante-grid-print">'
        for d in ORDEM_VOLANTE:
            classe = "dezena-volante-print"
            if d in jogo_set: classe += " marcada"
            html_print += f'<div class="{classe}"></div>'
        html_print += '</div></div>'
    html_print += '</div>'
    
    st.markdown(html_print, unsafe_allow_html=True)

    st.download_button("⬇️ Baixar CSV", jogos_para_csv(jogos), "jogos.csv", "text/csv")
