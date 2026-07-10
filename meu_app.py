import streamlit as st
import pandas as pd
import requests
import itertools
import math
import random

from collections import Counter


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Lotofácil | Análises e Desdobramentos",
    page_icon="🍀",
    layout="wide"
)


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
        font-size: 20px;
        color: #dbeafe;
        font-weight: 700;
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

    .stButton button {
        background-color: #1e88ff;
        color: white;
        border-radius: 8px;
        font-weight: 800;
        border: none;
    }

    .stDownloadButton button {
        background-color: #16a34a;
        color: white;
        border-radius: 8px;
        font-weight: 800;
        border: none;
    }
</style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CONFIGURAÇÕES GERAIS
# ============================================================

BASE_URL = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil"
UNIVERSO_DEZENAS = [str(i).zfill(2) for i in range(1, 26)]


# ============================================================
# ESTADO DA APLICAÇÃO
# ============================================================

if "jogos_gerados" not in st.session_state:
    st.session_state.jogos_gerados = []

if "numero_geracao" not in st.session_state:
    st.session_state.numero_geracao = 0

if "conferencia_resultado" not in st.session_state:
    st.session_state.conferencia_resultado = None


# ============================================================
# FUNÇÕES DE BUSCA NA CAIXA
# ============================================================

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
    dezenas = [str(dezena).zfill(2) for dezena in dezenas]

    return {
        "numero": dados.get("numero"),
        "data": dados.get("dataApuracao"),
        "dezenas": dezenas,
        "municipio": (
            dados.get("nomeMunicipioUFSorteio")
            or dados.get("nomeMunicipioSorteio")
        ),
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

    df_freq = pd.DataFrame({
        "dezena": UNIVERSO_DEZENAS,
        "frequencia": [
            frequencia.get(dezena, 0)
            for dezena in UNIVERSO_DEZENAS
        ]
    })

    df_freq = df_freq.sort_values(
        by=["frequencia", "dezena"],
        ascending=[False, True]
    ).reset_index(drop=True)

    return df_freq


def calcular_atrasos(concursos):
    atrasos = {}

    for dezena in UNIVERSO_DEZENAS:
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
    numeros = [int(numero) for numero in jogo]

    pares = sum(1 for numero in numeros if numero % 2 == 0)
    impares = 15 - pares
    soma = sum(numeros)

    repetidas_ultimo = len(
        set(jogo).intersection(set(ultimo_resultado))
    )

    return {
        "pares": pares,
        "impares": impares,
        "soma": soma,
        "repetidas_ultimo": repetidas_ultimo
    }


def pontuar_jogo(jogo, mapa_freq, mapa_atraso):
    score_freq = sum(mapa_freq.get(dezena, 0) for dezena in jogo)
    score_atraso = sum(mapa_atraso.get(dezena, 0) for dezena in jogo)

    return score_freq + (score_atraso * 0.25)


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
    sobreposicao_max,
    seed=None
):
    rng = random.Random(seed)

    jogos_validos = []

    for combinacao in itertools.combinations(base, 15):
        jogo = list(combinacao)

        stats = estatisticas_jogo(jogo, ultimo_resultado)

        if not pares_min <= stats["pares"] <= pares_max:
            continue

        if not soma_min <= stats["soma"] <= soma_max:
            continue

        if not repetidas_min <= stats["repetidas_ultimo"] <= repetidas_max:
            continue

        pontos = pontuar_jogo(jogo, mapa_freq, mapa_atraso)

        jogos_validos.append({
            "jogo": jogo,
            "score": pontos,
            "pares": stats["pares"],
            "impares": stats["impares"],
            "soma": stats["soma"],
            "repetidas_ultimo": stats["repetidas_ultimo"],
            "desempate": rng.random()
        })

    jogos_validos = sorted(
        jogos_validos,
        key=lambda item: (item["score"], item["desempate"]),
        reverse=True
    )

    selecionados = []

    for item in jogos_validos:
        jogo_atual = set(item["jogo"])

        if not selecionados:
            selecionados.append(item)
        else:
            aprovado = True

            for selecionado in selecionados:
                jogo_selecionado = set(selecionado["jogo"])

                intersecao = len(
                    jogo_atual.intersection(jogo_selecionado)
                )

                if intersecao > sobreposicao_max:
                    aprovado = False
                    break

            if aprovado:
                selecionados.append(item)

        if len(selecionados) >= qtd_jogos:
            break

    # Completa a quantidade solicitada se a regra de sobreposição
    # não permitir selecionar jogos suficientes.
    if len(selecionados) < qtd_jogos:
        for item in jogos_validos:
            if item not in selecionados:
                selecionados.append(item)

            if len(selecionados) >= qtd_jogos:
                break

    for item in selecionados:
        item.pop("desempate", None)

    return selecionados[:qtd_jogos]


def jogos_para_csv(jogos):
    linhas = []

    for indice, item in enumerate(jogos, start=1):
        linha = {
            "Jogo": indice,
            "Dezenas": " ".join(item["jogo"]),
            "Pares": item["pares"],
            "Ímpares": item["impares"],
            "Soma": item["soma"],
            "Repetidas do último": item["repetidas_ultimo"],
            "Score": round(item["score"], 2)
        }

        for posicao, dezena in enumerate(item["jogo"], start=1):
            linha[f"D{posicao:02d}"] = dezena

        linhas.append(linha)

    df_csv = pd.DataFrame(linhas)

    return df_csv.to_csv(
        index=False,
        sep=";",
        encoding="utf-8-sig"
    )


# ============================================================
# CABEÇALHO
# ============================================================

st.markdown("# 🍀 Lotofácil | Análises e Desdobramentos")

st.markdown(
    """
<div class="subtitulo">
    Painel estatístico com base nos últimos concursos analisados
</div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# ÚLTIMO SORTEIO
# ============================================================

try:
    ultimo_concurso = buscar_concurso()

except Exception:
    st.error(
        "Não foi possível carregar o último concurso automaticamente da Caixa."
    )
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
    [
        f'<span class="dezena-resultado">{dezena}</span>'
        for dezena in dezenas_ultimo
    ]
)

st.markdown(
    f"""
<div class="ultimo-sorteio">
    <div class="ultimo-label">
        🍀 Último sorteio carregado automaticamente da Caixa
    </div>

    <div class="ultimo-concurso">
        Concurso {numero_ultimo} — {data_ultimo}
    </div>

    <div class="ultimo-local">
        Sorteio realizado em: <strong>{texto_local}</strong>
    </div>

    <div class="dezenas-resultado-container">
        {html_dezenas_resultado}
    </div>
</div>
    """,
    unsafe_allow_html=True
)


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
    max_value=20,
    value=18,
    step=1,
    help="O limite de 20 evita excesso de combinações e lentidão."
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
    options=UNIVERSO_DEZENAS,
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
# VALIDAÇÃO DOS FILTROS
# ============================================================

if pares_min > pares_max:
    st.sidebar.error("O mínimo de pares não pode ser maior que o máximo.")

if soma_min > soma_max:
    st.sidebar.error("A soma mínima não pode ser maior que a soma máxima.")

if repetidas_min > repetidas_max:
    st.sidebar.error(
        "O mínimo de repetidas não pode ser maior que o máximo."
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

mapa_freq = dict(
    zip(df_freq["dezena"], df_freq["frequencia"])
)

mapa_atraso = dict(
    zip(df_atrasos["dezena"], df_atrasos["atraso"])
)


# ============================================================
# VISÃO GERAL
# ============================================================

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown("## 📊 Visão Geral da Análise")

coluna_1, coluna_2 = st.columns(2)

with coluna_1:
    st.markdown("### 🔥 Dezenas mais fortes")

    dezenas_fortes = df_freq.head(10)

    html_fortes = "".join(
        [
            f'<span class="dezena-base">{linha["dezena"]}</span>'
            for _, linha in dezenas_fortes.iterrows()
        ]
    )

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

with coluna_2:
    st.markdown(
        f"### 📈 Frequência das dezenas nos últimos {len(concursos)} concursos"
    )

    grafico_freq = df_freq.sort_values("dezena")

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

coluna_1, coluna_2 = st.columns(2)

with coluna_1:
    dezenas_atrasadas = df_atrasos.head(10)

    html_atrasadas = "".join(
        [
            f'<span class="dezena-fria">{linha["dezena"]}</span>'
            for _, linha in dezenas_atrasadas.iterrows()
        ]
    )

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

with coluna_2:
    grafico_atrasos = df_atrasos.sort_values("dezena")

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
    df_base = df_base[
        ~df_base["dezena"].isin(dezenas_para_descartar)
    ]

base_sugerida = df_base.head(tamanho_base)["dezena"].tolist()

base_sugerida = sorted(
    base_sugerida,
    key=lambda dezena: int(dezena)
)

html_base = "".join(
    [
        f'<span class="dezena-base">{dezena}</span>'
        for dezena in base_sugerida
    ]
)

st.markdown(html_base, unsafe_allow_html=True)

if dezenas_para_descartar:
    st.warning(
        "Dezenas descartadas temporariamente: "
        + ", ".join(dezenas_para_descartar)
    )

st.caption(
    "A base é formada pelas dezenas mais frequentes dentro do período "
    "analisado, desconsiderando as dezenas descartadas."
)


# ============================================================
# GERAÇÃO DO DESDOBRAMENTO
# ============================================================

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown("## 🧩 Geração de jogos")

jogos_gerados = st.session_state.jogos_gerados

if len(base_sugerida) < 15:
    st.error("A base sugerida precisa ter pelo menos 15 dezenas.")
    st.session_state.jogos_gerados = []
    jogos_gerados = []

else:
    total_combinacoes_base = math.comb(len(base_sugerida), 15)

    st.info(
        f"A base atual possui {len(base_sugerida)} dezenas e gera "
        f"**{total_combinacoes_base:,}** combinações possíveis de 15 dezenas."
        .replace(",", ".")
    )

    coluna_gerar, coluna_texto = st.columns([1, 2])

    with coluna_gerar:
        gerar_novo = st.button(
            "🔄 Gerar novo desdobramento",
            use_container_width=True,
            type="primary"
        )

    with coluna_texto:
        st.caption(
            "Após alterar filtros, base ou quantidade de jogos, "
            "clique neste botão para gerar um novo desdobramento."
        )

    if gerar_novo:
        if pares_min > pares_max:
            st.error("Corrija os filtros de pares antes de gerar os jogos.")

        elif soma_min > soma_max:
            st.error("Corrija os filtros de soma antes de gerar os jogos.")

        elif repetidas_min > repetidas_max:
            st.error("Corrija os filtros de repetidas antes de gerar os jogos.")

        else:
            st.session_state.numero_geracao += 1

            with st.spinner("Gerando novo desdobramento..."):
                st.session_state.jogos_gerados = gerar_desdobramento(
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
                    sobreposicao_max=sobreposicao_max,
                    seed=st.session_state.numero_geracao
                )

            st.session_state.conferencia_resultado = None

    jogos_gerados = st.session_state.jogos_gerados

    if not jogos_gerados:
        st.warning(
            "Nenhum jogo foi gerado ainda. "
            "Clique em **Gerar novo desdobramento**."
        )

    else:
        st.success(f"{len(jogos_gerados)} jogos gerados com sucesso.")

        for indice, item in enumerate(jogos_gerados, start=1):
            html_jogo = "".join(
                [
                    f'<span class="dezena-jogo">{dezena}</span>'
                    for dezena in item["jogo"]
                ]
            )

            st.markdown(
                f"""
<div class="jogo-box">
    <div class="jogo-titulo">Jogo {indice}</div>

    <div>{html_jogo}</div>

    <div style="margin-top:10px;color:#cbd5e1;font-size:13px;">
        Pares: <strong>{item["pares"]}</strong> |
        Ímpares: <strong>{item["impares"]}</strong> |
        Soma: <strong>{item["soma"]}</strong> |
        Repetidas do último: <strong>{item["repetidas_ultimo"]}</strong> |
        Score: <strong>{round(item["score"], 2)}</strong>
    </div>
</div>
                """,
                unsafe_allow_html=True
            )

        csv_jogos = jogos_para_csv(jogos_gerados)

        st.download_button(
            label="⬇️ Baixar jogos em CSV",
            data=csv_jogos,
            file_name="desdobramento_lotofacil.csv",
            mime="text/csv"
        )


# ============================================================
# CONFERÊNCIA DOS JOGOS
# ============================================================

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown("## 🔎 Conferência dos jogos")

if not jogos_gerados:
    st.info(
        "Gere um desdobramento antes de realizar a conferência."
    )

else:
    coluna_concurso, coluna_botao = st.columns([2, 1])

    with coluna_concurso:
        concurso_conferencia = st.number_input(
            "Informe o número do concurso para conferir",
            min_value=1,
            value=int(numero_ultimo),
            step=1
        )

    with coluna_botao:
        st.markdown("<br>", unsafe_allow_html=True)

        conferir_jogos = st.button(
            "🔎 Conferir jogos",
            use_container_width=True
        )

    if conferir_jogos:
        try:
            with st.spinner("Consultando resultado do concurso..."):
                resultado_conferencia = buscar_concurso(
                    int(concurso_conferencia)
                )

            dezenas_sorteadas = resultado_conferencia["dezenas"]
            dezenas_sorteadas_set = set(dezenas_sorteadas)

            linhas_conferencia = []

            for indice, item in enumerate(jogos_gerados, start=1):
                jogo = item["jogo"]

                acertos = sorted(
                    set(jogo).intersection(dezenas_sorteadas_set),
                    key=lambda dezena: int(dezena)
                )

                linhas_conferencia.append({
                    "Jogo": indice,
                    "Acertos": len(acertos),
                    "Dezenas acertadas": " ".join(acertos),
                    "Dezenas do jogo": " ".join(jogo)
                })

            st.session_state.conferencia_resultado = {
                "numero": resultado_conferencia["numero"],
                "data": resultado_conferencia["data"],
                "dezenas": dezenas_sorteadas,
                "linhas": linhas_conferencia
            }

        except Exception:
            st.error(
                "Não foi possível consultar esse concurso. "
                "Verifique o número e tente novamente."
            )

    conferencia = st.session_state.conferencia_resultado

    if conferencia:
        html_dezenas_conferencia = "".join(
            [
                f'<span class="dezena-resultado">{dezena}</span>'
                for dezena in conferencia["dezenas"]
            ]
        )

        st.markdown(
            f"""
<div class="ultimo-sorteio">
    <div class="ultimo-label">
        Resultado utilizado para conferência
    </div>

    <div class="ultimo-concurso">
        Concurso {conferencia["numero"]} — {conferencia["data"]}
    </div>

    <div class="dezenas-resultado-container">
        {html_dezenas_conferencia}
    </div>
</div>
            """,
            unsafe_allow_html=True
        )

        df_conferencia = pd.DataFrame(conferencia["linhas"])

        maior_acerto = int(df_conferencia["Acertos"].max())

        if maior_acerto >= 11:
            st.success(
                f"🏆 Maior pontuação encontrada: {maior_acerto} acertos."
            )
        else:
            st.info(
                f"Maior pontuação encontrada: {maior_acerto} acertos."
            )

        st.dataframe(
            df_conferencia.sort_values(
                by=["Acertos", "Jogo"],
                ascending=[False, True]
            ),
            use_container_width=True,
            hide_index=True
        )

        csv_conferencia = df_conferencia.to_csv(
            index=False,
            sep=";",
            encoding="utf-8-sig"
        )

        st.download_button(
            label="⬇️ Baixar conferência em CSV",
            data=csv_conferencia,
            file_name=f"conferencia_lotofacil_{conferencia['numero']}.csv",
            mime="text/csv"
        )


# ============================================================
# LEITURA COMBINATÓRIA
# ============================================================

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown("## 🧠 Leitura combinatória")

coluna_1, coluna_2, coluna_3 = st.columns(3)

with coluna_1:
    st.markdown("### Distribuição par/ímpar")

    if jogos_gerados:
        df_paridade = pd.DataFrame(jogos_gerados)

        st.dataframe(
            df_paridade[
                ["pares", "impares", "soma", "repetidas_ultimo"]
            ].rename(
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

with coluna_2:
    st.markdown("### Repetição do último concurso")

    if jogos_gerados:
        df_repeticoes = pd.DataFrame({
            "Jogo": list(range(1, len(jogos_gerados) + 1)),
            "Repetidas": [
                jogo["repetidas_ultimo"]
                for jogo in jogos_gerados
            ]
        })

        st.bar_chart(
            df_repeticoes,
            x="Jogo",
            y="Repetidas",
            use_container_width=True
        )
    else:
        st.caption("Gere jogos para visualizar esta leitura.")

with coluna_3:
    st.markdown("### Faixa de soma")

    if jogos_gerados:
        somas = [jogo["soma"] for jogo in jogos_gerados]

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
# RESUMO FINAL
# ============================================================

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown("## 📌 Resumo do painel")

st.markdown(
    """
<div class="info-box">
    Este painel reúne análise de frequência, atrasos, formação de base,
    filtros combinatórios, geração de desdobramentos e conferência
    dos jogos com resultados oficiais consultados na Caixa.
</div>
    """,
    unsafe_allow_html=True
)

total_combinacoes_lotofacil = math.comb(25, 15)

coluna_1, coluna_2, coluna_3, coluna_4 = st.columns(4)

with coluna_1:
    st.markdown(
        f"""
<div class="metric-card">
    <div class="metric-label">Concursos analisados</div>
    <div class="metric-value">{len(concursos)}</div>
</div>
        """,
        unsafe_allow_html=True
    )

with coluna_2:
    st.markdown(
        f"""
<div class="metric-card">
    <div class="metric-label">Combinações da Lotofácil</div>
    <div class="metric-value">
        {total_combinacoes_lotofacil:,}
    </div>
</div>
        """.replace(",", "."),
        unsafe_allow_html=True
    )

with coluna_3:
    st.markdown(
        f"""
<div class="metric-card">
    <div class="metric-label">Base sugerida</div>
    <div class="metric-value">{len(base_sugerida)}</div>
</div>
        """,
        unsafe_allow_html=True
    )

with coluna_4:
    st.markdown(
        f"""
<div class="metric-card">
    <div class="metric-label">Desdobramento atual</div>
    <div class="metric-value">{len(jogos_gerados)} jogos</div>
</div>
        """,
        unsafe_allow_html=True
    )

st.markdown(
    """
<br>
<div style="color:#94a3b8;font-size:13px;text-align:center;">
    Análise estatística e combinatória. Este painel não garante premiação
    e não substitui uma decisão pessoal de jogo.
</div>
    """,
    unsafe_allow_html=True
)
