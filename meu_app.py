import streamlit as st
import requests
import pandas as pd
import random
import math
import io
from collections import Counter

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Lotofácil | Análises e Desdobramentos",
    page_icon="🍀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS VISUAL
# ============================================================

st.markdown(
    """
<style>
    .main {
        background-color: #0b0f16;
    }

    h1, h2, h3, h4, h5, h6, p, div, span, label {
        color: #ffffff;
    }

    .stApp {
        background-color: #0b0f16;
    }

    section[data-testid="stSidebar"] {
        background-color: #262833;
    }

    .card {
        background: #141a23;
        border: 1px solid #2f3745;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin-bottom: 14px;
    }

    .card-title {
        color: #9fb3c8;
        font-size: 13px;
        margin-bottom: 8px;
    }

    .card-value {
        color: #4094ff;
        font-size: 26px;
        font-weight: 800;
    }

    .ultimo-sorteio {
        border: 2px solid #1e88ff;
        border-radius: 14px;
        padding: 20px 24px;
        margin: 10px 0 22px 0;
        background: linear-gradient(90deg, #111827, #162033);
        box-shadow: 0 0 16px rgba(30,136,255,0.28);
    }

    .ultimo-label {
        font-size: 16px;
        color: #93c5fd;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .ultimo-concurso {
        font-size: 25px;
        color: #ffffff;
        font-weight: 900;
        margin-bottom: 12px;
    }

    .ultimo-local {
        color: #cbd5e1;
        font-size: 15px;
        margin-bottom: 14px;
    }

    .ultimo-local strong {
        color: #ffffff;
    }

    .dezenas-resultado-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        align-items: center;
        margin-top: 6px;
    }

    .dezena-resultado {
        display: inline-flex;
        justify-content: center;
        align-items: center;
        width: 42px;
        height: 42px;
        border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, #5cff75, #16a34a 65%, #0f7a35);
        color: #ffffff;
        font-weight: 900;
        font-size: 15px;
        border: 2px solid rgba(255,255,255,0.18);
        box-shadow:
            0 0 10px rgba(34,197,94,0.45),
            inset 0 2px 5px rgba(255,255,255,0.25),
            inset 0 -4px 8px rgba(0,0,0,0.22);
    }

    .dezena {
        display: inline-flex;
        justify-content: center;
        align-items: center;
        width: 38px;
        height: 38px;
        border-radius: 50%;
        color: white;
        font-weight: 900;
        margin: 5px;
        font-size: 14px;
        background: #334155;
    }

    .forte {
        background: #ff6b22;
    }

    .intermediaria {
        background: #0ea5e9;
    }

    .fraca {
        background: #64748b;
    }

    .base {
        background: #22c55e;
    }

    .jogo {
        background: #111827;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 8px;
        color: #ffffff;
        font-size: 16px;
    }

    .info-box {
        background: #1d2b3f;
        border-left: 4px solid #4094ff;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 16px;
        color: #ffffff;
    }
</style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# CONSTANTES
# ============================================================

URL_CAIXA_LOTOFACIL = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil"

TODAS_DEZENAS = [str(i).zfill(2) for i in range(1, 26)]

# ============================================================
# FUNÇÕES DE BUSCA NA CAIXA
# ============================================================

@st.cache_data(ttl=900)
def buscar_ultimo_concurso_caixa():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json,text/plain,*/*",
        "Referer": "https://loterias.caixa.gov.br/Paginas/Lotofacil.aspx"
    }

    resposta = requests.get(
        URL_CAIXA_LOTOFACIL,
        headers=headers,
        timeout=20
    )

    resposta.raise_for_status()
    dados = resposta.json()

    return normalizar_dados_concurso(dados)


@st.cache_data(ttl=900)
def buscar_concurso_caixa(numero_concurso):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json,text/plain,*/*",
        "Referer": "https://loterias.caixa.gov.br/Paginas/Lotofacil.aspx"
    }

    url = f"{URL_CAIXA_LOTOFACIL}/{numero_concurso}"

    resposta = requests.get(
        url,
        headers=headers,
        timeout=20
    )

    resposta.raise_for_status()
    dados = resposta.json()

    return normalizar_dados_concurso(dados)


@st.cache_data(ttl=900)
def buscar_ultimos_concursos_caixa(quantidade):
    ultimo = buscar_ultimo_concurso_caixa()
    numero_ultimo = int(ultimo["numero"])

    concursos = []

    for numero in range(numero_ultimo, numero_ultimo - quantidade, -1):
        try:
            concursos.append(buscar_concurso_caixa(numero))
        except:
            pass

    return sorted(concursos, key=lambda x: int(x["numero"]))


def normalizar_dados_concurso(dados):
    numero = dados.get("numero", "")
    data = dados.get("dataApuracao", "")
    local = dados.get("localSorteio", "")
    municipio = dados.get("nomeMunicipioUFSorteio", "")

    dezenas = dados.get("listaDezenas", [])
    dezenas = [str(d).zfill(2) for d in dezenas]

    return {
        "numero": numero,
        "data": data,
        "local": local,
        "municipio": municipio,
        "dezenas": dezenas
    }

# ============================================================
# FUNÇÕES DE ANÁLISE
# ============================================================

def calcular_frequencia(concursos):
    contador = Counter()

    for concurso in concursos:
        contador.update(concurso["dezenas"])

    return {dez: contador.get(dez, 0) for dez in TODAS_DEZENAS}


def classificar_dezenas(frequencia):
    ordenadas = sorted(
        frequencia.items(),
        key=lambda x: (-x[1], int(x[0]))
    )

    fortes = [d for d, f in ordenadas[:5]]
    fracas = [d for d, f in ordenadas[-6:]]

    intermediarias = [
        d for d, f in ordenadas
        if d not in fortes and d not in fracas
    ]

    return fortes, intermediarias, fracas, ordenadas


def montar_base_18(fortes, intermediarias, fracas):
    base = []

    base.extend(fortes[:5])
    base.extend(intermediarias[:11])
    base.extend(fracas[:2])

    return sorted(list(set(base)), key=lambda x: int(x))


def gerar_jogos(base, quantidade_jogos, dezenas_por_jogo=15):
    jogos = set()
    tentativas = 0

    while len(jogos) < quantidade_jogos and tentativas < 10000:
        jogo = tuple(
            sorted(
                random.sample(base, dezenas_por_jogo),
                key=lambda x: int(x)
            )
        )

        jogos.add(jogo)
        tentativas += 1

    return [list(j) for j in jogos]


def jogos_para_csv(jogos):
    dados = []

    for idx, jogo in enumerate(jogos, 1):
        linha = {"Jogo": idx}

        for pos, dez in enumerate(jogo, 1):
            linha[f"D{pos}"] = dez

        dados.append(linha)

    df = pd.DataFrame(dados)

    buf = io.StringIO()
    df.to_csv(buf, index=False, sep=";")

    return buf.getvalue()


def render_dezenas(dezenas, classe_css):
    html = ""

    for dez in dezenas:
        html += f'<span class="dezena {classe_css}">{dez}</span>'

    st.markdown(html, unsafe_allow_html=True)


def render_jogo(jogo, idx):
    html = ""

    for dez in jogo:
        html += f'<span class="dezena">{dez}</span>'

    st.markdown(
        f"""
<div class="jogo">
    <strong>Jogo {idx:02d}</strong> — {html}
</div>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown("## 🍀 Menu Principal")
st.sidebar.markdown("---")
st.sidebar.markdown("### uma seção:")
st.sidebar.markdown("🔴 📊 **Painel de controle**")
st.sidebar.markdown("1️⃣ Últimos concursos")
st.sidebar.markdown("2️⃣ Frequência das bolas")
st.sidebar.markdown("3️⃣ Leitura estatística")
st.sidebar.markdown("4️⃣ Estratégia próximo sorteio")
st.sidebar.markdown("5️⃣ Base de 18 dezenas")
st.sidebar.markdown("6️⃣ Dezenas fora")
st.sidebar.markdown("7️⃣ Desdobramento jogos")
st.sidebar.markdown("8️⃣ Matemática aleatória")
st.sidebar.markdown("✅ Resumo final")
st.sidebar.markdown("---")

st.sidebar.markdown("## 🎯 Filtros rápidos")

quantidade_concursos = st.sidebar.number_input(
    "Quantidade de concursos para análise",
    min_value=1,
    max_value=100,
    value=11,
    step=1
)

quantidade_jogos = st.sidebar.number_input(
    "Quantidade de jogos para chance simulada",
    min_value=1,
    max_value=100,
    value=12,
    step=1
)

if st.sidebar.button("🔄 Atualizar sorteio da Caixa"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")

st.sidebar.markdown(
    """
<div style="
    background:#284769;
    padding:14px;
    border-radius:8px;
    color:#dbeafe;
    font-size:14px;
    line-height:1.5;
">
    Análise baseada automaticamente nos últimos concursos da Lotofácil
    carregados diretamente da Caixa. Uso estatístico e combinatório,
    sem garantia de premiação.
</div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# TÍTULO
# ============================================================

st.markdown("# 🍀 Lotofácil | Análises e Desdobramentos")
st.markdown("### Painel estatístico com base nos últimos concursos analisados")

# ============================================================
# BUSCA AUTOMÁTICA NA CAIXA
# ============================================================

try:
    ultimo_concurso = buscar_ultimo_concurso_caixa()
    concursos = buscar_ultimos_concursos_caixa(quantidade_concursos)

except:
    st.error("Não foi possível buscar automaticamente os dados da Caixa.")
    st.warning("Verifique sua internet ou tente novamente.")
    st.stop()

# ============================================================
# ÚLTIMO SORTEIO NO TOPO
# ============================================================

numero_ultimo = ultimo_concurso["numero"]
data_ultimo = ultimo_concurso["data"]
dezenas_ultimo = ultimo_concurso["dezenas"]
dezenas_ultimo_texto = " ".join(dezenas_ultimo)

local_sorteio = ultimo_concurso["local"]
municipio_sorteio = ultimo_concurso["municipio"]

if municipio_sorteio:
    texto_local = municipio_sorteio
elif local_sorteio:
    texto_local = local_sorteio
else:
    texto_local = "Local não informado"

html_dezenas_resultado = "".join(
    [f'<span class="dezena-resultado">{dez}</span>' for dez in dezenas_ultimo]
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
# INFO DO PAINEL
# ============================================================

st.markdown(
    """
<div class="info-box">
    Este painel reúne uma análise estatística feita para a Lotofácil,
    incluindo frequência das dezenas, seleção de base com 18 números,
    dezenas temporariamente descartadas, geração de jogos e leitura
    combinatória.
</div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# CÁLCULOS PRINCIPAIS
# ============================================================

frequencia = calcular_frequencia(concursos)

fortes, intermediarias, fracas, ordenadas = classificar_dezenas(frequencia)

base_18 = montar_base_18(
    fortes,
    intermediarias,
    fracas
)

total_combinacoes_lotofacil = math.comb(25, 15)
total_combinacoes_base_18 = math.comb(18, 15)

jogos_gerados = gerar_jogos(
    base=base_18,
    quantidade_jogos=quantidade_jogos,
    dezenas_por_jogo=15
)

# ============================================================
# CARDS RESUMO
# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
<div class="card">
    <div class="card-title">Concursos analisados</div>
    <div class="card-value">{len(concursos)}</div>
</div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
<div class="card">
    <div class="card-title">Total de combinações da Lotofácil</div>
    <div class="card-value">{total_combinacoes_lotofacil:,}</div>
</div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
<div class="card">
    <div class="card-title">Base sugerida</div>
    <div class="card-value">{len(base_18)}</div>
</div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"""
<div class="card">
    <div class="card-title">Desdobramento</div>
    <div class="card-value">{quantidade_jogos} jogos</div>
</div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

# ============================================================
# VISÃO GERAL DA ANÁLISE
# ============================================================

st.markdown("## 📊 Visão Geral da Análise")

col_esq, col_dir = st.columns([1, 1])

with col_esq:
    st.markdown("### 🔥 Dezenas mais fortes")
    render_dezenas(fortes, "forte")

    st.markdown("### ⚖️ Grupo intermediário")
    render_dezenas(intermediarias, "intermediaria")

    st.markdown("### ❄️ Dezenas mais fracas no recorte")
    render_dezenas(fracas, "fraca")

    st.markdown("### 🎯 Base principal sugerida com 18 dezenas")
    render_dezenas(base_18, "base")

with col_dir:
    st.markdown(
        f"### Frequência das dezenas nos últimos {len(concursos)} concursos"
    )

    df_freq = pd.DataFrame(
        {
            "Dezena": list(frequencia.keys()),
            "Frequência": list(frequencia.values())
        }
    )

    df_freq["Dezena_Num"] = df_freq["Dezena"].astype(int)
    df_freq = df_freq.sort_values("Dezena_Num")

    st.bar_chart(
        df_freq.set_index("Dezena")["Frequência"]
    )

# ============================================================
# ÚLTIMOS CONCURSOS
# ============================================================

st.markdown("## 🧾 Últimos concursos carregados da Caixa")

dados_concursos = []

for concurso in concursos:
    dados_concursos.append(
        {
            "Concurso": concurso["numero"],
            "Data": concurso["data"],
            "Dezenas": " ".join(concurso["dezenas"])
        }
    )

df_concursos = pd.DataFrame(dados_concursos)

st.dataframe(
    df_concursos,
    use_container_width=True,
    hide_index=True
)

# ============================================================
# FREQUÊNCIA DETALHADA
# ============================================================

st.markdown("## 🔢 Frequência detalhada das dezenas")

df_freq_tabela = pd.DataFrame(
    [
        {
            "Dezena": dez,
            "Frequência": freq
        }
        for dez, freq in sorted(
            frequencia.items(),
            key=lambda x: int(x[0])
        )
    ]
)

st.dataframe(
    df_freq_tabela,
    use_container_width=True,
    hide_index=True
)

# ============================================================
# DEZENAS FORA DA BASE
# ============================================================

dezenas_fora = [
    dez for dez in TODAS_DEZENAS
    if dez not in base_18
]

st.markdown("## 🚫 Dezenas fora da base sugerida")

render_dezenas(dezenas_fora, "fraca")

# ============================================================
# GERAÇÃO DE JOGOS
# ============================================================

st.markdown(f"## 🎲 Desdobramento gerado — {quantidade_jogos} jogos")

for idx, jogo in enumerate(jogos_gerados, 1):
    render_jogo(jogo, idx)

# ============================================================
# DOWNLOAD CSV
# ============================================================

csv_jogos = jogos_para_csv(jogos_gerados)

st.download_button(
    "⬇️ Baixar jogos gerados em CSV",
    data=csv_jogos,
    file_name=f"lotofacil_jogos_concurso_{numero_ultimo}.csv",
    mime="text/csv"
)

# ============================================================
# RESUMO FINAL
# ============================================================

st.markdown("## ✅ Resumo final")

st.markdown(
    f"""
- **Último concurso carregado automaticamente:** {numero_ultimo}
- **Data do último sorteio:** {data_ultimo}
- **Dezenas sorteadas:** {dezenas_ultimo_texto}
- **Concursos analisados:** {len(concursos)}
- **Base sugerida:** {" ".join(base_18)}
- **Dezenas fora da base:** {" ".join(dezenas_fora)}
- **Jogos gerados:** {quantidade_jogos}
- **Total de combinações possíveis da Lotofácil:** {total_combinacoes_lotofacil:,}
- **Total de combinações dentro da base de 18 dezenas:** {total_combinacoes_base_18:,}
    """.replace(",", ".")
)

st.warning(
    "Atenção: esta ferramenta faz análise estatística e combinatória. "
    "Ela não garante premiação, acerto ou resultado futuro."
)
