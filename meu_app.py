import streamlit as st
import pandas as pd
import requests
import itertools
import math
from collections import Counter
from datetime import datetime

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Lotofácil | Análises e Desdobramentos",
    page_icon="🍀",
    layout="wide"
)

# ============================================================
# ESTADO DA SESSÃO (SESSION STATE)
# ============================================================
if "jogos_gerados" not in st.session_state:
    st.session_state["jogos_gerados"] = []

# ============================================================
# CSS
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

    .ultimo-local strong {
        color: #ffffff;
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
        box-shadow:
            0 0 10px rgba(34,197,94,0.45),
            inset 0 2px 5px rgba(255,255,255,0.25),
            inset 0 -4px 8px rgba(0,0,0,0.22);
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

    /* Estilo para as dezenas que foram acertadas na conferência */
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

    /* Estilo dos cartões de premiação */
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

    .stDownloadButton button {
        background-color: #16a34a !important;
        color: white !important;
        border-radius: 8px;
        font-weight: 800;
    }
</style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# FUNÇÕES DE BUSCA NA CAIXA
# ============================================================

BASE_URL = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil"


@st.cache_data(ttl=600)
def buscar_concurso(numero=None):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json,text/plain,*/*"
    }

    if numero is None:
        url = BASE_URL
    else:
        url = f"{BASE_URL}/{numero}"

    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()
    dados = response.json()

    dezenas = dados.get("listaDezenas", [])
    dezenas = [str(d).zfill(2) for d in dezenas]

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
            if concurso["dezenas"]:
                concursos.append(concurso)
        except Exception:
            continue

    return concursos


# ============================================================
# FUNÇÕES DE ANÁLISE
# ============================================================

def analisar_concursos(concursos):
    todas_dezenas = []

    for concurso in concursos:
        todas_dezenas.extend(concurso["dezenas"])

    frequencia = Counter(todas_dezenas)

    universo = [str(i).zfill(2) for i in range(1, 26)]

    df_freq = pd.DataFrame({
        "dezena": universo,
        "frequencia": [frequencia.get(dezena, 0) for dezena in universo]
    })

    df_freq = df_freq.sort_values(
        by=["frequencia", "dezena"],
        ascending=[False, True]
    ).reset_index(drop=True)

    return df_freq


def calcular_atrasos(concursos):
    universo = [str(i).zfill(2) for i in range(1, 26)]
    atrasos = {}

    for dezena in universo:
        atraso = 0

        for concurso in concursos:
            if dezena in concurso["dezenas"]:
                break
            atraso += 1

        atrasos[dezena] = atraso

    df_atrasos = pd.DataFrame({
        "dezena": list(atrasos.keys()),
        "atraso": list(atrasos.values())
    })

    df_atrasos = df_atrasos.sort_values(
        by=["atraso", "dezena"],
        ascending=[False, True]
    ).reset_index(drop=True)

    return df_atrasos


def estatisticas_jogo(jogo, ultimo_resultado):
    numeros = [int(x) for x in jogo]

    pares = sum(1 for n in numeros if n % 2 == 0)
    impares = 15 - pares
    soma = sum(numeros)
    repetidas_ultimo = len(set(jogo).intersection(set(ultimo_resultado)))

    return {
        "pares": pares,
        "impares": impares,
        "soma": soma,
        "repetidas_ultimo": repetidas_ultimo
    }


def pontuar_jogo(jogo, mapa_freq, mapa_atraso):
    score_freq = sum(mapa_freq.get(d, 0) for d in jogo)
    score_atraso = sum(mapa_atraso.get(d, 0) for d in jogo)

    return score_freq + score_atraso * 0.25


def gerar_desdobramento(
    base,
    qtd_jogos,
    ultimo_resultado,
    mapa_freq,
    mapa_atraso,
    pares_min,
    pares_max,
    soma_min,
    soma_max,
    repetidas_min,
    repetidas_max,
    sobreposicao_max
):
    combinacoes = list(itertools.combinations(base, 15))

    jogos_validos = []

    for combo in combinacoes:
        jogo = list(combo)
        stats = estatisticas_jogo(jogo, ultimo_resultado)

        if not (pares_min <= stats["pares"] <= pares_max):
            continue

        if not (soma_min <= stats["soma"] <= soma_max):
            continue

        if not (repetidas_min <= stats["repetidas_ultimo"] <= repetidas_max):
            continue

        pontos = pontuar_jogo(jogo, mapa_freq, mapa_atraso)

        jogos_validos.append({
            "jogo": jogo,
            "score": pontos,
            "pares": stats["pares"],
            "impares": stats["impares"],
            "soma": stats["soma"],
            "repetidas_ultimo": stats["repetidas_ultimo"]
        })

    jogos_validos = sorted(jogos_validos, key=lambda x: x["score"], reverse=True)

    selecionados = []

    for item in jogos_validos:
        jogo_atual = set(item["jogo"])

        if not selecionados:
            selecionados.append(item)
        else:
            aprovado = True

            for selecionado in selecionados:
                intersecao = len(jogo_atual.intersection(set(selecionado["jogo"])))

                if intersecao > sobreposicao_max:
                    aprovado = False
                    break

            if aprovado:
                selecionados.append(item)

        if len(selecionados) >= qtd_jogos:
            break

    if len(selecionados) < qtd_jogos:
        for item in jogos_validos:
            if item not in selecionados:
                selecionados.append(item)

            if len(selecionados) >= qtd_jogos:
                break

    return selecionados[:qtd_jogos]


def jogos_para_csv(jogos):
    linhas = []

    for idx, item in enumerate(jogos, start=1):
        linha = {
            "Jogo": idx,
            "Dezenas": " ".join(item["jogo"]),
            "Pares": item["pares"],
            "Ímpares": item["impares"],
            "Soma": item["soma"],
            "Repetidas do último": item["repetidas_ultimo"],
            "Score": round(item["score"], 2)
        }

        for pos, dezena in enumerate(item["jogo"], start=1):
            linha[f"D{pos:02d}"] = dezena

        linhas.append(linha)

    return pd.DataFrame(linhas).to_csv(index=False, sep=";", encoding="utf-8-sig")


# ============================================================
# CABEÇALHO
# ============================================================

st.markdown("# 🍀 Lotofácil | Análises e Desdobramentos")
st.markdown(
    '<div class="subtitulo">Painel estatístico com base nos últimos concursos analisados</div>',
    unsafe_allow_html=True
)

# ============================================================
# ÚLTIMO SORTEIO NO TOPO
# ============================================================

try:
    ultimo_concurso = buscar_concurso()
except Exception as erro:
    st.error("Não foi possível carregar o último concurso automaticamente da Caixa.")
    st.stop()

numero_ultimo = ultimo_concurso["numero"]
data_ultimo = ultimo_concurso["data"]
dezenas_ultimo = ultimo_concurso["dezenas"]

municipio_sorteio = ultimo_concurso["municipio"]
local_sorteio = ultimo_concurso["local"]

if municipio_sorteio:
    texto_local = municipio_sorteio
elif local_sorteio:
    texto_local = local_sorteio
else:
    texto_local = "Local não informado"

html_dezenas_resultado = "".join(
    [f'<span class="dezena-resultado">{dezena}</span>' for dezena in dezenas_ultimo]
)

html_ultimo_sorteio = (
    f'<div class="ultimo-sorteio">'
    f'<div class="ultimo-label">🍀 Último sorteio carregado automaticamente da Caixa</div>'
    f'<div class="ultimo-concurso">Concurso {numero_ultimo} — {data_ultimo}</div>'
    f'<div class="ultimo-local">Sorteio realizado em: <strong>{texto_local}</strong></div>'
    f'<div class="dezenas-resultado-container">{html_dezenas_resultado}</div>'
    f'</div>'
)

st.markdown(html_ultimo_sorteio, unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("⚙️ Configurações")

qtd_concursos = st.sidebar.number_input(
    "Quantidade de concursos para análise",
    min_value=5,
    max_value=100,
    value=11,
    step=1
)

tamanho_base = st.sidebar.number_input(
    "Tamanho da base sugerida",
    min_value=15,
    max_value=25,
    value=18,
    step=1
)

qtd_jogos = st.sidebar.number_input(
    "Quantidade de jogos no desdobramento",
    min_value=1,
    max_value=100,
    value=12,
    step=1
)

st.sidebar.divider()

dezenas_para_descartar = st.sidebar.multiselect(
    "Dezenas temporariamente descartadas",
    options=[str(i).zfill(2) for i in range(1, 26)],
    default=[]
)

st.sidebar.divider()

st.sidebar.subheader("Filtros combinatórios")

pares_min = st.sidebar.slider(
    "Mínimo de pares",
    min_value=0,
    max_value=15,
    value=6
)

pares_max = st.sidebar.slider(
    "Máximo de pares",
    min_value=0,
    max_value=15,
    value=9
)

soma_min = st.sidebar.number_input(
    "Soma mínima",
    min_value=120,
    max_value=300,
    value=170,
    step=1
)

soma_max = st.sidebar.number_input(
    "Soma máxima",
    min_value=120,
    max_value=300,
    value=220,
    step=1
)

repetidas_min = st.sidebar.slider(
    "Mínimo de repetidas do último concurso",
    min_value=0,
    max_value=15,
    value=8
)

repetidas_max = st.sidebar.slider(
    "Máximo de repetidas do último concurso",
    min_value=0,
    max_value=15,
    value=11
)

sobreposicao_max = st.sidebar.slider(
    "Sobreposição máxima entre jogos",
    min_value=8,
    max_value=15,
    value=13
)

# ============================================================
# CARREGAMENTO DOS CONCURSOS
# ============================================================

with st.spinner("Carregando concursos da Caixa..."):
    concursos = carregar_concursos(qtd_concursos)

if not concursos:
    st.error("Nenhum concurso foi carregado.")
    st.stop()

df_freq = analisar_concursos(concursos)
df_atrasos = calcular_atrasos(concursos)

mapa_freq = dict(zip(df_freq["dezena"], df_freq["frequencia"]))
mapa_atraso = dict(zip(df_atrasos["dezena"], df_atrasos["atraso"]))

# ==========================================
# PREPARAÇÃO DA LISTA DE OPÇÕES PARA CONFERÊNCIA
# ==========================================
opcoes_concurso = {}
for c in concursos:
    opcoes_concurso[f"Concurso {c['numero']} ({c['data']})"] = c['dezenas']
opcoes_concurso["Inserir Dezenas Manualmente"] = []

# ============================================================
# VISÃO GERAL DA ANÁLISE
# ============================================================

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown("## 📊 Visão Geral da Análise")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🔥 Dezenas mais fortes")

    dezenas_fortes = df_freq.head(10)

    html_fortes = ""

    for _, row in dezenas_fortes.iterrows():
        html_fortes += f'<span class="dezena-base">{row["dezena"]}</span>'

    st.markdown(html_fortes, unsafe_allow_html=True)

    st.dataframe(
        dezenas_fortes.rename(
            columns={
                "dezena": "Dezena",
                "frequencia": "Frequência"
            }
        ),
        use_container_width=True,
        hide_index=True
    )

with col2:
    st.markdown(f"### 📈 Frequência das dezenas nos últimos {len(concursos)} concursos")

    grafico_freq = df_freq.copy()
    grafico_freq = grafico_freq.sort_values("dezena")

    st.bar_chart(
        grafico_freq,
        x="dezena",
        y="frequencia",
        use_container_width=True
    )

# ============================================================
# ATRASOS
# ============================================================

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown("## 🧊 Dezenas em atraso")

col1, col2 = st.columns(2)

with col1:
    dezenas_atrasadas = df_atrasos.head(10)

    html_atrasadas = ""

    for _, row in dezenas_atrasadas.iterrows():
        html_atrasadas += f'<span class="dezena-fria">{row["dezena"]}</span>'

    st.markdown(html_atrasadas, unsafe_allow_html=True)

    st.dataframe(
        dezenas_atrasadas.rename(
            columns={
                "dezena": "Dezena",
                "atraso": "Concursos sem sair"
            }
        ),
        use_container_width=True,
        hide_index=True
    )

with col2:
    grafico_atrasos = df_atrasos.copy()
    grafico_atrasos = grafico_atrasos.sort_values("dezena")

    st.bar_chart(
        grafico_atrasos,
        x="dezena",
        y="atraso",
        use_container_width=True
    )

# ============================================================
# BASE SUGERIDA
# ============================================================

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown("## 🎯 Base sugerida")

df_base = df_freq.copy()

if dezenas_para_descartar:
    df_base = df_base[~df_base["dezena"].isin(dezenas_para_descartar)]

base_sugerida = df_base.head(tamanho_base)["dezena"].tolist()
base_sugerida = sorted(base_sugerida, key=lambda x: int(x))

html_base = ""

for dezena in base_sugerida:
    html_base += f'<span class="dezena-base">{dezena}</span>'

st.markdown(html_base, unsafe_allow_html=True)

if dezenas_para_descartar:
    st.warning(
        "Dezenas descartadas temporariamente: "
        + ", ".join(dezenas_para_descartar)
    )

st.caption(
    "A base é montada pelas dezenas mais frequentes dentro do período analisado, "
    "desconsiderando as dezenas temporariamente descartadas."
)

# ============================================================
# GERAÇÃO DO DESDOBRAMENTO (MODIFICADO COM O BOTÃO DE GERAR NOVO)
# ============================================================

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown("## 🧩 Geração de jogos")

if len(base_sugerida) < 15:
    st.error("A base sugerida precisa ter pelo menos 15 dezenas.")
else:
    total_combinacoes_base = math.comb(len(base_sugerida), 15)

    st.info(
        f"A base atual com {len(base_sugerida)} dezenas gera "
        f"{total_combinacoes_base:,}".replace(",", ".")
        + " combinações possíveis de 15 dezenas."
    )

    # 🚀 BOTÃO DE GERAR DESDOBRAMENTO NOVO
    if st.button("🎲 Gerar Novo Desdobramento", use_container_width=True, type="primary"):
        st.session_state["jogos_gerados"] = gerar_desdobramento(
            base=base_sugerida,
            qtd_jogos=qtd_jogos,
            ultimo_resultado=dezenas_ultimo,
            mapa_freq=mapa_freq,
            mapa_atraso=mapa_atraso,
            pares_min=pares_min,
            pares_max=pares_max,
            soma_min=soma_min,
            soma_max=soma_max,
            repetidas_min=repetidas_min,
            repetidas_max=repetidas_max,
            sobreposicao_max=sobreposicao_max
        )
        if not st.session_state["jogos_gerados"]:
            st.warning("Nenhum jogo foi encontrado com os filtros atuais. Tente flexibilizar os critérios na lateral.")
        else:
            st.success(f"{len(st.session_state['jogos_gerados'])} jogos gerados com sucesso e salvos no painel!")

# ============================================================
# RENDERIZAÇÃO E CONFERÊNCIA DOS JOGOS SALVOS
# ============================================================

if st.session_state["jogos_gerados"]:
    jogos_para_exibir = st.session_state["jogos_gerados"]
    
    # 🚀 SEÇÃO COMPLETA DE CONFERÊNCIA DE ACERTOS
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("## 🎟️ Conferência de Acertos")
    
    col_conf1, col_conferir_btn = st.columns([3, 1])
    
    with col_conf1:
        selecao_concurso = st.selectbox(
            "Selecione o concurso para conferir seus jogos atuais:",
            options=list(opcoes_concurso.keys()),
            label_visibility="collapsed"
        )
    
    dezenas_alvo = []
    if selecao_concurso == "Inserir Dezenas Manualmente":
        dezenas_manuais_input = st.text_input("Digite 15 dezenas separadas por espaço (ex: 01 02 03...):")
        if dezenas_manuais_input:
            dezenas_alvo = [d.zfill(2) for d in dezenas_manuais_input.strip().split() if d.isdigit()][:15]
    else:
        dezenas_alvo = opcoes_concurso[selecao_concurso]
        
    # Exibe as dezenas que serão usadas como gabarito de teste
    if dezenas_alvo:
        html_gabarito = "".join([f'<span class="dezena-resultado">{d}</span>' for d in dezenas_alvo])
        st.markdown(f"<div style='margin-bottom:15px;'><strong>Gabarito de Conferência:</strong><br>{html_gabarito}</div>", unsafe_allow_html=True)

    # 🚀 BOTÃO DE CONFERÊNCIA
    rodar_conferencia = col_conferir_btn.button("🔍 Rodar Conferência", use_container_width=True)

    # Dicionário para armazenar contadores de faixas de acertos
    contadores_premios = {11: 0, 12: 0, 13: 0, 14: 0, 15: 0}
    mapa_acertos_jogos = {}

    if dezenas_alvo:
        for idx, item in enumerate(jogos_para_exibir):
            acertos = set(item["jogo"]).intersection(set(dezenas_alvo))
            qtd_acertos = len(acertos)
            mapa_acertos_jogos[idx] = acertos
            if qtd_acertos in contadores_premios:
                contadores_premios[qtd_acertos] += 1

        if rodar_conferencia:
            st.markdown("### 🏆 Painel de Premiações")
            c_p1, c_p2, c_p3, c_p4, c_p5 = st.columns(5)
            c_p1.markdown(f'<div class="premio-card"><div class="premio-titulo">11 Acertos</div><div class="premio-value premio-valor">{contadores_premios[11]} jg</div></div>', unsafe_allow_html=True)
            c_p2.markdown(f'<div class="premio-card"><div class="premio-titulo">12 Acertos</div><div class="premio-value premio-valor">{contadores_premios[12]} jg</div></div>', unsafe_allow_html=True)
            c_p3.markdown(f'<div class="premio-card"><div class="premio-titulo">13 Acertos</div><div class="premio-value premio-valor">{contadores_premios[13]} jg</div></div>', unsafe_allow_html=True)
            c_p4.markdown(f'<div class="premio-card"><div class="premio-titulo">14 Acertos</div><div class="premio-value premio-valor">{contadores_premios[14]} jg</div></div>', unsafe_allow_html=True)
            c_p5.markdown(f'<div class="premio-card"><div class="premio-titulo">15 Acertos</div><div class="premio-value premio-valor">{contadores_premios[15]} jg</div></div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

    # Impressão visual da lista de jogos salvos
    st.markdown("### 📋 Seus Jogos Atuais")
    for idx, item in enumerate(jogos_para_exibir):
        html_jogo = ""
        acertos_desse_jogo = mapa_acertos_jogos.get(idx, set()) if dezenas_alvo else set()

        for dezena in item["jogo"]:
            if dezena in acertos_desse_jogo and rodar_conferencia:
                html_jogo += f'<span class="dezena-acerto">{dezena}</span>'
            else:
                html_jogo += f'<span class="dezena-jogo">{dezena}</span>'

        texto_conferencia_stats = ""
        if dezenas_alvo and rodar_conferencia:
            texto_conferencia_stats = f' | Acertos neste concurso: <strong style="color:#facc15;font-size:14px;">{len(acertos_desse_jogo)} ACERTOS</strong>'

        st.markdown(
            f"""
<div class="jogo-box">
    <div class="jogo-titulo">Jogo {idx + 1}</div>
    <div>{html_jogo}</div>
    <div style="margin-top:10px;color:#cbd5e1;font-size:13px;">
        Pares: <strong>{item["pares"]}</strong> |
        Ímpares: <strong>{item["impares"]}</strong> |
        Soma: <strong>{item["soma"]}</strong> |
        Repetidas do último: <strong>{item["repetidas_ultimo"]}</strong> |
        Score: <strong>{round(item["score"], 2)}</strong>{texto_conferencia_stats}
    </div>
</div>
            """,
            unsafe_allow_html=True
        )

    csv = jogos_para_csv(jogos_para_exibir)
    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(
        label="⬇️ Baixar jogos salvos em CSV",
        data=csv,
        file_name="desdobramento_lotofacil.csv",
        mime="text/csv"
    )
else:
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.info("💡 Escolha suas definições de filtros na lateral esquerda e clique em 'Gerar Novo Desdobramento' para iniciar a montagem dos cartões.")

# ============================================================
# LEITURA COMBINATÓRIA
# ============================================================

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown("## ## 🧠 Leitura combinatória")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Distribuição par/ímpar")
    if st.session_state["jogos_generados" if "jogos_generados" in st.session_state else "jogos_gerados"]:
        df_paridade = pd.DataFrame(st.session_state["jogos_gerados"])
        st.dataframe(
            df_paridade[["pares", "impares", "soma", "repetidas_ultimo"]].rename(
                columns={
                    "pares": "Pares",
                    "impares": "Ímpares",
                    "soma": "Soma",
                    "repetidas_ultimo": "Repetidas do último"
                }
            ),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.caption("Gere jogos para visualizar esta leitura.")

with col2:
    st.markdown("### Repetição do último concurso")
    if st.session_state["jogos_gerados"]:
        repeticoes = [j["repetidas_ultimo"] for j in st.session_state["jogos_gerados"]]

        df_repeticoes = pd.DataFrame({
            "Repetidas": repeticoes
        })

        st.bar_chart(df_repeticoes, y="Repetidas", use_container_width=True)
    else:
        st.caption("Gere jogos para visualizar esta leitura.")

with col3:
    st.markdown("### Faixa de soma")
    if st.session_state["jogos_gerados"]:
        somas = [j["soma"] for j in st.session_state["jogos_gerados"]]

        st.metric("Menor soma", min(somas))
        st.metric("Maior soma", max(somas))
        st.metric("Média", round(sum(somas) / len(somas), 2))
    else:
        st.caption("Gere jogos para visualizar esta leitura.")

# ============================================================
# HISTÓRICO CARREGADO
# ============================================================

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

with st.expander("📚 Ver concursos analisados"):
    linhas_historico = []

    for concurso in concursos:
        linhas_historico.append({
            "Concurso": concurso["numero"],
            "Data": concurso["data"],
            "Dezenas": " ".join(concurso["dezenas"])
        })

    st.dataframe(
        pd.DataFrame(linhas_historico),
        use_container_width=True,
        hide_index=True
    )

# ============================================================
# RESUMO FINAL DA PÁGINA
# ============================================================

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown("## 📌 Resumo do painel")

st.markdown(
    """
<div class="info-box">
    Este painel reúne uma análise estatística feita para a Lotofácil, incluindo frequência das dezenas,
    seleção de base com 18 números, dezenas temporariamente descartadas, geração de jogos e leitura combinatória.
</div>
    """,
    unsafe_allow_html=True
)

total_combinacoes_lotofacil = math.comb(25, 15)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
<div class="metric-card">
    <div class="metric-label">Concursos analisados</div>
    <div class="metric-value">{len(concursos)}</div>
</div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
<div class="metric-card">
    <div class="metric-label">Total de combinações da Lotofácil</div>
    <div class="metric-value">{total_combinacoes_lotofacil:,}</div>
</div>
        """.replace(",", ","),
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
<div class="metric-card">
    <div class="metric-label">Base sugerida</div>
    <div class="metric-value">{len(base_sugerida)}</div>
</div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"""
<div class="metric-card">
    <div class="metric-label">Desdobramento</div>
    <div class="metric-value">{len(st.session_state["jogos_gerados"])} jogos</div>
</div>
        """,
        unsafe_allow_html=True
    )

st.markdown(
    """
<br>
<div style="color:#94a3b8;font-size:13px;text-align:center;">
    Análise estatística e combinatória. Este painel não garante premiação e não substitui decisão pessoal de jogo.
</div>
    """,
    unsafe_allow_html=True
)
